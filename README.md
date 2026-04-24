
# FirewallTester

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

- Artefatos Disponíveis (SeloD);

- Artefatos Funcionais (SeloF);

- Artefatos Sustentáveis (SeloS);

- Experimentos Reprodutíveis (SeloR).

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

* **Appliance (Recomendado):** Baixe e importe os arquivos de *appliance* via interface gráfica do GNS3 (`File -> Import appliance`), os _links_ para esses arquivos são apresentados a seguir. No primeiro uso, o GNS3 baixará automaticamente a imagem do Docker Hub e configurará os modelos de nós. Seguem os arquivos das _appliances_ do FirewallTester:
    * [host-docker-firewallTester.gns3a](https://github.com/luizabasseto/firewallTester/blob/main/gns3_projects/old/host-docker-firewallTester.gns3a): Configura os _hosts_ comuns do cenário (clientes/servidores).
    * [firewall-docker-firewallTester.gns3a](https://github.com/luizabasseto/firewallTester/blob/main/gns3_projects/old/firewall-docker-firewallTester.gns3a): Configura o nó de firewall com suporte a múltiplas interfaces de rede.
    > **Observação:** Embora ambos utilizem a mesma imagem base do Docker Hub, cada *appliance* já define a quantidade adequada de placas de rede e ícones específicos para facilitar a montagem da topologia.

* **Docker Hub (Manual):** Caso prefira configurar os nós manualmente no GNS3, utilize a imagem [luizarthur/cyberinfra:firewall_tester](https://hub.docker.com/layers/luizarthur/cyberinfra/firewall_tester/images/sha256-3198d6b4b9d07571da945d5e5999a4907fbbd0ea398425f93bf5609b56ac9d0d). Após o *pull* da imagem, você deverá criar os modelos de _host_ comum e _firewall_ dentro das preferências do GNS3. Note que a imagem utilizada tanto para os _hosts_ comuns quanto para o _firewall_ é a mesma. A distinção entre eles reside apenas no número de interfaces: enquanto _hosts_ comuns operam com uma única placa de rede, o _firewall_ normalmente deve ser configurado com múltiplas placas para interligar os diferentes segmentos da topologia.


#### B. Instalação do FirewallTester

Com o ecossistema GNS3/Docker pronto, siga os passos para instalar a aplicação:

1. Clone o repositório do projeto:

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

Concluída a instalação, o **FirewallTester** estará pronto para uso. Para executá-lo, utilize o comando `python3 main.py` dentro do diretório do projeto.


### Utilizando o FirewallTester

Com o ecossistema composto por Docker, GNS3 e FirewallTester devidamente instalado e configurado, a ferramenta está pronta para a validação de regras de segurança. Nas seções a seguir, detalhamos a interface do software, descrevendo as funcionalidades de cada aba e suas respectivas aplicações nos cenários de teste.

### Criação e Configuração do Cenário de Rede no GNS3

Para que o FirewallTester funcione corretamente, recomenda-se iniciar primeiro o cenário de rede no GNS3. Isso envolve a criação dos _hosts_ que representarão os dispositivos da rede (clientes e servidores para simulação de fluxos de rede) e de um ou mais nós de _firewall_, cujas regras de segurança serão o alvo dos testes.

> **Nota:** Caso opte por iniciar o FirewallTester antes da topologia no GNS3, será necessário clicar no botão **"Refresh hosts"** na interface do software. Isso garante que os dispositivos e _firewalls_ ativos sejam detectados e fiquem disponíveis para seleção e teste.

Existem duas formas de preparar este ambiente de rede para testes:

#### Opção A: Utilizando um Cenário Pronto (Recomendado para Testes Iniciais)

Para o primeiro contato com a ferramenta, utilize o projeto de exemplo já configurado. Ele contém uma topologia funcional com endereçamento e rotas pré-definidos. Isso pode ser feito acessando o arquivo [redeArtigoSBRC2026.gns3project](https://github.com/luizabasseto/firewallTester/blob/main/gns3_projects/redeArtigoSBRC2026.gns3project), que está disponível na pasta do projeto ou pré-instalado na VM.

Após abrir o projeto de rede GNS3 já existente e configurado, basta abrir o projeto no GNS3 e clicar no botão **"Start"** (ícone de _play_) para iniciar todos os nós do projeto.

#### Opção B: Criando um Cenário Personalizado (Do Zero)

Se desejar criar sua própria topologia, siga estes passos fundamentais:

1. **Criação do Projeto:** No GNS3, crie um novo projeto em branco (`File -> New blank project`) e atribua um nome a ele.

2. **Montagem da Topologia:** Arraste os elementos de rede para a área de trabalho e conecte-os utilizando os cabos virtuais.
    * **Uso de Imagens Docker do FirewallTester (Obrigatório):** Para que o FirewallTester consiga controlar o envio e recebimento de pacotes, todos os nós (clientes e *firewalls*) devem obrigatoriamente utilizar a imagem Docker específica do projeto FirewallTester (conforme detalhado na seção anterior). 
    * **Nota sobre compatibilidade:** É possível incluir *firewalls* ou elementos de rede que utilizem outras imagens; todavia, a ferramenta não terá controle sobre eles para a geração ou captura de tráfego de rede para os testes.

3. **Endereçamento e Roteamento:** Configure os endereços IP e as tabelas de roteamento diretamente no GNS3, seja via terminal ou pelo menu *Edit Config* de cada nó. 
    > **Importante:** O FirewallTester **não gerencia configurações de rede** (IPs, rotas, NAT, etc); sua função limita-se exclusivamente à validação das regras de _firewall_.


### Inicializando o FirewallTester

Após a preparação da topologia e do ambiente de execução, o próximo passo é estabelecer a comunicação entre o FirewallTester e o ecossistema do GNS3. Este processo permite que a ferramenta identifique os ativos da rede e mapeie os pontos de origem e destino para a geração de tráfego, permitindo validar se o _firewall_ está operando em conformidade com as políticas de segurança estabelecidas.

Para inicializar a ferramenta corretamente, siga as etapas a seguir:

1.  **Ative a Simulação:** Certifique-se de que a simulação no GNS3 esteja em execução (botão *Start/Play* pressionado e nós com indicadores verdes).

2.  **Abra a Interface Gráfica:** Inicie o software FirewallTester. Ao abrir, a interface principal será exibida, conforme ilustrado na **Figura 1**.

3. **Execução e Varredura Automática:** Ao iniciar o software, ele realizará automaticamente a identificação dos contêineres ativos no GNS3. O método de inicialização depende do seu ambiente:
    * Execute o comando `python3 main.py` dentro do diretório do projeto via terminal.
    * Clique no ícone do **FirewallTester** disponível na barra de tarefas (inicialização rápida) ou no menu principal do sistema, se estiver utilizando a VM do FirewallTester.

4.  **Verificação de Dispositivos:** Verifique a barra de status inferior ou acesse a aba **Hosts**. Você deverá visualizar a listagem de todos os seus contêineres (ex.: `host-1`, `firewall-1`).

5.  **Sincronização Manual:** Caso a lista de dispositivos apareça vazia, clique no botão **Refresh Hosts** para forçar uma nova detecção dos componentes da rede.

<img width="1209" height="694" alt="image" src="[https://github.com/user-attachments/assets/adbc60d9-dad9-452f-ae91-178c4a0d2347](https://github.com/user-attachments/assets/adbc60d9-dad9-452f-ae91-178c4a0d2347)" />

**Figura 1:** Interface gráfica do FirewallTester exibindo a aba de gerenciamento de Hosts.


A seguir, detalham-se as principais funcionalidades de cada aba da interface do FirewallTester.

### Aba _Hosts_

A aba **Hosts**, ver Figura 1, é a interface responsável pelo gerenciamento e visualização de todos os ativos de rede detectados no ambiente do GNS3. É através dela que o usuário estabelece a base para os testes de conectividade e segurança.

As principais funcionalidades desta aba incluem:

* **Inventário de Dispositivos:** Lista todos os contêineres Docker ativos na topologia (clientes, servidores e *firewalls*). Cada dispositivo é identificado pelo nome definido no projeto do GNS3 (ex: `host-1`, `firewall-01`).

* **Sincronização de Ambiente (_Refresh Hosts_):** Permite forçar uma nova varredura no GNS3 para detectar nós que foram iniciados após a abertura do **FirewallTester**, garantindo que a lista de alvos esteja sempre atualizada.

* **Definição de Serviços de Rede:** Permite determinar quais serviços estarão disponíveis para teste em cada host. No contexto da ferramenta, esses serviços são representados por **portas TCP/UDP**, que podem ser adicionadas ou removidas para simular aplicações reais (como HTTP na porta 80 ou SSH na porta 22).

* **Configuração de Alvos:** Ao definir as portas em cada host, o usuário mapeia os pontos de escuta que o **FirewallTester** utilizará para verificar se o tráfego está sendo corretamente permitido ou bloqueado pelo *firewall*.

Em resumo, a aba **Hosts** não apenas identifica "quem" está na rede, mas também estabelece "quais portas" serão testadas, servindo como a base de configuração essencial para o motor de testes da aplicação.

### Aba *Firewall Rules*

A aba ***Firewall Rules*** funciona como a central de gerência de políticas de segurança do projeto. Como ilustrado na **Figura 2**, esta interface fornece um ambiente completo para a redação, instalação e manutenção de regras de filtragem (como as do *iptables*) diretamente nos nós de *firewall* ativos no GNS3.

<img width="1279" height="775" alt="image" src="[https://github.com/user-attachments/assets/c10090a2-2ce7-46e7-8bda-6079341f2644](https://github.com/user-attachments/assets/c10090a2-2ce7-46e7-8bda-6079341f2644)" />

**Figura 2:** Interface de gerenciamento e edição de regras de *firewall*.

As principais funcionalidades desta interface incluem:

* **Editor de Regras Integrado:** Oferece um editor de texto dedicado que torna o trabalho de redigir políticas de segurança mais amigável e organizado do que o terminal padrão do GNS3.

* **Implantação de Regras:** Permite enviar as regras redigidas diretamente para o _host_ selecionado como *firewall* no cenário. Por padrão, a ferramenta oferece a opção de **limpar as regras anteriores** antes de aplicar o novo conjunto, garantindo que não haja conflitos de políticas.

* **Consulta em Tempo Real:** Fornece a funcionalidade de **listar as regras atuais**, permitindo que o usuário visualize o que está efetivamente instalado e rodando no _host_ remoto sem sair da aplicação.

* **Persistência e Portabilidade:** Inclui recursos para **salvar** o conjunto de regras redigido no _host_ hospedeiro ou **carregar** arquivos com regras de firewall previamente salvas, facilitando a reutilização de cenários de teste.

Dessa forma, o **FirewallTester** atua não apenas como um testador, mas como uma interface de controle, eliminando a necessidade de interação direta via linha de comando nos terminais individuais dos contêineres para a configuração das regras de _firewall_.

### Aba *Firewall Tests*

A aba ***Firewall Tests*** é o ambiente onde o usuário planeja e configura os procedimentos de validação de regras de Firewall. Como ilustrado na **Figura 3**, esta interface permite criar, editar e gerenciar uma lista de casos de teste que verificarão se a política de segurança do *firewall* está sendo efetivamente aplicada.

<img width="947" height="470" alt="image" src="[https://github.com/user-attachments/assets/5ecc1b3f-7f52-4128-8109-49c93df17fb3](https://github.com/user-attachments/assets/5ecc1b3f-7f52-4128-8109-49c93df17fb3)" />

**Figura 3:** Interface de configuração e planejamento dos casos de teste.

Nesta aba, o usuário define os parâmetros fundamentais para a execução das validações:

* **Definição do Escopo do Teste:** Especificam-se os *hosts* de origem e destino, o protocolo utilizado (**TCP**, **UDP** ou **ICMP**) e a porta de destino. 

* **Suporte a Testes Externos:** No caso do protocolo ICMP, a ferramenta permite validar a conectividade via *ping* com nós externos. Isso possibilita testar inclusive a comunicação direta com *hosts* da Internet, expandindo a validação para além da rede local.

* **Ação Esperada (*Expected Result*):** Para cada teste, o usuário define se o resultado esperado é **Liberado** ou **Bloqueado**. Essa definição é essencial para que o software determine automaticamente se a regra de *firewall* está cumprindo o seu propósito.

* **Gerenciamento e Repetibilidade:** As regras configuradas compõem uma tabela interativa que suporta operações de **edição**, **exclusão** e **exportação**. Essas funcionalidades garantem a organização dos cenários e permitem que as validações sejam repetidas com precisão em diferentes momentos ou ambientes.

Em resumo, a aba **Firewall Tests** organiza a inteligência dos testes, permitindo que o usuário mapeie fluxos internos e externos para auditar rigorosamente o comportamento do *firewall*.

#### Execução e Análise de Resultados

Após a definição dos casos de teste, o FirewallTester permite validar a política de segurança de forma dinâmica e intuitiva. A execução pode ser realizada de duas maneiras, oferecendo flexibilidade ao administrador de rede:

1.  **Execução Unitária:** Permite disparar um único teste específico (uma linha da tabela). Esta função é ideal para validar correções pontuais em regras de *firewall* sem a necessidade de reprocessar todo o cenário.

2.  **Execução em Lote (Todos os Testes):** O software percorre toda a lista de testes sequencialmente. Esta funcionalidade é fundamental para garantir a **não regressão** da segurança, ou seja, para verificar se uma nova regra inserida para liberar um serviço não acabou bloqueando indevidamente outro fluxo que já estava funcionando.

#### Feedback Visual e Diagnóstico

A interface utiliza um sistema de cores e termos padronizados para fornecer um diagnóstico imediato sobre o estado de cada regra (conforme exemplificado na **Figura 3**):

* **Verde ou Azul (`Pass`):** Indica que o comportamento do tráfego está em conformidade com o planejado. Por exemplo, um teste marcado em verde confirma que um acesso permitido (ex. HTTP) foi realizado com sucesso, enquanto o azul valida que um bloqueio pretendido (ex. SSH) foi efetivamente executado pelo *firewall*.

* **Vermelho (`Fail`):** Sinaliza uma falha de conformidade. Ocorre quando o resultado real é oposto ao esperado (ex. um fluxo que deveria estar livre foi bloqueado por uma regra genérica).

* **Amarelo (`Error`):** Indica que ocorreu um erro técnico na execução do teste, como a impossibilidade de alcançar um *host* ou uma falha de configuração na interface de rede, impedindo a conclusão da análise.

> **Ciclo de Teste Contínuo:** Com esse *feedback* visual, o administrador pode refinar as regras no *firewall* e reexecutar as validações instantaneamente. Esse processo substitui a complexidade do terminal por um ciclo ágil de correção e verificação, garantindo que a implementação final atinja plena conformidade com o planejamento lógico de segurança.

### Aba _Settings_ (Configurações)

Esta é uma aba técnica fundamental para a correta integração entre o software e o sistema de arquivos dos contêineres Docker e do _host_ hospedeiro. Nela, o usuário define os caminhos e diretórios que regem o comportamento da ferramenta, tais como:

* **Caminhos de Binários:** Onde estão localizados os _scripts_ e softwares de cliente/servidor (usados para gerar e receber tráfego) dentro dos contêineres.

* **Repositório de Regras:** O diretório padrão para salvar e carregar os conjuntos de regras de *firewall* redigidos na aplicação.

* **Logs e Exportação:** Definição de onde serão armazenados os relatórios de testes e capturas de pacotes.

Essa centralização permite que o FirewallTester seja facilmente adaptado para novos cenários ou versões de imagens Docker sem a necessidade de alterar o código-fonte da aplicação.

> Nota: Por padrão, as definições de diretórios atendem a todos os requisitos do projeto. A edição desses campos é opcional e voltada apenas para casos onde o usuário deseje adaptar o software a uma estrutura de arquivos personalizada.

### Aba _Help_ (Ajuda)

A aba _Help_ atua como um guia de suporte rápido para o usuário, fornecendo informações sobre atalhos de teclado que agilizam a operação da ferramenta, orientações sobre o fluxo de trabalho e _links_ diretos para a página oficial e repositório do projeto.

### Aba _About_ (Sobre)

Nesta aba, são apresentadas as informações institucionais do projeto. Nela constam a versão atual do software, os créditos de desenvolvimento, informações de licença e o contato dos autores. Além disso, fornece o _link_ para o repositório oficial, permitindo que a comunidade acadêmica e técnica acompanhe a evolução da ferramenta e contribua com o seu desenvolvimento.


Em suma, a organização do FirewallTester em abas especializadas oferece um fluxo de trabalho estruturado que integra, em uma única interface, todas as etapas críticas da gestão de segurança de redes. Ao unir o inventário dinâmico de ativos, a edição direta de políticas de filtragem e um motor de testes com feedback visual imediato, a ferramenta elimina a fragmentação de tarefas entre múltiplos terminais. Essa abordagem não apenas simplifica a operação técnica, mas estabelece um ciclo de auditoria contínua e preciso, garantindo que a implementação prática das regras de firewall esteja sempre em estrita conformidade com o planejamento lógico de segurança.


### Passo a passo do teste mínimo

Com o intuito de ilustrar a operabilidade do **FirewallTester**, descreve-se a seguir um cenário de teste minimalista. Este exemplo foca na validação de uma regra de bloqueio SSH e na identificação de efeitos colaterais em outras rotas.

Você pode acompanhar este procedimento via **[tutorial em vídeo](https://www.youtube.com/watch?v=qyCBiV2q7rA)** ou pelas diretrizes do texto a seguir.

[![Assista ao vídeo](https://img.youtube.com/vi/qyCBiV2q7rA/0.jpg)](https://www.youtube.com/watch?v=qyCBiV2q7rA)

#### 1. Preparação do Ambiente (Via VM)

A forma mais rápida de experimentar pela primeira vez o FirewallTester é utilizando a máquina virtual pré-configurada, sendo assim:

* Importe o arquivo `.ova` no VirtualBox e inicie a VM.

* O **GNS3** abrirá automaticamente com o cenário base carregado.

* **Importante:** Clique no botão de triângulo verde (*Start*) no GNS3 para ligar todos os nós. O **FirewallTester** só consegue interagir com _hosts_ (contêineres) do cenário de rede do GNS3, que estejam ativos.

#### 2. Inicialização do Software

Abra o **FirewallTester** pelo ícone na área de trabalho ou via terminal:

```bash
python3 main.py
```

> No caso de executar via terminal, lembre-se de estar dentro da parta do projeto (`~/firewalltester/`).

#### 3. Verificação de Conectividade (Aba _Hosts_)

Acesse a aba **Hosts** e confirme se os dispositivos `host-1`, `host-2` e `firewall-1` exibem o status **On** (indicador verde). Isso garante que os serviços de teste estão prontos para responder.

#### 4. Configuração da Bateria de Testes (Aba _Firewall Tests_)

Crie ou carregue os seguintes testes para validar a política de segurança:

1.  **HTTP (Porta TCP/80):** Origem `host-1` → Destino `host-2`. Esperado: **Allowed**.

2.  **SSH (Porta TCP/22):** Origem `host-1` → Destino `host-2`. Esperado: **Blocked**.

3.  **SSH Reverso (Porta TCP/22):** Origem `host-2` → Destino `host-1`. Esperado: **Allowed**.

#### 5. Implementação da Regra (Aba _Firewall Rules_)

Selecione o `firewall-1` e aplique a política que deseja testar:

1.  Defina a política padrão: `iptables -P FORWARD ACCEPT`.

2.  Adicione a restrição: `iptables -A FORWARD -p tcp --dport 22 -j DROP`.

3.  Clique em **Apply rules from hosts**. O campo de saída confirmará a execução do comando no contêiner.

#### 6. Execução e Análise Visual

Retorne à aba **Firewall Tests** e utilize o botão **Test All**. O software fornecerá o diagnóstico visual imediato:

* **Teste 1 (Verde - Pass):** O tráfego HTTP fluiu como esperado, pois não há regras bloqueando a porta TCP/80.

* **Teste 2 (Azul - Pass):** O bloqueio SSH foi bem-sucedido. O _firewall_ barrou o pacote conforme a regra inserida.

* **Teste 3 (Vermelho - Fail):** **Atenção aqui.** O teste falhou porque a regra escrita foi muito genérica (`--dport 22`). Ela acabou bloqueando o SSH em ambos os sentidos, impedindo que o `host-2` acessasse o `host-1`.

Assim, este resultado demonstra a utilidade da ferramenta: o administrador percebe visualmente (cor vermelha) que sua regra de _firewall_ causou um bloqueio indevido em um fluxo que deveria estar liberado, permitindo o ajuste imediato da sintaxe para especificar as interfaces ou IPs de origem/destino corretos.


> **Nota:** Neste exemplo, para que todos os testes atinjam a conformidade (status *Pass*), é necessário aumentar a especificidade da regra de filtragem. Ao substituir o comando anterior por `iptables -A FORWARD -d 192.168.2.2 -p tcp --dport 22 -j DROP`, o bloqueio deixa de ser genérico e passa a ser aplicado exclusivamente aos pacotes destinados ao `host-2` (192.168.2.2). Essa alteração permite que o fluxo reverso (do `host-2` para o `host-1`) seja liberado pela política padrão do *firewall*, uma vez que o destino não coincide mais com a regra de restrição, corrigindo o erro de conformidade identificado anteriormente pelo FirewallTester e garantindo que o planejamento lógico seja respeitado integralmente.


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
