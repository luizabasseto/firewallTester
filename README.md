# Firewall Tester

Este software foi desenvolvido para aprimorar a segurança de redes por meio de testes de firewall práticos e eficientes. Mais do que uma simples ferramenta de teste, ele também atua como um valioso recurso educacional, projetado para simplificar e melhorar o processo de aprendizagem sobre firewalls. Com uma interface intuitiva e interativa, os estudantes podem visualizar e experimentar a criação e aplicação de regras de firewall, tornando conceitos complexos mais fáceis de compreender e promovendo um aprendizado mais profundo e eficaz.

O software permite a criação de cenários de rede utilizando o GNS3. Os hosts dentro do cenário devem utilizar imagens Docker para a criação de contêineres destinados aos testes de firewall (esta versão do software suporta apenas contêineres). Após a configuração do cenário de rede no GNS3 e a inicialização de todos os hosts, é possível executar o software de testes de regras de firewall na máquina que está rodando os contêineres. O sistema oferece uma interface gráfica que permite:

* Criar testes de firewall;
* Definir e editar regras de firewall nos hosts do cenário;
* Adicionar e remover portas que representam serviços de rede a serem testados;

Além disso, o software permite salvar os resultados dos testes e executá-los novamente posteriormente, por exemplo, em outro computador.


## Estrutura do Repositório

O repositório está organizado da seguinte forma:

```
firewallTester/
├── assets/            # Imagens e arquivos auxiliares
├── core/              # Lógica principal da aplicação
├── docker/            # Configurações relacionadas aos contêineres
├── gns3_projects/     # Projetos de exemplo para uso no GNS3
├── ui/                # Interface gráfica do usuário
├── main.py            # Arquivo principal para execução
├── requirements.txt   # Dependências do projeto
```


## Selos Considerados

Os selos considerados para avaliação deste artefato são:

* Disponível
* Funcional
* Reprodutível

## Informações Básicas

Para execução do artefato, recomenda-se o seguinte ambiente:

### Requisitos de Hardware

Este projeto depende da execução simultânea de:

* Topologias de rede no GNS3;
* Containers Docker;
* Possivelmente múltiplos hosts simulados;
* Aplicação desenvolvida em Python.

Assim, para garantir o funcionamento adequado do FirewallTester, especialmente durante a execução de topologias de rede no GNS3 com múltiplos nós em Docker, recomenda-se que a máquina host atenda aos seguintes requisitos que estão divididos em mínimo/recomendado:

* CPU: 4 núcleos / 8 núcleos;
* Memória RAM: 8 GB / 16 GB ou mais;
* Armazenamento: 20 GB / 50 GB+ livre (SSD recomendável);
* Virtualização: Suporte a VT-x/AMD-V habilitado na BIOS.

### Requisitos de Software

* Python 3.10 ou superior
* Docker
* GNS3
* VirtualBox (para execução da VM do GNS3)


### Dependências

As dependências do projeto estão listadas no arquivo `requirements.txt`.

Para instalá-las, execute:

```bash
pip3 install -r requirements.txt
```
Caso ocorra erro na instalação, será necessário instalar e ativar um ambiente virtual Python, executando os seguintes comandos:

```bash
python -m venv .venv
source .venv/bin/activate
```

Além disso, é necessário:

* Utilizar o GNS3 para criação dos cenários de rede
* Utilizar contêineres Docker como hosts e firewalls

Caso utilize a máquina virtual fornecida, ela já contém parte das dependências configuradas.


### Preocupações com Segurança

Este software executa comandos de firewall (como regras `iptables`) dentro de contêineres Docker.

Para garantir a segurança durante a execução:

* Utilize ambientes isolados (como máquinas virtuais);
* Evite executar o software diretamente no sistema host com privilégios elevados;
* Não exponha portas desnecessárias para redes externas;
* Utilize apenas cenários controlados para testes.


## Instalação

Siga os passos abaixo para instalar e executar o projeto:

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


## Teste Mínimo e Experimentação

Este tutorial tem como objetivo evidenciar um teste minímo da ferramenta.

Assista ao vídeo de tutorial (https://www.youtube.com/watch?v=qyCBiV2q7rA) ou siga os passos disponibilizado após ele.

[![Assista ao vídeo](https://img.youtube.com/vi/qyCBiV2q7rA/0.jpg)](https://www.youtube.com/watch?v=qyCBiV2q7rA)

### Pré-requisitos do ambiente

Antes de abrir o software, configure seu ambiente virtual.

- Baixe o VirtualBox, disponível em:  
  https://www.virtualbox.org/wiki/Downloads
- Instale a VM do GNS3 usando o arquivo disponível em: https://drive.google.com/drive/folders/1IWIF4bGQZ7yR9pshSHVH1eTzxMzTgrOu?usp=sharing.
- Após concluir a instalação, configure as configurações de rede.

### Configurações de rede

- Crie um projeto no GNS3 ou utilize do modelo já disponibilizado na VM.
- Caso opte por criar outro projeto, arraste contêineres Docker para a área de trabalho (ex.: hosts e firewalls).
- Conecte-os usando cabos de rede virtual.

> **Importante:** Configure endereços IP estáticos e rotas por meio da configuração de rede do GNS3 (Edit Config) ou via terminal.

### Inicializando o FirewallTester

- Com a simulação do GNS3 em execução (botão Play pressionado).
- Abra o software através da interface gráfica.
- Assim que iniciado, o software fará a varredura dos componentes dos contêineres.
- Verifique a barra de status inferior ou a aba **Hosts**. Você deve ver seus contêineres listados (ex.: `host-1`, `firewall-1`).
- Se a lista estiver vazia, clique em **Atualizar Hosts**.

### Gerenciando serviços (Aba Hosts)

**Verificar o status do servidor:** certifique-se de que esteja **On**, pois os testes falharão se o servidor de destino estiver desligado.

**Edição de portas:** selecione um host para visualizar as portas abertas, adicione novas para simular serviços e observe que o servidor reinicia automaticamente para aplicar as alterações.

### Aplicando regras de segurança (Aba regras de rirewall)

É aqui que você define como o firewall deve se comportar.
 1. No topo, escolha o contêiner que atuará como firewall (ex.: `Firewall-1`).
 2. Escreva seu script de firewall (sintaxe iptables ou shell script). Exemplo: ``iptables -A FORWARD -p tcp --dport 80 -j DROP``.

**Opções:**
- Resetar antes de aplicar: marque esta opção se quiser limpar regras antigas antes de aplicar as novas.
- Aplicar Regras (Deploy): envia o script para o contêiner e o executa.
- Verifique a caixa de saída para confirmar que não há erros de sintaxe no iptables.

### Criando e executando testes (Aba testes de firewall)

#### Adicionando um teste

Configure os campos na caixa **Novo teste**:

- **Origem:** quem envia o pacote (ex.: `Host-1`).
- **Destino:** quem recebe (ex.: `Host-2`). O sistema recupera o endereço IP automaticamente.
- **Protocolo:** TCP, UDP ou ICMP.

  > **Nota:** Para ICMP (Ping), a porta é ignorada ou tratada como contagem.
- **Porta Dst:** a porta de destino (ex.: `80`).

#### Resultado Esperado

- **Allowed (Permitido):** você espera que o pacote chegue ao destino (Sucesso).
- **Blocked (Bloqueado):** você espera que o firewall bloqueie o pacote (Timeout / Recusado).

Clique em **Add** para colocar o teste na fila.

**Executando Testes**

- **Test Row:** selecione um teste na tabela e clique neste botão para executar apenas esse teste.
- **Test All:** abre uma janela de progresso e executa a lista sequencialmente.
- **Cancel:** se precisar interromper, clique em **Cancel** na janela de progresso. A interrupção é imediata.

**Resultados**

- **Verde (Allowed):** Permitido era o esperado e a conexão foi bem-sucedida. O teste passou.
- **Azul (Blocked):** Bloqueado era o esperado e a conexão falhou. O firewall funcionou. O teste passou.
- **Vermelho (Failed):** O resultado real foi diferente do esperado (ex.: você esperava que fosse bloqueado, mas foi permitido).
- **Amarelo (Error):** Erro técnico (ex.: host desligado, rota inexistente, erro no script Python).


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
