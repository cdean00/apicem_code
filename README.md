# apicem_code
Python scripts used for APIC-EM projects.

## get_router_info
Python 3.6

### Requires
Netmiko

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
Netmiko is used to connect to the routers and the input file matches Netmiko's required fields.
See [Netmiko](https://github.com/ktbyers/netmiko) for additional information on how Netmiko works.
For security, username and password are entered during runtime instead of saving in the CSV file, otherwise those would be
required in the input CSV file.

The inputfile header must include at least the following, in order:
1. device_type
2. ip

The output file header is as follows, in order:
1. serial_id
2. serial_cl_ip
3. cox_circuit_id
4. cl_circuit_id
5. address

After the router information is collected, get_router_info writes the information to a new CSV file.
Warning, the output file will be overwritten if it already exists!

### Roadmap:
* Multiprocesses to speed up runtime.
* Less static methods to allow for more customization.
