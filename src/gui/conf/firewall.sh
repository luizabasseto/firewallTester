iptables -A INPUT -p tcp --dport 23 -j DROP
iptables -t nat -A POSTROUTING -o eth0 -j MASQUERADE
