

!pip install google-genai

import os
from google.colab import userdata
os.environ['GOOGLE_API_KEY'] = userdata.get('GOOGLE_API_KEY')

from google import genai

client = genai.Client()

for model in client.models.list():
  print(model.name)

modelo = 'gemini-2.0-flash'

import os
import datetime
import uuid
import re
import google.generativeai as genai

# Importa 'userdata' apenas em ambiente Colab.
# Em outro ambiente, você usaria 'os.getenv()' diretamente.
try:
    from google.colab import userdata
    IS_COLAB = True
except ImportError:
    IS_COLAB = False
    print("Não rodando no Google Colab. Usando variável de ambiente para API Key.")

# --- Configuração da Google Generative AI ---
# Obtém a API Key. No Colab usa userdata, fora usa variável de ambiente OS.
if IS_COLAB:
    # No Colab, a chave é obtida de 'Secrets' (ícone de chave na barra lateral)
    # Certifique-se de que a chave está salva lá com o nome 'GOOGLE_API_KEY'
    GOOGLE_API_KEY = userdata.get('GOOGLE_API_KEY')
else:
    # Fora do Colab, obtém da variável de ambiente padrão do sistema operacional
    GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')


# Configura a API Key e inicializa o modelo
ai_model = None
if GOOGLE_API_KEY:
    try:
        # Configura a API Key
        genai.configure(api_key=GOOGLE_API_KEY)

        # --- Seleciona o modelo ---
        # Você listou os modelos, agora usamos o nome escolhido:
        MODEL_NAME = 'gemini-2.0-flash' # Seu modelo selecionado

        # Inicializa o modelo generativo
        ai_model = genai.GenerativeModel(MODEL_NAME)
        print(f"🤖: Google Generative AI configurada com o modelo '{MODEL_NAME}'.")

    except Exception as e:
        # Captura erros na configuração ou inicialização do modelo
        ai_model = None
        print(f"🤖: Erro ao configurar ou inicializar modelo Google AI: {e}. As respostas serão fixas (fallback).")
else:
    # Mensagem se a chave API não for encontrada
    ai_model = None
    print("🤖: GOOGLE_API_KEY não encontrada. As respostas serão fixas (fallback).")


# --- Dados de Usuários e Ligações (SIMULADOS) ---
# (Reaproveitados do código anterior)
users = {
    'user_idoso_1': {'role': 'idoso', 'name': 'Dona Maria'},
    'user_tutor_1': {'role': 'tutor', 'name': 'João'},
    'user_tutor_2': {'role': 'tutor', 'name': 'Ana'}
}
user_links = {
    'user_tutor_1': 'user_idoso_1',
    'user_tutor_2': 'user_idoso_1'
}
user_names_to_ids = {v['name'].lower(): k for k, v in users.items()}

# --- Armazenamento em Memória (NÃO PERSISTENTE) ---
# (Reaproveitados do código anterior)
agendamentos_db = {}

# --- Contexto do Usuário Atual na Sessão do Terminal ---
# (Reaproveitados do código anterior)
current_user_id = None
current_idoso_id = None

# --- Funções Auxiliares de Parsing Simples ---
# (Reaproveitados do código anterior - Mantêm a lógica de formatos fixos)

def parse_simple_appointment(text):
    if not text.lower().startswith('agendar '): return None, None
    partes = text[len('agendar '):].strip().split(' dia ')
    if len(partes) < 2: return None, None
    descricao = partes[0].strip()
    data_hora_parte = partes[1].strip()
    match = re.search(r'(\d{1,2}/\d{1,2}(?:/\d{2,4})?)\s+(\d{1,2}:\d{2})', data_hora_parte)
    if match:
        data_str = match.group(1)
        hora_str = match.group(2)
        try:
            if len(data_str.split('/')) == 2: data_str += f'/{datetime.date.today().year}'
            data_hora_agendamento = None
            for fmt in ('%d/%m/%Y %H:%M', '%d/%m/%y %H:%M'):
                try: data_hora_agendamento = datetime.datetime.strptime(f"{data_str} {hora_str}", fmt); break
                except ValueError: pass
            if data_hora_agendamento: return descricao.capitalize(), data_hora_agendamento.replace(second=0, microsecond=0)
            else: return None, None
        except ValueError: return None, None
    return None, None

def parse_simple_medication(text):
    if not text.lower().startswith('medicação '): return None, None, None, None
    partes_str = text[len('medicação '):].strip()
    partes = partes_str.split(';')
    if len(partes) != 4: return None, None, None, None
    try:
        nome = partes[0].strip().capitalize()
        dosagem = partes[1].strip()
        frequencia_str = partes[2].strip()
        hora_str = partes[3].strip()
        primeira_hora_obj = datetime.datetime.strptime(hora_str, '%H:%M').time()
        if not nome or not dosagem or not frequencia_str: return None, None, None, None
        return nome, dosagem, frequencia_str, primeira_hora_obj
    except ValueError: return None, None, None, None
    except Exception as e: print(f"Erro inesperado no parsing de medicação: {e}"); return None, None, None, None

# --- Funções de Gerenciamento de Usuários e Notificação ---
# (Reaproveitadas do código anterior)

def get_idoso_data(idoso_id):
    if idoso_id not in agendamentos_db:
        agendamentos_db[idoso_id] = {'appointments': [], 'medications': []}
    return agendamentos_db[idoso_id]

def get_users_to_notify(idoso_id, user_who_scheduled_id):
    notified_ids = set()
    notified_ids.add(idoso_id)
    for tutor_id, linked_idoso in user_links.items():
        if linked_idoso == idoso_id: notified_ids.add(tutor_id)
    return list(notified_ids)

def get_user_name(user_id):
    return users.get(user_id, {}).get('name', 'Usuário Desconhecido')

def formatar_lista_completa_simples(dados_idoso):
    appointments = dados_idoso.get('appointments', [])
    medications = dados_idoso.get('medications', [])

    if not appointments and not medications:
        return f"🤖: Não há lembretes ou agendamentos salvos para {get_user_name(current_idoso_id)} nesta sessão."

    texto = f"🤖: Lembretes e agendamentos para {get_user_name(current_idoso_id)} (nesta sessão):\n"

    if appointments:
        texto += "\n📅 Compromissos Agendados:\n"
        appointments_ordenados = sorted(appointments, key=lambda x: x['data_hora'])
        future_appointments_exist = False
        for ag in appointments_ordenados:
            if ag['data_hora'] < datetime.datetime.now() - datetime.timedelta(minutes=5):
                continue
            future_appointments_exist = True
            data_fmt = ag['data_hora'].strftime('%d/%m/%Y')
            hora_fmt = ag['data_hora'].strftime('%H:%M')
            notified_names = [get_user_name(uid) for uid in ag.get('notified_users', [])]
            texto += f"- {ag['descricao']} em {data_fmt} às {hora_fmt} (Notificar: {', '.join(notified_names)})\n"
        if not future_appointments_exist:
             texto += "  (Nenhum compromisso futuro nesta sessão)\n"

    if medications:
        texto += "\n💊 Medicações Cadastradas:\n"
        for med in medications:
             primeira_hora_fmt = med['primeira_hora'].strftime('%H:%M')
             notified_names = [get_user_name(uid) for uid in med.get('notified_users', [])]
             texto += (f"- {med['nome']} ({med['dosagem']}) {med['frequencia']} "
                       f"(primeira dose hoje às {primeira_hora_fmt}) "
                       f"(Notificar: {', '.join(notified_names)})\n")
    elif not appointments:
         pass

    texto += "\nPara adicionar, use 'agendar ...' ou 'medicação ...'."
    texto += f"Para gerenciar outro usuário, digite 'usar [nome]'.\n"
    texto += "Digite 'ajuda' para ver os formatos."

    return texto

# --- Função para Gerar Resposta com Google AI (ou Fallback) ---

def generate_response_with_ai(prompt_text, fallback_text="Desculpe, não consegui gerar a resposta agora."):
    """Chama a API do Google AI para gerar texto. Usa fallback se a API não estiver disponível ou falhar."""
    if ai_model:
        try:
            # Adiciona um toque de personalidade e instrução para o bot
            full_prompt = (
                "Você é Leo, um assistente personal amigável que ajuda idosos e cuidadores a gerenciar lembretes. "
                "Seja prestativo, claro e use linguagem simples (português do Brasil). "
                "Gere uma resposta curta baseada no seguinte pedido/contexto, formulando-a diretamente como se fosse o bot Leo falando:\n\n"
                f"Contexto: {prompt_text}"
            )
            response = ai_model.generate_content(full_prompt)
            # Verifica se a resposta tem texto e se não foi bloqueada
            # finish_reason 0 é unset, 1 é stop (sucesso). Outros valores indicam bloqueio.
            # https://ai.google.dev/api/python/google/ai/generativetext/StopReason
            if response and response.text and response.candidates[0].finish_reason == 1:
                 return "🤖: " + response.text.strip()
            else:
                # Se a IA não gerar texto ou for bloqueada, retorna o fallback
                print(f"🤖 (AI Fallback): AI did not return text or was blocked. Response: {response}")
                return "🤖: " + fallback_text

        except Exception as e:
            # Em caso de qualquer erro na API, retorna o fallback
            print(f"🤖 (AI Error): Erro na chamada da API: {e}")
            return "🤖: " + fallback_text
    else:
        # Se o modelo não foi inicializado (sem chave, etc.), retorna o fallback diretamente
        return "🤖: " + fallback_text

# --- Lógica Principal Simplificada com Múltiplos Usuários E IA ---

def processar_input_simples(input_texto):
    global current_user_id, current_idoso_id

    input_texto_lower = input_texto.strip().lower()

    # --- Comando para Trocar/Logar Usuário ---
    if input_texto_lower.startswith('usar '):
        nome_usuario = input_texto_lower[len('usar '):].strip()
        user_id = user_names_to_ids.get(nome_usuario)

        if user_id and user_id in users:
            current_user_id = user_id
            user_role = users[user_id]['role']

            if user_role == 'idoso':
                current_idoso_id = user_id
                get_idoso_data(current_idoso_id)
                # Usa IA para gerar a mensagem de login para idoso
                prompt = f"Gere uma mensagem amigável e acolhedora para um usuário idoso, confirmando que ele(a) ({get_user_name(current_user_id)}) fez login no assistente Leo e agora está gerenciando os próprios lembretes. Mencione o nome do idoso."
                return generate_response_with_ai(prompt, fallback_text=f"Olá, {get_user_name(current_user_id)}! Você está gerenciando seus próprios lembretes.")

            elif user_role == 'tutor':
                linked_idoso_id = user_links.get(user_id)
                if linked_idoso_id and linked_idoso_id in users:
                    current_idoso_id = linked_idoso_id
                    get_idoso_data(current_idoso_id)
                    # Usa IA para gerar a mensagem de login para tutor
                    prompt = f"Gere uma mensagem amigável e profissional para um cuidador/tutor, confirmando que ele(a) ({get_user_name(current_user_id)}) fez login no assistente Leo e agora está gerenciando os lembretes do idoso {get_user_name(current_idoso_id)}. Mencione o nome do tutor e o nome do idoso."
                    return generate_response_with_ai(prompt, fallback_text=f"Olá, {get_user_name(current_user_id)}! Você está gerenciando os lembretes de {get_user_name(current_idoso_id)}.")

                else:
                    current_user_id = None
                    current_idoso_id = None
                    return ("🤖: Usuário é um tutor, mas não está ligado a um idoso válido nesta demo. "
                            "Tente `usar [nome]` novamente com um tutor válido.")
        else:
            return ("🤖: Usuário não encontrado. 😕\n"
                    "Tente um dos nomes disponíveis: " + ", ".join([u['name'] for u in users.values()]) + ".")

    # --- Forçar login se não estiver autenticado ---
    if current_user_id is None:
        return ("🤖: Por favor, diga quem você é para começar a gerenciar lembretes.\n"
                "Digite `usar [nome]` (Ex: `usar Dona Maria` ou `usar João`).")

    # --- Comandos que requerem um idoso selecionado ---
    dados_idoso = get_idoso_data(current_idoso_id)

    if input_texto_lower == 'sair':
        # Usa IA para gerar mensagem de despedida
        prompt = f"Gere uma mensagem de despedida amigável e prestativa para o final de uma conversa com um assistente de lembretes chamado Leo (português do Brasil). Mencione que ele (o usuário) pode voltar a qualquer hora."
        return generate_response_with_ai(prompt, fallback_text="Ok, encerrando. Até mais! 👋")

    elif input_texto_lower == 'ajuda':
         # Usa IA para gerar a introdução da ajuda
         intro_prompt = f"Gere uma introdução amigável e prestativa para a mensagem de ajuda de um assistente de lembretes chamado Leo que ajuda idosos e cuidadores (português do Brasil). Mencione que você (Leo) está gerenciando lembretes para {get_user_name(current_idoso_id)}."
         intro_text = generate_response_with_ai(intro_prompt, fallback_text=f"Olá, sou Leo (Demo Simples). Estou gerenciando lembretes para {get_user_name(current_idoso_id)}.")

         # Hardcode a lista de comandos e formatos (IA não deve inventar comandos)
         help_commands = (
             "\nUse os formatos exatos:\n\n"
             "📅 Para agendar compromisso:\n"
             "`agendar [Descrição] dia DD/MM HH:MM`\n"
             "Ex: `agendar Consulta Oftalmologista dia 10/08 11:00`\n\n"
             "💊 Para medicação:\n"
             "`medicação [Nome]; [Dosagem]; [Frequência]; HH:MM`\n"
             "Ex: `medicação Remédio X; 1 pílula; 12 em 12 horas; 07:00`\n\n"
             "✅ Outros comandos:\n"
             "- `ver`: Mostrar lembretes salvos para este usuário nesta sessão.\n"
             "- `usar [nome]`: Trocar para gerenciar lembretes de outro usuário (Ex: `usar João`).\n"
             "- `sair`: Encerrar.\n"
             "- `ajuda`: Mostrar esta mensagem.\n"
             "\n⚠️ Lembretes são perdidos ao fechar o chat. Notificações são simuladas e respostas são geradas por IA (se configurado)."
         )
         return intro_text + help_commands # Combina a intro da IA com os comandos fixos

    elif input_texto_lower == 'ver':
        return formatar_lista_completa_simples(dados_idoso) # Esta função já formata com base nos dados

    elif input_texto_lower.startswith('agendar '):
        descricao, data_hora = parse_simple_appointment(input_texto)
        if descricao and data_hora:
            users_to_notify = get_users_to_notify(current_idoso_id, current_user_id)
            dados_idoso['appointments'].append({
                'id': str(uuid.uuid4()),
                'descricao': descricao,
                'data_hora': data_hora,
                'criado_em': datetime.datetime.now(),
                'agendado_por': current_user_id,
                'notified_users': users_to_notify
            })
            data_fmt = data_hora.strftime('%d/%m/%Y')
            hora_fmt = data_hora.strftime('%H:%M')
            notified_names = [get_user_name(uid) for uid in users_to_notify]

            # Usa IA para gerar a mensagem de confirmação de agendamento
            prompt = (
                f"Gere uma mensagem de confirmação amigável e clara em português do Brasil para um agendamento salvo. "
                f"Os detalhes são: '{descricao}', na data {data_fmt}, às {hora_fmt}. O agendamento é para o usuário {get_user_name(current_idoso_id)}. "
                f"Mencione que os usuários {', '.join(notified_names)} seriam notificados (simuladamente). O usuário que está interagindo é {get_user_name(current_user_id)} ({users[current_user_id]['role']}). Adapte a linguagem ao perfil."
            )
            return generate_response_with_ai(prompt, fallback_text=f"Pronto! ✅ Lembrete para '{descricao}' agendado para {data_fmt} às {hora_fmt} para {get_user_name(current_idoso_id)}. Usuários a serem notificados: {', '.join(notified_names)}.")

        else:
            # Mantém a mensagem de erro de parsing fixa, pois precisa ser específica sobre o formato
            return ("🤖: Desculpe, não entendi o formato para agendar compromisso. 🤔\n"
                    "Use o formato exato: `agendar [Descrição] dia DD/MM HH:MM`\n"
                    "Ex: `agendar Exame de Sangue dia 05/07 08:30`")

    elif input_texto_lower.startswith('medicação '):
         nome, dosagem, frequencia_str, primeira_hora = parse_simple_medication(input_texto)
         if nome and dosagem and frequencia_str and primeira_hora:
            users_to_notify = get_users_to_notify(current_idoso_id, current_user_id)
            dados_idoso['medications'].append({
                'id': str(uuid.uuid4()),
                'nome': nome,
                'dosagem': dosagem,
                'frequencia': frequencia_str,
                'primeira_hora': primeira_hora,
                'criado_em': datetime.datetime.now(),
                'cadastrado_por': current_user_id,
                'notified_users': users_to_notify
            })
            primeira_hora_fmt = primeira_hora.strftime('%H:%M')
            notified_names = [get_user_name(uid) for uid in users_to_notify]

            # Usa IA para gerar a mensagem de confirmação de medicação
            prompt = (
                f"Gere uma mensagem de confirmação amigável e clara em português do Brasil para um lembrete de medicação salvo. "
                f"Detalhes: '{nome}' ({dosagem}), Frequência: {frequencia_str}, Primeira dose hoje às: {primeira_hora_fmt}. O lembrete é para o usuário {get_user_name(current_idoso_id)}. "
                f"Mencione que os usuários {', '.join(notified_names)} seriam notificados (simuladamente). O usuário que está interagindo é {get_user_name(current_user_id)} ({users[current_user_id]['role']}). Adapte a linguagem ao perfil."
            )
            return generate_response_with_ai(prompt, fallback_text=(f"Pronto! ✅ Lembrete para '{nome}' ({dosagem}) {frequencia_str}, "
                    f"primeira dose hoje às {primeira_hora_fmt} salvo para {get_user_name(current_idoso_id)}. "
                    f"Usuários a serem notificados: {', '.join(notified_names)}."))

         else:
            # Mantém a mensagem de erro de parsing fixa
            return ("🤖: Desculpe, não entendi o formato para medicação. 🤔\n"
                    "Use o formato exato: `medicação [Nome]; [Dosagem]; [Frequência]; HH:MM`\n"
                    "Ex: `medicação Vitamina D; 1 gota; 1 vez ao dia; 10:00`")

    else:
        # Usa IA para gerar a resposta de "não entendi"
        prompt = (
            f"Gere uma resposta curta e amigável em português do Brasil para o usuário de um assistente de lembretes chamado Leo, "
            f"indicando que você (Leo) não entendeu a última mensagem e sugerindo que ele digite 'ajuda'."
        )
        return generate_response_with_ai(prompt, fallback_text="🤖: Desculpe, não entendi o que você quis dizer. 😕 Digite `ajuda` para ver os comandos.")


# --- Função Principal para Executar no Terminal (Adaptada para Colab) ---

def run_terminal_chatbot_multiusuario_ai():
    """Loop principal para rodar o chatbot multiusuário com IA no terminal (ou Colab)."""
    print("="*70)
    print(" Bem-vindo ao Leo: O Lembrete Amigo (Demo Multi-Usuário c/ IA) ")
    print("="*70)
    print("Nesta demo, simule interações como Idoso ou Tutor.")
    print("Usuários disponíveis: " + ", ".join([f"{u['name']} ({u['role']})" for u in users.values()]))
    print("\n⚠️ Para começar, diga quem você é. Digite `usar [nome]` (Ex: `usar Dona Maria`).")
    print("\n⚠️ Lembretes são temporários, notificações são simuladas e algumas respostas são geradas por IA (se a chave estiver configurada).")

    # Mensagem inicial (pode ser gerada pela IA, mas fixa para simplicidade inicial ao rodar)
    print("🤖: Olá! Sou Leo. Diga 'usar [seu nome]' para começar.")


    while True:
        try:
            # Usa input() para simular a interação no terminal ou célula Colab
            user_input = input("Você: ")

            if user_input.strip().lower() == 'sair':
                # A resposta de sair é gerada na função processar_input_simples
                print(processar_input_simples(user_input))
                break

            # Processa o input e obtém a resposta (que já inclui "🤖: ")
            response = processar_input_simples(user_input)

            # Imprime a resposta
            print(response)

        except EOFError:
            print("\n🤖: Entrada interrompida. Encerrando.")
            break
        except Exception as e:
            print(f"🤖: Ocorreu um erro inesperado: {e}")
            print("🤖: Desculpe, algo deu errado. Por favor, comece novamente digitando 'usar [nome]'.")
            global current_user_id, current_idoso_id
            current_user_id = None
            current_idoso_id = None


# --- Executar o Chatbot ---
if __name__ == "__main__":
    # --- Instruções Adicionais para Colab/Usuário ---
    # No Google Colab:
    # 1. Execute a célula '!pip install google-generativeai' (se não fez).
    # 2. Salve sua API Key nos 'Secrets' (ícone de chave na barra lateral) com o nome 'GOOGLE_API_KEY'.
    # 3. Execute a primeira célula do código (import os, userdata...).
    # 4. Execute a célula principal (run_terminal_chatbot_multiusuario_ai()).
    #
    # Fora do Colab:
    # 1. Instale a biblioteca: pip install google-generativeai
    # 2. Obtenha a API Key: https://aistudio.google.com/ ou Google Cloud.
    # 3. Configure a API Key como variável de ambiente antes de executar o script.
    #    No Linux/macOS: export GOOGLE_API_KEY='SUA_CHAVE_AQUI'
    #    No Windows (cmd): set GOOGLE_API_KEY=SUA_CHAVE_AQUI
    #    No Windows (PowerShell): $env:GOOGLE_API_KEY='SUA_CHAVE_AQUI'
    # 4. Execute o script: python seu_arquivo.py

    run_terminal_chatbot_multiusuario_ai()
