import requests
import json
import base64
import re
import sys
import socket
import binascii
import time

class Statseeker():
    """
    This class is used to perform all functions from within Statseeker RestAPI.  The restAPI user and URL are hard coded in the top of the class and used in many functions.
    """

    def __init__(self):
        """
        Runs every call to class Statseeker.  Includes get_headers().
        Inputs: None
        Outputs: None
        """
        #Every call to class Statseeker will need headers
        self.headers = self.get_headers()

    def get_headers(self):
        """
        Creates the login information for Statseeker RestAPI.
        Inputs: None
        Outputs:
            - headers: Request Headers
        """

        user = "admin"
        pwd = "tabz-et6f^"

        #use username and password from class
        basic_data = user + ":" + pwd
        basic_data = basic_data.encode("ascii")
        auth_data = base64.b64encode(basic_data)

        #Set ISE restAPI header information into dictionary
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            }
        #create Authorization header in headers dictionary
        headers["Authorization"] = "Basic " + auth_data.decode()
        #print (headers)
        return (headers)

    def get_device(self,deviceIp):
        """
        Get device details
        Inputs:
            -deviceIp: IPv4 address of device
        Outputs:
            -result: Results from method
        """

        result = {
            'success': False,
            'response': '',
            'error': '',
        }

        params = {
            'fields': ["sysName","ipaddress"],
            'ipaddress_filter': "IS(\"" + deviceIp + "\")"
        }
        #check danforth server
        server_url = "https://statseeker.nts.wustl.edu/api/"
        url = server_url + "v2.1/cdt_device"
        resp = requests.get(url,params = params, headers=self.headers, verify=False)
        num_devices = resp.json()['data']['objects'][0]['data_total']

        if num_devices == 1:
            dnfResult = resp.json()['data']['objects'][0]['data'][0]['id']

        else:
            dnfResult = []

        #check med server
        server_url = "https://128.252.8.3/api/"
        url = server_url + "v2.1/cdt_device"
        resp = requests.get(url,params = params, headers=self.headers, verify=False)
        num_devices = resp.json()['data']['objects'][0]['data_total']

        if num_devices == 1:
            medResult = resp.json()['data']['objects'][0]['data'][0]['id']

        else:
            medResult = []

        print ("Danforth:" + str(dnfResult) + " - Med: " + str(medResult))
        return (dnfResult,medResult)

    def device_add(self,deviceIp,deviceLocation):
        """
        Adds a device to Statseeker.
        Inputs:
            -deviceIp: IPv4 address of device
        Outputs:
            -result: Results from method
        """

        #set up the result default options
        result = {
            'success': False,
            'response': '',
            'error': '',
        }
        #set empty values
        responsednf = ''
        responsemed = ''
        #call the get_device query
        (dnfQuery,medQuery) = self.get_device(deviceIp)

        #if the dnfQuery doesn't come back empty, create a response
        print ("Danforth: " + str(dnfQuery))
        if dnfQuery != []:
            responsednf = "Device already exists in Danforth Statseeker"
        #if the medQuery doesn't come back empty, create a response
        print ("Med: " + str(medQuery))
        if medQuery != []:
            responsemed = "Device already exists in Med Statseeker"
        #create the results if the device exists
        if responsednf != '' or responsemed != '':
            result['response'] = responsednf,responsemed

        #if the device is found to already exist, exit the function and return the results
        if dnfQuery !=[] or medQuery != []:
            result['error'] = "None"
            return (result)

        #if you reach this point, the device does not exist, and you can continue to add it
        #determine which statseeker to add the device to
        if "Medical" in deviceLocation:
            server_url = "https://128.252.8.3/api/"

        else:
            server_url = "https://statseeker.nts.wustl.edu/api/"

        ###
        ###set up the function with the neccessary data
        ###
        #configure the url for adding a device and declare the data in the body
        url = server_url + "v2.1/discover/execute"

        params = {
            'mode': "single",
            'ip': deviceIp,
            'verbose': "0",
            'minimal': "true",
            'runPostProcessing': "false"
        }

        ###
        ###run the function main API calls
        ###
        #GET execute request to add device
        #Timeout the request in 5 seconds because statseeker takes 90 seconds to finish otherwise
        print ("ADDING DEVICE")
        try:
            resp = requests.get(url,params = params, headers=self.headers, verify=False, timeout=(5, 5))
        except requests.exceptions.Timeout:
            #if resp.status_code == 200:
            result['success'] = True
            result['response'] = deviceIp + " added successfully.  Please verify the device was added in Statseeker."
            result['error'] = "None"
            print (result)
            return (result)

    def device_delete(self,deviceIp):
        """
        Removes a device from Statseeker.
        Inputs:
            -deviceIp: IPv4 address of device
        Outputs:
            -result: Results from method
        """

        result = {
            'success': False,
            'response': '',
            'error': '',
        }

        #set empty values
        responsednf = ''
        responsemed = ''
        #call the get_device query
        (dnfQuery,medQuery) = self.get_device(deviceIp)

        #if the dnfQuery does come back empty, create a response
        if dnfQuery == []:
            responsednf = "Device does not exist in Danforth Statseeker"

        #if the medQuery does come back empty, create a response
        if medQuery == []:
            responsemed = "Device does not exist in Med Statseeker"

        #create the results if the device exists
        if responsednf != '' or responsemed != '':
            result['response'] = responsednf,responsemed

        #if the device is not found in either server, exit the function and return the results
        if dnfQuery ==[] and medQuery == []:
            result['error'] = "None"
            return (result)

        #if you reach this point, the device exists, and you can continue to remove it
        #determine which statseeker to remove the device from (or both)
        if dnfQuery != []:
            server_url = "https://statseeker.nts.wustl.edu/api/"
            url = server_url + "v2.1/cdt_device/" + str(dnfQuery)
            print ("REMOVING DEVICE FROM DANFORTH")
            #DELETE execute request to add device
            dnfresp = requests.delete(url, headers=self.headers, verify=False)

            if dnfresp.status_code == 200:
                result['success'] = True
                responsednf = deviceIp + " removed successfully from Danforth"
                responsemed = []
                result['error'] = "None"

            else:
                responsednf = resp.text
                result['error'] = resp.status_code

        if medQuery != []:
            server_url = "https://128.252.8.3/api/"
            url = server_url + "v2.1/cdt_device/" + str(medQuery)
            print ("REMOVING DEVICE FROM MED")
            #DELETE execute request to add device
            #medresp = requests.delete(url, headers=self.headers, verify=False)

            if medresp.status_code == 200:
                result['success'] = True
                responsemed = deviceIp + " removed successfully from Med"
                result['error'] = "None"

            else:
                result['error'] = resp.status_code

        result['response'] = responsednf,responsemed
        print (result)
        return (result)
