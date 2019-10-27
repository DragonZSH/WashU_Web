from django.test import TestCase

# Create your tests here.


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





'''
device_add() funciton  and device_delete() functions come form views.py
I mainly edited the "RUN FUNCTIONS" part

'''


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

# ---------------------- edited part below------------------------------------------------------------------------------


             #Run Functions
            print("STARTING ISE")
            try:
                ise = ISE()
                ise_device_add_result = ise.device_add(deviceName,
                                                       deviceIp,
                                                       deviceDescription,
                                                       deviceLocation,
                                                       deviceType,
                                                       radiusSecret,
                                                       tacacsSecret)
                print("ISE FINISHED")
            except Exception as e1:
                print("ISE FAILED")
                print("Error:", e1)


            print("STARTING PRIME")
            try:
                prime = Prime()
                prime_device_add_result = prime.device_add(deviceIp, deviceSNMP)
                print("PRIME FINISHED")
            except Exception as e2:
                print("PRIME FAILED")
                print("Error:", e2)


            print("STARTING NETBRAIN")
            try:
                netbrain = Netbrain()
                netbrain_device_add_result = netbrain.device_add(deviceIp)
                netbrain.logout()
                print("NETBRAIN FINISHED")
            except Exception as e3:
                print("NETBRAIN FAILED")
                print("Error:", e3)


            print("STARTING STATSEEKER")
            try:
                statseeker = Statseeker()
                statseeker_device_add_result = statseeker.device_add(deviceIp, deviceLocation)
                print("STATSEEKER FINISHED")
            except Exception as e4:
                print("STATSEEKER FAILED")
                print("Error:", e4)


# ---------------------- edited part above------------------------------------------------------------------------------




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

# ---------------------- edited part below------------------------------------------------------------------------------

            #Run Functions
            print ("STARTING ISE")
            try:
                ise = ISE()
                ise_device_delete_result = ise.device_delete(deviceIp)
                print("ISE FINISHED")
            except Exception as e1:
                print("ISE FAILED")
                print("Error:", e1)



            print("STARTING PRIME")
            try:
                prime = Prime()
                prime_device_delete_result = prime.device_delete(deviceIp)
                print("PRIME FINISHED")
            except Exception as e2:
                print("PRIME FAILED")
                print("Error:", e2)


            print("STARTING NETBRAIN")
            try:
                netbrain = Netbrain()
                netbrain_device_delete_result = netbrain.device_delete(deviceIp)
                netbrain.logout()
                print("NETBRAIN FINISHED")
            except Exception as e3:
                print("NETBRAIN FAILED")
                print("Error:", e3)


            print("STARTING STATSEEKER")
            try:
                statseeker = Statseeker()
                statseeker_device_delete_result = statseeker.device_delete(deviceIp)
                print("STATSEEKER FINISHED")
            except Exception as e4:
                print("STATSEEKER FAILED")
                print("Error:", e4)



# ---------------------- edited part above------------------------------------------------------------------------------




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



