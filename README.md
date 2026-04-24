
# Firewall Tester

  

Este repositório acompanha o artigo submetido ao SBRC 2026 intitulado:

  

"FirewallTester: desenvolvimento de ferramenta para automação de testes e validação de regras de firewalls".

  

Este software foi desenvolvido para aprimorar a segurança de redes por meio de testes de _firewall_ práticos e eficientes. Mais do que uma simples ferramenta de teste, ele também atua como um valioso recurso educacional, projetado para simplificar e melhorar o processo de aprendizagem a respeito de _firewalls_. Com uma interface intuitiva e interativa, os estudantes podem visualizar e experimentar a criação e aplicação de regras de _firewall_, tornando conceitos complexos mais fáceis de compreender e promovendo um aprendizado mais profundo e eficaz.

  

O software permite a criação de cenários de rede utilizando o [GNS3](https://www.gns3.com/). Os _hosts_ dentro do cenário devem utilizar imagens [Docker](https://www.docker.com/) para a criação de contêineres destinados aos testes de _firewall_ (esta versão do software suporta apenas contêineres). Após a configuração do cenário de rede no GNS3 e a inicialização de todos os _hosts_, é possível executar o software de testes de regras de _firewall_ na máquina que está rodando os contêineres (hospedeira). O sistema oferece uma interface gráfica que permite:

  

* Criar testes de _firewall_;

* Definir e editar regras de _firewall_ nos _hosts_ do cenário de rede;

* Adicionar e remover portas que representam serviços de rede a serem testados;

  

Além disso, o software permite salvar os resultados dos testes e executá-los novamente posteriormente, por exemplo, em outro computador.

  
  
  

## Estrutura do Repositório

  

O repositório está organizado da seguinte forma:

  

```

firewallTester/

├── assets/ # Imagens e arquivos auxiliares

├── core/ # Lógica principal da aplicação

├── docker/ # Configurações relacionadas aos contêineres

├── gns3_projects/ # Projetos de exemplo para uso no GNS3

├── ui/ # Interface gráfica do usuário

├── main.py # Arquivo principal para execução

├── requirements.txt # Dependências do projeto

```



## Selos Considerados

  

Os selos considerados para avaliação deste artefato são:

- Artefatos Disponíveis (SeloD)

- Artefatos Funcionais (SeloF)

- Artefatos Sustentáveis (SeloS)

- Experimentos Reprodutíveis (SeloR)

  

Com base nos códigos e documentação disponibilizados neste repositório.

  

## Informações Básicas

  

Para execução do artefato, recomenda-se o seguinte ambiente de execução:

  

### Requisitos de Hardware

  

Este projeto depende da execução simultânea de:

  

* Topologias de rede no GNS3;

* Containers Docker;

* Possivelmente múltiplos _hosts_ simulados;

* Aplicação desenvolvida em [Python](https://www.python.org/).

  

Assim, para garantir o funcionamento adequado do FirewallTester, especialmente durante a execução de topologias de rede no GNS3 com múltiplos nós em Docker, recomenda-se que a máquina hospedeira atenda aos seguintes requisitos que estão divididos em mínimo/recomendado:

  

* CPU: 4 núcleos / 8 núcleos;

* Memória RAM: 8 GB / 16 GB ou mais;

* Armazenamento: 20 GB / 50 GB+ livre (SSD recomendável);

* Virtualização: Suporte a VT-x/AMD-V habilitado na BIOS.

  

### Requisitos de Software

  

O ecossistema do FirewallTester depende da integração de diversas ferramentas. Para sua execução, são necessários os seguintes softwares:

  

* Python 3.10 ou superior;

* Docker;

* [GNS3](https://gns3.com/software/download): para o pleno funcionamento do simulador, pode ser necessária a instalação de dependências como o [ubridge](https://github.com/GNS3/ubridge) e o [libvirt](https://libvirt.org/). Além disso, é preciso instalar e configurar os _appliances_ que representarão os _hosts_ na topologia — a escolha destes depende dos cenários e elementos de rede que se deseja emular;

* [VirtualBox](https://www.virtualbox.org/) (opcional): recomendado para a execução da VM do FirewallTester devidamente instalado e configurado (GNS3, Docker, _appliances_, etc), proporcionando uma experiência de uso mais simplificada e amigável.

  
  

### Dependências do FirewallTester

  

As dependências do projeto FirewallTester estão listadas no arquivo `requirements.txt`. A seguir, uma breve descrição de cada componente:

  

* PyQt5: Framework utilizado para o desenvolvimento da interface gráfica (GUI), permitindo uma interação intuitiva com as funcionalidades do sistema;

  

* Docker: Biblioteca (SDK) necessária para a orquestração e gerenciamento dos containers que executam os serviços de _firewall_ e ferramentas de rede;

  

* Scapy: Poderosa ferramenta de manipulação de pacotes, utilizada para a criação, envio e captura de tráfego de rede personalizado para os testes de filtragem.

  

Para essas dependências, execute:

  

```bash

pip3 install -r requirements.txt

```

Caso ocorra erro na instalação, será necessário instalar e ativar um ambiente virtual Python, executando os seguintes comandos:

  

```bash

python -m venv .venv

source .venv/bin/activate

```

Caso o arquivo não carregue, é necessário a instalação dos seguintes bibliotecas:

  

```bash

pip3 install PyQt5==5.15.11 docker==7.1.0 scapy==2.7.0 python-dotenv==1.2.2

```

  

Essas versões foram fixadas para garantir reprodutibilidade do ambiente.

Além disso, é necessário:

  

* Utilizar o GNS3 para criação dos cenários de rede;

* Utilizar contêineres Docker como _hosts_ e _firewalls_.

  

Caso utilize a máquina virtual fornecida, ela já contém parte das dependências configuradas.

  
  

### Preocupações com Segurança

  

O FirewallTester executa comandos de filtragem (como regras _iptables_) dentro de contêineres Docker em cenários de rede do GNS3. Por padrão, essa arquitetura provê o isolamento do ambiente emulado, o que mitiga significativamente os riscos de segurança ao sistema hospedeiro - ainda mais se o ambiente for executado via VM do FirewallTester.

  

Ainda assim, para reforçar a segurança durante a execução, recomenda-se:

  

* Uso de Ambientes Isolados: Utilize máquinas virtuais dedicadas (como a GNS3 VM);

  

* Privilégios Restritos: Evite executar o software diretamente no sistema _host_ com privilégios elevados;

  

* Controle de Portas: Não exponha portas desnecessárias para redes externas;

  

* Cenários Controlados: Utilize exclusivamente redes de teste e ambientes laboratoriais.

  

* Execução de iptables: a aplicação requer privilégios de superusuário dentro dos contêineres Docker. Não execute fora de ambientes isolados.

  

## Instalação do FirewallTester

O FirewallTester depende de um ecossistema complexo que inclui GNS3, Docker e diversas dependências de sistema (como `ubridge` e `libvirt`). Devido a essa complexidade, oferecemos duas formas de configurar o ambiente:

### 1. Opção Recomendada: Máquina Virtual (Pronta para Uso)

Para uma experiência fluida, recomendamos fortemente o uso da **VM pré-configurada**. Ela já contém todo o ambiente (GNS3, dependências e cenários de teste) pronto para execução imediata, sendo a escolha ideal para o primeiro contato com a ferramenta. Para utilizar tal VM os passos são:

1.  **Instale o VirtualBox:** Baixe a versão compatível com seu sistema em [virtualbox.org](https://www.virtualbox.org/wiki/Downloads).

2.  **Baixe a VM:** Acesse o arquivo `.ova` (ex. `FirewallTester-v2.0.ova`) no Google Drive: [Pasta da VM FirewallTester](https://drive.google.com/drive/folders/1IWIF4bGQZ7yR9pshSHVH1eTzxMzTgrOu?usp=sharing).

3.  **Importe o arquivo:** Dê um clique duplo no arquivo `.ova` baixado e siga as instruções padrão do assistente de importação do VirtualBox.

4. **Inicie o Ambiente:** Selecione a VM e clique em "Iniciar". O sistema carregará a interface gráfica do Linux e o login será realizado automaticamente. Ao iniciar, o GNS3 também deverá abrir de forma padrão. Para começar os testes, basta clicar no **ícone do FirewallTester**, que está disponível no menu de inicialização rápida (_taskbar_) ou no menu principal do sistema.
   >  *Nota: Caso o acesso seja solicitado em algum momento, as credenciais do sistema Linux são:* **Usuário:** `aluno` | **Senha:** `123mudar`

### 2. Instalação Manual (Avançado)

Esta opção é destinada a usuários que já possuem o **Python, GNS3 e Docker configurados** em sua distribuição Linux. Certifique-se de que o GNS3 e seus componentes (`libvirt`, `ubridge`) estejam operacionais antes de prosseguir.

#### A. Configuração dos Nós de Rede (Docker/GNS3)

Antes de executar o software, você deve garantir que o GNS3 possua a imagem Docker necessária para os _hosts_ do cenário (_hosts_ comuns e _firewall_). Essa configuração é feita apenas uma vez através de uma destas opções:

* **Appliance (Recomendado):** Importe os arquivos de *appliance* via interface gráfica do GNS3 (`File -> Import appliance`). No primeiro uso, o GNS3 baixará automaticamente a imagem do Docker Hub e configurará os modelos de nós. Há dois arquivos, sendo esses:
    * [host-docker-firewallTester.gns3a](https://github.com/luizabasseto/firewallTester/blob/main/gns3_projects/old/host-docker-firewallTester.gns3a): Configura os _hosts_ comuns do cenário (clientes/servidores).
    * [firewall-docker-firewallTester.gns3a](https://github.com/luizabasseto/firewallTester/blob/main/gns3_projects/old/firewall-docker-firewallTester.gns3a): Configura o nó de firewall com suporte a múltiplas interfaces de rede.
    > **Observação:** Embora ambos utilizem a mesma imagem base do Docker Hub, cada *appliance* já define a quantidade adequada de placas de rede e ícones específicos para facilitar a montagem da topologia.

* **Docker Hub (Manual):** Caso prefira configurar os nós manualmente no GNS3, utilize a imagem [luizarthur/cyberinfra:firewall_tester](https://hub.docker.com/r/luizarthur/cyberinfra). Após o *pull* da imagem, você deverá criar os modelos de _host_ comum e _firewall_ dentro das preferências do GNS3. Note que a imagem utilizada tanto para os _hosts_ comuns quanto para o firewall é a mesma. A distinção entre eles reside apenas no número de interfaces: enquanto _hosts_ comuns operam com uma única placa de rede, o _firewall_ normalmente deve ser configurado com múltiplas placas para interligar os diferentes segmentos da topologia.


#### B. Instalação do FirewallTester

Com o ecossistema GNS3/Docker pronto, siga os passos para instalar a aplicação:

1. Clone o repositório:

```bash
git clone https://github.com/luizabasseto/firewallTester.git
cd firewallTester
```
2. Crie um ambiente virtual (opcional, mas recomendado):
```bash
python -m venv venv
source venv/bin/activate
```

3. Instale as dependências:

```bash
pip3 install -r requirements.txt
```
4. Execute a aplicação:

```bash
python3 main.py
```

A seguir, apresenta-se um exemplo de uso do FirewallTester utilizando a máquina virtual pré-configurada do projeto.
  

## Teste Mínimo

  

Este tutorial tem como objetivo apresentar um teste mínimo da ferramenta.

  

Assim, para isso, assista ao vídeo de tutorial (https://www.youtube.com/watch?v=qyCBiV2q7rA) ou siga os passos disponibilizado no texto a seguir.

  

[![Assista ao vídeo](https://img.youtube.com/vi/qyCBiV2q7rA/0.jpg)](https://www.youtube.com/watch?v=qyCBiV2q7rA)

  
### Passo a passo do teste mínimo

**1. Subir o ambiente**

Execute os containers que simulam cliente, _firewall_ e servidor:

    cd docker_infra/
    
    docker compose up -d --build

Observação: Esse processo pode levar alguns minutos na primeira execução.

  **2. Iniciar a aplicação**

Volte para a raiz do projeto e execute:

    cd ..
    
    source venv/bin/activate # opcional, apenas se estiver com o ambiente virtual ativo
    
    python3 main.py

**3. Verificar os hosts**

Na aba "Hosts", confirme se aparecem:

 - host-1 (cliente)
 - host-2 (servidor)
 - firewall-1

Se não aparecerem, clique em "Refresh Hosts".

A tela exibida, deverá ser semelhante a esta:

<img width="1209" height="694" alt="image" src="https://github.com/user-attachments/assets/adbc60d9-dad9-452f-ae91-178c4a0d2347" />

Certifique-se de que os hosts estejam ativos também, olhando no botão de switch ou no label 'Server Status', no canto direito de cada card de cada host, ou clique em "Start all" para confirmar que estão todos ligados. 

**4. Criar testes de conectividade**
Na aba "Firewall Tests", crie os seguintes testes:

 - Teste 1 — HTTP permitido:

	- Origem (Source): host-1

	- Destino (Destination): host-2

	- Porta (Port): 80

	- Esperado (Expected Result): Permitido (Allowed)

- Teste 2 — SSH bloqueado

	- Origem (Source): host-1

	- Destino (Destination): host-2

	- Porta (Port): 22

	- Esperado (Expected Result): Bloqueado (Blocked)

- Teste 3 — Comunicação reversa

	- Origem (Source): host-2

	- Destino (Destination): host-1

	- Porta (Port): 22

	- Esperado (Expected Result): Permitido (Allowed)

 Conforme os testes vão sendo criadas, eles serão exibidos conforme a tabela listada na imagem abaixo:
 <img width="1209" height="693" alt="image" src="https://github.com/user-attachments/assets/3827436b-0cc1-4c57-8b16-59c936258334" />


**5. Aplicar regras de firewall**
Na aba "Firewall Rules":
- Selecione o container do firewall (firewall-1);
- Insira as seguintes regras:

		    iptables -P FORWARD ACCEPT
		    iptables -A FORWARD -p tcp --dport 22 -j DROP

- Clique em "Apply rules from hosts". Deverá estar dessa forma configurado:
  <img width="1279" height="775" alt="image" src="https://github.com/user-attachments/assets/c10090a2-2ce7-46e7-8bda-6079341f2644" />


**6. Executar os testes**

Volte para "Firewall Tests" e clique em "Test all".

  **7. Interpretar os resultados**

Após a execução, os testes serão exibidos com cores:

- Teste 1 (porta 80) Permitido: Verde

- Teste 2 (porta 22 client→server) Bloqueado: Azul

- Teste 3 (server→client) Falha: Vermelho

Sendo exibidos da seguinte forma: <img width="947" height="470" alt="image" src="https://github.com/user-attachments/assets/5ecc1b3f-7f52-4128-8109-49c93df17fb3" />


A regra aplicada:

    iptables -A FORWARD -p tcp --dport 22 -j DROP

bloqueia todo tráfego TCP destinado à porta 22, independentemente da origem. Ou seja, ela bloqueia:
host-1 → host-2 e do host-2 → host-1. Por isso o Teste 3 falha, mesmo esperando sucesso.


### Criação e Configuração do Cenário de Rede no GNS3

  

Para realizar os testes, siga as diretrizes a seguir para preparar o ambiente no GNS3:



1. **Criação do Projeto:** Crie um novo projeto no GNS3 ou utilize o modelo já disponibilizado na VM.

2. **Uso de Imagens Docker dentro do GNS3:** Os *hosts* do cenário de rede no GNS3 devem, obrigatoriamente, utilizar a imagem Docker específica do projeto, tal como descrito na seção Configuração dos Nós de Rede (Docker/GNS3), anteriormente.

3. **Configuração da Topologia:** Arraste os contêineres para a área de trabalho e conecte-os utilizando os cabos de rede virtual.

4. **Endereçamento e Roteamento:** Configure os endereços IP e as rotas nos dispositivos diretamente no GNS3. Isso pode ser feito através do menu _Edit Config_ (nos _hosts_ do cenário) ou via terminal, acessível ao clicar nos elementos da rede enquanto estiverem em execução. É importante ressaltar que **o FirewallTester não gerencia configurações de rede; sua função limita-se à validação das regras de _firewall_**.
  
> **Atenção: É obrigatório iniciar o cenário de rede no GNS3 antes de abrir o FirewallTester**. Caso o cenário não esteja em execução, o software não conseguirá localizar os contêineres e apresentará erros de conexão.

 

### Inicializando o FirewallTester

  

- Com a simulação do GNS3 em execução (botão _Play_ pressionado).

- Abra o software através da interface gráfica.

- Assim que iniciado, o software fará a varredura dos componentes dos contêineres.

- Verifique a barra de status inferior ou a aba **Hosts**. Você deve ver seus contêineres listados (ex.: `host-1`, `firewall-1`).

- Se a lista estiver vazia, clique em **Atualizar Hosts**.

  

### Gerenciando serviços (Aba Hosts)

  

**Verificar o status do servidor:** certifique-se de que esteja **On**, pois os testes falharão se o servidor de destino estiver desligado.

  

**Edição de portas:** selecione um _host_ para visualizar as portas abertas, adicione novas para simular serviços e observe que o servidor reinicia automaticamente para aplicar as alterações.

  

### Aplicando regras de segurança (Aba regras de _firewall_)

  

É aqui que você define como o _firewall_ deve se comportar.

1. No topo, escolha o contêiner que atuará como _firewall_ (ex.: `Firewall-1`).

2. Escreva seu _script_ de _firewall_ (sintaxe `iptables` ou _shell script_). Exemplo: ``iptables -A FORWARD -p tcp --dport 80 -j DROP``.

  

**Opções:**

- "Resetar" antes de aplicar: marque esta opção se quiser limpar regras antigas antes de aplicar as novas.

- Aplicar Regras (_Deploy_): envia o _script_ para o contêiner e o executa.

- Verifique a caixa de saída para confirmar que não há erros de sintaxe no `iptables`.

  

### Criando e executando testes (Aba testes de _firewall_)

  

#### Adicionando um teste

  

Configure os campos na caixa **Novo teste**:

  

- **Origem:** quem envia o pacote (ex.: `Host-1`).

- **Destino:** quem recebe (ex.: `Host-2`). O sistema recupera o endereço IP automaticamente.

- **Protocolo:** TCP, UDP ou ICMP.

  

> **Nota:** Para ICMP (Ping), a porta é ignorada ou tratada como contagem.

- **_Porta Dst_:** a porta de destino (ex.: `80`).

  

#### Resultado Esperado

  

- **_Allowed_ (Permitido):** você espera que o pacote chegue ao destino (Sucesso).

- **_Blocked_ (Bloqueado):** você espera que o _firewall_ bloqueie o pacote (_Timeout_ / Recusado).

  

Clique em **_Add_** para colocar o teste na fila.

  

**Executando Testes**

  

- **_Test Row_:** selecione um teste na tabela e clique neste botão para executar apenas esse teste.

- **_Test All_:** abre uma janela de progresso e executa a lista sequencialmente.

- **_Cancel_:** se precisar interromper, clique em **_Cancel_** na janela de progresso. A interrupção é imediata.

  

**Resultados**

  

- **Verde (_Allowed_):** Permitido era o esperado e a conexão foi bem-sucedida. O teste passou.

- **Azul (_Blocked_):** Bloqueado era o esperado e a conexão falhou. O _firewall_ funcionou. O teste passou.

- **Vermelho (_Failed_):** O resultado real foi diferente do esperado (ex.: você esperava que fosse bloqueado, mas foi permitido).

- **Amarelo (Error):** Erro técnico (ex.: _host_ desligado, rota inexistente, erro no _script_ Python).

  
  

## Licença

  

Este programa é um software livre: você pode redistribuí-lo e/ou modificá-lo sob os termos da Licença Pública Geral GNU (GNU General Public License), conforme publicada pela Free Software Foundation, seja na versão 3 da licença ou (a seu critério) qualquer versão posterior.

  

Este programa é distribuído na esperança de que seja útil, mas **SEM QUALQUER GARANTIA**; sem mesmo a garantia implícita de **COMERCIALIZAÇÃO** ou **ADEQUAÇÃO A UMA FINALIDADE ESPECÍFICA**. Consulte a Licença Pública Geral GNU para mais detalhes.

  

Você deve ter recebido uma cópia da Licença Pública Geral GNU junto com este programa. Caso contrário, consulte: [https://www.gnu.org/licenses/](https://www.gnu.org/licenses/)

  
  

## Contato

  

Desenvolvido por:

  

**Luiz Arthur Feitosa dos Santos**

Professor na UTFPR – Campo Mourão

  

Email: [luiz.arthur.feitosa.santos@gmail.com](mailto:luiz.arthur.feitosa.santos@gmail.com)

  

**Luiza Batista Basseto**

Estudante na UTFPR – Campo Mourão

  

Email: [luizabasseto.1@gmail.com](mailto:luizabasseto.1@gmail.com)
