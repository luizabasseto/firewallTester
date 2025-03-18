iptables -t nat -A POSTROUTING -o eth0 -j MASQUERADE
iptables -A INPUT -p tcp --dport 23 -j DROP
iptables -t nat -A PREROUTING -i eth0 -p tcp --dport 8081 -j DNAT --to 10.1.0.1:80
