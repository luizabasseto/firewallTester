#!/usr/local/bin/python

from scapy.all import IP, ICMP, sr1
import time

def ping(host, count=4):
    """Envia pacotes ICMP Echo Request e verifica a resposta."""
    print(f"\nPING {host}:")

    for seq in range(1, count + 1):
        packet = IP(dst=host) / ICMP()
        start_time = time.time()

        reply = sr1(packet, timeout=1, verbose=False)  # Envia o pacote e aguarda resposta

        if reply:
            elapsed_time = (time.time() - start_time) * 1000
            print(f"Resposta do {host}: Tempo = {elapsed_time:.2f} ms")
        else:
            print(f"Sem resposta do {host}")

        time.sleep(1)

if __name__ == "__main__":
    target_host = "172.17.0.3"
    ping(target_host)
