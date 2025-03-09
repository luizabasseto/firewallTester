iptables -t nat -A POSTROUTING -o eth0 -j MASQUERADE
iptables -A FORWARD -p tcp --dport 22 -j REJECT
iptables -A FORWARD -p icmp --icmp-type echo-request -j DROP














