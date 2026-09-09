import zipfile
import os
import json
import io

caminho_do_arquivo = r""

if not os.path.exists(caminho_do_arquivo):
    print(f"Erro: Arquivo não encontrado em {caminho_do_arquivo}")
    exit()

if zipfile.is_zipfile(caminho_do_arquivo):
    with zipfile.ZipFile(caminho_do_arquivo, 'r') as zf:
        if 'project.gns3' in zf.namelist():
            with zf.open('project.gns3') as f:
                conteudo_json_str = io.TextIOWrapper(f, encoding="utf-8").read()
                raw_data = json.loads(conteudo_json_str)

            nodes_limpos = []
            for node in raw_data.get("topology", {}).get("nodes", []):
                properties = node.get("properties", {})
                
                nodes_limpos.append({
                    "name": node.get("name"),
                    "node_type": node.get("node_type"),
                    "mac_address": properties.get("mac_address"),
                    "environment": properties.get("environment"),
                    "image": properties.get("image")
                })

            links_limpos = []
            for link in raw_data.get("topology", {}).get("links", []):
                nodes_conexao = []
                for n in link.get("nodes", []):
                    node_id = n.get("node_id")
                    node_obj = next((item for item in raw_data["topology"]["nodes"] if item["node_id"] == node_id), None)
                    node_name = node_obj["name"] if node_obj else node_id
                    
                    label_interface = n.get("label", {}).get("text", "")
                    nodes_conexao.append(f"{node_name} ({label_interface})")
                
                links_limpos.append(" <---> ".join(nodes_conexao))

            topologia_sanitizada = {
                "nome_projeto": raw_data.get("name"),
                "dispositivos": nodes_limpos,
                "conexoes": links_limpos
            }

            caminho_salvar_json = "../topologia_extraida.json" 
            with open(caminho_salvar_json, 'w', encoding='utf-8') as arquivo_saida:
                json.dump(topologia_sanitizada, arquivo_saida, indent=2, ensure_ascii=False)
                