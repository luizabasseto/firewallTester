echo "Clear all rules from the default chains"
iptables -F
iptables -t nat -F
iptables -t mangle -F

echo "Clear all rules from user-defined chains (if any)"
iptables -X

echo "Set default policies to ACCEPT (allow all traffic)"
iptables -P INPUT ACCEPT
iptables -P OUTPUT ACCEPT
iptables -P FORWARD ACCEPT

echo "Zero the packet and byte counters"
iptables -Z
