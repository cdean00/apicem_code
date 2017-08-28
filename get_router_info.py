from napalm import get_network_driver
import csv
from pprint import pprint
from getpass import getpass
from socket import gethostbyaddr
from argparse import ArgumentParser
import sys

def main(args):

    #Load get_router_info with input and output files.
    get_router_info(args.inputfile, args.outputfile)

# Expects path to CSV with connection info w/ header hostname (FQDN or IP). See napalm for addtl. details.
# Writes CSV file with paycenter details for Jinja2 templates. Collected values are hostname, loopback0, subnet_id,
# serial0_ip, serial1_ip, cox_circuit_id, cl_circuit_id, and address.
def get_router_info(inputfile, outputfile):

    invalid_input_error = r"% Invalid input detected at '^' marker."

    # Request username and password used to connect to routers.
    username = input('Enter username:')
    password = getpass()

    # pc_router list to store each router dictionary
    pc_routers = []

    # Read csv file containing paycenter routers connection details, create dictionary of each row, and append the dictionary to pc_routers list
    with open(inputfile, 'r') as csvfile:
        dict_reader = csv.DictReader(csvfile)
        for row in dict_reader:
            pc_routers.append(row)

    # Open CSV file to write router info to
    with open(outputfile, 'w') as csvfile:

        fieldnames = ['hostname', 'loopback0_ip', 'subnet_id', 'serial0_ip', 'serial1_ip', 'cl0_bgp_nei', 'cl1_bgp_nei', 'cl0_circuit_id', 'cl1_circuit_id', 'cox_circuit_id', 'address']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames, delimiter=',', lineterminator='\n')

        writer.writeheader()

        # Add username and password inputted above to router dictionaries.
        for router in pc_routers:
            router['username'] = username
            router['password'] = password

        for router in pc_routers:
            # Variables used write output from routers
            router_dict = {}
            hostname = ''
            loopback0_ip = ''
            subnet_id = ''
            serial0_ip = ''
            serial1_ip = ''
            cl0_bgp_nei = ''
            cl1_bgp_nei = ''
            cl0_circuit_id = ''
            cl1_circuit_id = ''
            cox_circuit_id = ''
            address = ''

            # Seperate output from previous router
            print('\n--------------------------------------------------------------------------------\n')

            print('Connecting to {}...\n'.format(router['hostname']))

            # Connecting to router
            router['username'] = username
            router['password'] = password
            driver = get_network_driver('ios')
            device = driver(router['hostname'], router['username'], router['password'])
            device.open()

            #Collect router information
            router_facts = device.get_facts()
            router_int_ip = device.get_interfaces_ip()
            router_interfaces = device.get_interfaces()
            router_bgp_neighbors = device.get_bgp_neighbors()
            router_snmp_info = device.get_snmp_information()

            ################################################
            # Subnet ID
            ################################################
            # Use loopback0 to find subnet ID
            print('Finding subnet ID...')
            try:
                for key, value in router_int_ip['Loopback0']['ipv4'].items():
                    loopback0_ip = key

                #Splitting loopback_ip to pull out subnet ID (subnet ID is third octect)
                loopback0_ip_split = loopback0_ip.split('.')
                subnet_id = loopback0_ip_split[2]

            except KeyError:
                print('Error: Interface not found on device. None will be used for field value.')
                subnet_id = 'None'

            # Debug output
            #print('Loopback0 IP Address: {}'.format(loopback0_ip))
            #print('subnet_id = {}'.format(subnet_id))

            ################################################
            # Serial IP - located on serial interface
            ################################################
            print('Finding Serial IP...')

            # List of serial IP addresses
            serial_ip_addr = []
            # Dictionary of serial interfaces
            serial_interfaces = {}
            # List of Up serial interfaces
            serial_up = []

            # Find all serial interfaces on router
            for key, value in router_interfaces.items():
                if 'Serial' in key:
                    serial_interfaces[key] = value

            # Determine serial interfaces that are in an Up state
            for key, value in serial_interfaces.items():
                if value['is_up']:
                    serial_up.append(key)

            # Filter by Up serial interfaces and record the IP address
            for serial in serial_up:
                for key, value in router_int_ip[serial]['ipv4'].items():
                    serial_ip_addr.append(key)

            # Debug output
            #print(serial_up)
            #pprint(serial_ip_addr)


            # Add serial IP addresses to global variables
            if len(serial_ip_addr) > 0:
                serial0_ip = serial_ip_addr[0]
            if len(serial_ip_addr) > 1:
                serial1_ip = serial_ip_addr[1]

            ################################################
            # CenturyLink IP - locating in BGP configuration
            ################################################
            print('Finding CenturyLink IP...')

            # Find CentruyLink IP from BGP neighborships and peer IP
            bgp_peers = router_bgp_neighbors['global']['peers']

            # Loop over bgp_peers to create list of CL IP addresses
            cl_bgp_ip = []
            for key, value in bgp_peers.items():
                cl_bgp_ip.append(key)

            # Debug output
            #pprint(cl_bgp_ip)

            # Add CL BGP neighbor IPs to global variables
            if len(cl_bgp_ip) > 0:
                cl0_bgp_nei = cl_bgp_ip[0]
            if len(cl_bgp_ip) > 1:
                cl1_bgp_nei = cl_bgp_ip[1]

            ################################################
            # Cox Circuit ID
            ################################################
            print('Finding Cox Circuit ID...')
            #Recording Cox circuit ID which is the description on interface f0/0
            cox_circuit_id = router_interfaces['FastEthernet0/0']['description']

            ################################################
            # CenturyLink Circuit ID
            ################################################
            print('Finding CenturyLink Circuit IDs...')
            #Recording CenturyLink circuit ID which is the description on the serial interface
            if len(serial_up) > 0:
                cl0_circuit_id = router_interfaces[serial_up[0]]['description']
            if len(serial_up) > 1:
                cl1_circuit_id = router_interfaces[serial_up[1]]['description']

            ################################################
            # Address
            ################################################
            print('Finding address...')
            #Recording SNMP location
            address = router_snmp_info['location']

            #Inserting values into pc_router dictionary
            print('Creating paycenter dictionary...')
            router_dict['hostname'] = router_facts['hostname']
            router_dict['loopback0_ip'] = loopback0_ip
            router_dict['subnet_id'] = subnet_id
            router_dict['serial0_ip'] = serial0_ip
            router_dict['serial1_ip'] = serial1_ip
            router_dict['cl0_bgp_nei'] = cl0_bgp_nei
            router_dict['cl1_bgp_nei'] = cl1_bgp_nei
            router_dict['cl0_circuit_id'] = cl0_circuit_id
            router_dict['cl1_circuit_id'] = cl1_circuit_id
            router_dict['cox_circuit_id'] = cox_circuit_id
            router_dict['address'] = address

            #Display router information found
            print('\n')
            pprint(router_dict)

            print('\nClosing connection to {}...'.format(router['hostname']))
            device.close()

            writer.writerow(router_dict)

if __name__ == '__main__':

    # Parse command-line arguments
    parser = ArgumentParser()
    parser.add_argument('inputfile', help='''Input filename.
                                      Must be CSV file containing hostname or IP address of router. Header name must be "hostname".
                                      ''')
    parser.add_argument('outputfile', help='Output filename to write device info in CSV format. Warning: file will be overwritten if exists!')

    args = parser.parse_args()

    main(args)
