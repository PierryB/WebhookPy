from flask import Flask, request
import requests
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.config['JSONIFY_PRETTYPRINT_REGULAR'] = False

INSTANCE = os.getenv("INSTANCE_NAME")
API_KEY = os.getenv("API_KEY")
BASE_URL = f"{os.getenv('EVOLUTION_URL')}/message/sendText"
PORT = int(os.getenv("PORT", 3010))

@app.route('/messages-upsert', methods=['POST'])
def messages_upsert():
    data = request.json.get('data', {})
    key = data.get('key', {})

    # Ignora se a mensagem foi enviada por ele mesmo
    is_from_me = key.get('fromMe') is True
    if is_from_me:
        print("🚫 Ignorando mensagem enviada por mim mesmo")
        return '', 200

    # Ignora mensagens de grupo
    remote_jid = key.get('remoteJid', '')
    is_group = remote_jid.endswith('@g.us')
    if is_group:
        print("👥 Ignorando mensagem de grupo")
        return '', 200

    # Remover após testes
    print("🚫 Ignorando mensagem, testes...")
    return '', 200

    # Detecta número do remetente
    sender = key.get('participant') or key.get('remoteJid') or request.json.get('sender')
    if not sender:
        print("❌ Não foi possível identificar o número do remetente.")
        return '', 400

    sender = sender.split('@')[0]
    message = data.get('message', {}).get('conversation')

    if not message or not isinstance(message, str):
        print(f"🚫 Ignorando mensagem não textual de {sender}")
        return '', 200

    print(f"📩 Mensagem recebida de {sender}: {message}")

    try:
        response = requests.post(
            f"{BASE_URL}/{INSTANCE}",
            json={
                "number": sender,
                "text": f"Você disse: {message}"
            },
            headers={
                "Content-Type": "application/json",
                "apikey": API_KEY
            }
        )
        response.raise_for_status()
        print(f"✅ Resposta enviada para {sender}")
        return '', 200
    except Exception as e:
        print(f"❌ Erro ao responder: {str(e)}")
        return '', 500

if __name__ == '__main__':
    app.run(port=PORT)
