import json

# String recebida (formato incorreto)
raw_string = "{id: 1, timestamp_teste: 2025, timestamp_send: 2025-02-13T00:11:57.711983, timestamp_recv: 2025-02-13T00:11:57.713534, client_host: fHost-1.teste, client_ip: 127.0.1.1, client_port: 33213, server_ip: 192.168.122.218, server_port: 80, protocol: tcp, server_response: True}"

# Correção manual para JSON válido
fixed_string = (
    raw_string.replace("{", '{"')  # Adiciona aspas na primeira chave
    .replace("}", '"}')  # Adiciona aspas na última chave
    .replace(": ", '": ')  # Adiciona aspas após os nomes das chaves
    .replace(", ", ', "')  # Adiciona aspas antes das chaves seguintes
    .replace("True", "true")  # Corrige booleano para JSON válido
    .replace("False", "false")  # Corrige booleano para JSON válido
)

# Correção específica para strings e datas
fixed_string = fixed_string.replace('": "', '": "')  # Evita duplicação de aspas

# Adiciona aspas ao redor dos valores de string e datas
for key in ["client_host", "client_ip", "server_ip", "protocol", "timestamp_send", "timestamp_recv"]:
    fixed_string = fixed_string.replace(f'{key}": ', f'{key}": "').replace(", ", '", ', 1)

# Converte para JSON válido
json_data = json.loads(fixed_string)

# Exibe o resultado corrigido
print(json_data)

