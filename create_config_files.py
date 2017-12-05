# -*- coding: utf-8 -*-

from argparse import ArgumentParser
from jinja2 import Environment, FileSystemLoader
import logging
import csv
import os


def main(args):
    template_variables = args.template_variables
    template_filename = args.template_filename

    template_variables_path = os.path.abspath(template_variables)
    #template_filename_path = os.path.abspath(template_filename)

    create_config(template_variables_path, template_filename)

def create_config(template_variables, template_filename):
    #Creating Jinja2 environment and template objects
    env = Environment(loader=FileSystemLoader('./templates/'))
    template = env.get_template(template_filename)

    #Opening CSV file
    with open(template_variables, 'r') as csvfile:
        #Creating DictReader object that by default uses the first row in the CSV file as the keys and the remaining rows as values.
        #This makes it easy pass dictionary variables into the Jinja2 template object from a CSV file.
        dictreader = csv.DictReader(csvfile)


        #Iterate over dictreader and create configuration files for each row.
        for row in dictreader:
            #Using hostname to name new configuration file.
            config_filename = './configurations/' + row['hostname'] + '.conf'

            #Creating new config
            config = template.render(row)

            #Opening new file to write config to
            with open(config_filename, 'w') as configfile:
                configfile.write(config)

if __name__ == '__main__':
    parser_description = '''create_config_files.py requires two inputs: a CSV file containing variable information for the template\n
                            and the template filename that will be used to create the configuration files. The templates must be\n
                            located in a folder named templates/ located in the same folder as create_config_files.py.'''

    # Parse command-line arguments
    parser = ArgumentParser(description=parser_description)
    parser.add_argument('template_variables', help='CSV file that containts the template variable information.')
    parser.add_argument('template_filename', help='Filename of template that will be used to create configurations.')

    args = parser.parse_args()

    main(args)
