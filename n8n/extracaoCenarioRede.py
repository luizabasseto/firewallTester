import zipfile
import os
import json
import io

caminho_do_arquivo = r"/home/aluizabatista/firewallTester/gns3_projects/redeArtigoSBRC2026.gns3project"
if not os.path.exists(caminho_do_arquivo):
    print(f"Erro: Arquivo não encontrado em {caminho_do_arquivo}")
    exit()

print(f"Tentando ler o arquivo: {caminho_do_arquivo}\n")

if not zipfile.is_zipfile(caminho_do_arquivo):
    print("O arquivo NÃO é um arquivo ZIP válido.")
else:
    print("O arquivo é um arquivo ZIP.")
    
    try:
        with zipfile.ZipFile(caminho_do_arquivo, 'r') as zf:
            arquivos_no_zip = zf.namelist()
            
            arquivo_json_principal = None
            if 'project.gns3' in arquivos_no_zip:
                arquivo_json_principal = 'project.gns3'
            
            if arquivo_json_principal:
                print(f"\nExtraindo o JSON da Topologia ({arquivo_json_principal})...")
                
                with zf.open(arquivo_json_principal) as f:
                    conteudo_json_str = io.TextIOWrapper(f, encoding="utf-8").read()
                    
                    dados_da_topologia = json.loads(conteudo_json_str)
                    
                    caminho_salvar_json = "../topologia_extraida.json" 
                    with open(caminho_salvar_json, 'w', encoding='utf-8') as arquivo_saida:
                        json.dump(dados_da_topologia, arquivo_saida, indent=4, ensure_ascii=False)
                        
                    print(f"\nArquivo JSON salvo com sucesso em: {caminho_salvar_json}")
                    
            else:
                print("\nNão foi possível encontrar o arquivo 'project.gns3' dentro do ZIP.")

    except Exception as e:
        print(f"\nOcorreu um erro ao ler o conteúdo do ZIP: {e}")