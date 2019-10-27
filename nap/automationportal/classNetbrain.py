#####
#####
#####
#Written for NetBrain version 7.1a
#####
#####
#####

import requests
import json
import base64
import re
import sys
import datetime
import glob
import os
import difflib
import smtplib
import time
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email import encoders

class Netbrain():
    """
    This class is used to perform all functions from within NetBrain RestAPI.
    The restAPI user and URL are hard coded in the top of the class and used in many functions.
    """

    #set NetBrain restapi username and password
    #this section is the only thing you should have to edit
    user = "restapi"
    pwd = "ysBzuRGn1kPM6MYxUxey74qb"
    authentication_id = "Tacacs"

    tenant = "1cef537c-00ed-9d83-5245-557177282203"
    domain = "36d3d870-4ba2-4f93-a60e-d80e7c30a22c"

    #set ISE base restAPI url
    server_url = "https://netbrain.net.wustl.edu/ServicesAPI/API/"

    def __init__(self):
        """
        Runs every call to class NetBrain.  Includes get_headers(), get_token(), and set_domain().
        Inputs: None
        Outputs: None
        """

        #Every call will need headers
        self.headers = self.get_headers()
        self.token = self.get_token()
        self.set_domain = self.set_domain()

    def get_headers(self):
        """
        Creates the login information for NetBrain RestAPI.
        Inputs: None
        Outputs:
            - headers: Request Headers
        """
        #Set restAPI header information into dictionary
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            }

        return (headers)

    def get_token(self):
        """
        Retrieves a token for NetBrain RestAPI.
        Inputs: None
        Outputs:
            - token: Authentication token
        """

        #set url
        url = self.server_url + "V1/Session"
        #set data
        #this is where the login goes
        #Authentication_id is required for external users only
        data = {
            "username": self.user,
            "password": self.pwd,
            "authentication_id": self.authentication_id
        }
        #run api call
        resp = requests.post(url,data=json.dumps(data),headers=self.headers, verify=True)

        token = resp.json()["token"]
        self.headers["Token"] = token
        print ("I GOT A NETBRAIN TOKEN!!!: " + token)
        return (token)

    def set_domain(self):
        """
        Retrieves a token for NetBrain RestAPI.
        Inputs:
            -tenant: NetBrain tenant
            -domain: NetBrain domain
        Outputs: None
        """

        #set url
        url = self.server_url + "V1/Session/CurrentDomain"
        #set data
        data = {
        	"tenantId": self.tenant,
        	"domainId": self.domain
        }

        #run api call
        resp = requests.put(url,data=json.dumps(data),headers=self.headers, verify=True)

    def logout(self):
        url= self.server_url + "V1/Session"
        data = {
            "token": self.token
        }
        resp = requests.delete(url,data=json.dumps(data),headers=self.headers, verify=True)
        print ("I LOGGED OUT OF NETBRAIN!!!")
        return (resp.text)

    def device_query(self,deviceIp):
        """
        Checks to see if a device exists in NetBrain.
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
        ###
        #Query IP of device
        ###
        #set url
        url = self.server_url + "V1/CMDB/Devices"

        ###
        ###run the function main API calls
        ###
        #set params
        params = {
            "ip": deviceIp
        }
        #run api call
        resp = requests.get(url, params=params, headers=self.headers, verify=True)
        #set value for the output of the devices
        exists = resp.json()['devices']
        #if the devic does not exist, the output will be a blank list
        if exists != []:
            result['success'] = True
            result['response'] = resp.text
            result['error'] = "None"
            return (result)
        #otherwise set the result as a blank list
        else:
            result = []
            return (result)

    def device_add(self,deviceIp):
        """
        Adds a device to NetBrain.
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

        #run a device query
        #if the device already exists, exit out with a message
        #if the device does not exist, continue to add
        deviceQuery = self.device_query(deviceIp)
        if deviceQuery != []:
            result['response'] = "Device already exists"
            result['error'] = "None"
            return (result)

        ###
        #Add IP to Seeds of Discovery Task
        #This will add the requested IP address as a seed device in the existing API discovery task
        #This is a new feature in NetBrain 7.1.  It can be tracked by logging in and looking at run history.
        ###
        #set url
        #url must include discovery task ID
        url = self.server_url + "V1/CMDB/Discovery/Tasks/2c2aa0e6-a0b4-d8cc-59c7-7ae14ae3b424/Seeds"
        #set data
        data={
            "seeds": [
                {
                    "mgmtIP": deviceIp,
                    #allow ssh only
                    "cliType": "1"
                }
            ]
        }
        #run api call
        resp = requests.post(url,data=json.dumps(data),headers=self.headers, verify=True)

        ###
        #Run Discovery Task
        #This will run the discovery task with the included IP address in the above step
        ###
        #set url
        url = self.server_url + "V1/CMDB/Discovery/Tasks/2c2aa0e6-a0b4-d8cc-59c7-7ae14ae3b424/Run"
        #run api call
        resp = requests.post(url,headers=self.headers, verify=True)

        ###
        #Get status of discovery task
        ###
        #set url
        url = self.server_url + "V1/CMDB/Discovery/Tasks/2c2aa0e6-a0b4-d8cc-59c7-7ae14ae3b424/Status"
        resp = requests.get(url,headers=self.headers, verify=True)
        #run api call over and over until the task status is no longer "running" which is number 2
        #status of 10 is complete.  Anything else should be printed in the result page

        while True:
            resp = requests.get(url,headers=self.headers, verify=True)
            if resp.json()["taskStatus"] != 2:
                print (str(resp.json()["taskStatus"]))
                break
            #wait 2 seconds in between checks.  No point in checking too often.
            time.sleep(2)

        #create a value for the task status number
        taskStatus = resp.json()["taskStatus"]

        ###
        #Get results of discovery task
        ###
        #set url
        url = self.server_url + "V1/CMDB/Discovery/Tasks/2c2aa0e6-a0b4-d8cc-59c7-7ae14ae3b424/Results"
        #run api call
        resp = requests.get(url,headers=self.headers, verify=True)

        #display success results
        if taskStatus == 10:
            result['success'] = True
            result['response'] = resp.text
            result['error'] = "None"
            print (result)
            return (result)
        #display failure results
        else:
            result['response'] = resp.text + " TaskStatus: " + taskStatus
            result['error'] = resp.status_code
            print (result)
            return (result)

    def device_delete(self,deviceIp):
        """
        Removes a device to NetBrain.
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

        #run a device query
        #if the device already exists, exit out with a message
        #if the device does not exist, continue to add
        deviceQuery = self.device_query(deviceIp)
        if deviceQuery == []:
            result['response'] = "Device does not exist"
            result['error'] = "None"
            return (result)

        ###
        #Delete IP
        #This will delete the requested IP address
        ###
        #set url
        url = self.server_url + "V1/CMDB/Devices"
        #set data
        data = {
          "IPs": [
            deviceIp
          ]
        }

        #run api call
        resp = requests.delete(url,data=json.dumps(data),headers=self.headers, verify=True)

        #display success results
        if resp.json()['statusCode'] == 790200:
            result['success'] = True
            result['response'] = resp.json()['statusDescription']
            result['error'] = "None"
            print (result)
            return (result)
        #display failure results
        else:
            result['response'] = resp.text
            result['error'] = resp.status_code
            print (result)
            return (result)

    def get_group_devices(self):
        """
        Gets a list of all successfully discovered devices sorted by hostname
        Inputs: None
        Outputs:
            -result: Results from method
        """

        ###
        ###set up the function with the neccessary data
        ###
        #configure the url for adding a device and declare the data in the body
        url = self.server_url + "API/CMDB/device/getGroupDevices"

        params = "groupName=All Devices"

        ###
        ###run the function main API calls
        ###
        resp = requests.get(url, params=params, headers=self.headers, verify=False)
        respData = resp.json()['devices']

        if resp.status_code == 200:
            result = sorted(respData, key=lambda d: d['mgmtIP'])
            #print (result)
            return (result)

        else:
            result = deviceIp + ": Status Code: " + str(resp.status_code) + ", Response: " + str(resp.text)
            print (result)
            return (result)

    def get_connected_switchport(self,deviceIp):
        """
        Gets the connected L2 switchports of an interface and device it belongs to.
        Inputs:
            -deviceIp: IPv4 address
        Outputs:
            -result: Results from method
        """

        ###
        ###set up the function with the neccessary data
        ###
        #configure the url for adding a device and declare the data in the body
        url = self.server_url + "API/CMDB/site/getConnectedSwitchPort"

        data={
            "IP": deviceIp
        }

        ###
        ###run the function main API calls
        ###
        resp = requests.get(url, params=data, headers=self.headers, verify=False)
        respData = resp.json()

        if "Success" in resp.text and resp.status_code == 200:
            hostname = respData['hostname']
            interface = respData['interface']
            result = deviceIp + ": " + " Device: " + str(hostname) + "  Interface: " + str(interface)
            #result = "Status Code: " + str(resp.status_code) + ", Response: " + str(resp.text)
            print (result)
            return (result)

        else:
            result = deviceIp + ": Status Code: " + str(resp.status_code) + ", Response: " + str(resp.text)
            print (result)
            return (result)

    def calc_path(self,protocol,sourceIp,sourcePort,destinationIp,destinationPort):
        """
        Calculates the path between two IPs.
        Inputs:
            -protocol: IP, TCP, UDP
            -sourceIp: IPv4 address
            -sourcePort: Port number
            -destinationIp: IPv4 address
            -pathAnalysisSet: Layer 2 or Layer 3
            -destinationPort: Port number
        Outputs:
            -result: Results from method
        """

        ###
        ###set up the function with the neccessary data
        ###
        #configure the url for adding a device and declare the data in the body
        calcurl = self.server_url + "API/CMDB/path/calcPath"
        url = self.server_url + "API/CMDB/path/getPath/"

        data={
            "sourceIp": sourceIp,
            "sourcePort": sourcePort,
            "destIp": destinationIp,
            "destPort": destinationPort,
            "pathAnalysisSet":1,
            "protocol": protocol,
            "isLive":1
        }

        ###
        ###run the function main API calls
        ###
        calc = requests.post(calcurl, data=json.dumps(data), headers=self.headers, verify=False)
        taskId = calc.json()["taskID"]

        time.sleep(30)
        resp = requests.get(url + str(taskId), headers=self.headers, verify=False)
        respData = resp.json()["hopList"]

        if "Success" in resp.text and resp.status_code == 200:
            result = respData
            print (result)
            return (result)

        else:
            result = deviceIp + ": Status Code: " + str(resp.status_code) + ", Response: " + str(resp.text)
            print (result)
            return (result)

    def calc_path_ris(self,sourceIp,destinationIp):
        """
        Calculates the path between two IPs.
        Inputs:
            -sourceIp: IPv4 address
            -destinationIp: IPv4 address
        Outputs:
            -result: Results from method
        """

        ###
        ###set up the function with the neccessary data
        ###
        #configure the url for adding a device and declare the data in the body
        calcpathurl = self.server_url + "API/CMDB/path/calcPath"
        getpathurl = self.server_url + "API/CMDB/path/getPath/"

        data={
            "sourceIp": sourceIp,
            "destIp": destinationIp,
            "pathAnalysisSet":2,
            "protocol": "IPv4",
            "isLive":1
        }

        ###
        ###run the function main API calls
        ###
        calc = requests.post(calcpathurl, data=json.dumps(data), headers=self.headers, verify=False)
        taskId = calc.json()["taskID"]

        time.sleep(60)
        resp = requests.get(getpathurl + str(taskId), headers=self.headers, verify=False)

        if "Success" in resp.text and resp.status_code == 200:
            respData = resp.json()["hopList"]
            srcDeviceName = resp.json()['hopList'][0]['srcDeviceName']
            interfaceName = resp.json()['hopList'][0]['inboundInterface']
            #outboundInterface = resp.json()['hopList'][0]['outboundInterface']

            #result = "Device: " + srcDeviceName + ", Inbound Interface: " + inboundInterface + ", Outbound Interface: " + outboundInterface
            #print (result)

            #create a list to store nextOutboundInterface
            #netbrain API groups 3 variables together but the outbound interface actually goes with the next device shown in the next hop
            #because of this you have to store the outboundInterface variable to use for the next loop.
            srcDeviceNameList = []
            interfaceList = []
            bandwidthList = []

            for hop in respData:
                srcDeviceName = hop['srcDeviceName']
                if srcDeviceName == destinationIp:
                    break
                #inboundInterface = hop['inboundInterface']

                #check device port bandwidth
                url = self.server_url + "API/CMDB/interface/getInterfaceAttribute"

                params = {
                    'hostname': srcDeviceName,
                    'interfaceName': interfaceName
                }
                resp = requests.get(url,params = params, headers=self.headers, verify=False)
                attributes = resp.json()['attributes']
                try:
                    speed = resp.json()['attributes'][interfaceName]['bandwidth']
                    if speed == 20000000:
                        bandwidth = "20G"
                    elif speed == 10000000:
                        bandwidth = "10G"
                    elif speed == 1000000:
                        bandwidth = "1G"
                    elif speed == 100000:
                        bandwidth = "100M"
                    #ASA uses Kbps
                    elif speed == 10000:
                        bandwidth = "10G"
                    else:
                        bandwidth = str(speed)
                except TypeError as t:
                    bandwidth = ""
                except KeyError as e:
                    bandwidth = "N/A"

                srcDeviceNameList.append(srcDeviceName)
                interfaceList.append(interfaceName)
                bandwidthList.append(bandwidth)

                #define the Interface for the next hop
                interfaceName = hop['outboundInterface']

            result = {
                'srcDeviceNameList': srcDeviceNameList,
                'interfaceList': interfaceList,
                'bandwidthList': bandwidthList
            }

            return (srcDeviceNameList,
            interfaceList,
            bandwidthList
            )

        else:
            result = "Device: " + srcDeviceName + ", Status: " + str(resp.status_code) + ", Response: " + str(resp.text)
            print (result)
            return (result)
