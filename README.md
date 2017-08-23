# apicem_code
Python scripts / code used for APIC-EM projects.

## get_router_info
Python 3.6

### Requires:
Netmiko
csv
pprint
getpass
socket
argparse

### Description:
The get_router_info module was created for a lifecycle project that replaced approximately 100 branch routers. get_router_info
is used to log into each production router to gather required information that will be transferred to the new routers. The output
CSV file will be used in another module to dynamically create the new router configuration files. Finally those files will be
uploaded to APIC-EM for use with PnP. See the work_file folder for examples of the input and output files.

### Future Improvements:
* Multiprocesses to speed up runtime.
* Less static methods to allow for more customization.

### Methods
**get_router_info(inputfile, outputfile)**

Requires two strings inputfile and outputfile. Inputfile and outputfile must be filepaths to the file location.
Both files must be CSV file formats. The inputfile is used to connect to the routers. The output file is used to write
the information collected from the routers. Warning, the output file provided will be overwritten if it already exists.
The inputfile header must include the following, in order:
1. device_type
2. username
3. password
4. ip

The output file header is as follows, in order:
1. serial_id
2. serial_cl_ip
3. cox_circuit_id
4. cl_circuit_id
5. address

After the router information is collected, get_router_info writes the information to a new CSV file.
Warning, the output file will be overwritten if it already exists!
