#!/opt/rh/rh-python36/root/usr/bin/python

# Example custom dynamic inventory script for Ansible, in Python.
# https://www.jeffgeerling.com/blog/creating-custom-dynamic-inventories-ansible
# https://docs.ansible.com/ansible/2.5/user_guide/intro_dynamic_inventory.html
# Note that you must ensure this script has the execute permission. git update-index --chmod=+x path/to/file


import argparse
import json
import subprocess


def create_inventory():
    """Interrogate terraform output for the needed information to put together an inventory for Ansible.
    :return: A JSON formatted inventory acceptable by Ansible.
    :rtype: dict
    """

    # terraform output -json
    # {
    #     "Test01": {
    #         "sensitive": False,
    #         "type": "string",
    #         "value": "172.24.76.139"
    #     }
    # }

    # Capture the terraform output and convert it into python objects that can be manipulated.
    output = subprocess.check_output(["terraform", "output", "-json"], universal_newlines=True)
    terraform_output = json.loads(output)

    # Transform the json from terraform into what ansible needs.
    list_hosts = list(terraform_output.keys())
    json_for_ansible = {'all': {'hosts': list_hosts}}
    host_vars = {}
    for name_host in list_hosts:
        host_vars[name_host] = {'ansible_host': terraform_output[name_host]['value']}
        # A git hosting provider needs port 22 to for git to work properly.
        # The OS level SSH connection can't use 22 then.
        if "gitlab" in name_host.lower():
            host_vars[name_host]['ansible_port'] = '2222'
    json_for_ansible['_meta'] = {'hostvars': host_vars}

    # Return the ansible json.
    # {
    #     "all": {
    #         "hosts": ["Test01"]
    #     },
    #     "_meta": {
    #         "hostvars": {
    #             "Test01": {
    #                 "ansible_host": "172.24.76.139"
    #             }
    #         }
    #     }
    # }

    return json_for_ansible


def empty_inventory():
    """Empty inventory for testing.
    return: The smallest amount of json that ansible will accept for an inventory.
    :rtype: dict
    """
    return {'_meta': {'hostvars': {}}}


def main(is_list, name_host):
    """ The main entry point for the script.
    :param is_list: List information about all the hosts.
    :type is_list: bool
    :param name_host: The name of the host to display variables for.
    :type name_host: str
    :return: A JSON dump of the produced inventory.
    :rtype: str
    """
    # The script is designed to work with list or host.
    if (is_list and name_host) or not (is_list or name_host):
        raise ValueError("You must specify that a list of all hosts is to be produced OR a hostname to work with.")

    # Put together all of the inventory.
    if is_list:
        return json.dumps(create_inventory())
    else:
        # Producing a list of variables for a host is not currently implemented.
        return json.dumps(empty_inventory())


if __name__ == "__main__":
    # Parse the command line arguments.
    parser = argparse.ArgumentParser()
    parser.add_argument('--list', action='store_true')
    parser.add_argument('--host', action='store')
    args = parser.parse_args()

    # Call the main function with the provided arguments.
    the_inventory = main(args.list, args.host)

    # Print the inventory.
    print(the_inventory)
