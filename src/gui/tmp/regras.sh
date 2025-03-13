iptables -t nat -A POSTROUTING -o eth0 -j MASQUERADE
iptables -A INPUT	-p tcp --dport 80 -j REJECT
