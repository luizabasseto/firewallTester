def create_help_tab(self):
    self.help_frame = QWidget()
    main_layout = QVBoxLayout(self.help_frame)
    main_layout.setAlignment(Qt.AlignTop)
    self.notebook.addTab(self.help_frame, "Help") 

    help_text_browser = QTextBrowser()
    help_text_browser.setOpenExternalLinks(True) 
    help_content = """
    <html>
    <head>
        <style>
            h1 { color: #2c3e50; }
            h2 { color: #34495e; border-bottom: 1px solid #ccc; }
            p  { font-size: 14px; line-height: 1.6; }
            ul { list-style-type: disc; margin-left: 20px; }
            li { margin-bottom: 10px; }
            code { background-color: #f4f4f4; padding: 2px 5px; border-radius: 4px; font-family: monospace; }
        </style>
    </head>
    <body>
        <h1>Como Usar o Firewall Tester</h1>
        <p>
            Esta ferramenta foi projetada para automatizar testes de regras de firewall
            em um ambiente de laboratório usando GNS3 e Docker.
        </p>

        <h2> Guia de Início Rápido</h2>
        <ul>
            <li>
                <b>Passo 1: Prepare o Ambiente</b><br>
                Certifique-se de que sua topologia no GNS3 está rodando, com os containers Docker (hosts) iniciados.
            </li>
            <li>
                <b>Passo 2: Conecte a Ferramenta</b><br>
                Clique no botão <b>"Atualizar Hosts"</b> na aba principal. A ferramenta irá detectar
                automaticamente todos os containers em execução.
            </li>
            <li>
                <b>Passo 3: Edite as Regras de Firewall</b><br>
                Selecione um host que funcionará como firewall na aba "Firewall". Utilize o editor
                para carregar, modificar e aplicar conjuntos de regras <code>iptables</code>.
            </li>
            <li>
                <b>Passo 4: Crie os Testes</b><br>
                Vá para a aba "Testes de Firewall", defina os testes de conectividade desejados
                (ex: de <code>hostA</code> para <code>hostB</code> na porta <code>80/tcp</code>) e adicione-os à lista.
            </li>
            <li>
                <b>Passo 5: Execute e Analise</b><br>
                Clique em <b>"Executar Testes Selecionados"</b>. Os resultados (Sucesso/Falha) serão exibidos
                na tabela, ajudando a validar suas regras de firewall.
            </li>
        </ul>
    </body>
    </html>
    """
    help_text_browser.setHtml(help_content)
    main_layout.addWidget(help_text_browser)