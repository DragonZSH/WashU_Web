from django.shortcuts import render
from django.http import HttpResponse
from django.contrib import messages
from django.conf import settings

from .forms import DeviceAddForm, DeviceIpForm, DeviceDeployForm, DeviceIpListForm, DeviceIpOrMACListForm, CalcPathForm, CalcPathRISForm
from .classISE import ISE
from .classPrime import Prime
from .classNetbrain import Netbrain
from .classStatseeker import Statseeker

import requests
import json
import base64
import time
import re
import logging

# Create your views here.
def connectAuth(request):
    wustlEduGroupNames = ['ORG-WUIT-SI-NE-Network', 'ORG-WUIT-SI-SOC-CC', 'ORG-WUIT-SI-SOC-MAC', 'WUIT_EUS_SI_NetworkGear_ContrReadWrite', 'WUIT_EUS_SI_NetworkGear_ReadWrite', 'InfoSec Users', 'ORG-WUIT-SI-NE-InfServ']
    #fakeGroups = ['ORG-FAKEGROUP', 'ORG-NOTREAL']
    result = False
    for item in wustlEduGroupNames:
        if item in request.META['wustlEduGroups']:
            result = True
    return (result)

def connectAuth_EUS(request):
    wustlEduGroupNames = ['ORG-WUIT-EUS-Engineering', 'snwuit-si-network-telecom']
    #fakeGroups = ['ORG-FAKEGROUP', 'ORG-NOTREAL']
    result = False
    for item in wustlEduGroupNames:
        if item in request.META['wustlEduGroups']:
            result = True
    return (result)

def connectAuth_RIS(request):
    wustlEduGroupNames = ['RIS-IT-ADMIN']
    #fakeGroups = ['ORG-FAKEGROUP', 'ORG-NOTREAL']
    result = False
    for item in wustlEduGroupNames:
        if item in request.META['wustlEduGroups']:
            result = True
    return (result)

def noaccess(request):
    return render(request, 'automationportal/noaccess.html')

def index(request):
    if not connectAuth(request) and not connectAuth_EUS(request):
        return render(request, 'automationportal/noaccess.html')
    return render(request, 'automationportal/home.html')

def mygroups(request):
    REQ_META = request.META['wustlEduGroupMembership']
    metaListGroup = REQ_META.split(";")
    metaListGroupSorted = sorted(metaListGroup, key=lambda s: s.lower())

    userGroupList = []

    tacacsRegex = r'CN=ORG-WUIT-SI-NE-Network,OU=Groups,DC=accounts,DC=ad,DC=wustl,DC=edu|CN=ORG-WUIT-SI-SOC-CC,OU=Groups,DC=accounts,DC=ad,DC=wustl,DC=edu|CN=ORG-WUIT-SI-SOC-MAC,OU=Groups,DC=accounts,DC=ad,DC=wustl,DC=edu|CN=WUIT_EUS_SI_NetworkGear_ContrReadWrite,OU=Application Groups,OU=Resource Groups,OU=WUIT,OU=Groups,DC=accounts,DC=ad,DC=wustl,DC=edu|CN=WUIT_EUS_SI_NetworkGear_ReadWrite,OU=Application Groups,OU=Resource Groups,OU=WUIT,OU=Groups,DC=accounts,DC=ad,DC=wustl,DC=edu|CN=InfoSec Users,OU=Migration-Medpriv,OU=Groups,DC=accounts,DC=ad,DC=wustl,DC=edu|CN=ORG-WUIT-EUS-Engineering,OU=Groups,DC=accounts,DC=ad,DC=wustl,DC=edu'
    tacacsFind = re.findall(tacacsRegex, str(metaListGroupSorted))
    userGroupList = userGroupList + tacacsFind
    logging.info("TACACS FIND: " + str(tacacsFind))
    logging.info("-----")

    tacacsRORegex = r'CN=ORG-WUIT-SI-SOC-PAA,OU=Groups,DC=accounts,DC=ad,DC=wustl,DC=edu|CN=WUIT_EUS_SI_NetworkGear_ContrRead,OU=Application Groups,OU=Resource Groups,OU=WUIT,OU=Groups,DC=accounts,DC=ad,DC=wustl,DC=edu|CN=WUIT_EUS_SI_NetworkGear_Read,OU=Application Groups,OU=Resource Groups,OU=WUIT,OU=Groups,DC=accounts,DC=ad,DC=wustl,DC=edu'
    tacacsROFind = re.findall(tacacsRORegex, str(metaListGroupSorted))
    userGroupList = userGroupList + tacacsROFind
    logging.info("TACACS Read Only FIND: " + str(tacacsROFind))
    logging.info("-----")

    vpnRegex = r'CN=ORG-WUIT-SI-NE-Network,OU=Groups,DC=accounts,DC=ad,DC=wustl,DC=edu|CN=ORG-WUIT-SI-SOC-CC,OU=Groups,DC=accounts,DC=ad,DC=wustl,DC=edu|CN=ORG-WUIT-SI-SOC-MAC,OU=Groups,DC=accounts,DC=ad,DC=wustl,DC=edu|CN=WUIT_EUS_SI_NetworkGear_ContrReadWrite,OU=Application Groups,OU=Resource Groups,OU=WUIT,OU=Groups,DC=accounts,DC=ad,DC=wustl,DC=edu|CN=WUIT_EUS_SI_NetworkGear_ReadWrite,OU=Application Groups,OU=Resource Groups,OU=WUIT,OU=Groups,DC=accounts,DC=ad,DC=wustl,DC=edu|CN=grsw50_students,OU=Papercut,OU=IdM Resources,OU=IdM Groups,DC=accounts,DC=ad,DC=wustl,DC=edu|CN=vpn-users_cfuusers,OU=VPN Access,OU=IST,OU=IdM Groups,DC=accounts,DC=ad,DC=wustl,DC=edu|CN=vpn-users_fpm,OU=VPN Access,OU=IST,OU=IdM Groups,DC=accounts,DC=ad,DC=wustl,DC=edu|CN=vpn-users_fpm_usn,OU=VPN Access,OU=IST,OU=IdM Groups,DC=accounts,DC=ad,DC=wustl,DC=edu|CN=vpn-users_fpm_dcadmin,OU=VPN Access,OU=IST,OU=IdM Groups,DC=accounts,DC=ad,DC=wustl,DC=edu|CN=firesaftey_vpn,OU=VPN Access,OU=IST,OU=IdM Groups,DC=accounts,DC=ad,DC=wustl,DC=edu|CN=VPN-users_IST,OU=VPN Access,OU=IST,OU=IdM Groups,DC=accounts,DC=ad,DC=wustl,DC=edu|CN=law_vpn,OU=VPN Access,OU=law,OU=danforth campus,OU=Groups,DC=accounts,DC=ad,DC=wustl,DC=edu|CN=vpn-users_mscit,OU=cits,OU=Medical Campus,OU=Groups,DC=accounts,DC=ad,DC=wustl,DC=edu|CN=VPN-users_NSS-IST,OU=VPN Access,OU=IST,OU=IdM Groups,DC=accounts,DC=ad,DC=wustl,DC=edu|CN=BU_Faculty,OU=Business,OU=IdM Groups,DC=accounts,DC=ad,DC=wustl,DC=edu|CN=BU_Staff,OU=Business,OU=IdM Groups,DC=accounts,DC=ad,DC=wustl,DC=edu|CN=BU_Students,OU=Business,OU=IdM Groups,DC=accounts,DC=ad,DC=wustl,DC=edu|CN=bu_guests-degree,OU=Business,OU=IdM Groups,DC=accounts,DC=ad,DC=wustl,DC=edu|CN=bu-guests-enrolled,OU=Business,OU=IdM Groups,DC=accounts,DC=ad,DC=wustl,DC=edu|CN=bu_guests-majorsminors,OU=Business,OU=IdM Groups,DC=accounts,DC=ad,DC=wustl,DC=edu|CN=bu_guests-vpn,OU=OLIN,OU=Groups,DC=accounts,DC=ad,DC=wustl,DC=edu|CN=olin_vpn-users_library,OU=VPN Access,OU=olin library,OU=danforth campus,OU=Groups,DC=accounts,DC=ad,DC=wustl,DC=edu|CN=vpn-users_wuit_srv_rmt_low,OU=VPN Access,OU=IST,OU=IdM Groups,DC=accounts,DC=ad,DC=wustl,DC=edu|CN=vpn-users_wuit_srv_rmt_mod,OU=VPN Access,OU=IST,OU=IdM Groups,DC=accounts,DC=ad,DC=wustl,DC=edu|CN=vpn-users_wuit_srv_rmt_high,OU=VPN Access,OU=IST,OU=IdM Groups,DC=accounts,DC=ad,DC=wustl,DC=edu|CN=vpn-users_wushcs,OU=VPN Access,OU=IST,OU=IdM Groups,DC=accounts,DC=ad,DC=wustl,DC=edu'
    vpnFind = re.findall(vpnRegex, str(metaListGroupSorted))
    userGroupList = userGroupList + vpnFind
    logging.info("VPN FIND: " + str(vpnFind))
    logging.info("-----")

    msvpnRegex = r'CN=WUIT_EUS_SI_NETWORKING_VPN_USERS,OU=Resource Groups,OU=WUIT,OU=Groups,DC=accounts,DC=ad,DC=wustl,DC=edu|CN=Genetics_Vpn,OU=genetics,OU=network security,OU=CITS,OU=Medical Campus,OU=Groups,DC=accounts,DC=ad,DC=wustl,DC=edu|CN=GenomeSciences_Vpn,OU=genome science,OU=network security,OU=CITS,OU=Medical Campus,OU=Groups,DC=accounts,DC=ad,DC=wustl,DC=edu|CN=WUIT_EUS_9999_VPN_USERS,OU=resource groups,OU=wuit,OU=Groups,DC=accounts,DC=ad,DC=wustl,DC=edu'
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
        'tacacsROFind': tacacsROFind,
        'vpnFind': vpnFind,
        'msvpnFind': msvpnFind,
        'ibxFind': ibxFind,
        'diffGroupList': diffGroupList,
    })

def get_device(request):

    ise = ISE()
    ise.get_device(deviceIp)
    prime = Prime()
    prime.get_device(deviceIp)
    #netbrain = Netbrain()
    #netbrain.get_device(deviceIp)
    #netbrain.logout()

def device_add(request):
    if not connectAuth(request):
        return render(request, 'automationportal/noaccess.html')

    #if form is submitted
    if request.method == 'POST':
        #will handle the request later
        form = DeviceAddForm(request.POST)

        #If the form is valid, run the device_add functions
        if form.is_valid():
            #Enter Variables Here
            deviceName = form.cleaned_data['deviceName']
            deviceIp = form.cleaned_data['deviceIp']
            deviceDescription = form.cleaned_data['deviceDescription']
            deviceLocation = form.cleaned_data['deviceLocation']
            deviceType = form.cleaned_data['deviceType']
            deviceSNMP = form.cleaned_data['deviceSNMP']
            radiusSecret = "Wa5#U^R@d!UsK3y"
            tacacsSecret = "WaSH(#T@cAC5Ke3"

            #Run Functions
            print ("STARTING ISE")
            ise = ISE()
            ise_device_add_result = ise.device_add(deviceName,
                deviceIp,
                deviceDescription,
                deviceLocation,
                deviceType,
                radiusSecret,
                tacacsSecret)
            print ("ISE FINISHED")
            print ("--------------------")
            print ("STARTING PRIME")
            prime = Prime()
            prime_device_add_result = prime.device_add(deviceIp,deviceSNMP)
            print ("PRIME FINISHED")
            print ("--------------------")
            print ("STARTING NETBRAIN")
            netbrain = Netbrain()
            netbrain_device_add_result = netbrain.device_add(deviceIp)
            netbrain.logout()
            print ("NETBRAIN FINISHED")
            print ("--------------------")
            print ("STARTING STATSEEKER")
            statseeker = Statseeker()
            statseeker_device_add_result = statseeker.device_add(deviceIp,deviceLocation)
            print ("STATSEEKER FINISHED")
            print ("--------------------")

        return render(request, 'automationportal/deviceaddresult.html', {
            'deviceIp': deviceIp,
            'deviceName': deviceName,
            'deviceDescription': deviceDescription,
            'netbrainResult': netbrain_device_add_result,
            'primeResult': prime_device_add_result,
            'iseResult': ise_device_add_result,
            'statseekerResult': statseeker_device_add_result,
        })

    #If the form is not valid, pass empty form
    else:
        form = DeviceAddForm()

    #returning page with form
    return render(request, 'automationportal/deviceadd.html', {'form':form});

def device_delete(request):
    if not connectAuth(request):
        return render(request, 'automationportal/noaccess.html')

    #if form is submitted
    if request.method == 'POST':
        #will handle the request later
        form = DeviceIpForm(request.POST)

        #If the form is valid, run the device_delete functions
        if form.is_valid():
            #Enter Variables Here
            deviceIp = form.cleaned_data['deviceIp']

            #Run Functions
            print ("STARTING ISE")
            ise = ISE()
            ise_device_delete_result = ise.device_delete(deviceIp)
            print ("ISE FINISHED")
            print ("--------------------")
            print ("STARTING PRIME")
            prime = Prime()
            prime_device_delete_result = prime.device_delete(deviceIp)
            print ("PRIME FINISHED")
            print ("--------------------")
            print ("STARTING NETBRAIN")
            netbrain = Netbrain()
            netbrain_device_delete_result = netbrain.device_delete(deviceIp)
            netbrain.logout()
            print ("NETBRAIN FINISHED")
            print ("--------------------")
            print ("STARTING STATSEEKER")
            statseeker = Statseeker()
            statseeker_device_delete_result = statseeker.device_delete(deviceIp)
            print ("STATSEEKER FINISHED")
            print ("--------------------")

        return render(request, 'automationportal/devicedeleteresult.html', {
            'deviceIp': deviceIp,
            'netbrainResult': netbrain_device_delete_result,
            'primeResult': prime_device_delete_result,
            'iseResult': ise_device_delete_result,
            'statseekerResult': statseeker_device_delete_result
        })

    #If the form is not valid, pass empty form
    else:
        form = DeviceIpForm()

    #returning page with form
    return render(request, 'automationportal/devicedelete.html', {'form':form});

def device_deploy(request):
    if not connectAuth(request):
        return render(request, 'automationportal/noaccess.html')

    #if form is submitted
    if request.method == 'POST':
        #will handle the request later
        form = DeviceDeployForm(request.POST)

        #If the form is valid, run the device_delete functions
        if form.is_valid():
            #Enter Variables Here
            deviceIp = form.cleaned_data['deviceIp']
            deviceTemplate = form.cleaned_data['deviceTemplate']
            #asaChoice = form.cleaned_data['asaChoice']
            deviceNameif = form.cleaned_data['deviceNameif']
            #deviceType = form.cleaned_data['deviceType']

            #set up variables for templates

            #if deviceType == "MED_2960_L2" or "MED_3650_L2" or "MED_3850_L3" or "MED_4500_L2":
            if deviceTemplate == "Med":
                templateList = [ "WUSTL Add Local Username",
                "WUSTL Banner",
                "WUSTL VTY Configuration",
                "WUSTL SNMP Configuration",
                "WUSTL Logging Configuration",
                "WUSTL NTP Configuration",
                "WUSTL Hardening Configuration MED",
                "WUSTL QoS Configuration - IOS",
                "WUSTL TACACS Configuration"
                ]

            else:
                templateList = [ "WUSTL Add Local Username",
                "WUSTL Banner",
                "WUSTL VTY Configuration",
                "WUSTL SNMP Configuration",
                "WUSTL Logging Configuration",
                "WUSTL NTP Configuration",
                "WUSTL Hardening Configuration DNF",
                "WUSTL QoS Configuration - IOS",
                "WUSTL TACACS Configuration"
                ]
            #print (templateList)
            #Run Functions
            prime = Prime()
            (prime_device_deploy_result,prime_device_deploy_resultList) = prime.deploy_template(deviceIp,templateList,deviceNameif)

            return render(request, 'automationportal/devicedeployresult.html', {
                'deviceIp': deviceIp,
                'primeResult': prime_device_deploy_result,
                'primeResultList': prime_device_deploy_resultList,
            })

    #If the form is not valid, pass empty form
    else:
        form = DeviceDeployForm()

    #returning page with form
    return render(request, 'automationportal/devicedeploy.html', {'form':form});

def get_connected_switchport(request):
    if not connectAuth(request) and not connectAuth_EUS(request):
        return render(request, 'automationportal/noaccess.html')
    #if form is submitted
    if request.method == 'POST':
        #will handle the request later
        form = DeviceIpListForm(request.POST)

        #If the form is valid, run the device_delete functions
        if form.is_valid():
            #Enter Variables Here
            deviceIpString = form.cleaned_data['deviceIp'].replace(" ","")
            deviceIp = deviceIpString.split(',')
            resultList = []

            #Run Functions
            netbrain = Netbrain()
            for ip in deviceIp:
                result = netbrain.get_connected_switchport(ip)
                resultList.append(result)

            netbrain_get_connected_switchport_result = resultList
            netbrain.logout()
            print ('\n'.join(netbrain_get_connected_switchport_result))
            return render(request, 'automationportal/getswitchportresult.html', {
                'netbrainResult': netbrain_get_connected_switchport_result,
            })

    #If the form is not valid, pass empty form
    else:
        form = DeviceIpListForm()

    #returning page with form
    return render(request, 'automationportal/getswitchport.html', {'form':form});

def get_client_details(request):
    #if form is submitted

    if request.method == 'POST':
        #will handle the request later
        form = DeviceIpOrMACListForm(request.POST)

        #If the form is valid, run the device_delete functions
        if form.is_valid():
            #Enter Variables Here
            deviceIpString = form.cleaned_data['deviceIpOrMAC'].replace(" ","")
            deviceIp = deviceIpString.split(',')
            resultList = []
            while '' in deviceIp:
                deviceIp.remove('')
            print (deviceIp)
            #Run Functions
            prime = Prime()
            for ip in deviceIp:
                connectionType, deviceName, clientInterface, ipAddress, macAddress, apName = prime.get_client_details(ip)
                resultList.extend((
                    connectionType,
                    deviceName,
                    clientInterface,
                    ipAddress,
                    macAddress,
                    apName,
                    "-"))

            prime_get_client_details_result = resultList

            print ('\n'.join(prime_get_client_details_result))
            return render(request, 'automationportal/getclientdetailsresult.html', {
                'primeResult': prime_get_client_details_result,
                'connectionType': connectionType,
                'deviceName': deviceName,
                'clientInterface': clientInterface,
                'ipAddress': ipAddress,
                'macAddress': macAddress,
                'apName': apName,
            })

    #If the form is not valid, pass empty form
    else:
        form = DeviceIpOrMACListForm()

    #returning page with form
    return render(request, 'automationportal/getclientdetails.html', {'form':form});


def calc_path(request):
    if not connectAuth(request):
        return render(request, 'automationportal/noaccess.html')
    #if form is submitted
    if request.method == 'POST':
        #will handle the request later
        form = CalcPathForm(request.POST)

        #If the form is valid, run the device_add functions
        if form.is_valid():
            #Enter Variables Here
            protocol = form.cleaned_data['protocol']
            sourceIp = form.cleaned_data['sourceIp']
            sourcePort = form.cleaned_data['sourcePort']
            destinationIp = form.cleaned_data['destinationIp']
            destinationPort = form.cleaned_data['destinationPort']
            type = 1

            #Run Functions
            netbrain = Netbrain()
            netbrain_calc_path_result = netbrain.calc_path(type,protocol,sourceIp,sourcePort,destinationIp,destinationPort)
            netbrain.logout()

            return render(request, 'automationportal/calcpathresult.html', {
                'netbrainResult': netbrain_calc_path_result,
            })

    #If the form is not valid, pass empty form
    else:
        form = CalcPathForm()

    #returning page with form
    return render(request, 'automationportal/calcpath.html', {'form':form});

def calc_path_ris(request):
    if not connectAuth(request) and not connectAuth_RIS(request):
        return render(request, 'automationportal/noaccess.html')
    #if form is submitted
    if request.method == 'POST':
        #will handle the request later
        form = CalcPathRISForm(request.POST)

        #If the form is valid, run the device_add functions
        if form.is_valid():
            #Enter Variables Here
            sourceIp = form.cleaned_data['sourceIp']
            destinationIp = form.cleaned_data['destinationIp']

            #Run Functions
            netbrain = Netbrain()
            (srcDeviceNameList,interfaceList,bandwidthList) = netbrain.calc_path_ris(sourceIp,destinationIp)
            netbrain.logout()

            return render(request, 'automationportal/calcpathrisresult.html', {
                'srcDeviceNameList': srcDeviceNameList,
                'interfaceList': interfaceList,
                'bandwidthList': bandwidthList,
            })

    #If the form is not valid, pass empty form
    else:
        form = CalcPathRISForm()

    #returning page with form
    return render(request, 'automationportal/calcpathris.html', {'form':form});


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

            getDevicesByIPResponseStatusCode = requests.get(getDevicesByIP_url, params="IP=" + checkIP, headers=headers, verify=False).json()["statusCode"]
            getDevicesByIPResponseHostname = requests.get(getDevicesByIP_url, params="IP=" + checkIP, headers=headers, verify=False).json()["devices"][0]["hostname"]


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
