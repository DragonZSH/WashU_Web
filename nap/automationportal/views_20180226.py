from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.contrib import messages
from django.conf import settings
from .forms import DeviceAddForm, DeviceDeleteForm, CalcPathForm
from django.contrib.auth.decorators import login_required

import requests
import json
import base64
import time
import re
import logging
import sys

# Create your views here.
def connectAuth(request):
    wustlEduGroupNames = ['ORG-WUIT-SI-NE-Network', 'ORG-WUIT-SI-SOC-CC', 'ORG-WUIT-SI-SOC-MAC', 'WUIT_EUS_SI_NetworkGear_ContrReadWrite', 'WUIT_EUS_SI_NetworkGear_ReadWrite']
    #fakeGroups = ['ORG-FAKEGROUP', 'ORG-NOTREAL']
    result = False
    for item in wustlEduGroupNames:
        if item in request.META['wustlEduGroups']:
            result = True
    return (result)




def index(request):
    if not connectAuth(request):
        return render(request, 'automationportal/noaccess.html') 
    return render(request, 'automationportal/home.html')
         



def mygroups(request):
    REQ_META = request.META['wustlEduGroupMembership']
    metaListGroup = REQ_META.split(";")
    metaListGroupSorted = sorted(metaListGroup, key=lambda s: s.lower())
    
    userGroupList = []

    tacacsRegex = r'CN=ORG-WUIT-SI-NE-Network,OU=Groups,DC=accounts,DC=ad,DC=wustl,DC=edu|CN=ORG-WUIT-SI-SOC-CC,OU=Groups,DC=accounts,DC=ad,DC=wustl,DC=edu|CN=ORG-WUIT-SI-SOC-MAC,OU=Groups,DC=accounts,DC=ad,DC=wustl,DC=edu|CN=WUIT_EUS_SI_NetworkGear_ContrReadWrite,OU=Application Groups,OU=Resource Groups,OU=WUIT,OU=Groups,DC=accounts,DC=ad,DC=wustl,DC=edu|CN=WUIT_EUS_SI_NetworkGear_ReadWrite,OU=Application Groups,OU=Resource Groups,OU=WUIT,OU=Groups,DC=accounts,DC=ad,DC=wustl,DC=edu'
    tacacsFind = re.findall(tacacsRegex, str(metaListGroupSorted))
    userGroupList = userGroupList + tacacsFind
    logging.info("TACACS FIND: " + str(tacacsFind))
    logging.info("-----")

    vpnRegex = r'CN=grsw50_students,OU=Papercut,OU=IdM Resources,OU=IdM Groups,DC=accounts,DC=ad,DC=wustl,DC=edu|CN=vpn-users_cfuusers,OU=VPN Access,OU=IST,OU=IdM Groups,DC=accounts,DC=ad,DC=wustl,DC=edu|CN=vpn-users_fpm,OU=VPN Access,OU=IST,OU=IdM Groups,DC=accounts,DC=ad,DC=wustl,DC=edu|CN=vpn-users_fpm_usn,OU=VPN Access,OU=IST,OU=IdM Groups,DC=accounts,DC=ad,DC=wustl,DC=edu|CN=vpn-users_fpm_dcadmin,OU=VPN Access,OU=IST,OU=IdM Groups,DC=accounts,DC=ad,DC=wustl,DC=edu|CN=firesaftey_vpn,OU=VPN Access,OU=IST,OU=IdM Groups,DC=accounts,DC=ad,DC=wustl,DC=edu|CN=VPN-users_IST,OU=VPN Access,OU=IST,OU=IdM Groups,DC=accounts,DC=ad,DC=wustl,DC=edu|CN=law_vpn,OU=VPN Access,OU=law,OU=danforth campus,OU=Groups,DC=accounts,DC=ad,DC=wustl,DC=edu|CN=vpn-users_mscit,OU=cits,OU=Medical Campus,OU=Groups,DC=accounts,DC=ad,DC=wustl,DC=edu|CN=VPN-users_NSS-IST,OU=VPN Access,OU=IST,OU=IdM Groups,DC=accounts,DC=ad,DC=wustl,DC=edu|CN=BU_Faculty,OU=Business,OU=IdM Groups,DC=accounts,DC=ad,DC=wustl,DC=edu|CN=BU_Staff,OU=Business,OU=IdM Groups,DC=accounts,DC=ad,DC=wustl,DC=edu|CN=BU_Students,OU=Business,OU=IdM Groups,DC=accounts,DC=ad,DC=wustl,DC=edu|CN=bu_guests-degree,OU=Business,OU=IdM Groups,DC=accounts,DC=ad,DC=wustl,DC=edu|CN=bu-guests-enrolled,OU=Business,OU=IdM Groups,DC=accounts,DC=ad,DC=wustl,DC=edu|CN=bu_guests-majorsminors,OU=Business,OU=IdM Groups,DC=accounts,DC=ad,DC=wustl,DC=edu|CN=bu_guests-vpn,OU=OLIN,OU=Groups,DC=accounts,DC=ad,DC=wustl,DC=edu|CN=olin_vpn-users_library,OU=VPN Access,OU=olin library,OU=danforth campus,OU=Groups,DC=accounts,DC=ad,DC=wustl,DC=edu|CN=vpn-users_wuit_srv_rmt_low,OU=VPN Access,OU=IST,OU=IdM Groups,DC=accounts,DC=ad,DC=wustl,DC=edu|CN=vpn-users_wuit_srv_rmt_mod,OU=VPN Access,OU=IST,OU=IdM Groups,DC=accounts,DC=ad,DC=wustl,DC=edu|CN=vpn-users_wuit_srv_rmt_high,OU=VPN Access,OU=IST,OU=IdM Groups,DC=accounts,DC=ad,DC=wustl,DC=edu|CN=vpn-users_wushcs,OU=VPN Access,OU=IST,OU=IdM Groups,DC=accounts,DC=ad,DC=wustl,DC=edu'
    vpnFind = re.findall(vpnRegex, str(metaListGroupSorted))
    userGroupList = userGroupList + vpnFind
    logging.info("VPN FIND: " + str(vpnFind))
    logging.info("-----")
   
    msvpnRegex = r'CN=WUIT_EUS_SI_NETWORKING_VPN_USERS,OU=Resource Groups,OU=WUIT,OU=Groups,DC=accounts,DC=ad,DC=wustl,DC=edu|CN=Genetics_Vpn,OU=genetics,OU=network security,OU=CITS,OU=Medical Campus,OU=Groups,DC=accounts,DC=ad,DC=wustl,DC=edu|CN=GenomeSciences_Vpn,OU=genome science,OU=network security,OU=CITS,OU=Medical Campus,OU=Groups,DC=accounts,DC=ad,DC=wustl,DC=edu|CN=WUIT_EUS_9999_VPN_USERS,OU=Resource Groups,OU=WUIT,OU=Groups,DC=accounts,DC=ad,DC=wustl,DC=edu'
    msvpnFind = re.findall(msvpnRegex, str(metaListGroupSorted))
    userGroupList = userGroupList + msvpnFind
    logging.info("MSVPN FIND: " + str(msvpnFind))
    logging.info("-----")
    
    ibxRegex = r'CN=ib-admin-group,OU=ipam,OU=nss,OU=IST,OU=CFU,OU=danforth campus,OU=Groups,DC=accounts,DC=ad,DC=wustl,DC=edu|CN=artsci-group-ib,OU=ipam,OU=nss,OU=IST,OU=CFU,OU=danforth campus,OU=Groups,DC=accounts,DC=ad,DC=wustl,DC=edu|CN=biochemistry-group-ib,OU=ipam,OU=nss,OU=IST,OU=CFU,OU=danforth campus,OU=Groups,DC=accounts,DC=ad,DC=wustl,DC=edu|CN=biology-group-ib,OU=ipam,OU=nss,OU=IST,OU=CFU,OU=danforth campus,OU=Groups,DC=accounts,DC=ad,DC=wustl,DC=edu|CN=biostatistics-group-ib,OU=ipam,OU=nss,OU=IST,OU=CFU,OU=danforth campus,OU=Groups,DC=accounts,DC=ad,DC=wustl,DC=edu|CN=business-group-ib,OU=ipam,OU=nss,OU=IST,OU=CFU,OU=danforth campus,OU=Groups,DC=accounts,DC=ad,DC=wustl,DC=edu|CN=cellbio-group-ib,OU=ipam,OU=nss,OU=IST,OU=CFU,OU=danforth campus,OU=Groups,DC=accounts,DC=ad,DC=wustl,DC=edu|CN=devbio-group-ib,OU=ipam,OU=nss,OU=IST,OU=CFU,OU=danforth campus,OU=Groups,DC=accounts,DC=ad,DC=wustl,DC=edu|CN=engineering-group-ib,OU=ipam,OU=nss,OU=IST,OU=CFU,OU=danforth campus,OU=Groups,DC=accounts,DC=ad,DC=wustl,DC=edu|CN=eps-group-ib,OU=ipam,OU=nss,OU=IST,OU=CFU,OU=danforth campus,OU=Groups,DC=accounts,DC=ad,DC=wustl,DC=edu|CN=facilities-group-ib,OU=ipam,OU=nss,OU=IST,OU=CFU,OU=danforth campus,OU=Groups,DC=accounts,DC=ad,DC=wustl,DC=edu|CN=genetics-group-ib,OU=ipam,OU=nss,OU=IST,OU=CFU,OU=danforth campus,OU=Groups,DC=accounts,DC=ad,DC=wustl,DC=edu|CN=genome-group-ib,OU=ipam,OU=nss,OU=IST,OU=CFU,OU=danforth campus,OU=Groups,DC=accounts,DC=ad,DC=wustl,DC=edu|CN=hvac-group-ib,OU=ipam,OU=nss,OU=IST,OU=CFU,OU=danforth campus,OU=Groups,DC=accounts,DC=ad,DC=wustl,DC=edu|CN=istserver-group-ib,OU=ipam,OU=nss,OU=IST,OU=CFU,OU=danforth campus,OU=Groups,DC=accounts,DC=ad,DC=wustl,DC=edu|CN=law-group-ib,OU=ipam,OU=nss,OU=IST,OU=CFU,OU=danforth campus,OU=Groups,DC=accounts,DC=ad,DC=wustl,DC=edu|CN=library-group-ib,OU=ipam,OU=nss,OU=IST,OU=CFU,OU=danforth campus,OU=Groups,DC=accounts,DC=ad,DC=wustl,DC=edu|CN=mathematics-group-ib,OU=ipam,OU=nss,OU=IST,OU=CFU,OU=danforth campus,OU=Groups,DC=accounts,DC=ad,DC=wustl,DC=edu|CN=microbiology-group-ib,OU=ipam,OU=nss,OU=IST,OU=CFU,OU=danforth campus,OU=Groups,DC=accounts,DC=ad,DC=wustl,DC=edu|CN=msns-group-ib,OU=ipam,OU=nss,OU=IST,OU=CFU,OU=danforth campus,OU=Groups,DC=accounts,DC=ad,DC=wustl,DC=edu|CN=neurobiology-group-ib,OU=ipam,OU=nss,OU=IST,OU=CFU,OU=danforth campus,OU=Groups,DC=accounts,DC=ad,DC=wustl,DC=edu|CN=pcg-group-ib,OU=ipam,OU=nss,OU=IST,OU=CFU,OU=danforth campus,OU=Groups,DC=accounts,DC=ad,DC=wustl,DC=edu|CN=physics-group-ib,OU=ipam,OU=nss,OU=IST,OU=CFU,OU=danforth campus,OU=Groups,DC=accounts,DC=ad,DC=wustl,DC=edu|CN=powermeters-group-ib,OU=ipam,OU=nss,OU=IST,OU=CFU,OU=danforth campus,OU=Groups,DC=accounts,DC=ad,DC=wustl,DC=edu|CN=psychology-group-ib,OU=ipam,OU=nss,OU=IST,OU=CFU,OU=danforth campus,OU=Groups,DC=accounts,DC=ad,DC=wustl,DC=edu|CN=radiology-group-ib,OU=ipam,OU=nss,OU=IST,OU=CFU,OU=danforth campus,OU=Groups,DC=accounts,DC=ad,DC=wustl,DC=edu|CN=resnet-group-ib,OU=ipam,OU=nss,OU=IST,OU=CFU,OU=danforth campus,OU=Groups,DC=accounts,DC=ad,DC=wustl,DC=edu|CN=samfox-group-ib,OU=ipam,OU=nss,OU=IST,OU=CFU,OU=danforth campus,OU=Groups,DC=accounts,DC=ad,DC=wustl,DC=edu|CN=socialwork-group-ib,OU=ipam,OU=nss,OU=IST,OU=CFU,OU=danforth campus,OU=Groups,DC=accounts,DC=ad,DC=wustl,DC=edu|CN=solutionscenter-group-ib,OU=ipam,OU=nss,OU=IST,OU=CFU,OU=danforth campus,OU=Groups,DC=accounts,DC=ad,DC=wustl,DC=edu|CN=surgery-group-ib,OU=ipam,OU=nss,OU=IST,OU=CFU,OU=danforth campus,OU=Groups,DC=accounts,DC=ad,DC=wustl,DC=edu|CN=teachingcenter-group-ib,OU=ipam,OU=nss,OU=IST,OU=CFU,OU=danforth campus,OU=Groups,DC=accounts,DC=ad,DC=wustl,DC=edu|CN=nrg-group-ib,OU=ipam,OU=nss,OU=IST,OU=CFU,OU=danforth campus,OU=Groups,DC=accounts,DC=ad,DC=wustl,DC=edu|CN=studentunion-group-ib,OU=ipam,OU=nss,OU=IST,OU=CFU,OU=danforth campus,OU=Groups,DC=accounts,DC=ad,DC=wustl,DC=edu|CN=istwebteam-group-ib,OU=ipam,OU=nss,OU=IST,OU=CFU,OU=danforth campus,OU=Groups,DC=accounts,DC=ad,DC=wustl,DC=edu|CN=genomeinstitute-group-ib,OU=ipam,OU=nss,OU=IST,OU=CFU,OU=danforth campus,OU=Groups,DC=accounts,DC=ad,DC=wustl,DC=edu|CN=msns-ronoc-group-ib,OU=ipam,OU=nss,OU=IST,OU=CFU,OU=danforth campus,OU=Groups,DC=accounts,DC=ad,DC=wustl,DC=edu|CN=chemistry-group-ib,OU=ipam,OU=nss,OU=IST,OU=CFU,OU=danforth campus,OU=Groups,DC=accounts,DC=ad,DC=wustl,DC=edu|CN=mediaservices-group-ib,OU=ipam,OU=nss,OU=IST,OU=CFU,OU=danforth campus,OU=Groups,DC=accounts,DC=ad,DC=wustl,DC=edu|CN=adminwithoutgrid-group-ib,OU=ipam,OU=nss,OU=IST,OU=CFU,OU=danforth campus,OU=Groups,DC=accounts,DC=ad,DC=wustl,DC=edu|CN=wuit-vra-group-ib,OU=ipam,OU=nss,OU=IST,OU=CFU,OU=danforth campus,OU=Groups,DC=accounts,DC=ad,DC=wustl,DC=edu|CN=admin-ro-group-ib,OU=ipam,OU=nss,OU=IST,OU=CFU,OU=danforth campus,OU=Groups,DC=accounts,DC=ad,DC=wustl,DC=edu'
    #ibxRegex = r'CN=FAKEGROUP'
    ibxFind = re.findall(ibxRegex, str(metaListGroupSorted))
    
    userGroupList = userGroupList + ibxFind
    
    logging.info("IBX FIND: " + str(ibxFind))
    logging.info("-----")

    diffGroupList = sorted(list(set(metaListGroup) - set(userGroupList)), key=lambda s: s.lower())
    #logging.info("DIFF GROUP LIST: " + str(diffGroupList))
    #logging.info("")
    
    return render(request, 'automationportal/mygroups.html', {
        'metaListGroupSorted': metaListGroupSorted,
        'tacacsFind': tacacsFind,
        'vpnFind': vpnFind,
        'msvpnFind': msvpnFind,
        'ibxFind': ibxFind,
        'diffGroupList': diffGroupList,
    })



def deviceadd(request):
    if not connectAuth(request):
        return render(request, 'automationportal/noaccess.html') 
    #if form is submitted
    if request.method == 'POST':
        #will handle the request later
        form = DeviceAddForm(request.POST)
 
        #checking if the form is valid or not 
        if form.is_valid():
            #variables in script
            user = form.cleaned_data['username']
            pwd = form.cleaned_data['password']
            iseuser = "restapi"         
            isepwd = "ysBzuRGn1kPM6MYxUxey74qb"  
            netbrainserver_url = "http://netbrain.net.wustl.edu/ServicesAPI/"
            primeserver_url = "https://prime.net.wustl.edu/webacs/api/v3/"
            iseserver_url = "https://pan-01.ise.wustl.edu:9060/ers/"
            headers = {"Content-Type": "application/json", "Accept": "application/json"}
            iseheaders = {"Content-Type": "application/json", "Accept": "application/json"}
            TENANT = "Initial Tenant"
            DOMAIN = "WUIT" 
            
            #netbrain/prime header information
            token_url= netbrainserver_url + "API/login"
            basic_data = user + ":" + pwd           
            basic_data = basic_data.encode("ascii")
            auth_data = base64.b64encode(basic_data)
            headers["Authorization"] = "Basic " + auth_data.decode()

            #ise header information
            isebasic_data = iseuser + ":" + isepwd
            isebasic_data = isebasic_data.encode("ascii")
            iseauth_data = base64.b64encode(isebasic_data)
            iseheaders["Authorization"] = "Basic " + iseauth_data.decode()
            
            #Get NetBrain Token
            gettoken = requests.post(token_url,headers=headers)
            
            if "Incorrect username or password" in gettoken.json()["statusDescription"]:
                messages.warning(request, 'Username or password is incorrect.')
                return render(request, 'automationportal/deviceadd.html', {})

            elif gettoken.json()['statusDescription'] == "Success.":
                global token
                token = gettoken.json()["token"]
                headers["Token"]=token


                #set tenant and domain
                setCurrentDomain_url = netbrainserver_url + "API/setCurrentDomain"
                setCurrentDomainResponse = requests.post(setCurrentDomain_url,data=json.dumps({"tenantName":TENANT,"domainName":DOMAIN}),headers=headers)

                #Check if device already exists and stop script if so
                checkIP = form.cleaned_data['discoverIp']

                #getDevicesByIP_url = netbrainserver_url + "API/CMDB/device/getDevicesByIP"
        
                #getDevicesByIPResponseStatusCode = requests.get(getDevicesByIP_url, params="IP=" + checkIP, headers=headers).json()["statusCode"]
                #getDevicesByIPResponseHostname = requests.get(getDevicesByIP_url, params="IP=" + checkIP, headers=headers).json()["devices"][0]["hostname"]

                #if getDevicesByIPResponseStatusCode == 0 and getDevicesByIPResponseHostname != "":
                #    print (getDevicesByIPResponseHostname)  
                #    messages.warning(request, 'Device "' + getDevicesByIPResponseHostname + '" already exists with IP: ' + checkIP)
                #    return render(request, 'automationportal/deviceadd.html', {
                #        'discoverIp': form.cleaned_data['discoverIp'],
                #        })

                   # logout_url= netbrainserver_url + "API/logout"
                   # requests.post(logout_url,data=json.dumps({"token": token}),headers=headers)

                #else:

                #Run ISE Add Device
                addNetworkDevice_url = iseserver_url + "config/networkdevice"
                data={
                    "NetworkDevice" : {
                        "name" : form.cleaned_data['deviceName'],
                        "description" : form.cleaned_data['deviceDescription'] + " - created by RestAPI",
                        "authenticationSettings" : {
                            "networkProtocol" : "RADIUS",
                            "radiusSharedSecret" : "Wa5#U^R@d!UsK3y"
                        },
                        "tacacsSettings" : {
                            "sharedSecret" : "WaSH(#T@cAC5Ke3",
                            "connectModeOptions" : "OFF"
                        },
                        "profileName" : "Cisco",
                        "coaPort" : 1700,
                        "NetworkDeviceIPList" : [ {
                            "ipaddress" : form.cleaned_data['discoverIp'],
                            "mask" : 32
                        } ],
                        "NetworkDeviceGroupList" : [ "Location#All Locations#" + form.cleaned_data['deviceLocation'], "Device Type#All Device Types#" + form.cleaned_data['deviceType'] ]
                      }
                }
                global addNetworkDeviceResponse
                addNetworkDeviceResponse = requests.post(addNetworkDevice_url,data=json.dumps(data),headers=iseheaders)
                iseStatusCode = str(addNetworkDeviceResponse.status_code)
                
                #Run NetBrain IP Discovery
                discoverIPNow_url = netbrainserver_url + "API/CMDB/discovery/discoverIPNow"
                data={
                    "mgmtIPs":[form.cleaned_data['discoverIp']],
                    "cliType": "1"
                }
                global discoverIPNowResponse
                discoverIPNowResponse = requests.post(discoverIPNow_url,data=json.dumps(data),headers=headers).json()["taskId"]

                #Run Prime IP Discovery
                bulkImport_url = primeserver_url + "op/devices/bulkImport"
                data={
                    "devicesImport" : {
                        "devices" : {
                            "device" : [ {
                                "ipAddress" : form.cleaned_data['discoverIp'],
                                "credentialProfileName" : "WUSTL_creds"
                            } ]
                        }
                    }
                }
                global bulkImportResponse
                bulkImportResponse = requests.put(bulkImport_url,data=json.dumps(data),headers=headers, verify=False).json()["mgmtResponse"]["bulkImportResult"][0]["jobName"]
                
                
                #Run all jobs until break
                while True:
                    timeout = time.time() + 60*1
                    
                    #run netbrain
                    getDiscoveryResult_url = netbrainserver_url + "API/CMDB/discovery/getDiscoveryResult/" + discoverIPNowResponse
                    getDiscoveryResultResponse = requests.get(getDiscoveryResult_url,headers=headers)
                    
                    #run prime
                    runHistory_url = primeserver_url + "op/jobService/runhistory"
                    runHistoryResponse = requests.get(runHistory_url,headers=headers, params="jobName=" + bulkImportResponse, verify=False)
            
                    #find the result for both in json
                    netbrainJobResult = getDiscoveryResultResponse.json()["executionLog"][0]["isFinished"]
                    primeJobResult = runHistoryResponse.json()["mgmtResponse"]["job"]
                    
                    #print(str(netbrainJobResult))
                    #print(str(primeJobResult))
                    
                    #if results are no longer false, or the job times out, break the while loop
                    if (netbrainJobResult != False and primeJobResult !=[]) or time.time() > timeout:
                        break

                #time in between running the while loop
                time.sleep(3.0)

                #save the output and censor the snmp string
                global resultLog
                netbrainResultLog = re.sub(r'\[(.*?)\]\[version', '[*****][version', getDiscoveryResultResponse.json()["devicesLog"][0]["deviceLog"]) 
                primeResultLog = str(runHistoryResponse.json()["mgmtResponse"]['job'])

                if iseStatusCode == "201":
                    iseLocationCode = re.sub(r'.*\/', '', str(addNetworkDeviceResponse.headers['Location']))
                    getNetworkDeviceResponse = requests.get(addNetworkDevice_url + "/" + iseLocationCode,headers=iseheaders).json()['NetworkDevice']
                    iseResultLog = str(getNetworkDeviceResponse)

                elif iseStatusCode == "400": 
                    iseResultLog = "Response [" + iseStatusCode + "].  Network Device Create failed: Device Name Already Exists."
                else:
                    iseResultLog = "ERROR: Response [" + iseStatusCode + "].  Unknown Response."
                

                logout_url= netbrainserver_url + "API/logout"
                requests.post(logout_url,data=json.dumps({"token": token}),headers=headers)

                #if valid rendering new view with values
                #the form values contains in cleaned_data dictionary
                return render(request, 'automationportal/deviceaddresult.html', {
                    'discoverIp': form.cleaned_data['discoverIp'],
                    'deviceName': form.cleaned_data['deviceName'],
                    'deviceDescription': form.cleaned_data['deviceDescription'],
                    #'username': form.cleaned_data['username'],
                    #'password': form.cleaned_data['password'],
                    #'deviceType': form.cleaned_data['deviceType'],
                    #'deviceLocation': form.cleaned_data['deviceLocation'],
                    'netbrainResultLog': netbrainResultLog,
                    'primeResultLog': primeResultLog,
                    'iseResultLog': iseResultLog,
                })

    else:
        #creating a new form
        form = DeviceAddForm()

    #returning form
    return render(request, 'automationportal/deviceadd.html', {'form':form});





def devicedelete(request):
    if not connectAuth(request):
        return render(request, 'automationportal/noaccess.html') 
    #if form is submitted
    if request.method == 'POST':
        #will handle the request later
        form = DeviceDeleteForm(request.POST)
 
        #checking if the form is valid or not 
        if form.is_valid():
            #variables in script
            user = form.cleaned_data['username']
            pwd = form.cleaned_data['password']
            iseuser = "restapi"         
            isepwd = "ysBzuRGn1kPM6MYxUxey74qb"  
            netbrainserver_url = "http://netbrain.net.wustl.edu/ServicesAPI/"
            primeserver_url = "https://prime.net.wustl.edu/webacs/api/v3/"
            iseserver_url = "https://pan-01.ise.wustl.edu:9060/ers/"
            headers = {"Content-Type": "application/json", "Accept": "application/json"}
            iseheaders = {"Content-Type": "application/json", "Accept": "application/json"}
            TENANT = "Initial Tenant"
            DOMAIN = "WUIT" 

            #netbrain/prime header information
            token_url= netbrainserver_url + "API/login"
            basic_data = user + ":" + pwd           
            basic_data = basic_data.encode("ascii")
            auth_data = base64.b64encode(basic_data)
            headers["Authorization"] = "Basic " + auth_data.decode()

            #ise header information
            isebasic_data = iseuser + ":" + isepwd
            isebasic_data = isebasic_data.encode("ascii")
            iseauth_data = base64.b64encode(isebasic_data)
            iseheaders["Authorization"] = "Basic " + iseauth_data.decode()

            #Get NetBrain Token
            gettoken = requests.post(token_url,headers=headers)
            
            if "Incorrect username or password" in gettoken.json()["statusDescription"]:
                messages.warning(request, 'Username or password is incorrect.')
                return render(request, 'automationportal/devicedelete.html', {})

            elif gettoken.json()['statusDescription'] == "Success.":
                global token
                token = gettoken.json()["token"]
                headers["Token"]=token
            
                #set tenant and domain
                setCurrentDomain_url = netbrainserver_url + "API/setCurrentDomain"
                setCurrentDomainResponse = requests.post(setCurrentDomain_url,data=json.dumps({"tenantName":TENANT,"domainName":DOMAIN}),headers=headers)

                #Run ISE Remove Device
                getNetworkDevice_url = iseserver_url + "config/networkdevice"
                getNetworkDeviceResponseResources = requests.get(getNetworkDevice_url, params="filter=ipaddress.EQ." + form.cleaned_data['discoverIp'], headers=iseheaders).json()["SearchResult"]["resources"]
                #print (str(getNetworkDeviceResponseResources))

                if getNetworkDeviceResponseResources == []:
                    iseResultLog = "The device IP does not exist.  There is nothing to delete.  This could be because the IP falls within a larger subnet."

                else:
                    getNetworkDeviceResponseId = requests.get(getNetworkDevice_url, params="filter=ipaddress.EQ." + form.cleaned_data['discoverIp'], headers=iseheaders).json()["SearchResult"]["resources"][0]["id"]
                    #print (str(getNetworkDeviceResponseId))

                    deleteNetworkDevice = requests.delete(getNetworkDevice_url + "/" + getNetworkDeviceResponseId,headers=iseheaders)
                    #iseStatusCode = str(deleteNetworkDevice.status_code)            

                    #if iseStatusCode == "204":
                    iseResultLog = "Network Device Was Successfully Deleted."

                    #elif iseStatusCode == "404": 
                    #    iseResultLog = "ERROR: Response [" + iseStatusCode + "].  The network device does not exist."
                    #else:
                    #    iseResultLog = "ERROR: Response [" + iseStatusCode + "].  Unknown Response."

                #Run NetBrain Remove Device
                checkIP = form.cleaned_data['discoverIp']

                getDevicesByIP_url = netbrainserver_url + "API/CMDB/device/getDevicesByIP"
                getDevicesByIPResponse = requests.get(getDevicesByIP_url, params="IP=" + checkIP, headers=headers)

                if getDevicesByIPResponse.json()['devices'] == []:
                    netbrainResultLog = "The device IP does not exist.  There is nothing to delete."

                else:
                    deleteDevice_url = netbrainserver_url + "API/CMDB/device/deleteDevice"
                    data={
                        "IP": form.cleaned_data['discoverIp']
                    }
                    global deleteDeviceResponse
                    deleteDeviceResponse = requests.delete(deleteDevice_url,data=json.dumps(data),headers=headers)
                    netbrainResultLog = "Network Device Was Successfully Deleted."

                #Run Prime Remove Device
                exportDevices_url = primeserver_url + "op/devices/exportDevices"
                
                global exportDevicesResponse

                exportDevicesResponse = requests.get(exportDevices_url,params = "ipAddress=" + form.cleaned_data['discoverIp'],headers=headers, verify=False).json()["mgmtResponse"]["devicesExportResult"][0]["devices"]
                print (str(exportDevicesResponse))
                if exportDevicesResponse['device'] == []:
                    primeResultLog = "The device IP does not exist.  There is nothing to delete."

                else:
                    data={
                        "removalJobParamsDTO" : {
                            #"deleteAPs" : true,
                            "ipAddressList" : {
                                "ipAddressList" : [ {
                                    "address" : form.cleaned_data['discoverIp']
                                } ]
                            }
                        }
                    }
                    removalJob_url = primeserver_url + "op/devices/removalJob"
                    removalJobResults = requests.post(removalJob_url,data=json.dumps(data),headers=headers, verify=False).json()["mgmtResponse"]["removalJobResultDTO"][0]["jobName"]  

                    #Run all jobs until break
                    while True:
                        timeout = time.time() + 60*1
                                   
                        #run prime
                        runHistory_url = primeserver_url + "op/jobService/runhistory"
                        runHistoryResponse = requests.get(runHistory_url,headers=headers, params="jobName=" + removalJobResults, verify=False)
                
                        #find the result for both in json
                        primeJobResult = runHistoryResponse.json()["mgmtResponse"]["job"]
                        
                        #print(str(primeJobResult))
                        
                        #if results are no longer false, or the job times out, break the while loop
                        if primeJobResult !=[] or time.time() > timeout:
                            break
                            #if results are no longer false, or the job times out, break the while loop

                    #time in between running the while loop
                    time.sleep(3.0)
                    
                    primeResultLog = "Network Device Was Successfully Deleted."

                logout_url= netbrainserver_url + "API/logout"
                requests.post(logout_url,data=json.dumps({"token": token}),headers=headers)
    
                #if form is submitted
                return render (request, 'automationportal/devicedeleteresult.html', {
                    'discoverIp': form.cleaned_data['discoverIp'],
                    #'username': form.cleaned_data['username'],
                    #'password': form.cleaned_data['password'],
                    'iseResultLog': iseResultLog,
                    'primeResultLog': primeResultLog,
                    'netbrainResultLog': netbrainResultLog,
                })

    else:
        #creating a new form
        form = DeviceDeleteForm()

    #returning form
    return render(request, 'automationportal/devicedelete.html', {'form':form});    







def ipsearch(request):
    if not connectAuth(request):
        return render(request, 'automationportal/noaccess.html') 
    #if form is submitted
    if request.method == 'POST':
        #will handle the request later
        form = DeviceAddForm(request.POST)
 
        #checking if the form is valid or not 
        if form.is_valid():
            #variables in script

            #Check if device already exists and stop script if so
            checkIP = form.cleaned_data['discoverIp']

            getDevicesByIP_url = netbrainserver_url + "API/CMDB/device/getDevicesByIP"
    
            getDevicesByIPResponseStatusCode = requests.get(getDevicesByIP_url, params="IP=" + checkIP, headers=headers).json()["statusCode"]
            getDevicesByIPResponseHostname = requests.get(getDevicesByIP_url, params="IP=" + checkIP, headers=headers).json()["devices"][0]["hostname"]


            if getDevicesByIPResponseStatusCode == 0 and getDevicesByIPResponseHostname != "":
                #print (getDevicesByIPResponseHostname)  
                messages.warning(request, 'Device "' + getDevicesByIPResponseHostname + '" already exists with IP: ' + checkIP)
                return render(request, 'automationportal/ipsearch.html', {
                    'discoverIp': form.cleaned_data['discoverIp'],
                    })
            else:
                return render(request, 'automationportal/ipsearch.html', {
                'discoverIp': form.cleaned_data['discoverIp'],
                })
            






def calcpath(request):
    if not connectAuth(request):
        return render(request, 'automationportal/noaccess.html') 
    #if form is submitted
    if request.method == 'POST':
        #will handle the request later
        form = CalcPathForm(request.POST)
 
        #checking if the form is valid or not 
        if form.is_valid():
            #variables in script
            user = form.cleaned_data['username']
            pwd = form.cleaned_data['password']
            netbrainserver_url = "http://netbrain.net.wustl.edu/ServicesAPI/"
            headers = {"Content-Type": "application/json", "Accept": "application/json"}
            iseheaders = {"Content-Type": "application/json", "Accept": "application/json"}
            TENANT = "Initial Tenant"
            DOMAIN = "WUIT" 

            
            #netbrain/prime header information
            token_url= netbrainserver_url + "API/login"
            basic_data = user + ":" + pwd           
            basic_data = basic_data.encode("ascii")
            auth_data = base64.b64encode(basic_data)
            headers["Authorization"] = "Basic " + auth_data.decode()
            
            #Get NetBrain Token
            gettoken = requests.post(token_url,headers=headers)
            
            if "Incorrect username or password" in gettoken.json()["statusDescription"]:
                messages.warning(request, 'Username or password is incorrect.')
                return render(request, 'automationportal/calcpath.html', {})

            elif gettoken.json()['statusDescription'] == "Success.":
                global token
                token = gettoken.json()["token"]
                headers["Token"]=token

                #set tenant and domain
                setCurrentDomain_url = netbrainserver_url + "API/setCurrentDomain"
                setCurrentDomainResponse = requests.post(setCurrentDomain_url,data=json.dumps({"tenantName":TENANT,"domainName":DOMAIN}),headers=headers)

                calcPath_url = netbrainserver_url + "API/CMDB/path/calcPath"
                data={
                    "sourceIp": form.cleaned_data['sourceIp'],
                    "sourcePort": form.cleaned_data['sourcePort'],
                    "destIp": form.cleaned_data['destIp'],
                    "destPort": form.cleaned_data['destPort'],
                    "pathAnalysisSet":1,
                    "protocol":form.cleaned_data['protocol'],
                    "isLive":1
                }
                global calcPathResponse
                calcPathResponse = requests.post(calcPath_url,data=json.dumps(data),headers=headers).json()["taskID"]

                #run netbrain
                getPath_url = netbrainserver_url + "API/CMDB/path/getPath/"
                print (str(getPath_url + calcPathResponse))
                print ("token: " + token)
                time.sleep(20)
                getPathResponse = requests.get(getPath_url + calcPathResponse,headers=headers).json()

                #save the outputhopList
                global netbrainResultLog
                netbrainResultLog = json.dumps(getPathResponse, indent=2)             
                print (netbrainResultLog)

                logout_url= netbrainserver_url + "API/logout"
                requests.post(logout_url,data=json.dumps({"token": token}),headers=headers)

                #if valid rendering new view with values
                #the form values contains in cleaned_data dictionary
                return render(request, 'automationportal/calcpathresult.html', {
                    'netbrainResultLog': netbrainResultLog,
                })

    else:
        #creating a new form
        form = CalcPathForm()

    #returning form
    return render(request, 'automationportal/calcpath.html', {'form':form});



def noaccess(request):
    return render(request, 'automationportal/noaccess.html')



            