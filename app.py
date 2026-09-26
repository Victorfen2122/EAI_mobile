import os
from flask import Flask, render_template_string, request, jsonify
from google import genai

app = Flask(__name__)

API_KEY = os.environ.get("GEMINI_API_KEY")
client = genai.Client(api_key=API_KEY) if API_KEY else None

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no, viewport-fit=cover">
    <title>EdgarAI Mobile</title>
    <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <script src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"></script>

    <style>
        :root {
            --bg-body: #0b0f17;
            --bg-header: rgba(18, 24, 38, 0.9);
            --bg-card-bot: #161e2e;
            --bg-input: #1a2333;
            --primary: #3b82f6;
            --primary-grad: linear-gradient(135deg, #3b82f6, #1d4ed8);
            --text: #f3f4f6;
            --text-muted: #9ca3af;
            --border: rgba(255, 255, 255, 0.08);
        }

        * {
            box-sizing: border-box;
            margin: 0;
            padding: 0;
            font-family: 'Plus Jakarta Sans', sans-serif;
            -webkit-tap-highlight-color: transparent;
        }

        body {
            background-color: var(--bg-body);
            color: var(--text);
            display: flex;
            flex-direction: column;
            height: 100vh;
            height: 100dvh;
            overflow: hidden;
        }

        /* Header Móvil estilo App */
        header {
            background: var(--bg-header);
            backdrop-filter: blur(12px);
            border-bottom: 1px solid var(--border);
            padding: 12px 16px;
            padding-top: max(12px, env(safe-area-inset-top));
            display: flex;
            align-items: center;
            justify-content: space-between;
            z-index: 10;
            flex-shrink: 0;
        }

        .header-brand {
            display: flex;
            align-items: center;
            gap: 10px;
        }

        .header-avatar {
            width: 36px;
            height: 36px;
            background: linear-gradient(135deg, #3b82f6, #8b5cf6);
            border-radius: 10px;
            display: flex;
            align-items: center;
            justify-content: center;
            color: #fff;
            font-size: 1rem;
            box-shadow: 0 4px 12px rgba(59, 130, 246, 0.3);
        }

        .header-info {
            display: flex;
            flex-direction: column;
        }

        .header-title {
            font-weight: 700;
            font-size: 1rem;
            color: #fff;
        }

        .header-status {
            display: flex;
            align-items: center;
            gap: 5px;
            font-size: 0.72rem;
            color: #10b981;
        }

        .status-dot {
            width: 6px;
            height: 6px;
            background: #10b981;
            border-radius: 50%;
            box-shadow: 0 0 6px #10b981;
        }

        .btn-reset {
            background: rgba(255, 255, 255, 0.05);
            border: 1px solid var(--border);
            color: var(--text-muted);
            width: 36px;
            height: 36px;
            border-radius: 10px;
            display: flex;
            align-items: center;
            justify-content: center;
            cursor: pointer;
            transition: all 0.2s ease;
        }

        .btn-reset:active {
            transform: scale(0.9);
            background: rgba(255, 255, 255, 0.1);
        }

        /* Área de Chat Móvil */
        #chat {
            flex: 1;
            overflow-y: auto;
            padding: 16px;
            display: flex;
            flex-direction: column;
            gap: 14px;
            scroll-behavior: smooth;
        }

        .msg {
            max-width: 88%;
            padding: 12px 16px;
            border-radius: 18px;
            font-size: 0.95rem;
            line-height: 1.5;
            word-break: break-word;
            animation: popIn 0.2s cubic-bezier(0.175, 0.885, 0.32, 1.275);
        }

        @keyframes popIn {
            from { opacity: 0; transform: scale(0.95) translateY(10px); }
            to { opacity: 1; transform: scale(1) translateY(0); }
        }

        .user {
            align-self: flex-end;
            background: var(--primary-grad);
            color: #ffffff;
            border-bottom-right-radius: 4px;
            box-shadow: 0 4px 12px rgba(37, 99, 235, 0.3);
        }

        .bot {
            align-self: flex-start;
            background: var(--bg-card-bot);
            color: var(--text);
            border-bottom-left-radius: 4px;
            border: 1px solid var(--border);
        }

        .bot p { margin-bottom: 8px; }
        .bot p:last-child { margin-bottom: 0; }
        .bot code { background: rgba(0,0,0,0.4); padding: 2px 5px; border-radius: 4px; font-family: monospace; }

        /* Typing Indicator */
        .typing {
            display: none;
            align-self: flex-start;
            background: var(--bg-card-bot);
            border: 1px solid var(--border);
            padding: 12px 16px;
            border-radius: 18px;
            border-bottom-left-radius: 4px;
            gap: 5px;
            align-items: center;
        }

        .typing span {
            width: 7px;
            height: 7px;
            background-color: var(--text-muted);
            border-radius: 50%;
            animation: blink 1.4s infinite ease-in-out both;
        }

        .typing span:nth-child(1) { animation-delay: -0.32s; }
        .typing span:nth-child(2) { animation-delay: -0.16s; }

        @keyframes blink {
            0%, 80%, 100% { transform: scale(0.4); opacity: 0.4; }
            40% { transform: scale(1); opacity: 1; }
        }

        /* Barra de Entrada de Texto */
        .input-bar {
            background: var(--bg-header);
            border-top: 1px solid var(--border);
            padding: 10px 12px;
            padding-bottom: max(10px, env(safe-area-inset-bottom));
            display: flex;
            align-items: center;
            gap: 10px;
            flex-shrink: 0;
        }

        .input-container {
            flex: 1;
            background: var(--bg-input);
            border: 1px solid var(--border);
            border-radius: 22px;
            padding: 2px 6px 2px 16px;
            display: flex;
            align-items: center;
        }

        .input-container:focus-within {
            border-color: var(--primary);
        }

        input {
            flex: 1;
            background: transparent;
            border: none;
            outline: none;
            color: #fff;
            font-size: 0.95rem;
            padding: 10px 0;
        }

        input::placeholder {
            color: var(--text-muted);
        }

        .btn-send {
            width: 40px;
            height: 40px;
            background: var(--primary-grad);
            border: none;
            border-radius: 50%;
            color: white;
            display: flex;
            align-items: center;
            justify-content: center;
            cursor: pointer;
            transition: transform 0.15s ease;
            flex-shrink: 0;
            box-shadow: 0 4px 10px rgba(59, 130, 246, 0.3);
        }

        .btn-send:active {
            transform: scale(0.9);
        }

        .btn-send i {
            font-size: 0.95rem;
            margin-left: 2px;
        }
    </style>
</head>
<body>

    <header>
        <div class="header-brand">
            <div class="header-avatar">
                <i class="fa-solid fa-robot"></i>
            </div>
            <div class="header-info">
                <span class="header-title">EdgarAI</span>
                <span class="header-status">
                    <div class="status-dot"></div> En línea
                </span>
            </div>
        </div>
        <button class="btn-reset" onclick="limpiarChat()" title="Nuevo Chat">
            <i class="fa-solid fa-rotate-right"></i>
        </button>
    </header>

    <div id="chat">
        <div class="msg bot">
            ¡Hola! Soy <b>EdgarAI</b>. ¿En qué te ayudo hoy?
        </div>
    </div>

    <div style="padding-left: 16px; margin-bottom: 6px;">
        <div class="typing" id="typing">
            <span></span>
            <span></span>
            <span></span>
        </div>
    </div>

    <div class="input-bar">
        <div class="input-container">
            <input type="text" id="msg" placeholder="Escribe un mensaje..." autocomplete="off" onkeypress="if(event.key==='Enter') enviar()">
        </div>
        <button class="btn-send" onclick="enviar()">
            <i class="fa-solid fa-paper-plane"></i>
        </button>
    </div>

    <script>
        async function enviar() {
            let input = document.getElementById("msg");
            let texto = input.value.trim();
            if (!texto) return;

            let chat = document.getElementById("chat");
            let typing = document.getElementById("typing");

            // Añadir mensaje del usuario
            chat.innerHTML += `<div class="msg user">${escapeHTML(texto)}</div>`;
            input.value = "";
            chat.scrollTop = chat.scrollHeight;

            // Mostrar animación de escritura
            typing.style.display = "flex";
            chat.scrollTop = chat.scrollHeight;

            try {
                let res = await fetch("/api/chat", {
                    method: "POST",
                    headers: {"Content-Type": "application/json"},
                    body: JSON.stringify({ mensaje: texto })
                });
                let data = await res.json();
                
                typing.style.display = "none";
                
                let htmlRespuesta = marked.parse(data.respuesta);
                chat.innerHTML += `<div class="msg bot">${htmlRespuesta}</div>`;
            } catch (e) {
                typing.style.display = "none";
                chat.innerHTML += `<div class="msg bot">⚠️ Error de conexión con EdgarAI.</div>`;
            }
            chat.scrollTop = chat.scrollHeight;
        }

        function limpiarChat() {
            document.getElementById("chat").innerHTML = `
                <div class="msg bot">
                    Chat reiniciado. ¡Hola! ¿En qué te puedo colaborar?
                </div>`;
        }

        function escapeHTML(str) {
            return str.replace(/[&<>'"]/g, 
                tag => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', "'": '&#39;', '"': '&quot;' }[tag] || tag)
            );
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