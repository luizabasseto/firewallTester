iptables -t nat -A POSTROUTING -o eth0 -j MASQUERADE
iptables -t nat -A PREROUTING -i eth0 -p tcp --dport 80 -j DNAT --to 10.1.0.1
iptables -A FORWARD -p tcp --dport 23 -j DROP
iptables -A INPUT -p tcp --dport 23 -j DROP
iptables -A INPUT ! -i eth1 -p tcp --dport 22 -j DROP
iptables -A FORWARD -i eth1 -p tcp --dport 22 -j ACCEPT
iptables -A FORWARD -p tcp --dport 22 -j DROP
