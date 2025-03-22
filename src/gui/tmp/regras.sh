iptables -t nat -A POSTROUTING -o eth0 -j MASQUERADE
iptables -t nat -A PREROUTING -i eth0 -p tcp --dport 80 -j DNAT --to 10.1.0.1
iptables -t nat -A PREROUTING -i eth0 -p tcp --dport 81 -j DNAT --to 10.1.0.2
iptables -t nat -A PREROUTING -i eth0 -p udp --dport 53 -j DNAT --to 10.1.0.1
