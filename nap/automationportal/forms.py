#importing forms
from django import forms
from .classISE import ISE

#creating our forms
class DeviceAddForm(forms.Form):
    ise = ISE()
    (deviceTypeList,deviceLocationList) = ise.get_device_type_and_location()
    snmpChoices = [('WUSTL_creds','v2'),('WUSTL_creds_snmpv3','v3')]
    deviceName = forms.CharField(widget=forms.TextInput({'placeholder': 'abc-123-wu-sw-0','size':'35'}),label='Enter the Device Hostname', max_length=30)
    deviceDescription = forms.CharField(widget=forms.TextInput({'placeholder': '3850 Switch in Building','size':'35'}),label='Enter a Description', max_length=30)
    deviceIp = forms.GenericIPAddressField(label='Enter the device IPv4 address', widget=forms.TextInput({'placeholder': '192.168.1.10','size':'35'}), max_length=15)
    deviceType = forms.CharField(label='Select the Device Type', widget=forms.Select(choices=deviceTypeList))
    deviceLocation = forms.CharField(label='Select the Device Location', widget=forms.Select(choices=deviceLocationList))
    deviceSNMP = forms.CharField(label='SNMP Version', initial='v2', widget=forms.Select(choices=snmpChoices))

class DeviceIpForm(forms.Form):
    deviceIp = forms.GenericIPAddressField(label='Enter the device IPv4 address', widget=forms.TextInput({'placeholder': '192.168.1.10','size':'35'}), max_length=15)

class DeviceIpListForm(forms.Form):
    deviceIp = forms.CharField(label='Enter device IPv4 address(es)', widget=forms.Textarea({'placeholder': '192.168.1.10, 192.168.1.11, 192.168.1.12','size':'70'}))

class DeviceDeployForm(forms.Form):
    templateChoices = [('Danforth','Danforth'),('Med','Med School')]
    deviceIp = forms.GenericIPAddressField(label='Enter the device IPv4 address', widget=forms.TextInput({'placeholder': '192.168.1.10','size':'35'}), max_length=15)
    #deviceTypeList = [('DNF_2960_L2','2960 - Danforth L2'),('MED_2960_L2','2960 - Med School L2'),('DNF_3650_L2','3650 - Danforth L2'),('MED_3650_L2','3650 - Med School L2'),('DNF_3850_L3','3850/4500-X - Danforth L3'),('MED_3850_L3','3850/4500-X - Med School L3'),('DNF_4500_L2','4506/7/10 - Danforth L2'),('MED_4500_L2','4506/7/10 - Med School L2'),('ASA','ASA')]
    #deviceType = forms.CharField(label='Select the Device Type', widget=forms.Select(choices=deviceTypeList))
    deviceTemplate = forms.CharField(label='Switch Template', initial='Danforth Switch', widget=forms.Select(choices=templateChoices))
    #asaChoice = forms.BooleanField(widget=forms.CheckboxInput(),label='Device is an ASA Device', required=False)
    deviceNameif = forms.CharField(widget=forms.TextInput({'size':'35'}),label='Enter the ASA mgmt nameif (skip if not ASA)', max_length=30, required=False)

    def clean(self):
        cleaned_data = super().clean()
        asaChoice = cleaned_data.get("asaChoice")
        deviceNameif = cleaned_data.get("deviceNameif")

        #if device type is ASA is checked
        if asaChoice:
            #if nameif is blank
            if deviceNameif == "":
                raise forms.ValidationError(
                    "Must enter an ASA mgmt nameif if the device is an ASA or VPN"
                )

class DeviceIpOrMACListForm(forms.Form):
    deviceIpOrMAC = forms.CharField(label='Enter device MAC and/or IPv4 address(es)', widget=forms.Textarea({'placeholder': '192.168.1.10, 192.168.1.11, 192.168.1.12, 00:11:22:33:44:55, 66:77:88:99:00:11'}))

class CalcPathForm(forms.Form):
    protocolChoices = [('IPv4','IP'),('TCP','TCP'),('UDP','UDP')]
    protocol = forms.CharField(label='Protocol', initial='IP', widget=forms.Select(choices=protocolChoices))
    sourceIp = forms.GenericIPAddressField(label='Enter the source IPv4 address', widget=forms.TextInput({'placeholder': '192.168.1.10','size':'35'}), max_length=15)
    sourcePort = forms.CharField(label='Enter the source port number', widget=forms.TextInput({'placeholder': '22 (if unknown type 12345)','size':'35'}), max_length=15)
    destinationIp = forms.GenericIPAddressField(label='Enter the destination IPv4 address', widget=forms.TextInput({'placeholder': '192.168.1.10','size':'35'}), max_length=15)
    destinationPort = forms.CharField(label='Enter the destination port number', widget=forms.TextInput({'placeholder': '22','size':'35'}), max_length=15)

class CalcPathRISForm(forms.Form):
    sourceIp = forms.GenericIPAddressField(label='Enter the starting IPv4 address', widget=forms.TextInput({'placeholder': '192.168.1.10','size':'35'}), max_length=15)
    destinationIp = forms.GenericIPAddressField(label='Enter the destination IPv4 address', widget=forms.TextInput({'placeholder': '192.168.1.10','size':'35'}), max_length=15)
