'''
@author: Michael Adams
@contributor: Nick Flamini
@use: This software is free to be used by anyone. No permission is needed.
@copyright: The author owns all copyrightto the below code. Contributors may request permission to make additions and changes the source code.
'''

from netmiko import ConnectHandler
from time import time
from time import sleep
import datetime
from multiprocessing.dummy import Pool as ThreadPool
import threading
from pathlib import Path
import json

class Switch_Driver:
    
    '''
    Constructor function. This logs the object into the switch
    @args hostname: hostname of the  device
    @args sw_username: username to log into the device
    @args sw_password: password associated with the hostname
    @args group: device group the device is a member of
    @args os: the operating system running on the device
    Possible device groups: access, cirbn-dist, cirbn-access, vpn-access, vss, resnet-dist, resnet-access, core, gw, voice-gw, special-access, dc-access
	Possible OS: ios, nx-os, dell
    '''
    
    def __init__(self, hostname, sw_username, sw_password, group, os):
        self.host = hostname
        self.user = sw_username
        self.password = sw_password
        self.device_group = group
        self.device_os = os
        self.net_connect = ConnectHandler(device_type='cisco_ios', ip=self.host + '.ilstu.net', username=self.user, password=self.password)
        output = self.net_connect.send_command('terminal length 0')

    '''
    Send custom command to the device.
    @args command: str command that needs to be run.
    @return: str
    '''
    def run_command(self, command):
        output = self.net_connect.send_command_timing(command, use_textfsm=False)
        return output
    '''
    Disconnect from the network device
    @return: str
    ''' 
    def disconnect(self):
        self.net_connect.disconnect()
        return self.host + ' has disconnected.'

    '''
    Save running-config to local storage
    @return: str
    '''
    def save(self):
        self.net_connect.send_command_timing('copy run start')
        self.net_connect.send_command_timing('') # Confirm
        self.net_connect.send_command_expect('', expect_string = r'\#') # Confirm again

        return self.host + 'has saved locally'

    '''
    Save running-config to atconfig
    @args username: username used to log into atconfig
    @args password: password associated with username
    @return: str
    '''
    def backup(self, username, password):
        scp_username = username
        scp_password = password
        try:
            if ('access' or 'cirbn') in self.device_group:
                if self.device_os == 'ios':
                    ### Turn off paging so no spacebar is needed
                    self.net_connect.send_command('terminal length 0')
                    ### Save to atconfig
                    self.net_connect.send_command_timing('copy run scp:')
                    self.net_connect.send_command_timing('10.40.201.21')
                    self.net_connect.send_command_timing(scp_username)
                    try:
                        self.net_connect.send_command_expect('/ilstu/config/cisco/rtr/' + self.host + '.cfg', expect_string = r'Password:')
                        self.net_connect.send_command_timing(scp_password)
                        print(self.host, 'backup is complete')
                    except:
                        print('**********', self.host, 'could not back up to atconfig')
                
                elif self.device_os == 'dell':
                    ### Turn off paging so no spacebar is needed
                    self.net_connect.send_command('terminal length 0')
                    ### Save to atconfig
                    try:
                        self.net_connect.send_command_timing('copy run scp://' + scp_username + '@10.40.201.21//ilstu/config/dell/' + self.host + '.cfg')
                        self.net_connect.send_command_timing(scp_password)
                        self.net_connect.send_command('y')
                        print(self.host, 'backup is complete')
                    except:
                        print('**********', self.host, 'could not back up to atconfig')

            elif self.device_group == 'resnet-dist':
                ### Turn off paging so no spacebar is needed
                self.net_connect.send_command('terminal length 0')
                ### Save to atconfig
                try:
                    self.net_connect.send_command_timing('copy run scp:')
                    self.net_connect.send_command_timing('10.40.201.21')
                    self.net_connect.send_command_timing(scp_username)
                    self.net_connect.send_command_expect('/ilstu/config/cisco/rtr/' + self.host + '.cfg', expect_string = r'Password:')
                    self.net_connect.send_command_timing(scp_password)
                    self.net_connect.send_command_expect('', expect_string = r'\#')
                    print(self.host, 'backup is complete')
                except:
                    print('**********', self.host, 'could not back up to atconfig')

            elif self.device_group == 'core':
                self.net_connect.send_command('terminal length 0')
                ### Save to atconfig
                try:
                    self.net_connect.send_command_timing('copy run scp:')
                    self.net_connect.send_command_timing('/ilstu/config/cisco/rtr/' + self.host + '.cfg')
                    self.net_connect.send_command_timing('default')
                    self.net_connect.send_command_timing('10.40.201.21')
                    output = self.net_connect.send_command_expect(scp_username, expect_string = r'(password:|yes/no)') # Waiting for either the password of add RSA key prompt
                    if 'password' in output: # If password prompt
                        self.net_connect.send_command_timing(scp_password)
                        self.net_connect.send_command_expect('', expect_string = r'\#')
                        print(self.host, 'backup is complete')
                    else: # If RSA key prompt
                        self.net_connect.send_command_timing('yes')
                        self.net_connect.send_command_timing(scp_password)
                        self.net_connect.send_command_expect('', expect_string = r'\#')
                        print(self.host, 'backup is complete')	
                except:
                    print('**********', self.host, 'could not back up to atconfig')

            elif self.device_group == 'vss':
                ### Turn off paging so no spacebar is needed
                self.net_connect.send_command('terminal length 0')
                try:
                    self.net_connect.send_command_timing('copy run scp:')
                    self.net_connect.send_command_timing('10.40.201.21')
                    self.net_connect.send_command_timing(scp_username)
                    self.net_connect.send_command_expect('/ilstu/config/cisco/rtr/' + self.host + '.cfg', expect_string = r'Password:') # Waiting for the password prompt
                    self.net_connect.send_command_timing(scp_password)
                    self.net_connect.send_command_expect('', expect_string = r'\#')
                    print(self.host, 'backup is complete')
                except:
                    print('**********', self.host, 'could not back up to atconfig')
            elif self.device_group == 'gw':
                if self.device_os == 'ios':
                    ### Turn off paging so no spacebar is needed
                    self.net_connect.send_command('terminal length 0')
                    ### Save to atconfig
                    self.net_connect.send_command_timing('copy run scp:')
                    self.net_connect.send_command_timing('10.40.201.21')
                    self.net_connect.send_command_timing(scp_username)
                    try:
                        self.net_connect.send_command_expect('/ilstu/config/cisco/rtr/' + self.host + '.cfg', expect_string = r'Password:')
                        self.net_connect.send_command_timing(scp_password)
                        print(self.host, 'backup is complete')
                    except:
                        print('**********', self.host, 'could not back up to atconfig')

            elif self.device_group == 'voice-gw':
                if self.device_os == 'ios':
                    ### Turn off paging so no spacebar is needed
                    self.net_connect.send_command('terminal length 0')
                    ### Save to atconfig
                    self.net_connect.send_command_timing('copy run scp:')
                    self.net_connect.send_command_timing('10.40.201.21')
                    self.net_connect.send_command_timing(scp_username)
                    try:
                        self.net_connect.send_command_expect('/ilstu/config/cisco/rtr/' + self.host + '.cfg', expect_string = r'Password:')
                        self.net_connect.send_command_timing(scp_password)
                        print(self.host, 'backup is complete')
                    except Exception as ex:
                        print('**********', self.host, 'could not back up to atconfig', ex)
        except Exception as ex:
            print('**********', self.host, 'was not able to run', ex)

        return self.host + 'has saved locally'

    '''
    Save running-config locally and to atconfig
    @args username: username used to log into atconfig
    @args password: password associated with username
    @return: str
    '''
    def save_and_backup(self, username, password):
        scp_username = username
        scp_password = password
        try:
            self.save()
            self.backup(scp_username, scp_password)
        except Exception as ex:
            print('**********', self.host, 'was not able to run', ex)

        return self.host + 'has saved locally and to atconfig'

    '''
    Find CDP neighbors on the device. Returns a list of dictionaries with Device ID and local port
    @args file: name of a file for the output to be written. This is will overwrite an existing file of the same name. File type is CSV.
    @return: list
    '''
    def get_cdp_neighbors(self, file = None):
        if self.device_os == 'ios':
            output = self.net_connect.send_command_timing('show cdp neighbors')
            output = output.splitlines()
            index = 0
            cdp_list = []
            for i in range(len(output)):
                ### Saving to a str then list with split removes empty space items
                temp_str = output[i]
                temp_list = temp_str.split()
                if len(temp_list) > 1:
                    if temp_list[0] == 'Device':
                        index = i + 1
                        break
            for i in range(index, len(output)):
                ### Saving to a str then list with split removes empty space items
                temp_str = output[i]
                temp_list = temp_str.split()
                if len(temp_list) > 1:
                    ### Some neighbors are on multiple lines. This makes sure the line is not used twice
                    if temp_list[0] == ('Gig' or 'Ten'):
                        continue
                    ### If 'Total' is in the line, all neighbors have been added to the list
                    if temp_list[0] == 'Total':
                        break
                    if temp_list[1] == 'Gig':
                        temp_list[1] = 'Gi'
                    elif temp_list[1] == 'Ten':
                        temp_list[1] = 'Te'
                    temp_dict = {'port': temp_list[1] + temp_list[2], 'device': temp_list[0]}
                    cdp_list.append(temp_dict)
                elif len(temp_list) == 1:
                    temp_host = temp_list[0]
                    temp_str = output[i + 1]
                    temp_list = temp_str.split()
                    if temp_list[0] == 'Gig':
                        temp_list[0] = 'Gi'
                    elif temp_list[0] == 'Ten':
                        temp_list[0] = 'Te'
                    temp_dict = {'port':temp_list[0] + temp_list[1], 'device': temp_host}
                    cdp_list.append(temp_dict)
                ### If line is empty, go to the next iteration
                else:
                    continue
        if file != None:
            file = open('output/' + file + '.csv', 'w')
            file.write('Port,Device ID\n')
            for i in range(len(cdp_list)):
                file.write(cdp_list[i]['port'] + ',' + cdp_list[i]['device'] + '\n')
            file.close()        

        return cdp_list

    '''
    Find conected ports on the device. Command used 'show int status | include connected' By default, it returns just the ports that show connected.
    @args full: When true, returns a list of dictionaries with port number, description, VLAN, duplex, speed, and media type
    @args vlan: Returns only connected ports on a specified VLAN. Can only be used when full = True
    @args file: name of a file for the output to be written. This is will overwrite an existing file of the same name. File type is CSV.
    @return: list
    '''
    def get_connected_ports(self, full = False, vlan = None, file = None):
        if full == True:
            output_status = self.net_connect.send_command_timing('show int status | include connected')
            output_desc = self.net_connect.send_command_timing('show int desc | include up')
            desc_list = output_desc.splitlines()
            status_list = output_status.splitlines()
            connected_list = []
            if vlan == None:
                for i in range(len(status_list)):
                    ### Saving to a str then list with split removes empty space items
                    temp_str1 = status_list[i]
                    temp_list1 = temp_str1.split()
                    temp_str2 = desc_list[i]
                    temp_list2 = temp_str2.split()
                    desc = ''
                
                    if ('Po' and 'Ma' and 'Vl') not in temp_list1[0]:
                        for j in range(len(desc_list)):
                            ### Check to see that port numbers match
                            if temp_list1[0] == temp_list2[0]:
                                ### Checking for a description
                                if temp_list2[-1] != ('up' and 'down'):
                                    desc = temp_list2[-1]
                                    break
                                else:
                                    desc = 'No description'
                                    break
                        temp_dict = {'port': temp_list1[0], 'description': desc, 'vlan': temp_list1[-4], 'duplex': temp_list1[-3],
                                     'speed': temp_list1[-2], 'media': temp_list1[-1]}
                        connected_list.append(temp_dict)
            else:
                for i in range(len(status_list)):
                    ### Saving to a str then list with split removes empty space items
                    temp_str1 = status_list[i]
                    temp_list1 = temp_str1.split()
                    temp_str2 = desc_list[i]
                    temp_list2 = temp_str2.split()
                    desc = ''

                if ('Po' and 'Ma' and 'Vl') not in temp_list1[0] and temp_list1[-4] == vlan:
                    for j in range(len(desc_list)):
                        ### Check to see that port numbers match
                        if temp_list1[0] == temp_list2[0]:
                            ### Checking for a description
                            if temp_list2[-1] != ('up' and 'down'):
                                desc = temp_list2[-1]
                                break
                            else:
                                desc = 'No description'
                                break
                    temp_dict = {'port': temp_list1[0], 'description': desc, 'vlan': temp_list1[-4], 'duplex': temp_list1[-3],
                                    'speed': temp_list1[-2], 'media': temp_list1[-1]}
                    connected_list.append(temp_dict)
        else:
            output_status = self.net_connect.send_command_timing('show int status | include connected')
            status_list = output_status.splitlines()
            connected_list = []
            for i in range(len(status_list)):
                if ('Po' and 'Ma' and 'Vl') not in status_list[0]:
                    temp_str = status_list[i]
                    connected_list.append(temp_str.split()[0])
        if file != None:
            file = open('output/' + file + '.csv', 'w')
            if full == True:
                file.write('Port,Description,VLAN,Duplex,Speed,Media\n')
                for i in range(len(connected_list)):
                    file.write(connected_list[i]['port'] + ',' + connected_list[i]['description'] + ',' + str(connected_list[i]['vlan']) + ',' +
                               connected_list[i]['duplex'] + ',' + connected_list[i]['speed'] + ',' + connected_list[i]['media'] + '\n')
            else:
                file.write('Port,Description\n')
                for i in range(len(connected_list)):
                    file.write(connected_list[i]['port'] + ',' + connected_list[i]['description'] + '\n')
            file.close()

        return connected_list

    '''
    Find available ports. Command used 'show int status | include disabled'. Returns a list of disabled ports.
    @return: list
    '''
    def get_open_ports(self):
        output_status = self.net_connect.send_command_timing('show int status | include disabled')
        status_list = output_status.splitlines()
        disabled_list = []
        for i in range(len(status_list)):
           if (('Po' and 'Ma' and 'Vl') not in status_list[0]) and status_list[0] != 'Fa0':
                temp_str = status_list[i]
                disabled_list.append(temp_str.split()[0])

        return disabled_list
    
    '''
    Find enabled ports. Command used 'show int status | exclude disabled'. By default, it returns just a list of enabled ports
    @args full: When true, returns a list of dictionaries with port number, description, VLAN, duplex, speed, and media type
    @args vlan: Returns only enabled ports on a specified VLAN. Can only be used when full = True
    @args file: name of a file for the output to be written. This is will overwrite an existing file of the same name. File type is CSV.
    @return: list
    '''
    def get_active_ports(self, full = False, vlan = None, file = None):
        if full == True:
            output_status = self.net_connect.send_command_timing('show int status | exclude disabled')
            output_desc = self.net_connect.send_command_timing('show int desc | exclude admin')
            desc_list = output_desc.splitlines()
            status_list = output_status.splitlines()
            active_list = []
            if vlan == None:
                for i in range(2, len(status_list)):
                    ### Saving to a str then list with split removes empty space items
                    temp_str1 = status_list[i]
                    temp_list1 = temp_str1.split()
                    temp_str2 = desc_list[i]
                    temp_list2 = temp_str2.split()
                    desc = ''
                
                    if ('Po' and 'Ma' and 'Vl') not in temp_list1[0]:
                        for j in range(len(desc_list)):
                            ### Check to see that port numbers match
                            if temp_list1[0] == temp_list2[0]:
                                ### Checking for a description
                                if temp_list2[-1] != ('up' and 'down'):
                                    desc = temp_list2[-1]
                                    break
                                else:
                                    desc = 'No description'
                                    break
                        temp_dict = {'port': temp_list1[0], 'description': desc, 'vlan': temp_list1[-4], 'duplex': temp_list1[-3],
                                     'speed': temp_list1[-2], 'media': temp_list1[-1]}
                        active_list.append(temp_dict)
            else:
                for i in range(2, len(status_list)):
                    ### Saving to a str then list with split removes empty space items
                    temp_str1 = status_list[i]
                    temp_list1 = temp_str1.split()
                    temp_str2 = desc_list[i]
                    temp_list2 = temp_str2.split()
                    desc = ''

                    if ('Po' and 'Ma' and 'Vl') not in temp_list1[0] and temp_list1[-4] == str(vlan):
                        for j in range(len(desc_list)):
                            ### Check to see that port numbers match
                            if temp_list1[0] == temp_list2[0]:
                                ### Checking for a description
                                if temp_list2[-1] != ('up' and 'down'):
                                    desc = temp_list2[-1]
                                    break
                                else:
                                    desc = 'No description'
                                    break
                        temp_dict = {'port': temp_list1[0], 'description': desc, 'vlan': temp_list1[-4], 'duplex': temp_list1[-3],
                                        'speed': temp_list1[-2], 'media': temp_list1[-1]}
                        active_list.append(temp_dict)
        else:
            output_status = self.net_connect.send_command_timing('show int status | exclude disabled')
            status_list = output_status.splitlines()
            active_list = []
            for i in range(2, len(status_list)):
                if ('Po' and 'Ma' and 'Vl') not in status_list[0]:
                    temp_str = status_list[i]
                    active_list.append(temp_str.split()[0])

        if file != None:
            file = open('output/' + file + '.csv', 'w')
            if full == True:
                file.write('Port,Description,VLAN,Duplex,Speed,Media\n')
                for i in range(len(active_list)):
                    file.write(active_list[i]['port'] + ',' + active_list[i]['description'] + ',' + str(active_list[i]['vlan']) + ',' +
                               active_list[i]['duplex'] + ',' + active_list[i]['speed'] + ',' + active_list[i]['media'] + '\n')
            else:
                file.write('Port,Description\n')
                for i in range(len(active_list)):
                    file.write(active_list[i]['port'] + ',' + active_list[i]['description'] + '\n')
            file.close()

        return active_list

    '''
    Returns a list of dictionaries containing the MAC addresses on the device. Command varies depending on device type and os.
    @args full: When true, returns a list of dictionaries with MAC address, port, and VLAN
    @args vlan: Returns only MAC addresses on a specified VLAN. Can only be used when full = True
    @args file: str name of a file for the output to be written. This is will overwrite an existing file of the same name. File type is CSV.
    @return: list
    '''
    def get_mac_addresses(self, full = False, vlan = None, file = None):
        mac_list = []
        if full == True:
            if vlan == None:
                if 'access' in self.device_group and self.device_os == 'ios':
                    output = self.net_connect.send_command_timing('show mac address-table secure')
                    mac_output = output.splitlines()
                    mac_list = []
                    for i in range(3, len(mac_output)-1):
                        ### Saving to a str then list with split removes empty space items
                        temp_str = mac_output[i]
                        print(temp_str)
                        temp_list = temp_str.split()
                        print(temp_list)
                        mac_add = temp_list[1]
                        mac_port = temp_list[-1]
                        mac_vlan = temp_list[0]
                        temp_dict = {'mac': mac_add, 'port': mac_port, 'vlan': mac_vlan}
                        mac_list.append(temp_dict)
                elif self.device_group == 'vss' or 'dist' in self.device_group:
                    output = self.net_connect.send_command_timing('show mac address-table | include dynamic')
                    mac_output = output.splitlines()
                    mac_list = []
                    for i in range(len(mac_output)):
                        ### Saving to a str then list with split removes empty space items
                        temp_str = mac_output[i]
                        temp_list = temp_str.split()
                        mac_add = temp_list[2]
                        mac_port = temp_list[-1]
                        mac_vlan = temp_list[1]
                        temp_dict = {'mac': mac_add, 'port': mac_port, 'vlan': mac_vlan}
                        mac_list.append(temp_dict)
                elif self.device_os == 'dell':
                    output = self.net_connect.send_command_timing('show mac address-table | include Te')
                    mac_output = output.splitlines()
                    mac_list = []
                    for i in range(3, len(mac_output)):
                        ### Saving to a str then list with split removes empty space items
                        temp_str = mac_output[i]
                        temp_list = temp_str.split()
                        mac_add = temp_list[1]
                        mac_port = temp_list[-1]
                        mac_vlan = temp_list[0]
                        temp_dict = {'mac': mac_add, 'port': mac_port, 'vlan': mac_vlan}
                        mac_list.append(temp_dict)
            else:
                if 'access' in self.device_group and self.device_os == 'ios':
                    output = self.net_connect.send_command_timing('show mac address-table secure vlan ' + str(vlan))
                    mac_output = output.splitlines()
                    mac_list = []
                    for i in range(3, len(mac_output)):
                        ### Saving to a str then list with split removes empty space items
                        temp_str = mac_output[i]
                        temp_list = temp_str.split()
                        mac_add = temp_list[1]
                        mac_port = temp_list[-1]
                        mac_vlan = temp_list[0]
                        temp_dict = {'mac': mac_add, 'port': mac_port, 'vlan': mac_vlan}
                        mac_list.append(temp_dict)
                elif self.device_group == 'vss' or 'dist' in self.device_group:
                    output = self.net_connect.send_command_timing('show mac address-table vlan ' + str(vlan) + ' | include dynamic')
                    mac_output = output.splitlines()
                    mac_list = []
                    for i in range(len(mac_output)):
                        ### Saving to a str then list with split removes empty space items
                        temp_str = mac_output[i]
                        temp_list = temp_str.split()
                        mac_add = temp_list[2]
                        mac_port = temp_list[-1]
                        mac_vlan = temp_list[1]
                        temp_dict = {'mac': mac_add, 'port': mac_port, 'vlan': mac_vlan}
                        mac_list.append(temp_dict)
                elif self.device_os == 'dell':
                    output = self.net_connect.send_command_timing('show mac address-table | include Te')
                    mac_output = output.splitlines()
                    mac_list = []
                    for i in range(3, len(mac_output)):
                        ### Saving to a str then list with split removes empty space items
                        temp_str = mac_output[i]
                        temp_list = temp_str.split()
                        mac_add = temp_list[1]
                        mac_port = temp_list[-1]
                        mac_vlan = temp_list[0]
                        temp_dict = {'mac': mac_add, 'port': mac_port, 'vlan': mac_vlan}
                        mac_list.append(temp_dict)
        else:
            if 'access' in self.device_group and self.device_os == 'ios':
                output = self.net_connect.send_command_timing('show mac address-table secure')
                mac_output = output.splitlines()
                mac_list = []
                for i in range(3, len(mac_output)):
                    ### Saving to a str then list with split removes empty space items
                    temp_str = mac_output[i]
                    temp_list = temp_str.split()
                    mac_add = temp_list[1]
                    mac_port = temp_list[-1]
                    mac_vlan = temp_list[0]
                    temp_dict = {'mac': mac_add, 'port': mac_port}
                    mac_list.append(temp_dict)
            elif self.device_group == 'vss' or 'dist' in self.device_group:
                output = self.net_connect.send_command_timing('show mac address-table | include dynamic')
                mac_output = output.splitlines()
                mac_list = []
                for i in range(len(mac_output)):
                    ### Saving to a str then list with split removes empty space items
                    temp_str = mac_output[i]
                    temp_list = temp_str.split()
                    mac_add = temp_list[2]
                    mac_port = temp_list[-1]
                    mac_vlan = temp_list[1]
                    temp_dict = {'mac': mac_add, 'port': mac_port}
                    mac_list.append(temp_dict)
            elif self.device_os == 'dell':
                output = self.net_connect.send_command_timing('show mac address-table | include Te')
                mac_output = output.splitlines()
                mac_list = []
                for i in range(3, len(mac_output)):
                    ### Saving to a str then list with split removes empty space items
                    temp_str = mac_output[i]
                    temp_list = temp_str.split()
                    mac_add = temp_list[1]
                    mac_port = temp_list[-1]
                    mac_vlan = temp_list[0]
                    temp_dict = {'mac': mac_add, 'port': mac_port}
                    mac_list.append(temp_dict)

        if file != None:
            file = open('output/' + file, 'w')
            if full == True:
                file.write('MAC Address,Port,VLAN\n')
                for i in range(len(mac_list)):
                    file.write(mac_list[i]['mac'] + ',' + mac_list[i]['port'] + ',' + str(mac_list[i]['vlan']) + '\n')
            else:
                for i in range(len(mac_list)):
                    file.write('MAC Address,Port\n')
                    file.write(mac_list[i]['mac'] + ',' + mac_list[i]['port'] + '\n')
            file.close()   

        return mac_list

    '''
    Returns an IP address for the given MAC address(es).
    @args mac_address: Accepted input is a single MAC address string or a list of MAC addresses of any length
    @args file: str name of a file for the output to be written. This is will overwrite an existing file of the same name. File type is CSV.
    @return: str
    '''
    def get_ip_address(self, mac_address, file = None):
        ip_address = ''
        if isinstance(mac_address, str):
            if self.device_group == 'access':
                output = self.net_connect.send_command_timing('show cdp neighbor | include VSS|vss')
                uplink = output.splitlines()[0]
                self.net_connect.send_command_timing('ssh ' + uplink)
                self.net_connect.send_command_timing(self.password)
                output = self.net_connect.send_command_timing('show ip arp | include ' + mac_address)
                ### Saving to a str then list with split removes empty space items
                temp_str = output.splitlines()[0]
                temp_list = temp_str.split()
                ip_address = temp_list[1]
            elif self.device_group == 'resnet-access':
                output = self.net_connect.send_command_timing('show cdp neighbor | include dist')
                uplink = output.splitlines()[0]
                self.net_connect.send_command_timing('ssh ' + uplink)
                self.net_connect.send_command_timing(self.password)
                output = self.net_connect.send_command_timing('show ip arp | include ' + mac_address)
                ### Saving to a str then list with split removes empty space items
                temp_str = output.splitlines()[0]
                temp_list = temp_str.split()
                ip_address = temp_list[1]
            elif ('dist' or 'cirbn') in self.device_group or self.device_group == 'vss':
                output = self.net_connect.send_command_timing('show ip arp | include ' + mac_address)
                ### Saving to a str then list with split removes empty space items
                temp_str = output.splitlines()[0]
                temp_list = temp_str.split()
                ip_address = temp_list[1]
        elif isinstance(mac_address, list):
            ip_address = []
            if self.device_group == 'access':
                output = self.net_connect.send_command_timing('show cdp neighbor | include VSS|vss')
                uplink = output.splitlines()[0]
                self.net_connect.send_command_timing('ssh ' + uplink)
                self.net_connect.send_command_timing(self.password)
                for i in range(len(mac_address)):
                    output = self.net_connect.send_command_timing('show ip arp | include ' + mac_address[i])
                    ### Saving to a str then list with split removes empty space items
                    temp_str = output.splitlines()[0]
                    temp_list = temp_str.split()
                    ip_address.append(temp_list[1])
            elif self.device_group == 'resnet-access':
                output = self.net_connect.send_command_timing('show cdp neighbor | include dist')
                uplink = output.splitlines()[0]
                self.net_connect.send_command_timing('ssh ' + uplink)
                self.net_connect.send_command_timing(self.password)
                for i in range(len(mac_address)):
                    output = self.net_connect.send_command_timing('show ip arp | include ' + mac_address[i])
                    ### Saving to a str then list with split removes empty space items
                    temp_str = output.splitlines()[0]
                    temp_list = temp_str.split()
                    ip_address.append(temp_list[1])
            elif ('dist' or 'cirbn') in self.device_group or self.device_group == 'vss':
                ### Saving to a str then list with split removes empty space items
                for i in range(len(mac_address)):
                    output = self.net_connect.send_command_timing('show ip arp | include ' + mac_address[i])
                    ### Saving to a str then list with split removes empty space items
                    temp_str = output.splitlines()[0]
                    temp_list = temp_str.split()
                    temp_dict = {'mac': mac_address[i], 'ip': temp_list[1]}
                    ip_address.append(temp_dict)

        if file != None and isinstance(mac_address, list):
            file = open('output/' + file + '.csv', 'w')
            file.write('MAC Address,IP Address,\n')
            for i in range(len(ip_address)):
                file.write(ip_address[i]['mac'] + ',' + ip_address[i]['ip'] + '\n')
            file.close()   
        elif file != None and isinstance(mac_address, str):
            file = open('output/' + file + '.csv', 'w')
            file.write('MAC Address,IP Address,\n')
            file.write(ip_address)
        
        return ip_address

    '''
    Returns the running-config of a given port(s). Command used is 'show run interface [port]'
    @args port: Accepted input is a single port string or a list of ports of any length. port needs to include speed type, not just the number
    @args file: str name of a file for the output to be written. This is formatted like a show run. This is will overwrite an existing file of the same name. File type is TXT.
    @return: dict
    '''  
    def get_config_port(self, port, file = None):
        config_dict = {}
        if isinstance(port, str):
            output = self.net_connect.send_command_timing('show run int ' + port)
            config_output = output.splitlines()
            temp_list = []
            for i in range(4, (len(config_output) - 1)):
                temp_str = config_output[i].strip()
                temp_list.append(temp_str)

            config_dict = {port: temp_list}
        if isinstance(port, list):
            for i in range(len(port)):
                output = self.net_connect.send_command_timing('show run int ' + port[i])
                config_output = output.splitlines()
                temp_list = []
                for j in range(4, (len(config_output) - 1)):
                    temp_str = config_output[j].strip()
                    temp_list.append(temp_str)
                config_dict.update({port[i]: temp_list})
        
        if file != None:
            file = open('output/' + file + '.txt', 'w')
            for i in range(len(port)):
                file.write(config_dict[port[i]][0] + '\n')
                for j in range(1, len(config_dict[port[i]])):
                    file.write(' ' + config_dict[port[i]][j] + '\n')
                file.write('!\n')
            file.close()   
        return config_dict

    '''
    Find PoE ports on the device. Command used 'show power inline ' By default, it returns just a list of dictionaries with port, operational status, PoE to device, and Device ID
    @args full: When true, returns a list of dictionaries with port number, admin status, operational status, PoE from PS, PoE to device, device, and class
    @args state: Returns only ports that match the given state. Acceptable states are: all, admin_auto, admin_on, admin_off, oper_on, oper_off, and faulty. By default, it is set to all
    @args device: accepts any str and returns only the items that have the device string in Device ID
    @args file: name of a file for the output to be written. This will overwrite an existing file of the same name. File type is CSV.
    @return: list
    '''
    def get_poe_ports(self, full = False, state = 'all', device = 'all', file = None):
        poe_list = []
        if full == True:
            output = self.net_connect.send_command_timing('show power inline')
            output = output.splitlines()
            if state == 'all' and device == 'all':
                for i in range(len(output)):
                    ### Saving to a str then list with split removes empty space items
                    temp_str = output[i]
                    temp_list = temp_str.split()              
                    if len(temp_list) == 0:
                        continue
                    if len(temp_list) > 1 and '/' in temp_list[0]:
                        temp_device = ''
                        for j in range(5, len(temp_list) - 1):
                            if j == 5:
                                temp_device += temp_list[j]
                            else:
                                temp_device += ' ' + temp_list[j]
                        temp_dict = {'port': temp_list[0], 'admin_status': temp_list[1], 'oper_status': temp_list[2], 'poe_ps': temp_list[3], 'poe_device': temp_list[4],
                                     'device': temp_device, 'class': temp_list[-1]}
                        poe_list.append(temp_dict)
            elif 'admin' in state:
                if 'auto' in state:
                    for i in range(len(output)):
                        ### Saving to a str then list with split removes empty space items
                        temp_str = output[i]
                        temp_list = temp_str.split()          
                        if len(temp_list) == 0:
                            continue
                        elif len(temp_list) > 1 and '/' in temp_list[0] and 'auto' in temp_list[1]:                       
                            temp_device = ''
                            for j in range(5, len(temp_list) - 1):
                                if j == 5:
                                    temp_device += temp_list[j]
                                else:
                                    temp_device += ' ' + temp_list[j]
                            temp_dict = {'port': temp_list[0], 'admin_status': temp_list[1], 'oper_status': temp_list[2], 'poe_ps': temp_list[3], 'poe_device': temp_list[4],
                                         'device': temp_device, 'class': temp_list[-1]}
                            poe_list.append(temp_dict)
                elif 'on' in state:
                    for i in range(len(output)):
                        ### Saving to a str then list with split removes empty space items
                        temp_str = output[i]
                        temp_list = temp_str.split()              
                        if len(temp_list) == 0:
                            continue
                        elif len(temp_list) > 1 and '/' in temp_list[0] and 'on' in temp_list[1]:                     
                            temp_device = ''
                            for j in range(5, len(temp_list) - 1):
                                if j == 5:
                                    temp_device += temp_list[j]
                                else:
                                    temp_device += ' ' + temp_list[j]
                            temp_dict = {'port': temp_list[0], 'admin_status': temp_list[1], 'oper_status': temp_list[2], 'poe_ps': temp_list[3], 'poe_device': temp_list[4],
                                         'device': temp_device, 'class': temp_list[-1]}
                            poe_list.append(temp_dict)
                elif 'off' in state:
                    for i in range(len(output)):
                        ### Saving to a str then list with split removes empty space items
                        temp_str = output[i]
                        temp_list = temp_str.split()              
                        if len(temp_list) == 0:
                            continue
                        elif len(temp_list) > 1 and '/' in temp_list[0] and 'off' in temp_list[1]:                      
                            devtemp_deviceice = ''
                            for j in range(5, len(temp_list) - 1):
                                if j == 5:
                                    temp_device += temp_list[j] + 'here'
                                else:
                                    temp_device += ' ' + temp_list[j]
                            temp_dict = {'port': temp_list[0], 'admin_status': temp_list[1], 'oper_status': temp_list[2], 'poe_ps': temp_list[3], 'poe_device': temp_list[4],
                                         'device': temp_device, 'class': temp_list[-1]}
                            poe_list.append(temp_dict)
                if device != 'all':
                    temp_list = []
                    for i in range(len(poe_list)):
                        if device.lower() in poe_list[i]['device'].lower():
                            temp_list.append(poe_list[i])
                    poe_list = temp_list
            elif 'oper' in state and device == 'all':
                if 'on' in state:
                    for i in range(len(output)):
                        ### Saving to a str then list with split removes empty space items
                        temp_str = output[i]
                        temp_list = temp_str.split()          
                        if len(temp_list) == 0:
                            continue
                        elif len(temp_list) > 1 and '/' in temp_list[0] and 'on' in temp_list[2]:                       
                            device = ''
                            for j in range(5, len(temp_list) - 1):
                                if j == 5:
                                    temp_device += temp_list[j]
                                else:
                                    temp_device += ' ' + temp_list[j]
                            temp_dict = {'port': temp_list[0], 'admin_status': temp_list[1], 'oper_status': temp_list[2], 'poe_ps': temp_list[3], 'poe_device': temp_list[4],
                                         'device': temp_device, 'class': temp_list[-1]}
                            poe_list.append(temp_dict)
                elif 'off' in state:
                    for i in range(len(output)):
                        ### Saving to a str then list with split removes empty space items
                        temp_str = output[i]
                        temp_list = temp_str.split()          
                        if len(temp_list) == 0:
                            continue
                        elif len(temp_list) > 1 and '/' in temp_list[0] and 'on' in temp_list[2]:                       
                            temp_device = ''
                            for j in range(5, len(temp_list) - 1):
                                if j == 5:
                                    temp_device += temp_list[j]
                                else:
                                    temp_device += ' ' + temp_list[j]
                            temp_dict = {'port': temp_list[0], 'admin_status': temp_list[1], 'oper_status': temp_list[2], 'poe_ps': temp_list[3], 'poe_device': temp_list[4],
                                         'device': temp_device, 'class': temp_list[-1]}
                            poe_list.append(temp_dict)
                elif 'faulty' in state:
                    for i in range(len(output)):
                        ### Saving to a str then list with split removes empty space items
                        temp_str = output[i]
                        temp_list = temp_str.split()          
                        if len(temp_list) == 0:
                            continue
                        elif len(temp_list) > 1 and '/' in temp_list[0] and 'on' in temp_list[2]:                       
                            temp_device = ''
                            for j in range(5, len(temp_list) - 1):
                                if j == 5:
                                    temp_device += temp_list[j]
                                else:
                                    temp_device += ' ' + temp_list[j]
                            temp_dict = {'port': temp_list[0], 'admin_status': temp_list[1], 'oper_status': temp_list[2], 'poe_ps': temp_list[3], 'poe_device': temp_list[4],
                                         'device': temp_device, 'class': temp_list[-1]}
                            poe_list.append(temp_dict)
                if device != 'all':
                    temp_list = []
                    for i in range(len(poe_list)):
                        if device.lower() in poe_list[i]['device'].lower():
                            temp_list.append(poe_list[i])
                    poe_list = temp_list
        else:
            output = self.net_connect.send_command_timing('show power inline')
            output = output.splitlines()
            if state == 'all' and device == 'all':
                for i in range(len(output)):
                    ### Saving to a str then list with split removes empty space items
                    temp_str = output[i]
                    temp_list = temp_str.split()              
                    if len(temp_list) == 0:
                        continue
                    if len(temp_list) > 1 and '/' in temp_list[0]:
                        temp_device = ''
                        for j in range(5, len(temp_list) - 1):
                            if j == 5:
                                temp_device += temp_list[j]
                            else:
                                temp_device += ' ' + temp_list[j]
                        temp_dict = {'port': temp_list[0], 'oper_status': temp_list[2], 'poe_device': temp_list[4],'device': temp_device}
                        poe_list.append(temp_dict)
            elif 'admin' in state:
                if 'auto' in state:
                    for i in range(len(output)):
                        ### Saving to a str then list with split removes empty space items
                        temp_str = output[i]
                        temp_list = temp_str.split()          
                        if len(temp_list) == 0:
                            continue
                        elif len(temp_list) > 1 and '/' in temp_list[0] and 'auto' in temp_list[1]:                       
                            temp_device = ''
                            for j in range(5, len(temp_list) - 1):
                                if j == 5:
                                    temp_device += temp_list[j]
                                else:
                                    temp_device += ' ' + temp_list[j]
                            temp_dict = {'port': temp_list[0], 'oper_status': temp_list[2], 'poe_device': temp_list[4],'device': temp_device}
                            poe_list.append(temp_dict)
                elif 'on' in state:
                    for i in range(len(output)):
                        ### Saving to a str then list with split removes empty space items
                        temp_str = output[i]
                        temp_list = temp_str.split()              
                        if len(temp_list) == 0:
                            continue
                        elif len(temp_list) > 1 and '/' in temp_list[0] and 'on' in temp_list[1]:                     
                            temp_device = ''
                            for j in range(5, len(temp_list) - 1):
                                if j == 5:
                                    temp_device += temp_list[j]
                                else:
                                    temp_device += ' ' + temp_list[j]
                            temp_dict = {'port': temp_list[0], 'oper_status': temp_list[2], 'poe_device': temp_list[4],'device': temp_device}
                            poe_list.append(temp_dict)
                elif 'off' in state:
                    for i in range(len(output)):
                        ### Saving to a str then list with split removes empty space items
                        temp_str = output[i]
                        temp_list = temp_str.split()              
                        if len(temp_list) == 0:
                            continue
                        elif len(temp_list) > 1 and '/' in temp_list[0] and 'off' in temp_list[1]:                      
                            devtemp_deviceice = ''
                            for j in range(5, len(temp_list) - 1):
                                if j == 5:
                                    temp_device += temp_list[j] + 'here'
                                else:
                                    temp_device += ' ' + temp_list[j]
                            temp_dict = {'port': temp_list[0], 'oper_status': temp_list[2], 'poe_device': temp_list[4],'device': temp_device}
                            poe_list.append(temp_dict)
                if device != 'all':
                    temp_list = []
                    for i in range(len(poe_list)):
                        if device.lower() in poe_list[i]['device'].lower():
                            temp_list.append(poe_list[i])
                    poe_list = temp_list
            elif 'oper' in state and device == 'all':
                if 'on' in state:
                    for i in range(len(output)):
                        ### Saving to a str then list with split removes empty space items
                        temp_str = output[i]
                        temp_list = temp_str.split()          
                        if len(temp_list) == 0:
                            continue
                        elif len(temp_list) > 1 and '/' in temp_list[0] and 'on' in temp_list[2]:                       
                            device = ''
                            for j in range(5, len(temp_list) - 1):
                                if j == 5:
                                    temp_device += temp_list[j]
                                else:
                                    temp_device += ' ' + temp_list[j]
                            temp_dict = {'port': temp_list[0], 'oper_status': temp_list[2], 'poe_device': temp_list[4],'device': temp_device}
                            poe_list.append(temp_dict)
                elif 'off' in state:
                    for i in range(len(output)):
                        ### Saving to a str then list with split removes empty space items
                        temp_str = output[i]
                        temp_list = temp_str.split()          
                        if len(temp_list) == 0:
                            continue
                        elif len(temp_list) > 1 and '/' in temp_list[0] and 'on' in temp_list[2]:                       
                            temp_device = ''
                            for j in range(5, len(temp_list) - 1):
                                if j == 5:
                                    temp_device += temp_list[j]
                                else:
                                    temp_device += ' ' + temp_list[j]
                            temp_dict = {'port': temp_list[0], 'oper_status': temp_list[2], 'poe_device': temp_list[4],'device': temp_device}
                            poe_list.append(temp_dict)
                elif 'faulty' in state:
                    for i in range(len(output)):
                        ### Saving to a str then list with split removes empty space items
                        temp_str = output[i]
                        temp_list = temp_str.split()          
                        if len(temp_list) == 0:
                            continue
                        elif len(temp_list) > 1 and '/' in temp_list[0] and 'on' in temp_list[2]:                       
                            temp_device = ''
                            for j in range(5, len(temp_list) - 1):
                                if j == 5:
                                    temp_device += temp_list[j]
                                else:
                                    temp_device += ' ' + temp_list[j]
                            temp_dict = {'port': temp_list[0], 'oper_status': temp_list[2], 'poe_device': temp_list[4],'device': temp_device}
                            poe_list.append(temp_dict)
                if device != 'all':
                    temp_list = []
                    for i in range(len(poe_list)):
                        if device.lower() in poe_list[i]['device'].lower():
                            temp_list.append(poe_list[i])
                    poe_list = temp_list  
        if file != None:
            file = open('output/' + file + '.csv', 'w')
            if full == True:
                file.write('Port,Admin Status,Oper Status,PoE from PS,PoE to Device,Device ID,Class\n')
                for i in range(len(poe_list)):
                    file.write(poe_list[i]['port'] + ',' + poe_list[i]['admin_status'] + ',' + poe_list[i]['oper_status'] + ',' + str(poe_list[i]['poe_ps']) + ',' +
                               str(poe_list[i]['poe_device']) + ',' + poe_list[i]['device'] + ',' + str(poe_list[i]['class']) + '\n')
            else:
                file.write('Port,Oper Status\n')
                for i in range(len(poe_list)):
                    file.write(poe_list[i]['port'] + ',' + poe_list[i]['oper_status'] + str(poe_list[i]['poe_device']) + '\n')
            file.close()

        return poe_list

    '''
    Gets the vitals on a switch - Use a single key or a list of keys to return multiple values. If field is left blank then it returns all values.
    Keys avalable to use: 'hostname, 'serial', 'model', 'ios_ver', 'ios_file', 'last_reload', 'config_reg', 'power_supplies', 'power_watts', 'mods_used', 'mods_avail', 'poe_avail'
    @args key: a str or list for the values to be returned. If key is not specified, all values returned
    @return: dict, str, or list
    '''
    def get_vitals(self, key = 'None'):
        hostname = self.host
        serial = 'N/A'
        model = 'N/A'
        ios_ver = 'N/A'
        ios_file = 'N/A'
        last_reload = 'N/A'
        config_reg = 'N/A'
        power_watts = 'N/A'
        power_supplies = 'N/A'
        mods_used = 'N/A'
        mods_avail = 'N/A' 
        poe_avail = 'N/A'

        ### Avoiding making several 'show version' calls by adding output modifiers for each field needed
        output = self.net_connect.send_command_timing('show version | i Cisco IOS Software|System restarted|System image file is|processor \\(|processor with |Configuration register') ### 'processor with' is for 3650's
        version_list = output.splitlines()
        for i in range(len(version_list)):
            if i == 0:
                ### IOS Version
                ios_ver = version_list[i].split('Version')
                ios_ver = ios_ver[1].split(',')
                ios_ver = ios_ver[0]
            elif i == 1:
                ### Last reload
                last_reload = version_list[i]
                last_reload = last_reload.split('at')
                last_reload = last_reload[1]
            elif i == 2:
                ### IOS file
                ios_file = version_list[i]
                ios_file = ios_file.split()[-1]
                ios_file = ios_file.strip('\"')
            elif i == 3:
                ### Get Model
                model = version_list[i]
                model = model.split(' ')[1] 
            elif i == 4:
                ### Config register
                config_reg = version_list[i]
                config_reg = config_reg.split()
                config_reg = config_reg[-1]          

        ### Get power supply wattage
        power_watt = self.net_connect.send_command_timing('sh power | i PWR')
        power_watt = power_watt.splitlines()
        power_watts = []
        for line in power_watt:
            power_watts.append(line.split()[3])

        ### Power supplies
        power_supplies = self.net_connect.send_command_expect('sh run | i power redun', expect_string = r'\#')
        power_supplies = power_supplies.split()
        power_supplies = power_supplies[-1]

        ### PoE available
        try: 
            power_output = self.net_connect.send_command_timing('sh power in | i Remaining:') 
            power =  power_output.split('  ') 
            poe_avail = str(power[2].split(':')[1]) 
        except: 
            poe_avail = 'Non Poe' 
        
        ### Get SN
        try: 
            serial = self.net_connect.send_command_expect('sh snmp chassis') 
        except: 
            serial = 'N/a' 

        ### Get number of slots
        SlotAmount = '0'
        ### Gives us how many slots and indirectly tells me if it is a 1u switch. 
        if('4506' in model): 
            SlotAmount = 6 
        elif('4503' in model): 
            SlotAmount = 3 
        elif('2960' in model): 
            SlotAmount = 1 
        elif('3560' in model): 
            SlotAmount = 1 
        elif('3650' in model): 
            SlotAmount = 1 
        elif('9410' in model or 'C9410R' in model): 
            model = 'C9410R' 
            SlotAmount = 10 
        elif('for' in model): 
            try: 
                model = self.net_connect.send_command('sh ver | i WS') 
                model = model.split(' ')[1] 
                SlotAmount = 1 
            except: 
                pass 
            try: 
                model = self.net_connect.send_command('sh ver | i cisco C') 
                model = model.split(' ')[1] 
                SlotAmount = 1 
            except: 
                pass 
        else: 
            SlotAmount = 1 

        ### List of mods
        sh_mod_output = self.net_connect.send_command('sh mod') 
        sh_mod_output = sh_mod_output.split('\n') 
        mod_list = [] 
        if(SlotAmount != 1): 
            while('--+' not in sh_mod_output[0]): 
                del sh_mod_output[0] 
            del sh_mod_output[0] 
            ### List format [mod_num, port_num,serial_num,mod_model] 
            i = 0 
            ### We get an index out of bound error so this allows us to not crash our program. 
            try: 
                while('MAC address' not in sh_mod_output[i]): 
                    test = sh_mod_output[i].split()
                    test = test[-2]
                    mod_list.append(test)
                    i = i + 1
            except: 
                pass 
        else: 
            ### Left to rigt 
            ### For 1u Switches 
            if('2960' in model): 
                mod_list.append(['1','24/48','NA','1u']) 
            elif('3560' in model): 
                mod_list.append(['1','8/12/24/48','NA','1u']) 
            elif('3650' in model): 
                mod_list.append(['1','24/48','NA','1u']) 
            else: 
                mod_list.append(['1','Unknown','NA','1u']) 
        mods_used = mod_list

        ### Available mods
        mods_avail = SlotAmount - len(mod_list)
        ### Return values
        value = {'hostname': hostname,'serial': serial , 'model':model, 'ios_ver':ios_ver, 'ios_file':ios_file, 'last_reload':last_reload, 'config_reg':config_reg,
                 'power_supplies':power_supplies, 'power_wattage':power_watts, 'mods_used':mods_used, 'mods_avail':mods_avail, 'poe_avail':poe_avail}
        ### Return all if no key is used
        if(key == 'None'):
            return value
        ## Return multiple values based on list
        elif(type(key) is list):
            valuesReturn = []
            for item in key:
                valuesReturn.append(value[str(item)])
            return valuesReturn
        ### Return the single key used.
        else:
            return value[str(key)]

    '''
    Deletes all archive config files that are over one month old. This will also look for config files that equal the hostname. 
    This function will use a 'dir all' to find all the config files
    @return: str
    '''
    def erase_old_configs(self):
        month_list = ['Jan-', 'Feb-', 'Mar-', 'Apr-', 'May-', 'Jun-', 'Jul-', 'Aug-', 'Sep-', 'Oct-', 'Nov-', 'Dec-']
        file_list = []
        file_system = ''
        output = self.net_connect.send_command_expect('dir all', expect_string = r'\#')
        output = output.splitlines()
        for i in range(len(output)):
            ### Saving to a str then list with split removes empty space items
            temp_str = output[i]
            temp_list = temp_str.split()
            if len(temp_list) > 0 and temp_list[0] == 'Directory':
                file_system = temp_list[-1]
                continue
            ### Config files are in lines with 9 items
            if len(temp_list) == 9:
                for j in range(len(month_list)):
                    ### Check to see if the date string is in the filepath
                    if month_list[j] in temp_list[-1]:
                        filepath = file_system + temp_list[-1]
                        ### Determine if file is older than 30 days
                        month = temp_list[3]
                        ### Convert month str into an int
                        for k in range(len(month_list)):
                            if month in month_list[k]:
                                month = k + 1
                                break
                        day = int(temp_list[4])
                        year = int(temp_list[5])
                        file_date = datetime.date(year, month, day)
                        today = datetime.date.today()
                        time_diff = today - file_date
                        time_list = str(time_diff).split()
                        try:
                            time_diff = int(time_list[0])
                            if time_diff > 30:
                                file_list.append(filepath)
                                break
                        except:
                            pass
                    elif temp_list[-1].lower() == self.host.lower() + '.cfg':
                        filepath = file_system + temp_list[-1]
                        file_list.append(filepath)
                        break
        ### Delete the old config files
        for i in range(len(file_list)):
            self.net_connect.send_command_timing('delete ' + file_list[i])
            self.net_connect.send_command_timing('')
            self.net_connect.send_command_expect('', expect_string = r'\#')
        
        return self.host + ' deleted ' + str(len(file_list)) + ' files.'

    '''
    Finds any ports in err-disabled state. Returns a list of dictionaries.
    @args file: str name of a file for the output to be written. This is will overwrite an existing file of the same name. File type is CSV. Only the switches with err-disabled ports will be written
    @return: list or str
    '''
    def get_errdisabled(self, file = None):
        if (self.device_os == 'ios' or self.device_group == 'nx-os') and 'dc' not in self.device_group:
            output = self.net_connect.send_command_timing('show int status | i err-disabled')
            err_list = []
            if len(output) > 0:
                err_output = output.splitlines()
                for i in range(len(err_output)):
                    ### Saving to a str then list with split removes empty space items
                    temp_str = err_output[i]
                    temp_list = temp_str.split()
                    temp_dict = {'switch': self.host, 'port': temp_list[0], 'description': temp_list[1]}
                    ### Find the reason for the port being in errdisable state
                    output = self.net_connect.send_command_timing('show errdisable recovery')
                    recov_out = output.splitlines()
                    for j in range(len(recov_out)):
                        if temp_dict['port'] in recov_out[j]:
                            ### Saving to a str then list with split removes empty space items
                            temp_str = recov_out[j]
                            temp_list = temp_str.split()
                            temp_dict['reason'] = temp_list[1]
                        else:
                            temp_dict['reason'] = 'Unknown'
                    err_list.append(temp_dict)
                    if file != None:
                        file = open('output/' + file + '.csv', 'w')
                        file.write('Switch,Port,Description,Reason\n')
                        for i in range(len(err_list)):
                            file.write(err_list[i]['switch'] + ',' + err_list[i]['port'] + ',' + err_list[i]['description'] + ',' + err_list[i]['reason'])
            else:
                temp_dict = {'switch': self.host, 'port': 'None', 'description': 'None', 'reason': 'N/A'}  

        return err_list if len(err_list) > 0 else self.host + ' has no err-disabled ports.' 
    '''
    Pings the given IP address(es) and returns a list of dictionaries with all of the diagnostic values.
    @args ip: The IP address(es) to be pinged. Can be a str for a single IP or a list for any amount.
    @args num_pings: The number of times to ping the IP address. Default is 5. Number of pings must be 1-2147483647
    @args size: The size of the packets in bytes. Default is 100. Size must be 36-18024
    @args details: Returns a dictionary containing the IP, ping percentage, successful pings, total pings, packet size, and minimum, average, and maximum return times
    @return: list
    '''
    def ping(self, ip, num_pings = 5, size = 100):
        ping_list = []
        if isinstance(ip, str):
            output = self.net_connect.send_command_expect('ping ' + ip + ' repeat ' + str(num_pings) + ' size ' + str(size), expect_string = r'\#')
            out_list = output.splitlines()
            for i in range(len(out_list)):
                if 'Success' in out_list[i]:
                    ### Saving to a str then list with split removes empty space items
                    temp_dict = {}
                    ping_out = out_list[i]
                    temp_list1 = ping_out.split()
                    temp_dict['ip'] = ip
                    temp_dict['percent'] = temp_list1[3]
                    ### Parse successful/total
                    temp_list2 = temp_list1[5].split('/')
                    temp_dict['successful'] = temp_list2[0][1:]
                    temp_dict['total'] = num_pings
                    ### Parse min/avg/max
                    temp_list3 = temp_list1[9].split('/')
                    temp_dict['minimum'] = temp_list3[0]
                    temp_dict['average'] = temp_list3[1]
                    temp_dict['maximum'] = temp_list3[2]
                    ping_list.append(temp_dict)  
                    break
        elif isinstance(ip, list):
            for i in range(len(ip)):
                output = self.net_connect.send_command_expect('ping ' + ip[i] + ' repeat ' + str(num_pings) + ' size ' + str(size), expect_string = r'\#')
                out_list = output.splitlines()
                for j in range(len(out_list)):
                    if 'Success' in out_list[j]:
                        ### Saving to a str then list with split removes empty space items
                        temp_dict = {}
                        ping_out = out_list[j]
                        temp_list1 = ping_out.split()
                        temp_dict['ip'] = ip[i]
                        temp_dict['percent'] = temp_list1[3]
                        ### Parse successful/total
                        temp_list2 = temp_list1[5].split('/')
                        temp_dict['successful'] = temp_list2[0][1:]
                        temp_dict['total'] = num_pings
                        ### Parse min/avg/max
                        if temp_dict['percent'] != '0':
                            temp_list3 = temp_list1[9].split('/')
                            temp_dict['minimum'] = temp_list3[0]
                            temp_dict['average'] = temp_list3[1]
                            temp_dict['maximum'] = temp_list3[2]
                            ping_list.append(temp_dict)
                            break
                        else:
                            temp_dict['minimum'] = 'N/A'
                            temp_dict['average'] = 'N/A'
                            temp_dict['maximum'] = 'N/A'
                            ping_list.append(temp_dict)
                            break

        return ping_list

    '''
    Returns a boolean value of the ping status of a given IP address(es). Values are returned as a list of dictionaries. This uses a 3-ping test.
    @args ip: Can be a str for an single IP or a list for any number of IP's.
    @return: list
    '''
    def is_pingable(self, ip):
        pingable_list = []
        if isinstance(ip, str):
            output = self.net_connect.send_command_expect('ping ' + ip + ' repeat 3', expect_string = r'\#')
            out_list = output.splitlines()
            for i in range(len(out_list)):
                if 'Success' in out_list[i]:
                    temp_dict = {}
                    ping_out = out_list[i]
                    temp_list = ping_out.split()
                    temp_dict['ip'] = ip
                    percent = int(temp_list[3])
                    if percent > 0:
                        temp_dict['pingable'] = True
                    else:
                        temp_dict['pingable'] = False
                    pingable_list.append(temp_dict)

        elif isinstance(ip, list):
            for i in range(len(ip)):
                output = self.net_connect.send_command_expect('ping ' + ip[i], expect_string = r'\#')
                out_list = output.splitlines()
                print(out_list)
                for j in range(len(out_list)):
                    if 'Success' in out_list[j]:
                        temp_dict = {}
                        ping_out = out_list[j]
                        temp_list = ping_out.split()
                        temp_dict['ip'] = ip[i]
                        percent = int(temp_list[3])
                        if percent > 0:
                            temp_dict['pingable'] = True
                        else:
                            temp_dict['pingable'] = False
                        pingable_list.append(temp_dict)
        
        return pingable_list

    '''
    Returns a list of dictionaries of uplinks with input errors
    @args file: str name of a file for the output to be written. This is will overwrite an existing file of the same name. File type is CSV. Only the switches errors on the uplinks will be written.
    @return: list
    '''
    def monitor_uplinks(self, file = None):
        error_list = []
        uplink_list = []
        if 'access' in self.device_group or '':
            output = self.net_connect.send_command_timing('show int description')
            output = output.splitlines()
            for i in range(len(output)):
                temp_str = output[i]
                temp_list = temp_str.split()
                #print(temp_list)
                if len(temp_list) >= 4 and temp_list[1] != 'admin' and temp_list[0] != 'Interface':
                    if ('vss' or 'uplink' or 'dist') in temp_list[3].lower() and 'po' not in temp_list[0].lower():
                        temp_list = [temp_list[0], temp_list[3:]]
                        uplink_list.append(temp_list)
            for i in range(len(uplink_list)):
                port = uplink_list[i][0]
                desc = str(uplink_list[i][1])
                output = self.net_connect.send_command_timing('show int ' + port + ' | include input error')
                output = output.splitlines()
                temp_str = output[0]
                temp_list = temp_str.split()
                errors = temp_list[0]
                if int(errors):
                    if errors != 0:
                        temp_dict = {'host': self.host, 'port': port, 'description': desc, 'errors': errors}
                        error_list.append(temp_dict)

        if self.device_group == 'vss':
            output = self.net_connect.send_command_timing('show int description')
            output = output.splitlines()
            for i in range(len(output)):
                temp_str = output[i]
                temp_list = temp_str.split()
                #print(temp_list)
                if len(temp_list) >= 4 and temp_list[1] != 'admin' and temp_list[0] != 'Interface':
                    if ('core' or 'as0' or 'dist' or 'VSL') in temp_list[3].lower() and 'po' not in temp_list[0].lower():
                        temp_list = [temp_list[0], temp_list[3:]]
                        uplink_list.append(temp_list)
            for i in range(len(uplink_list)):
                port = uplink_list[i][0]
                desc = str(uplink_list[i][1])
                output = self.net_connect.send_command_timing('show int ' + port + ' | include input error')
                output = output.splitlines()
                temp_str = output[0]
                temp_list = temp_str.split()
                errors = temp_list[0]
                if int(errors):
                    if int(errors) != 0:
                        temp_dict = {'host': self.host, 'port': port, 'description': desc, 'errors': errors}
                        error_list.append(temp_dict)
        if self.device_group == 'core':
            output = self.net_connect.send_command_timing('show int description')
            output = output.splitlines()
            for i in range(len(output)):
                temp_str = output[i]
                temp_list = temp_str.split()
                #print(temp_list)
                if len(temp_list) >= 4 and 'Eth' in temp_list[0] and temp_list[3] != '--':
                    temp_list = [temp_list[0], temp_list[3:]]
                    uplink_list.append(temp_list)
            for i in range(len(uplink_list)):
                port = uplink_list[i][0]
                desc = str(uplink_list[i][1])
                output = self.net_connect.send_command_timing('show int ' + port + ' | include \"input error\"')
                output = output.splitlines()
                temp_str = output[0]
                temp_list = temp_str.split()
                errors = temp_list[0]
                if int(errors):
                    if int(errors) != 0:
                        temp_dict = {'host': self.host, 'port': port, 'description': desc, 'errors': errors}
                        uplink_list.append(temp_list)
        if file != None:
                    file = open('output/' + file + '.csv', 'w')
                    file.write('Host,Port,Description,Errors\n')
                    for i in range(len(error_list)):
                        file.write(error_list[i]['host'] + ',' + error_list[i]['port'] + ',' + error_list[i]['description'] + ',' + error_list[i]['errors'])

        return error_list
    
    def jsonFormat(self, data):
        with open(Path("DriversTesting.txt"), "w") as fileout:
            outdata = json.dumps(data, indent=4)
            fileout.write(outdata)
