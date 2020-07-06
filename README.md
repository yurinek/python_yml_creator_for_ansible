# Python YML Creator for Ansible

## Goals of the project

This script creates a dict list of database users from the interactive operator input. <br>

After that an ansible yml file is generated which stores new created user dict lists. <br>

This way there is no need for manual creation of ansible yml files. <br>

In this script created users have been tested to be successfully deployed to a remote Postgres database. <br>


## Prerequisits

Python3 should be installed.

## How to run

```hcl
python create_ansible_yaml.py
```

First the operator is prompted for the name of the user, then for the password. <br>
In case the name is not provided, the script stops. Assuming there is need for 2 users, just hit enter on the prompt for the third user name. <br>
In case password is not provided, a random 32 character password will be generated. <br>
Passwords are displayed, but not stored in the result file. Instead its md5 hash is stored.<br> <br>


In case there is an existing users yml file it can be given as --input parameter. <br>

```hcl
python create_ansible_yaml.py -i users_input.yml
```

This way the new users will be appended to existing users and altogether sorted alphabetically. <br>
If this script finds a plain text password in the existing users yml, it will generate a md5 hash for it <br>
and replace the password with its md5 hash. <br> <br>

In case of storing the result file in a repository, it is advised to additionally encrypt it, e.g. using Ansible Vault. <br> <br>

--expire parameter can be used to create users with expiration of their database account.

```hcl
python create_ansible_yaml.py -i users_input.yml -e yes
```
