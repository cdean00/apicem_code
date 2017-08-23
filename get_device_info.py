from netmiko import ConnectHandler
import csv
from pprint import pprint
from getpass import getpass
from socket import gethostbyaddr
import sys


'''
Expects path to CSV with connection info w/ header device_type, username, password, and ip. See netmiko for addtl. details.
Writes CSV file with paycenter details for APIC-EM templates. Header for apic-em CSV are: hostname, serialNumber, platformId, subnet_id,
serial_ip, serial_cl_ip, cox_circuit_id, cl_circuit_id, and address.
'''
def get_device_info(conn_details_path):

    file_path = conn_details_path
    invalid_input_error = r"% Invalid input detected at '^' marker."

    #Request username and password to be used to log into routers.
    username = input('Enter username:')
    password = getpass()

    #pc_router list to store router dictioNoneries and pc_route is a single router dictioNonery.
    pc_routers = []
    pc_router = {}

    #Read csv file containing paycenter routers connection details, create dictioNonery of each row, and append the dictioNonery to pc_routers list
    with open(file_path, 'r') as csvfile:
        dict_reader = csv.DictReader(csvfile)
        for row in dict_reader:
            pc_routers.append(row)

    #Open CSV file to write router info to
    with open('./work_files/inventory_pc.csv', 'w') as csvfile:
        fieldnames = ['subnet_id', 'serial_cl_ip', 'cox_circuit_id', 'cl_circuit_id', 'address']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames, delimiter=',', lineterminator='\n')

        writer.writeheader()

        #Add username and password inputted above to router dictioNoneries.
        for router in pc_routers:
            router['username'] = username
            router['password'] = password

        for router in pc_routers:
            #Seperate output from previous router
            print('\n--------------------------------------------------------------------------------\n')

            #Lookup hostname
            try:
                hostname = gethostbyaddr(router['ip'])
            except:
                hostname = '!'
                print('DNS lookup failed.')

            print('\nConnecting to {} - {}'.format(hostname[0], router['ip']))

            #Connecting to router
            net_connect = ConnectHandler(**router)

            #Determine if s0/0/0:0 or s0/1/0:0 is in use.
            serial0 = False
            serial1 = False
            output = net_connect.send_command('show interfaces summary')
            output_lines = output.splitlines()

            for line in output_lines:
                if '* Serial0/0/0:0' in line:
                    serial0 = True
                elif '* Serial0/1/0:0' in line:
                    serial1 = True

            #Issuing 'show ip int brief' to find loopback0 and serial IP
            output = net_connect.send_command('show ip int brief')
            output_split = output.split()

            '''
            Subnet ID
            '''
            #Determine where 'Loopback0' is located in output_split list.
            print('Finding subnet ID...')
            try:
                loopback0_index = output_split.index('Loopback0')
                loopback0_ip = output_split[loopback0_index + 1]

                #Splitting loopback_ip to pull out subnet ID (subnet ID is third octect)
                loopback0_ip_split = loopback0_ip.split('.')
                subnet_id = loopback0_ip_split[2]
            except ValueError:
                print('Error: Interface not found on device. None will be used for field value.')
                subnet_id = 'None'

            '''
            Serial CL IP - CenturyLink IP - located at s0/0/0:0 on routers
            '''
            print('Finding CenturyLink IP...')

            if serial0:
                try:
                    serial_cl_ip_index = output_split.index('Serial0/0/0:0')
                    serial_cl_ip = output_split[serial_cl_ip_index + 1]
                except ValueError:
                    print('Error: Interface not found on device. None will be used for field value.')
                    serial_cl_ip = 'None'
            elif serial1:
                try:
                    serial_cl_ip_index = output_split.index('Serial0/1/0:0')
                    serial_cl_ip = output_split[serial_cl_ip_index + 1]
                except ValueError:
                    print('Error: Interface not found on device. None will be used for field value.')
                    serial_cl_ip = 'None'

            '''
            Cox Circuit ID
            '''
            print('Finding Cox Circuit ID...')
            #Recording Cox circuit ID which is the description on f0/0
            output = net_connect.send_command('show run int f0/0 | inc desc')
            if invalid_input_error not in output:
                cox_split = output.split()
                cox_circuit_id = cox_split[1]
            else:
                cox_circuit_id = 'None'
                print('Interface not found on device. None will be used for field value.')

            '''
            CenturyLink Circuit ID
            '''
            print('Finding CenturyLink Circuit ID...')
            #Recording CenturyLink circuit ID which is the description on the serial interface
            if serial0:
                output = net_connect.send_command('show run int Serial0/0/0:0 | inc desc')
                if invalid_input_error not in output:
                    cl_split = output.split()
                    cl_circuit_id = cl_split[1]
                else:
                    cl_circuit_id = 'None'
            elif serial1:
                output = net_connect.send_command('show run int Serial0/1/0:0 | inc desc')
                if invalid_input_error not in output:
                    cl_split = output.split()
                    cl_circuit_id = cl_split[1]
                else:
                    cl_circuit_id = 'None'

            '''
            Address
            '''
            print('Finding address...')
            #Recording SNMP location
            output = net_connect.send_command('show snmp location')
            address = output

            #Inserting values into pc_router dictioNonery
            print('Creating paycenter dictioNonery...')
            pc_router['subnet_id'] = subnet_id
            pc_router['serial_cl_ip'] = serial_cl_ip
            pc_router['cox_circuit_id'] = cox_circuit_id
            pc_router['cl_circuit_id'] = cl_circuit_id
            pc_router['address'] = address

            #Display router information found
            print('\n')
            pprint(pc_router)

            print('\nClosing connection to {} - {}'.format(hostname[0], router['ip']))
            net_connect.disconnect()

            writer.writerow(pc_router)




#Parse over information and add required fields to inventory.csv

get_device_info('./work_files/prod_paycenters_test.csv')
