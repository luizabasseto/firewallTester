# TODOs 

## Core

### Client

- TODO - Fazer essa validação para todos logo no inicio, se não passar nem inicia os testes - colocar uma msg no status.

- TODO - colocar o valor -1 para caso de erro e colocar uma msg no status

- TODO - se o nome do host estiver errado no arquivo /etc/host esse programa não funciona! Bem isso está aqui para pegar o ip do cliente, então não sei se precisa pegar o nome para pegar o IP - ver como fazer isso só pegando o IP - ai uma questão que teria, seria se o cliente tiver mais que um IP.

- TODO - se o firewall barrar, está dando que é erro! mas foi o firewall, tinha que ver se há como identificar quando é erro e quando é o firewall, por agora vai ficar o status em 0, message["status"] = "1"

- TODO - o cliente não está mostrando o json que o server está enviando alterado! para mostrar o DNAT
- TODO - ver se compensa colocar o campo NAT para indicar um possível nat atualmente está no campo message

- TODO - enviar essas mensagens para a interface gráfica utilizando o objeto json - colocar um campo observação ou algo do gênero - caso contrário a interface gráfica pode quebrar, já que ela espera o json.

- TODO - se o firewall barrar, está dando que é erro! mas foi o firewall, tinha que ver se há como identificar quando é erro e quando é o firewall, por agora vai ficar o status em 0; message["status"] = '1'; message["status_msg"] = "Network Error"

### Containers

- TODO - if you are using DHCP, UDP ports 68 and 69 may be in use, so you will not be able to run these ports! See how to solve...

- TODO - if you are using DHCP, UDP ports 68 and 69 may be in use, so you will not be able to run these ports! see how to solve...

- TODO - if you are using DHCP, UDP ports 68 and 69 may be in use, so you will not be able to run these ports! see how to solve...

- TODO - make method to return hostname, interface, IP

### Server

-  TODO - Test and remove this method.
 def is_not_loopback(ip):
     return not ipaddress.ip_address(ip).is_loopback

- TODO - alterar o objeto json enviado pelo cliente, caso a mensagem esteja com um IP diferente do host de destino, isso significa que a mensagem passou por um nat, então seria legal colocar o IP/porta do host que recebeu e tratou a informação para informar que o DNAT foi bem sucessido ou não - isso tem que ser feito para tcp e udp.


## UI

### About Tab

- TODO: Check if the button to open the GitHub repository works

### Hosts Tab

- TODO - Ajustar mudança de portas 


### Main UI

- TODO - Standardize variable and function names - use English names.
- TODO - Leave all print and graphical messages in English - buttons, labels, etc...
- TODO - Refactor the code - remove duplicate code, see what can be improved, perhaps with the concept of object-oriented programming.
- TODO - Remove variables and code that are not being used - there may be useless code, especially since the change from label to treeview.
- TODO - Configuration tab - see if it is necessary and what to put there (e.g., location where rules should be loaded in the container; whether or not to display the container ID column, whether or not to start the servers, list iptables mangle rules, maybe list or not iptables nat or filter rules - now interface list filter and nat rules by default).
- TODO - Create a help for the user.
- TODO - When performing tests, check for errors such as testing a closed port on the server, the interface could warn about this (leave it, but warn).
- TODO - Verify the message flow, such as, it arrived at the server but did not return, indicate this in the interface.
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
- TODO - when saving and opening tests - do not reference the container ID, only the names and perhaps IPs (I think IPs are unavoidable for now), and when the rules are opened, the interface must relate or re-relate the hostname with the container_id, and perhaps the IPs (it would be nice not to relate with the IPs, because in the scenario the user could create or change the hostname to another IP and the test would continue to work).
- TODO - the combobox of "Edit firewall rules on host" should not show multiple lines for the same host (it shows one per host IP), but rather only one name.
- TODO - You need a scroll on the tabs and it also limits their size, because when you put too many hosts (about 7) the buttons to update hosts and exit the program disappeared, because the tabs pushed them off the screen. (Note: QTabWidget can handle this with scroll buttons).
- TODO - The information regarding docker containers is being performed three times in a row at the beginning, see if this is really necessary or if it can be done just once.
- TODO - relate the name of the docker image with the name used in the configuration tab.
