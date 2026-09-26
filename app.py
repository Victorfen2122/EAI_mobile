import os
from flask import Flask, render_template_string, request, jsonify
from google import genai

app = Flask(__name__)

# Lee la clave desde la variable de entorno
API_KEY = os.environ.get("GEMINI_API_KEY")
client = genai.Client(api_key=API_KEY) if API_KEY else None

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, user-scalable=no">
    <title>EdgarAI</title>
    <style>
        body { font-family: sans-serif; background-color: #1a1a1a; color: white; margin: 0; display: flex; flex-direction: column; height: 100vh; }
        header { background-color: #2b2b2b; padding: 15px; text-align: center; font-weight: bold; font-size: 1.2rem; }
        #chat { flex: 1; overflow-y: auto; padding: 15px; display: flex; flex-direction: column; gap: 10px; }
        .msg { padding: 10px 14px; border-radius: 12px; max-width: 80%; line-height: 1.4; word-wrap: break-word; }
        .user { background-color: #1f538d; align-self: flex-end; }
        .bot { background-color: #333; align-self: flex-start; }
        #input-area { display: flex; padding: 10px; background-color: #2b2b2b; }
        input { flex: 1; padding: 12px; border: none; border-radius: 8px; background-color: #1a1a1a; color: white; outline: none; font-size: 16px; }
        button { margin-left: 8px; padding: 12px 18px; border: none; border-radius: 8px; background-color: #1f538d; color: white; font-weight: bold; }
    </style>
</head>
<body>
    <header>🤖 EdgarAI</header>
    <div id="chat"></div>
    <div id="input-area">
        <input type="text" id="msg" placeholder="Escribe un mensaje..." onkeypress="if(event.key==='Enter') enviar()">
        <button onclick="enviar()">Enviar</button>
    </div>

    <script>
        async function enviar() {
            let input = document.getElementById("msg");
            let texto = input.value.trim();
            if (!texto) return;

            let chat = document.getElementById("chat");
            chat.innerHTML += `<div class="msg user">${texto}</div>`;
            input.value = "";
            chat.scrollTop = chat.scrollHeight;

            try {
                let res = await fetch("/api/chat", {
                    method: "POST",
                    headers: {"Content-Type": "application/json"},
                    body: JSON.stringify({ mensaje: texto })
                });
                let data = await res.json();
                chat.innerHTML += `<div class="msg bot">${data.respuesta}</div>`;
            } catch (e) {
                chat.innerHTML += `<div class="msg bot">Error de conexión con EdgarAI</div>`;
            }
            chat.scrollTop = chat.scrollHeight;
        }
    </script>
</body>
</html>
"""

@app.route("/")
def home():
    return render_template_string(HTML_TEMPLATE)

@app.route("/api/chat", methods=["POST"])
def api_chat():
    if not client:
        return jsonify({"respuesta": "Error: GEMINI_API_KEY no está configurada en las variables de entorno."})
    
    data = request.get_json()
    mensaje = data.get("mensaje", "")
    try:
        chat = client.chats.create(model="gemini-3.5-flash-lite")
        response = chat.send_message(mensaje)
        return jsonify({"respuesta": response.text})
    except Exception as e:
        return jsonify({"respuesta": f"Error: {e}"})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)