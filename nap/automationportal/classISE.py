import requests
import json
import base64
import re
import sys

class ISE():
    """
    This class is used to perform all functions from within Cisco ISE RestAPI.  The restAPI user and URL are hard coded in the top of the class and used in many functions.
    """

    #set ISE restapi username and password
    user = "restapi"
    pwd = "ysBzuRGn1kPM6MYxUxey74qb"
    #set ISE base restAPI url
    server_url = "https://pan-01.ise.wustl.edu:9060/ers/"

    def __init__(self):
        """
        Runs every call to class ISE.  Includes get_headers().
        Inputs: None
        Outputs: None
        """

        #Every call to class ISE will need headers
        self.headers = self.get_headers()

    def get_headers(self):
        """
        Creates the login information for Cisco ISE RestAPI.
        Inputs: None
        Outputs:
            - headers: Request Headers
        """

        #use username and password from class
        basic_data = self.user + ":" + self.pwd
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

    def get_device_type_and_location(self):
        """
        Checks Cisco ISE for the existing device types and locations.  This can be used to to populate dropdown menus on forms.
        Inputs: None
        Outputs:
            -deviceTypeList: List of device types
            -deviceLocationList: List of device locations
        """

        #Set the url for the method
        url = self.server_url + "config/networkdevice"

        #Initialize Variables
        deviceTypeList = [('','--Select Type--')]
        deviceLocationList = [('','--Select Location--')]
        hasNextPage = False
        i = 1
        params = "size=100&page=" + str(i)
        #print (params)
        #Run the command to get "SearchResult" items and start on page 1
        checkDeviceGroups = requests.get(url + "group", params=params, headers=self.headers).json()["SearchResult"]
        #print ("DeviceGroups: " + json.dumps(checkDeviceGroups,sort_keys=True,indent=4,separators=(',', ': ')))

        #Run the command to get the "SearchResult/resources" items and start on page 1.  This will contain the device Types and locations
        getDeviceTypeAndLocation = requests.get(url + "group", params=params, headers=self.headers).json()["SearchResult"]["resources"]
        #print ("DeviceTypeAndLocation: " + json.dumps(getDeviceTypeAndLocation,sort_keys=True,indent=4,separators=(',', ': ')))

        #Run the command to loop through the results for deviceType
        for deviceType in getDeviceTypeAndLocation:
            #If the "name" item contains text for device types, erase that text by replacing with '' and replace all # with - and append it to deviceTypeList list
            if "Device Type#All Device Types#" in deviceType['name']:
                subName = re.sub(r'.*?Device Type#All Device Types#', '', deviceType['name'])
                deviceTypeList.append( (subName,re.sub(r'#', ' - ', subName)) )
        #Run the command to loop through the results for deviceLocation
        for deviceLocation in getDeviceTypeAndLocation:
            #If the "name" item contains text for locations, erase that text by replacing with '' and replace all # with - and append it to deviceLocationList list
            if "Location#All Locations#" in deviceLocation['name']:
                subLocation = re.sub(r'.*?Location#All Locations#', '', deviceLocation['name'])
                deviceLocationList.append( (subLocation,re.sub(r'#', ' - ', subLocation)) )

        #If the results are more than 1 page mark hasNextPage as true and continue on
        if "nextPage" in checkDeviceGroups:
            hasNextPage = True
            i +=1
            params = "size=100&page=" + str(i)

        #Run as long as there are next pages available
        while hasNextPage:
            #print (str(params))
            #Run the command to get the "SearchResult/resources" items and go to the page specifid by the params
            getDeviceTypeAndLocation = requests.get(url + "group", params=params, headers=self.headers).json()["SearchResult"]["resources"]

            #Run the command to loop through the results for deviceType
            for deviceType in getDeviceTypeAndLocation:
                #If the "name" item contains text for device types, erase that text by replacing with '' and replace all # with - and append it to deviceTypeList list
                if "Device Type#All Device Types#" in deviceType['name']:
                    subName = re.sub(r'.*?Device Type#All Device Types#', '', deviceType['name'])
                    deviceTypeList.append( (subName,re.sub(r'#', ' - ', subName)) )
            #Run the command to loop through the results for deviceLocation
            for deviceLocation in getDeviceTypeAndLocation:
                #If the "name" item contains text for locations, erase that text by replacing with '' and replace all # with - and append it to deviceLocationList list
                if "Location#All Locations#" in deviceLocation['name']:
                    subLocation = re.sub(r'.*?Location#All Locations#', '', deviceLocation['name'])
                    deviceLocationList.append( (subLocation,re.sub(r'#', ' - ', subLocation)) )

            #Run the command to get the "SearchResult" items and go to the page specified by the params
            checkDeviceGroups = requests.get(url + "group", params=params, headers=self.headers).json()["SearchResult"]
            #print ("DeviceGroups: " + json.dumps(checkDeviceGroups,sort_keys=True,indent=4,separators=(',', ': ')))
            #Check to see if there is another page, if so add 1 to params
            if "nextPage" in checkDeviceGroups:
                #i +=1
                #print (str(hasNextPage))
                params = "page=" + str(i)
            #if there is not another page, set the hasNextPage as false to stop the loop
            else:
                hasNextPage = False

        return (deviceTypeList, deviceLocationList)

    def get_device(self, deviceIp):
        """
        Get device detailed info
        Input:
            - deviceIp: IPv4 address of device
        Outputs:
            -result: Results from method
        """
        result = {
            'success': False,
            'response': '',
            'error': '',
        }

        ###
        ###run the function main API calls
        ###
        #GET request to find device
        url = self.server_url + "config/networkdevice"

        resp = requests.get(url, params="filter=ipaddress.EQ." + deviceIp, headers=self.headers)
        found_device = resp.json()

        if found_device['SearchResult']['total'] == 1:
            device_oid = found_device['SearchResult']['resources'][0]['id']
            resp = requests.get(url + "/" + device_oid,headers=self.headers)

            if resp.status_code == 200:
                result['success'] = True
                result['response'] = resp.json()['NetworkDevice']
                result['error'] = "None"
                print (result)
                return (result)

            elif resp.status_code == 404:
                result['response'] = deviceIp + " not found. This could be because the IP falls within a larger subnet in ISE."
                result['error'] = resp.status_code
                print (result)
                return (result)

            else:
                result['response'] = resp.json()['ERSResponse']['messages'][0]['title']
                result['error'] = resp.status_code
                print (result)
                return (result)

        elif found_device['SearchResult']['total'] == 0:
                result['response'] = deviceIp + " not found. This could be because the IP falls within a larger subnet in ISE."
                result['error'] = 404
                print (result)
                return (result)

        else:
            result['response'] = resp.json()['ERSResponse']['messages'][0]['title']
            result['error'] = resp.status_code
            print (result)
            return (result)


    def device_add(self,deviceName,deviceIp,deviceDescription,deviceLocation,deviceType,radiusSharedSecret,tacacsSharedSecret):
        """
        Adds a device to Cisco ISE.
        Inputs:
            -deviceName: name of device
            -deviceIp: IPv4 address of device
            -deviceDescription: Description of device
            -deviceLocation: Location of device
            -deviceType: Device Type
            -radiusSharedSecret: Radius shared secret
            -tacacsSharedSecret: TACACS shared secret
        Outputs:
            -result: Results from method
        """

        result = {
            'success': False,
            'response': '',
            'error': '',
        }

        ###
        ###set up the function with the neccessary data
        ###
        #configure the url for adding a device and declare the data in the body
        url = self.server_url + "config/networkdevice"
        data={
            "NetworkDevice" : {
                "name" : deviceName,
                "description" : deviceDescription + " - created by RestAPI",
                "authenticationSettings" : {
                    "networkProtocol" : "RADIUS",
                    "radiusSharedSecret" : radiusSharedSecret
                },
                "tacacsSettings" : {
                    "sharedSecret" : tacacsSharedSecret,
                    "connectModeOptions" : "OFF"
                },
                "profileName" : "Cisco",
                "coaPort" : 1700,
                "NetworkDeviceIPList" : [ {
                    "ipaddress" : deviceIp,
                    "mask" : 32
                } ],
                "NetworkDeviceGroupList" : [ "Location#All Locations#" + deviceLocation, "Device Type#All Device Types#" + deviceType, "IPSEC#Is IPSEC Device#No" ]
              }
        }

        ###
        ###run the function main API calls
        ###
        #POST request to add device
        resp = requests.post(url,data=json.dumps(data),headers=self.headers)

        if resp.status_code == 201:
            result['success'] = True
            result['response'] = deviceName + " added successfully"
            result['error'] = "None"

            #Pull location code from successful device add
            iseLocationCode = re.sub(r'.*\/', '', str(resp.headers['Location']))

            #GET request to retrieve device information
            r = requests.get(url + "/" + iseLocationCode,headers=self.headers)
            print (result)
            return (result)

        else:
            result['response'] = resp.json()['ERSResponse']['messages'][0]['title']
            result['error'] = resp.status_code
            print (result)
            return (result)


    def device_delete(self,deviceIp):
        """
        Removes a device to Cisco ISE.
        Inputs:
            -deviceIp: Device IP Address
        Outputs:
            -result: Results from method
        """

        result = {
            'success': False,
            'response': '',
            'error': '',
        }

        #Set the url for the method
        url = self.server_url + "config/networkdevice"

        ###
        ###run the function main API calls
        ###
        #GET request to find device
        resp = requests.get(url, params="filter=ipaddress.EQ." + deviceIp, headers=self.headers)
        found_device = resp.json()

        #if the device exists, delete it
        if found_device['SearchResult']['total'] == 1:
            device_oid = found_device['SearchResult']['resources'][0]['id']
            resp = requests.delete(url + "/" + device_oid,headers=self.headers)

            if resp.status_code == 204:
                result['success'] = True
                result['response'] = "Device IP: " + deviceIp + " deleted successfully"
                result['error'] = "None"
                print (result)
                return (result)

            elif resp.status_code == 404:
                result['response'] = "Device not found. This could be because the IP falls within a larger subnet in ISE."
                result['error'] = resp.status_code
                print (result)
                return (result)

            else:
                result['response'] = resp.json()['ERSResponse']['messages'][0]['title']
                result['error'] = resp.status_code
                print (result)
                return (result)

        #if the device does not exist
        elif found_device['SearchResult']['total'] == 0:
                result['response'] = "Device not found. This could be because the IP falls within a larger subnet in ISE."
                result['error'] = 404
                print (result)
                return (result)
        else:
            result['response'] = resp.json()['ERSResponse']['messages'][0]['title']
            result['error'] = resp.status_code
            print (result)
            return (result)
