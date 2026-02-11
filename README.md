# Firewall Tester

This software was developed to enhance network security through practical and efficient firewall testing. More than just a testing tool, it serves as a valuable educational resource, designed to simplify and improve the learning process about firewalls. With an intuitive and interactive interface, students can visualize and experiment with firewall rule creation and application, making complex concepts easier to understand and fostering deeper, more effective learning.

The software enables the creation of network scenarios using [GNS3](https://www.gns3.com/). Hosts within the scenario should utilize Docker images to create containers for firewall testing (this version of the software supports only containers). Once the network scenario is set up in GNS3 and all hosts are powered on, you can launch the firewall rule testing software on the host running the containers. This software provides a graphical interface that allows you to:

- Create firewall tests;  
- Define and edit firewall rules on the scenario's hosts;  
- Add and remove ports that represent network services to be tested;  

Additionally, the software allows you to save test results and rerun them later, for example, on another computer.

## Project Organization

```
firewallTester/
├── assets/
├── core/
├── docker/
├── gns3_projects/
├── ui/
├── main.py
├── requirements.txt

```

## License

This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License or (at your option) any later version.

This program is distributed in the hope that it will be useful, but **WITHOUT ANY WARRANTY**; without even the implied warranty of **MERCHANTABILITY** or **FITNESS FOR A PARTICULAR PURPOSE**. See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with this program. If not, see <https://www.gnu.org/licenses/>.

## Contact

This software was developed by **Luiz Arthur Feitosa dos Santos**, professor at **UTFPR (Federal Technological University of Paraná) - Campo Mourão, Brazil**. 
Email: <luiz.arthur.feitosa.santos@gmail.com> | <luizsantos@utfpr.edu.br>.
And forked by **Luiza Batista Basseto**, student at  **UTFPR (Federal Technological University of Paraná) - Campo Mourão, Brazil**. Email: <luizabasseto.1@gmail.com> | <luizabatista@alunos.utfpr.edu.br>.

## Tutorial de Configuração

Assista ao vídeo de tutorial (https://www.youtube.com/watch?v=qyCBiV2q7rA) ou siga ao tutorial disponibilizado após ele.

[![Assista ao vídeo](https://img.youtube.com/vi/qyCBiV2q7rA/0.jpg)](https://www.youtube.com/watch?v=qyCBiV2q7rA)

### Pré-requisitos do ambiente

Antes de abrir o software, configure seu ambiente virtual.

- Baixe a máquina virtual do VirtualBox, disponível em:  
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
