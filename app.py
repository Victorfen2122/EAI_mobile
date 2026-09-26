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
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>EdgarAI</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&display=swap" rel="stylesheet">
    <style>
        * {
            box-sizing: border-box;
            margin: 0;
            padding: 0;
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
            -webkit-tap-highlight-color: transparent;
        }

        body {
            background-color: #0f172a;
            color: #f8fafc;
            display: flex;
            flex-direction: column;
            height: 100vh;
            height: 100dvh; /* Adaptable a barras de navegadores móviles */
            overflow: hidden;
        }

        /* Encabezado */
        header {
            background: rgba(30, 41, 59, 0.8);
            backdrop-filter: blur(12px);
            border-bottom: 1px solid rgba(255, 255, 255, 0.08);
            padding: 14px 20px;
            display: flex;
            align-items: center;
            justify-content: space-between;
            position: sticky;
            top: 0;
            z-index: 10;
        }

        .brand {
            display: flex;
            align-items: center;
            gap: 10px;
            font-weight: 600;
            font-size: 1.1rem;
            letter-spacing: -0.3px;
        }

        .avatar {
            width: 34px;
            height: 34px;
            background: linear-gradient(135deg, #3b82f6, #8b5cf6);
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 1.1rem;
            box-shadow: 0 2px 10px rgba(59, 130, 246, 0.3);
        }

        .status-badge {
            display: flex;
            align-items: center;
            gap: 6px;
            font-size: 0.75rem;
            color: #94a3b8;
        }

        .status-dot {
            width: 8px;
            height: 8px;
            background-color: #10b981;
            border-radius: 50%;
            box-shadow: 0 0 8px #10b981;
        }

        /* Área de Chat */
        #chat {
            flex: 1;
            overflow-y: auto;
            padding: 20px;
            display: flex;
            flex-direction: column;
            gap: 16px;
            scroll-behavior: smooth;
        }

        .msg {
            max-width: 85%;
            padding: 12px 16px;
            border-radius: 18px;
            font-size: 0.95rem;
            line-height: 1.5;
            word-break: break-word;
            animation: fadeIn 0.25s ease-out forwards;
        }

        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(8px); }
            to { opacity: 1; transform: translateY(0); }
        }

        .user {
            align-self: flex-end;
            background: linear-gradient(135deg, #2563eb, #1d4ed8);
            color: #ffffff;
            border-bottom-right-radius: 4px;
            box-shadow: 0 4px 12px rgba(37, 99, 235, 0.25);
        }

        .bot {
            align-self: flex-start;
            background-color: #1e293b;
            color: #e2e8f0;
            border-bottom-left-radius: 4px;
            border: 1px solid rgba(255, 255, 255, 0.05);
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
        }

        /* Indicador de escritura (Typing) */
        .typing {
            display: none;
            align-self: flex-start;
            background-color: #1e293b;
            padding: 12px 16px;
            border-radius: 18px;
            border-bottom-left-radius: 4px;
            gap: 5px;
        }

        .typing span {
            width: 6px;
            height: 6px;
            background-color: #64748b;
            border-radius: 50%;
            animation: pulse 1.4s infinite ease-in-out both;
        }

        .typing span:nth-child(1) { animation-delay: -0.32s; }
        .typing span:nth-child(2) { animation-delay: -0.16s; }

        @keyframes pulse {
            0%, 80%, 100% { transform: scale(0); }
            40% { transform: scale(1); }
        }

        /* Campo de Entrada de Texto */
        #input-container {
            padding: 12px 16px;
            background: #0f172a;
            border-top: 1px solid rgba(255, 255, 255, 0.08);
        }

        #input-area {
            display: flex;
            align-items: center;
            background-color: #1e293b;
            border-radius: 24px;
            padding: 4px 6px 4px 16px;
            border: 1px solid rgba(255, 255, 255, 0.08);
            transition: border-color 0.2s ease;
        }

        #input-area:focus-within {
            border-color: #3b82f6;
        }

        input {
            flex: 1;
            border: none;
            outline: none;
            background: transparent;
            color: #f8fafc;
            font-size: 0.95rem;
            padding: 10px 0;
        }

        input::placeholder {
            color: #64748b;
        }

        button {
            width: 40px;
            height: 40px;
            border: none;
            border-radius: 50%;
            background: linear-gradient(135deg, #3b82f6, #2563eb);
            color: white;
            display: flex;
            align-items: center;
            justify-content: center;
            cursor: pointer;
            transition: transform 0.15s ease, background 0.2s ease;
            flex-shrink: 0;
        }

        button:active {
            transform: scale(0.92);
        }

        button svg {
            width: 18px;
            height: 18px;
            fill: currentColor;
            margin-left: 2px;
        }
    </style>
</head>
<body>
    <header>
        <div class="brand">
            <div class="avatar">🤖</div>
            <span>EdgarAI</span>
        </div>
        <div class="status-badge">
            <div class="status-dot"></div>
            <span>En línea</span>
        </div>
    </header>

    <div id="chat">
        <div class="msg bot">¡Hola! Soy <b>EdgarAI</b>. ¿En qué te puedo ayudar hoy?</div>
    </div>

    <div class="typing" id="typing">
        <span></span>
        <span></span>
        <span></span>
    </div>

    <div id="input-container">
        <div id="input-area">
            <input type="text" id="msg" placeholder="Escribe un mensaje..." autocomplete="off" onkeypress="if(event.key==='Enter') enviar()">
            <button onclick="enviar()" aria-label="Enviar">
                <svg viewBox="0 0 24 24">
                    <path d="M2.01 21L23 12 2.01 3 2 10l15 2-15 2z"/>
                </svg>
            </button>
        </div>
    </div>

    <script>
        async function enviar() {
            let input = document.getElementById("msg");
            let texto = input.value.trim();
            if (!texto) return;

            let chat = document.getElementById("chat");
            let typing = document.getElementById("typing");

            // Mensaje del usuario
            chat.innerHTML += `<div class="msg user">${escapeHTML(texto)}</div>`;
            input.value = "";
            chat.scrollTop = chat.scrollHeight;

            // Mostrar indicador de "escribiendo..."
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
                chat.innerHTML += `<div class="msg bot">${formatText(data.respuesta)}</div>`;
            } catch (e) {
                typing.style.display = "none";
                chat.innerHTML += `<div class="msg bot">⚠️ Error de conexión con EdgarAI.</div>`;
            }
            chat.scrollTop = chat.scrollHeight;
        }

        function escapeHTML(str) {
            return str.replace(/[&<>'"]/g, 
                tag => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', "'": '&#39;', '"': '&quot;' }[tag] || tag)
            );
        }

        function formatText(text) {
            // Formato básico para saltos de línea y negritas
            return text
                .replace(/\n/g, "<br>")
                .replace(/\*\*(.*?)\*\*/g, "<b>$1</b>");
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