# apicem_code
Python scripts used for APIC-EM projects.

## get_router_info
Python 3.6

### Requires
Napalm

csv

pprint

getpass

socket

argparse

### Description
The get_router_info module was created for a lifecycle project that replaced approximately 100 branch routers. get_router_info
is used to log into each production router to gather required information that will be transferred to the new routers. The output
CSV file will be used in another module to dynamically create the new router configuration files. Finally those files will be
uploaded to APIC-EM for use with PnP. See the work_file folder for examples of the input and output files.

### Usage
```bash
python <input_file> <output_file>
```
where input_file is a CSV file containing connection details for the routers and output_file is a CSV file to write
the information collected from the routers. The output_file will be overwritten if it already exists.

### Methods

**get_router_info(input_file, output_file)**

Requires two strings inputfile and outputfile. Inputfile and outputfile must be filepaths to the file location.
Both files must be CSV file formats. The inputfile is used to connect to the routers. The output file is used to write
the information collected from the routers. The output file provided will be overwritten if it already exists.
Napalm is used to connect to the routers and requires the hostname or IP of the router in a CSV file.
See [NAPALM](https://github.com/napalm-automation/napalm) for additional information.
For security, username and password are entered during runtime instead of saving in the CSV file, otherwise those would be
required in the input CSV file.

The inputfile header only requires "hostname". The hostname can be the hostname or IP address of the router.

The output file header is "hostname,loopback0_ip,subnet_id,serial0_ip,serial1_ip,cl0_bgp_nei,cl1_bgp_nei,cl0_circuit_id,cl1_circuit_id,cox_circuit_id,address".


After the router information is collected, get_router_info writes the information to a new CSV file.
Warning, the output file will be overwritten if it already exists!

### Roadmap
* Multiprocesses to speed up runtime.
* Less static methods to allow for more customization.
