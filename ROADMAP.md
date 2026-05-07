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
