import Switch_Driver
import getpass
from multiprocessing.dummy import Pool as ThreadPool
from time import time

def read_devices(devices_filename):
	devices = []
	with open(devices_filename) as devices_file:
		for device_line in devices_file:
			#create list to be read into a list of dictionaries
			device_list = device_line.strip().split(',')
			devices.append({'hostname': device_list[0], 'group': device_list[1], 'os': device_list[2]})

	return devices

'''
This is where you call the SwitchDriver function you want to run.
'''
def worker(device_and_creds):
    device = device_and_creds[0]
    creds  = device_and_creds[1]
	### Creating friendly names for arguments in net_connect
	### device_type must match a preset type in netmiko. All devices in the list are Cisco or Cisco-like so device_type is being harcoded to cisco_ios
    device_hostname = device[0]
    device_group = device[1]
    device_os = device[2]
    user = creds[0]
    pw = creds[1]
    ### If connecting to atconfig is needed
    # scp_user = creds[2]
    # scp_password = creds[3]

    ### Create SwitchDriver object and call method
    ### Runs inside a try clause so the script keeps running if there is an error on the device
    try:
        drive = Switch_Driver.Switch_Driver(device_hostname, user, pw, device_group, device_os)
        drive.get_errdisabled()
    except:
        print('****************', device_hostname, 'did not start.')


devices = read_devices('host_files/backup_all_hosts.txt')
user = input('Username: ')
password = getpass.getpass('Password: ')
creds = [user, password]
### If needing to connect to atconfig
# scp_user = 'svc_scpatconfig'
# scp_password = getpass.getpass('SCP Password: ')
# creds = [user, password, scp_user, scp_password]

num_threads_str = input('\nNumber of threads (10): ') or '10'
num_threads = int(num_threads_str)

###Create list for passing to config worker
config_params_list = []

for i in range(len(devices)):
	device = [devices[i]['hostname'], devices[i]['group'], devices[i]['os']]
	config_params_list.append((device, creds))

starting_time = time()

print ('\n--- Creating threadpool\n')
threads = ThreadPool(num_threads)
results = threads.map(worker, config_params_list)

threads.close()
threads.join()

total_time = format((time()-starting_time)/60, '.2f')
print('\n---- Elapsed time: ', str(total_time) + ' minutes')