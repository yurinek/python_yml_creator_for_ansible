import random
import string
from io import StringIO
import hashlib
import argparse
import yaml
import os


# Initiate the parser
parser = argparse.ArgumentParser()
parser.add_argument("-i", "--input", help="append new users to existing input file")
parser.add_argument("-e", "--expire", help="Create users which authentification should expire")
# Read arguments from the command line
args = parser.parse_args()

old_contents_rest = ''
old_contents_user_dict = ''


# generate md5 hash
def create_md5(password, user):
    return 'md5' + hashlib.md5((password + user).encode('utf-8')).hexdigest()


# take input file which already has users to append new users to this file
def process_input_file(inputfile):
    global old_contents_rest
    global old_contents_user_dict
    virtual_file_rest = StringIO()
    virtual_file_user_dict = StringIO()
    with open(inputfile) as file:
        for line in file:
            # dicts which start with "-" are recognized as lists, so lets remove "-"
            user_dict = yaml.load(line.replace("-", ""), Loader=yaml.FullLoader)
            # ensure its the relevant users dict by checking object type and particular key names
            if type(user_dict) is dict and "name" in user_dict and "password" in user_dict:
                prev_name = user_dict.get("name")
                prev_password = user_dict.get("password")
                if 'md5' in prev_password:
                    pass
                else:
                    pw_key_value = {"password": create_md5(prev_password, prev_name)}
                    user_dict.update(pw_key_value)
                # only string can be written to file
                user_str = '  - ' + str(user_dict)
                virtual_file_user_dict.write(user_str + '\n')
            else:
                # preserve everything else from the input file in the output file
                if line != 'database_users:\n':
                    virtual_file_rest.write(line)
    contents = virtual_file_rest.getvalue()
    # write rest content to global var
    old_contents_rest = contents
    virtual_file_rest.close()
    contents = virtual_file_user_dict.getvalue()
    # write users dicts content to global var
    old_contents_user_dict = contents
    virtual_file_user_dict.close()


# generate new users
def generate_users():
    virtual_file = StringIO()
    real_file = open("users_new.yml", "w")
    user_dict = {"name": "", "password": "", "expires": False, "attributes": "LOGIN"}
    while True:
        name = input('Please provide user name (empty to stop): ')
        if name == '':
            # if no user name provided, consider it as end of user list
            break
        else:
            password = input('Please provide password (empty for random): ')
            # if user didnt provide password, its going to be randomly generated
            if password == '':
                password = ''.join(random.choice(string.ascii_uppercase + string.ascii_lowercase + string.digits) for _ in range(32))
            # pw_md5 = hashlib.md5((pw + name).encode('utf-8')).hexdigest()
            user_key_value = {"name": name}
            # the postgres way of storing md5 hashes: md5 string infront of md5 sum of: password + user_name
            pw_key_value = {"password": create_md5(password, name)}
            # if arg used, users should be generated with expiration of their account
            if args.expire:
                expire_key_value = {"expires": True}
                user_dict.update(expire_key_value)
            user_dict.update(user_key_value)
            user_dict.update(pw_key_value)
            # only string can be written to file
            user_str = str(user_dict)
            # write line by line
            virtual_file.write('  - ' + user_str + '\n')
            # display clear text password for the operator to know it (it is stored as md5 hash)
            print(f'User {name} with password {password} has been created')
            continue
    # append to input file users dicts, if no input file given var is empty
    contents = old_contents_user_dict + virtual_file.getvalue()
    virtual_file.close()
    contents_to_sort = sorted(contents.split('\n'))
    sorted_contents = '\n'.join(contents_to_sort)
    print(sorted_contents)
    # ansible likes double quotes
    if args.input:
        # append to input file rest contents
        ansible_acceptable_contents = (old_contents_rest + '\n\ndatabase_users:' + sorted_contents).replace("'", "\"")
    else:
        ansible_acceptable_contents = ('---\n\ndatabase_users:' + sorted_contents).replace("'", "\"")
    # when content is ready, write all lines to file on disk
    real_file.write(ansible_acceptable_contents)
    real_file.write('\n')
    real_file.close()


# in case file was given as arg, new users will be appended to this file.
# besides this we check if there are plain text passwords. If yes we convert it to md5
if args.input:
    process_input_file(args.input)


# create new users dicts from interactive input
generate_users()


# rename result file to input file
if args.input:
    os.rename(args.input, args.input + '_old')
    os.rename('users_new.yml', args.input)


