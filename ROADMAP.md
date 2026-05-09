# TODOs 

## Core

### Client

- TODO - Perform this validation for all at the beginning; if it fails, don't even start the tests - add a message to the status.

- TODO - Set the value to -1 in case of error and add a message to the status.

- TODO - If the hostname is incorrect in the /etc/hosts file, this program won't work! This is here to get the client's IP address, so I don't know if you need to get the name to get the IP address - see how to do this just by getting the IP address - then a question that would arise is if the client has more than one IP address.

- TODO - If the firewall blocks it, it's showing an error! But it was the firewall; you need to see if there's a way to identify when it's an error and when it's the firewall. For now, the status will remain at 0, message["status"] = "1"

- TODO - The client is not showing the JSON that the server is sending altered! To show the DNAT
- TODO - see if it's worthwhile to add the NAT field to indicate a possible NAT currently in the message field

- TODO - send these messages to the graphical interface using the json object - add a note field or something similar - otherwise the graphical interface may break, since it expects the json.

- TODO - if the firewall blocks it, it's showing an error! but it was the firewall, we had to see if there's a way to identify when it's an error and when it's the firewall, for now the status will remain at 0; message["status"] = '1'; message["status_msg"] = "Network Error"

### Containers

- TODO - if you are using DHCP, UDP ports 68 and 69 may be in use, so you will not be able to run these ports! See how to solve...

- TODO - if you are using DHCP, UDP ports 68 and 69 may be in use, so you will not be able to run these ports! see how to solve...

- TODO - if you are using DHCP, UDP ports 68 and 69 may be in use, so you will not be able to run these ports! see how to solve...

- TODO - make method to return hostname, interface, IP

- TODO - here I changed it so that the search is by the name of the image on DockerHub, which is firewall_tester - that is, the search is by the image and not by the host name - but this has a problem if docker is not used, but here it would only be possible to use docker! if filter_string in hostname:

### Server

- TODO - Test and remove this method. 
def is_not_loopback(ip):

return not ipaddress.ip_address(ip).is_loopback

- TODO - Change the JSON object sent by the client. If the message has a different IP address than the destination host, this means the message went through NAT. Therefore, it would be good practice to include the IP address/port of the host that received and processed the information to indicate whether the DNAT was successful or not. This needs to be done for both TCP and UDP.

- TODO - The server IP address may appear strangely here, as we are using the first IP address of the server host. As a rule, it may have been redirected to another IP address of the same server.

## UI

### About Tab

- TODO: Check if the button to open the GitHub repository works

### Hosts Tab

- TODO - Adjust port change


### Main UI

- TODO - Standardize variable and function names - use English names.
- TODO - Leave all print and graphical messages in English - buttons, labels, etc...
- TODO - Refactor the code - remove duplicate code, see what can be improved, perhaps with the concept of object-oriented programming.
- TODO - Remove variables and code that are not being used - there may be useless code, especially since the change from label to treeview.
- TODO - Configuration tab - see if it is necessary and what to put there (e.g., location where rules should be loaded in the container; whether or not to display the container ID column, whether or not to start the servers, list iptables mangle rules, maybe list or not iptables nat or filter rules - now interface list filter and nat rules by default).
- TODO - Create a help for the user.
- TODO - When performing tests, check for errors such as testing a closed port on the server, the interface could warn about this (leave it, but warn).
- TODO - Verify the message flow, such as, it arrived at the server but did not return, indicating this in the interface.
- TODO - Think about how to show the execution logs, which go to the text console, to the interface, this helps a lot in showing problems and the test flow.
- TODO - Think about how to show "packet" details - JSON objects returned by client/server in tests.
- TODO - In the container.py file - when starting a server on a port already in use by another program other than server.py, verify if it can really kill that process.
- TODO - Think about how to access some real services, such as HTTP, SSH, MYSQL, etc., and how to show this in the interface, currently outside of client.py/server.py only ICMP can be accessed externally.
- TODO - Think about tests of malformed packets such as those from nmap or scapy.
- TODO - Suggest tests that may be common in corporate environments.
- TODO - Suggest tests based on the services running in the environment.
- TODO - Suggest tests based on the tests proposed by the user, such as: if they asked host1 to access HTTP on host3, do the opposite as well.
- TODO - Perhaps it would be nice to have options to wait for test success considering DNAT, that is, to have an option that when enabled waits for the flow to go through a DNAT, otherwise the test would be considered failed!
- TODO - The scroll of the firewall tests is not working properly and is cutting off the last column of the tree. (Note: PyQt's QTreeWidget handles this better).
- TODO - Check if scroll is needed in other areas of the program (vertical and horizontal). (Note: PyQt handles this better with layouts and QScrollArea).
- TODO - Is it interesting to have a button to save firewall rules on the host? the user can do ctrl+c and ctrl+v - remembering that the rules are already saved in the container.
- TODO - if only the host or all hosts in the scenario are turned off, there is no problem for the interface, but if GNS3 is turned off and the same scenario is turned on again, the interface becomes inconsistent, even the host update button does not work properly! Also, the rules deployed in the firewall are lost.
- TODO - when saving and opening tests - do not reference the container ID, only the names and perhaps IPs (I think IPs are unavoidable for now), and when the rules are opened, the interface must report or re-report the hostname with the container_id, and perhaps the IPs (it would be nice not to report with the IPs, because in the scenario the user could create or change the hostname to another IP and the test would continue to work).
- TODO - the combobox of "Edit firewall rules on host" should not show multiple lines for the same host (it shows one per host IP), but rather only one name.
- TODO - You need to scroll on the tabs and it also limits their size, because when you put too many hosts (about 7) the buttons to update hosts and exit the program disappeared, because the tabs pushed them off the screen. (Note: QTabWidget can handle this with scroll buttons).
- TODO - The information regarding docker containers is being performed three times in a row at the beginning, see if this is really necessary or if it can be done just once.
- TODO - report the name of the docker image with the name used in the configuration tab.