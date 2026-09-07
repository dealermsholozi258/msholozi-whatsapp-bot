import os
import requests
from flask import Flask, request, jsonify

app = Flask(__name__)

VERIFY_TOKEN = os.environ.get("VERIFY_TOKEN", "")
ACCESS_TOKEN = os.environ.get("WHATSAPP_TOKEN", "")
PHONE_NUMBER_ID = os.environ.get("PHONE_NUMBER_ID", "1292096300643433")

@app.route("/", methods=["GET"])
def home():
    return "Servidor do Bot WhatsApp Ativo!", 200

@app.route("/webhook", methods=["GET", "POST", "HEAD"])
def webhook():
    if request.method == "HEAD":
        return "", 200

    if request.method == "GET":
        mode = request.args.get("hub.mode")
        token = request.args.get("hub.verify_token")
        challenge = request.args.get("hub.challenge")

        if mode and token:
            if mode == "subscribe" and token == VERIFY_TOKEN:
                print("WEBHOOK VERIFICADO COM SUCESSO!")
                return challenge, 200
            else:
                return "Token de verificação inválido", 403
        return "Servidor Webhook Ativo", 200

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
                msg_body = message.get("text", {}).get("body", "").strip().lower()

                print(f"Mensagem de {from_number}: {msg_body}")

                if msg_body in ["1", "menu", "olá", "ola"]:
                    resposta = (
                        "👋 *Bem-vindo à Loja de Pacotes de MB!*\n\n"
                        "Escolha uma das opções enviando o número:\n"
                        "1 - Ver Tabela de Preços de MB\n"
                        "2 - Como Fazer o Pagamento\n"
                        "3 - Falar com Atendente"
                    )
                elif msg_body == "2":
                    resposta = (
                        "💳 *DADOS PARA PAGAMENTO*\n\n"
                        "Envie o valor do pacote pretendido para:\n"
                        "📱 *M-Pesa / e-Mola:* 84XXXXXXX / 86XXXXXXX\n"
                        "Após realizar a transferência, envie o comprovativo aqui!"
                    )
                elif msg_body == "3":
                    resposta = "👤 Um atendente entrará em contacto em breve."
                else:
                    resposta = "🤖 Digite *menu* ou *1* para ver os pacotes de MB disponíveis."

                enviar_mensagem_whatsapp(from_number, resposta)

        except Exception as e:
            print(f"Erro ao processar mensagem: {e}")

        return jsonify({"status": "success"}), 200

def enviar_mensagem_whatsapp(to_number, text):
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

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
