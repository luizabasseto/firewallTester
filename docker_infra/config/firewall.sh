iptables -t nat -A POSTROUTING -o eth0 -j MASQUERADE
iptables -A INPUT -p tcp --dport 23 -j DROP
iptables -t nat -A PREROUTING -i eth0 -p tcp --dport 80 -j DNAT --to 10.1.0.2
