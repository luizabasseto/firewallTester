import json
from datetime import datetime

# Exemplo de variáveis
args = type('Args', (), {
    'testId': 1,
    'server_host': '192.168.122.2',
    'server_port': 80,
    'protocol': 'tcp'
})

filename_timestamp = datetime.now().strftime("%Y")
timestamp = datetime.now().isoformat()
client_host = "fHost-2.teste"
client_ip = "127.0.1.1"
client_port = 43533

# Criação do objeto message
message = {
    "id": args.testId,
    "timestamp_teste": filename_timestamp,
    "timestamp_send": timestamp,
    "timestamp_recv": timestamp,
    "client_host": client_host,
    "client_ip": client_ip,
    "client_port": client_port,
    "server_ip": args.server_host,
    "server_port": args.server_port,
    "protocol": args.protocol,
    "server_response": False
}

# Gera o JSON
json_string = json.dumps(message, indent=4)
print(json_string)
