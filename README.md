# Leo: O Lembrete Amigo para Idosos e Seus Cuidadores (Versão Terminal c/ IA)

## Sobre o Projeto: Leo, o Aliado Digital na Gestão Compartilhada da Rotina

O projeto **Leo** visa simplificar a gestão de rotinas importantes (saúde, medicações, compromissos) para pessoas idosas. Reconhecemos que essa tarefa envolve a participação ativa de **cuidadores, filhos, netos e outros familiares**. Leo é projetado para ser um assistente pessoal acessível via **WhatsApp** que atende a **dois usuários chave**: o próprio **idoso** (com interação direta e super simples) e o **cuidador/tutor** (com funcionalidades que facilitam a gestão e o acompanhamento).

Inspirado no **mural de geladeira**, um ponto de comunicação visual e lembretes para a família, Leo centraliza essas informações em um **ponto digital acessível**, permitindo que tanto o idoso quanto seu tutor possam "fixar" (cadastrar) e "consultar" (ver) os lembretes importantes de forma colaborativa.

Esta versão no terminal é uma **demonstração simples** que valida a lógica básica de como Leo recebe comandos textuais, simula o gerenciamento para múltiplos usuários e utiliza **Inteligência Artificial Generativa (Google AI)** para criar algumas das respostas do bot, tornando a interação mais natural para fins de demonstração.

**Importante:** Esta é uma versão simplificada para apresentação. O armazenamento é temporário, a interação com a IA é apenas na geração de texto de saída, e a comunicação real via WhatsApp e lembretes automáticos são partes da visão futura.

## Funcionalidades (Versão Terminal Simples c/ IA)

Esta versão demonstra a lógica de interação, simulação multiusuário e geração de texto com IA:

* **Simulação de Usuários (Idoso/Tutor):** Permite simular diferentes perfis de usuário usando o comando `usar [nome]`.
    * **Comando:** `usar [nome]` (Ex: `usar Dona Maria`, `usar João`)
* **Agendar Compromisso:** Salva um lembrete de consulta, exame, etc., associado ao idoso ativo.
    * **Formato:** `agendar [Descrição] dia DD/MM HH:MM` (use o ano atual se omitido)
    * *Exemplo:* `agendar Consulta Cardiologista dia 20/05 14:30`
    * *Resposta:* Gerada pela IA, confirmando o agendamento e quem seria notificado.
* **Salvar Medicação:** Salva informações de um lembrete de medicamento regular, associado ao idoso ativo.
    * **Formato:** `medicação [Nome]; [Dosagem]; [Frequência]; HH:MM` (use ponto e vírgula)
    * *Exemplo:* `medicação Dipirona; 500mg; 8 em 8 horas; 08:00`
    * *Resposta:* Gerada pela IA, confirmando a medicação e quem seria notificado.
* **Ver Lembretes:** Lista todos os compromissos e medicamentos salvos **para o idoso ativo** na memória durante a sessão atual. Mostra quem seria notificado para cada item.
    * **Comando:** `ver` ou `ver tudo`
* **Ajuda:** Exibe uma mensagem explicando os comandos. A introdução da mensagem é gerada pela IA.
    * **Comando:** `ajuda`
* **Comando não reconhecido:** Se o bot não entender um comando (fora dos formatos esperados), a resposta de "não entendi" é gerada pela IA.
* **Sair:** Encerra a execução.
    * **Comando:** `sair`
    * *Resposta:* Gerada pela IA.

## Como Funciona (Nesta Demo de Terminal)

1.  Você executa o script Python `chatbot_com_ia.py` (ou o nome que você deu).
2.  Leo inicia e pede para você se identificar usando `usar [nome]`.
3.  Você digita `usar [nome]` (Ex: `usar João`). Leo simula o login e diz para qual idoso (Ex: Dona Maria) você está gerenciando os lembretes. A mensagem de login é gerada pela IA.
4.  Você digita um comando como `agendar ...` ou `medicação ...`, seguindo os formatos exatos.
5.  O script processa o texto, extrai as informações (se o formato estiver correto) e determina quais usuários (o idoso e tutores ligados a ele na simulação) seriam notificados.
6.  As informações são guardadas **temporariamente** na memória do script.
7.  Uma **resposta** confirmando a ação e mencionando quem seria notificado é **gerada pela Google Generative AI** com base nos detalhes salvos e no perfil do usuário ativo, e então exibida.
8.  O comando `ver` exibe os lembretes salvos para o idoso ativo.
9.  Comandos `ajuda`, `sair` e entradas inesperadas também acionam respostas geradas pela IA.

**Importante:**

* A IA é usada **apenas para gerar o texto das respostas do bot**. Ela **não** entende comandos em linguagem natural livre nesta versão; a entrada do usuário *ainda* precisa seguir os formatos fixos.
* O armazenamento é **apenas na memória RAM** e os dados são perdidos quando o script é fechado.
* As notificações são **simuladas**; o código apenas determina e exibe quem *seria* notificado.

## Tecnologias Utilizadas (Nesta Versão c/ IA)

* **Linguagem:** Python
* **Inteligência Artificial:** Google Generative AI (Modelo `gemini-2.0-flash`) para geração de texto de saída.
* **Biblioteca AI:** `google-generativeai`
* **Armazenamento Temporário:** Estruturas de dados nativas do Python (dicionários e listas em memória).
* **Processamento de Comandos:** Lógica simples de string (como `split`, `startswith`) e expressões regulares (`re`) para extrair informações de comandos formatados.
* **Gerenciamento de Chave API:** Uso de variáveis de ambiente ou `google.colab.userdata` para obter a `GOOGLE_API_KEY`.

## Configuração e Instalação

Para rodar esta versão do Leo, você precisa:

1.  Ter **Python 3** instalado.
2.  Instalar a biblioteca Google Generative AI:
    ```bash
    pip install google-generativeai
    ```
3.  Obter uma **Google API Key** para a Generative AI. Você pode conseguir uma gratuitamente em:
    * [Google AI Studio](https://aistudio.google.com/) (recomendado para começar)
    * [Google Cloud Console](https://cloud.google.com/generative-ai)
4.  **Configurar a sua API Key:** Esta chave precisa estar acessível ao script. A forma mais segura (e que o código espera) é através de uma variável de ambiente chamada `GOOGLE_API_KEY`.
    * **No Google Colab:** Use o recurso "Secrets" (ícone de chave na barra lateral esquerda). Adicione um novo Secret chamado `GOOGLE_API_KEY` e cole sua chave lá. O código `userdata.get('GOOGLE_API_KEY')` irá recuperá-la.
    * **No Terminal (Linux/macOS):** Abra seu terminal e digite `export GOOGLE_API_KEY='SUA_CHAVE_AQUI'` antes de rodar o script. Para que seja permanente, adicione essa linha no seu arquivo `~/.bashrc`, `~/.zshrc` ou similar.
    * **No Terminal (Windows cmd):** Abra o Prompt de Comando e digite `set GOOGLE_API_KEY=SUA_CHAVE_AQUI` antes de rodar o script.
    * **No Terminal (Windows PowerShell):** Abra o PowerShell e digite `$env:GOOGLE_API_KEY='SUA_CHAVE_AQUI'` antes de rodar o script.
    * **Substituindo no Código (Não Recomendado):** Você **pode** colar sua chave diretamente onde `os.getenv('GOOGLE_API_KEY')` ou `userdata.get('GOOGLE_API_KEY')` é usado, mas **NÃO faça isso em código que você pretende compartilhar publicamente** (como no GitHub). Exemplo: `GOOGLE_API_KEY = 'SUA_CHAVE_AQUI'`.

5.  Baixe ou copie o código do script Python (`chatbot_com_ia.py`).
6.  Abra o terminal ou ambiente (como Google Colab) onde você configurou a chave.
7.  Navegue até a pasta onde salvou o arquivo.
8.  Execute o script: `python chatbot_com_ia.py`

## Uso

Após executar o script, Leo irá pedir para você se identificar. Digite `usar [nome]` com um dos nomes disponíveis (Ex: `usar Dona Maria` ou `usar João`). Em seguida, interaja usando os comandos e formatos listados na seção "Funcionalidades".

*Exemplos de Interação:*

