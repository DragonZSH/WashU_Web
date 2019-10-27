import requests
import json
import base64
import re
import sys
import socket
import binascii
import time

class Prime():
    """
    This class is used to perform all functions from within Cisco Prime RestAPI.  The restAPI user and URL are hard coded in the top of the class and used in many functions.
    """

    #set ISE restapi username and password
    user = "restapi"
    pwd = "ysBzuRGn1kPM6MYxUxey74qb"
    #set ISE base restAPI url
    server_url = "https://prime.net.wustl.edu/webacs/api/"

    def __init__(self):
        """
        Runs every call to class Prime.  Includes get_headers().
        Inputs: None
        Outputs: None
        """

        #Every call to class ISE will need headers
        self.headers = self.get_headers()

    def get_headers(self):
        """
        Creates the login information for Cisco Prime RestAPI.
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

    def get_device(self, deviceIp):
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

        url = self.server_url + "v4/data/Devices"
        resp = requests.get(url,params = "ipAddress=" + deviceIp, headers=self.headers, verify=False)
        num_devices = resp.json()['queryResponse']['@count']

        if resp.status_code == 200 and num_devices == 1:
            dev_id = resp.json()['queryResponse']['entityId'][0]['$']
            resp = requests.get(url + "/" + dev_id, headers=self.headers, verify=False)
            print (url + "/" + dev_id)
            if resp.status_code == 200:
                result['success'] = True
                result['response'] = resp.json()
                result['error'] = "None"
                print (result)
                return (result)

            elif resp.status_code == 404:
                result['response'] = "Device IP: " + deviceIP + " not found"
                result['error'] = resp.status_code
                print (result)
                return (result)

            else:
                result['response'] = resp.json()
                result['error'] = resp.status_code
                print (result)
                return (result)

        elif resp.status_code == 200 and num_devices == 0:
            result['response'] = "Device IP: " + deviceIp + " not found"
            result['error'] = 404
            print (result)
            return (result)

        else:
            result['response'] = resp.json()
            result['error'] = resp.status_code
            print (result)
            return (result)

    def device_add(self,deviceIp,deviceSNMP):
        """
        Adds a device to Cisco Prime Infrastructure.
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
        ###set up the function with the neccessary data
        ###
        #configure the url for adding a device and declare the data in the body
        url = self.server_url + "v4/op/devices/bulkImport"
        data={
            "devicesImport" : {
                "devices" : {
                    "device" : [ {
                        "ipAddress" : deviceIp,
                        "credentialProfileName" : deviceSNMP
                    } ]
                }
            }
        }

        ###
        ###run the function main API calls
        ###
        #POST request to add device
        resp = requests.put(url,data=json.dumps(data),headers=self.headers, verify=False)

        if resp.status_code == 200:
            result['success'] = True
            result['response'] = resp.json()['mgmtResponse']['bulkImportResult'][0]['jobName']
            result['error'] = "None"
            print (result)
            return (result)

        else:
            result['response'] = resp.text
            result['error'] = resp.status_code
            print (result)
            return (result)


    def device_delete(self,deviceIp):
        """
        Removes a device to Cisco Prime.
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
        try:
            host = socket.gethostbyaddr(deviceIp)
            deviceFQDN = host[0]
        except socket.error:
            deviceFQDN = deviceIp

        ###
        ###run the function main API calls
        ###
        #Set the url for the method
        url = self.server_url + "v4/op/devices/exportDevices"
        resp = requests.get(url,params = "ipAddress=" + deviceFQDN, headers=self.headers, verify=False)

        if resp.json()["mgmtResponse"]["devicesExportResult"][0]["devices"]['device'] == []:
            result['response'] = "Device not found."
            result['error'] = resp.status_code
            print (result)
            return (result)

        else:
            data={
                "removalJobParamsDTO" : {
                    #"deleteAPs" : true,
                    "ipAddressList" : {
                        "ipAddressList" : [ {
                            "address" : deviceFQDN
                        } ]
                    }
                }
            }

            url = self.server_url + "v4/op/devices/removalJob"
            resp = requests.post(url,data=json.dumps(data),headers=self.headers, verify=False)

            if resp.status_code == 200:
                result['success'] = True
                result['response'] = resp.json()["mgmtResponse"]["removalJobResultDTO"][0]["jobName"]
                result['error'] = "None"
                print (result)
                return (result)

            else:
                result['response'] = resp.text
                result['error'] = resp.status_code
                print (result)
                return (result)

    def export_devices(self):
        """
        Retrieves all wired network devices in Cisco Prime.
        Inputs: None
        Outputs:
            -result: Results from method
        """

        ###
        ###set up the function with the neccessary data
        ###
        #configure the url for adding a device and declare the data in the body

        #params = {
    #        'groupPath': "startsWith("Device Type")"#,
            #'groupPath': notStartsWith("Device Type/Wireless Controller")
    #    }

        ###
        ###run the function main API calls
        ###
        url = self.server_url + "v4/op/devices/exportDevices"
        #resp = requests.get(url,params = 'groupPath=startsWith("Device Type")', headers=self.headers, verify=False)
        resp = requests.get(url,params = 'groupId=84098', headers=self.headers, verify=False)
        respData = resp.json()['mgmtResponse']['devicesExportResult'][0]['devices']['device']

        if resp.status_code == 200:
            #result = sorted(respData, key=lambda d: d['ipAddress'])
            result = respData
            #print (result)
            return (result)

    def deploy_template(self,deviceIp,templateList,deviceNameif):
        """
        Deploys a template to a device via Cisco Prime.
        Inputs:
            -deviceIp: IPv4 address of device
            -templateList: List of templates to apply to device
                (Example)
                templateList = [
                    "WUSTL Add Local Username",
                    "WUSTL Remove Temporary Username"
                ]
            -deviceNameif: ASA Nameif used for management.  e.g. "outside"
            -deviceType: Choose device type from a list

        Outputs:
            -result: Results from method
            -resultList: List of results in human readable format
        """

        result = {
            'success': False,
            'response': '',
            'error': '',
        }

        ###
        ###run the function main API calls
        ###
        #Set the url for the method
        url = self.server_url + "v4/op/devices/exportDevices"
        resp = requests.get(url,params = "ipAddress=" + deviceIp, headers=self.headers, verify=False)

        if resp.json()["mgmtResponse"]["devicesExportResult"][0]["devices"]['device'] == []:

            try:
                host = socket.gethostbyaddr(deviceIp)
                deviceIp = host[0]
            except socket.error:
                pass

            resp = requests.get(url,params = "ipAddress=" + deviceIp, headers=self.headers, verify=False)

            if resp.json()["mgmtResponse"]["devicesExportResult"][0]["devices"]['device'] == []:
                result['response'] = "Device not found."
                result['error'] = resp.status_code
                resultList = result['response']
                print (result)
                return (result, resultList)

        else:

            #Get the targetDeviceID which is "entityId"
            url = self.server_url + "v4/data/Devices"
            resp = requests.get(url,params = "ipAddress=" + deviceIp, headers=self.headers, verify=False)
            targetDeviceID = resp.json()['queryResponse']['entityId'][0]['$']

            #User the targetDeviceID to get collection status
            resp = requests.get(url + "/" + targetDeviceID, headers=self.headers, verify=False)
            respData = resp.json()['queryResponse']['entity'][0]['devicesDTO']['collectionStatus']
            #deviceType = resp.json()['queryResponse']['entity'][0]['devicesDTO']['manufacturerPartNr'][0]['partNumber']

            #Set blank list for results

            if respData != "COMPLETED":
                result['response'] = ["Cannot push templates.  Please ensure the device is completely synchronized in Prime.  Collection status is: " + respData ]
                result['error'] = resp.status_code
                resultList = result['response']
                print (result)
                return (result, resultList)

            else:
                resultList = []
                for templateName in templateList:
                    data={
                        "cliTemplateCommand" : {
                            "targetDevices" : {
                                "targetDevice" : [ {
                                    "targetDeviceID" : targetDeviceID,
                                    "variableValues": {
                                        "variableValue": [ {
                                            "name": "nameif",
                                            "value": deviceNameif
                                        } ]
                                    }
                                } ]
                            },
                            "templateName" : templateName
                        }
                    }

                    url = self.server_url + "v4/op/cliTemplateConfiguration/deployTemplateThroughJob"
                    resp = requests.put(url,data=json.dumps(data),headers=self.headers, verify=False)

                    if resp.status_code == 200:
                        result['success'] = True
                        result['response'] = resp.json()["mgmtResponse"]["cliTemplateCommandJobResult"][0]["jobName"]
                        result['error'] = "None"
                        print (result)
                        response = str(result['response'])
                        success = str(result['success'])
                        resultList.append("SUCCESS - " + templateName + " - Job Name: " + response)

                    else:
                        result['response'] = resp.text
                        result['error'] = resp.status_code
                        print (result)
                        response = str(result['response'])
                        resultList.append("FAILED - " + templateName + " - Job Name: " + response)

                    #Wait half a second before continuing so jobs are run in order
                    time.sleep(.5)

                return (result, resultList)

    def get_client_details(self,deviceIpOrMAC):
        """
        Searches for client information in Cisco Prime.
        Inputs:
            -deviceIpOrMAC: IPv4 address or MAC address of client
        Outputs:
            -result: Results from method
            -connectionType: Wired or wireless
            -deviceName: Connected network device
            -clientInterface: Connected network device interface
            -ipAddress = IPv4 address of client
            -macAddress = MAC address of client
        """

        try:
            binascii.unhexlify(deviceIpOrMAC.replace(':',''))
            macAddr = True
        except binascii.Error:
            macAddr = False

        if macAddr == True:
            params = {
                '.full': 'true',
                'macAddress': "\"" + deviceIpOrMAC + "\"",
            }

        else:
            try:
                socket.inet_pton(socket.AF_INET, deviceIpOrMAC)
            except AttributeError:
                try:
                    socket.inet_aton(deviceIpOrMAC)
                    ipAddr = True
                except socket.error:
                    ipAddr = False
                result = deviceIpOrMAC.count('.') == 3
                return (result)
            except socket.error:
                ipAddr = False

            params = {
                '.full': 'true',
                'ipAddress': deviceIpOrMAC,
                '.sort': '+associationTime',
            }

        url = self.server_url + "v3/data/ClientDetails"
        resp = requests.get(url,params = params, headers=self.headers, verify=False)
        #print (resp.status_code)
        #print (resp.text)

        if "entity" in resp.text and resp.status_code == 200:

            totalDevices = resp.json()['queryResponse']['@count']
            print ("TOTAL DEVICES: " + str(totalDevices))
            count = 0
            status = resp.json()['queryResponse']['entity'][count]['clientDetailsDTO']['status']
            apName = ""
            if totalDevices > 1:
                while status != "ASSOCIATED" and count < totalDevices:
                    try:
                        status = resp.json()['queryResponse']['entity'][count]['clientDetailsDTO']['status']
                        print (str(count) + " " + status)
                        count = count + 1
                    except IndexError as e:
                        apName = "DEVICE NO LONGER ASSOCIATED"

            print (status)
            if status == "DISASSOCIATED":
                apName = "DEVICE NO LONGER ASSOCIATED"
            count = count - 1
            respData = resp.json()['queryResponse']['entity'][count]['clientDetailsDTO']
            connectionType = str(respData['connectionType'])
            deviceName = str(respData['deviceName'])
            clientInterface = str(respData['clientInterface'])
            try: 
                ipAddress = str(respData['ipAddress']['address'])
            except KeyError as i:
                ipAddress = "None Found"
            macAddress = str(respData['macAddress'])

            #result['success'] = True
            #result['response'] = str(resp.text)
            #result['error'] = "None"
            result = "Form Input: " + deviceIpOrMAC + ", Connection Type: " + connectionType + ", Device Name: " + deviceName + ", Client Interface: " + clientInterface + ", IP Address: " + ipAddress + ", MAC Address: " + macAddress + ", AP Name: " + apName
            print (result)

            if "apName" in resp.text:
                if status == "DISASSOCIATED":
                    apName = "DEVICE NO LONGER ASSOCIATED.  Last AP: " + str(respData['apName'])
                else:
                    apName = respData['apName']

            result = {
                'connectionType': connectionType,
                'deviceName': deviceName,
                'clientInterface': clientInterface,
                'ipAddress': ipAddress,
                'macAddress': macAddress,
                'apName': apName
            }
            return (result['connectionType'],
            result['deviceName'],
            result['clientInterface'],
            result['ipAddress'],
            result['macAddress'],
            result['apName'])

        elif "\"@count\":0" in resp.text and resp.status_code == 200:
            result = "Form Input: " + deviceIpOrMAC + ", Response: No Device Found."
            connectionType = deviceIpOrMAC
            deviceName = "Not Found"
            clientInterface = ""
            ifDescr = ""
            ipAddress = ""
            macAddress = ""
            apName = ""
            print (result)

            result = {
                'connectionType': connectionType,
                'deviceName': deviceName,
                'clientInterface': clientInterface,
                'ipAddress': ipAddress,
                'macAddress': macAddress,
                'apName': apName
            }
            return (result['connectionType'],
            result['deviceName'],
            result['clientInterface'],
            result['ipAddress'],
            result['macAddress'],
            result['apName'])

        else:
            result = "Form Input: " + deviceIpOrMAC + ", Response: " + str(resp.text) + ", Status Code: " + str(resp.status_code)
            connectionType = result
            deviceName = ""
            clientInterface = ""
            ifDescr = ""
            ipAddress = ""
            macAddress = ""
            apName = ""
            print (result)

            result = {
                'connectionType': connectionType,
                'deviceName': deviceName,
                'clientInterface': clientInterface,
                'ipAddress': ipAddress,
                'macAddress': macAddress,
                'apName': apName
            }
            return (result['connectionType'],
            result['deviceName'],
            result['clientInterface'],
            result['ipAddress'],
            result['macAddress'],
            result['apName'])
