import os
import requests
from flask import Flask, request, jsonify

app = Flask(__name__)

# Configurações obtidas das variáveis de ambiente no Render
VERIFY_TOKEN = os.environ.get("VERIFY_TOKEN", "SEU_VERIFY_TOKEN")
ACCESS_TOKEN = os.environ.get("WHATSAPP_TOKEN", "SEU_ACCESS_TOKEN")
PHONE_NUMBER_ID = os.environ.get("PHONE_NUMBER_ID", "SEU_PHONE_NUMBER_ID")
GRAPH_API_VERSION = os.environ.get("GRAPH_API_VERSION", "v18.0")

@app.route("/", methods=["GET"])
def home():
    return "Servidor do Bot WhatsApp Ativo!", 200

@app.route("/webhook", methods=["GET", "POST", "HEAD"])
def webhook():
    # 1. Trata requisições do UptimeRobot
    if request.method == "HEAD":
        return "", 200

    # 2. Trata a verificação de Token do Meta Developers
    if request.method == "GET":
        mode = request.args.get("hub.mode")
        token = request.args.get("hub.verify_token")
        challenge = request.args.get("hub.challenge")

        if mode and token:
            if mode == "subscribe" and token == VERIFY_TOKEN:
                print("WEBHOOK VERIFICADO COM SUCESSO PELA META!")
                return challenge, 200
            else:
                return "Token de verificação inválido", 403
        return "Servidor Webhook Ativo", 200

    # 3. Trata mensagens recebidas dos clientes via WhatsApp
    if request.method == "POST":
        data = request.get_json()
        print("Payload recebido:", data)

        try:
            entry = data.get("entry", [])[0]
            changes = entry.get("changes", [])[0]
            value = changes.get("value", {})
            messages = value.get("messages", [])

            if messages:
                message = messages[0]
                from_number = message["from"]
                
                # Obtém o texto enviado pelo cliente (se for mensagem de texto)
                msg_body = message.get("text", {}).get("body", "").strip().lower()

                print(f"Mensagem de {from_number}: {msg_body}")

                # Lógica do Menu de Pacotes de MB
                if msg_body in ["1", "menu", "olá", "ola", "boa noite", "bom dia", "boa tarde"]:
                    resposta = (
                        "👋 *Bem-vindo à Loja de Pacotes de MB!*\n\n"
                        "Escolha uma das opções abaixo enviando o número:\n"
                        "1️⃣ - Ver Tabela de Preços de MB\n"
                        "2️⃣ - Como Fazer o Pagamento\n"
                        "3️⃣ - Falar com Atendente\n"
                    )
                elif msg_body == "1":
                    resposta = (
                        "📶 *TABELA DE PACOTES DE MB*\n\n"
                        "🔹 500 MB -> XX MT\n"
                        "🔹 1 GB (1024 MB) -> XX MT\n"
                        "🔹 2 GB -> XX MT\n"
                        "🔹 5 GB -> XX MT\n\n"
                        "Para comprar, envie o comprovativo ou digite a opção *2* para dados de pagamento."
                    )
                elif msg_body == "2":
                    resposta = (
                        "💳 *DADOS PARA PAGAMENTO*\n\n"
                        "Envie o valor do pacote pretendido para:\n"
                        "📱 *M-Pesa / e-Mola:* 84XXXXXXX / 86XXXXXXX\n"
                        "👤 *Nome:* [Seu Nome]\n\n"
                        "Após realizar a transferência, envie o *comprovativo* aqui no chat!"
                    )
                elif msg_body == "3":
                    resposta = "👤 Um atendente entrará em contacto em breve. Por favor, aguarde alguns instantes."
                else:
                    resposta = (
                        "🤖 Opção não reconhecida.\n\n"
                        "Digite *1* ou *menu* para ver os nossos pacotes de MB disponíveis."
                    )

                def enviar_mensagem_whatsapp(to_number, text):
    """Envia mensagem usando a versão v18.0 fixada"""
    url = f"https://graph.facebook.com/v18.0/{PHONE_NUMBER_ID}/messages"
    
    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "messaging_product": "whatsapp",
        "to": to_number,
        "type": "text",
        "text": {"body": text}
    }

    try:
        res = requests.post(url, json=payload, headers=headers)
        print(f"RESPOSTA DA META ({res.status_code}): {res.text}")
    except Exception as e:
        print(f"ERRO DE CONEXÃO: {e}")
