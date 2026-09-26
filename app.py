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
    <title>EdgarAI</title>
    <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.7.0/styles/atom-one-dark.min.css">
    <script src="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.7.0/highlight.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"></script>

    <style>
        :root {
            --bg-body: #090d16;
            --bg-sidebar: #111827;
            --bg-card: #1f2937;
            --bg-hover: rgba(255, 255, 255, 0.08);
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
            height: 100vh;
            height: 100dvh;
            overflow: hidden;
        }

        /* Overlay para móvil cuando el menú está abierto */
        .sidebar-overlay {
            display: none;
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: rgba(0, 0, 0, 0.6);
            backdrop-filter: blur(4px);
            z-index: 99;
        }

        /* Sidebar (Historial) */
        .sidebar {
            width: 280px;
            background-color: var(--bg-sidebar);
            border-right: 1px solid var(--border);
            display: flex;
            flex-direction: column;
            padding: 16px;
            gap: 16px;
            flex-shrink: 0;
            z-index: 100;
            transition: transform 0.3s ease;
        }

        .brand {
            display: flex;
            align-items: center;
            gap: 12px;
            font-size: 1.1rem;
            font-weight: 700;
            color: #fff;
        }

        .brand-icon {
            width: 36px;
            height: 36px;
            background: var(--primary-grad);
            border-radius: 10px;
            display: flex;
            align-items: center;
            justify-content: center;
            box-shadow: 0 4px 12px rgba(59, 130, 246, 0.3);
        }

        .btn-new {
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 10px;
            background: rgba(255, 255, 255, 0.05);
            border: 1px solid var(--border);
            color: var(--text);
            padding: 12px 16px;
            border-radius: 12px;
            cursor: pointer;
            font-weight: 500;
            transition: all 0.2s ease;
        }

        .btn-new:hover {
            background: rgba(255, 255, 255, 0.1);
            border-color: var(--primary);
        }

        /* Lista del Historial */
        .history-section {
            flex: 1;
            overflow-y: auto;
            display: flex;
            flex-direction: column;
            gap: 6px;
        }

        .history-title {
            font-size: 0.75rem;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            color: var(--text-muted);
            margin: 8px 4px;
            font-weight: 600;
        }

        .history-item {
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding: 10px 12px;
            border-radius: 8px;
            cursor: pointer;
            font-size: 0.88rem;
            color: var(--text-muted);
            transition: all 0.2s;
            gap: 8px;
        }

        .history-item:hover, .history-item.active {
            background: var(--bg-hover);
            color: #fff;
        }

        .history-item span {
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
            flex: 1;
        }

        .history-item .btn-delete {
            opacity: 0;
            color: var(--text-muted);
            padding: 4px;
            border-radius: 4px;
            transition: opacity 0.2s, color 0.2s;
        }

        .history-item:hover .btn-delete {
            opacity: 1;
        }

        .history-item .btn-delete:hover {
            color: #ef4444;
        }

        .sidebar-footer {
            margin-top: auto;
            padding-top: 12px;
            border-top: 1px solid var(--border);
            font-size: 0.8rem;
            color: var(--text-muted);
            display: flex;
            align-items: center;
            gap: 8px;
        }

        .status-dot {
            width: 8px;
            height: 8px;
            background: #10b981;
            border-radius: 50%;
            box-shadow: 0 0 8px #10b981;
        }

        /* Contenedor Principal */
        .main-container {
            flex: 1;
            display: flex;
            flex-direction: column;
            height: 100%;
            position: relative;
        }

        /* Header Móvil */
        .mobile-header {
            display: none;
            background: rgba(17, 24, 39, 0.9);
            backdrop-filter: blur(12px);
            border-bottom: 1px solid var(--border);
            padding: 12px 16px;
            align-items: center;
            justify-content: space-between;
            z-index: 10;
        }

        .mobile-btn {
            background: transparent;
            border: none;
            color: var(--text);
            font-size: 1.2rem;
            cursor: pointer;
            padding: 4px;
        }

        /* Área de Chat */
        #chat {
            flex: 1;
            overflow-y: auto;
            padding: 24px 15%;
            display: flex;
            flex-direction: column;
            gap: 18px;
            scroll-behavior: smooth;
        }

        .msg-wrapper {
            display: flex;
            gap: 12px;
            animation: fadeIn 0.25s ease-out;
        }

        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(8px); }
            to { opacity: 1; transform: translateY(0); }
        }

        .msg-wrapper.user {
            flex-direction: row-reverse;
        }

        .avatar {
            width: 36px;
            height: 36px;
            border-radius: 10px;
            display: flex;
            align-items: center;
            justify-content: center;
            flex-shrink: 0;
            font-size: 0.9rem;
        }

        .user .avatar { background: #2563eb; color: #fff; }
        .bot .avatar { background: #10b981; color: #fff; }

        .msg-content {
            max-width: 80%;
            background-color: var(--bg-card);
            border: 1px solid var(--border);
            padding: 14px 18px;
            border-radius: 16px;
            line-height: 1.6;
            font-size: 0.95rem;
            word-break: break-word;
        }

        .user .msg-content {
            background: var(--primary-grad);
            border: none;
            color: #ffffff;
            border-top-right-radius: 4px;
        }

        .bot .msg-content {
            border-top-left-radius: 4px;
            color: #e5e7eb;
        }

        .msg-content pre {
            background: #0f172a !important;
            padding: 12px;
            border-radius: 8px;
            overflow-x: auto;
            margin: 10px 0;
            border: 1px solid var(--border);
        }

        .msg-content code {
            font-family: monospace;
            background: rgba(0,0,0,0.3);
            padding: 2px 6px;
            border-radius: 4px;
        }

        /* Caja de Entrada */
        .input-wrapper {
            padding: 16px 15% 24px 15%;
            background: linear-gradient(to top, var(--bg-body) 80%, transparent);
        }

        .input-box {
            display: flex;
            align-items: center;
            background: var(--bg-card);
            border: 1px solid var(--border);
            border-radius: 16px;
            padding: 6px 10px 6px 16px;
            box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.3);
            transition: all 0.2s ease;
        }

        .input-box:focus-within {
            border-color: var(--primary);
        }

        input {
            flex: 1;
            background: transparent;
            border: none;
            outline: none;
            color: #fff;
            font-size: 1rem;
            padding: 8px 0;
        }

        input::placeholder { color: var(--text-muted); }

        .btn-send {
            width: 40px;
            height: 40px;
            background: var(--primary-grad);
            border: none;
            border-radius: 12px;
            color: #fff;
            cursor: pointer;
            display: flex;
            align-items: center;
            justify-content: center;
            transition: transform 0.15s ease;
        }

        .btn-send:active { transform: scale(0.92); }

        /* Typing Indicator */
        .typing {
            display: none;
            gap: 6px;
            padding: 12px 18px;
            background: var(--bg-card);
            border-radius: 16px;
            width: fit-content;
            border: 1px solid var(--border);
            margin-left: 15%;
            margin-bottom: 10px;
        }

        .typing span {
            width: 8px;
            height: 8px;
            background: var(--text-muted);
            border-radius: 50%;
            animation: bounce 1.4s infinite ease-in-out both;
        }

        .typing span:nth-child(1) { animation-delay: -0.32s; }
        .typing span:nth-child(2) { animation-delay: -0.16s; }

        @keyframes bounce {
            0%, 80%, 100% { transform: scale(0); }
            40% { transform: scale(1); }
        }

        /* RESPONSIVE MÓVIL (< 768px) */
        @media (max-width: 768px) {
            .sidebar {
                position: fixed;
                top: 0;
                left: 0;
                bottom: 0;
                transform: translateX(-100%);
            }
            .sidebar.open {
                transform: translateX(0);
            }
            .sidebar-overlay.open {
                display: block;
            }
            .mobile-header { display: flex; }
            #chat { padding: 16px 12px; }
            .input-wrapper { padding: 10px 12px max(12px, env(safe-area-inset-bottom)) 12px; }
            .msg-content { max-width: 88%; }
            .typing { margin-left: 12px; }
        }
    </style>
</head>
<body>

    <div class="sidebar-overlay" id="overlay" onclick="toggleSidebar()"></div>

    <!-- Sidebar con Historial -->
    <aside class="sidebar" id="sidebar">
        <div class="brand">
            <div class="brand-icon"><i class="fa-solid fa-robot"></i></div>
            <span>EdgarAI</span>
        </div>

        <button class="btn-new" onclick="nuevoChat()">
            <i class="fa-solid fa-plus"></i>
            <span>Nuevo Chat</span>
        </button>

        <div class="history-title">Historial de chats</div>
        <div class="history-section" id="historyList">
            <!-- Se carga dinámicamente -->
        </div>

        <div class="sidebar-footer">
            <div class="status-dot"></div>
            <span>En línea</span>
        </div>
    </aside>

    <!-- Vista Principal -->
    <main class="main-container">
        <!-- Header Móvil -->
        <div class="mobile-header">
            <button class="mobile-btn" onclick="toggleSidebar()">
                <i class="fa-solid fa-bars"></i>
            </button>
            <div class="brand">
                <div class="brand-icon" style="width:30px; height:30px;"><i class="fa-solid fa-robot" style="font-size:0.8rem;"></i></div>
                <span style="font-size: 1.05rem; font-weight:700;">EdgarAI</span>
            </div>
            <button class="mobile-btn" onclick="nuevoChat()">
                <i class="fa-solid fa-plus"></i>
            </button>
        </div>

        <!-- Mensajes -->
        <div id="chat">
            <div class="msg-wrapper bot">
                <div class="avatar"><i class="fa-solid fa-robot"></i></div>
                <div class="msg-content">
                    ¡Hola! Soy <b>EdgarAI</b>. ¿En qué te ayudo hoy?
                </div>
            </div>
        </div>

        <!-- Indicador de Carga -->
        <div class="typing" id="typing">
            <span></span>
            <span></span>
            <span></span>
        </div>

        <!-- Caja de Entrada -->
        <div class="input-wrapper">
            <div class="input-box">
                <input type="text" id="msg" placeholder="Escribe un mensaje..." autocomplete="off" onkeypress="if(event.key==='Enter') enviar()">
                <button class="btn-send" onclick="enviar()">
                    <i class="fa-solid fa-paper-plane"></i>
                </button>
            </div>
        </div>
    </main>

    <script>
        let currentChatId = null;
        let chats = JSON.parse(localStorage.getItem('edgarai_chats') || '{}');

        window.onload = () => {
            renderHistory();
        };

        function toggleSidebar() {
            document.getElementById('sidebar').classList.toggle('open');
            document.getElementById('overlay').classList.toggle('open');
        }

        function renderHistory() {
            const list = document.getElementById('historyList');
            list.innerHTML = '';
            
            const chatIds = Object.keys(chats).reverse();
            if (chatIds.length === 0) {
                list.innerHTML = '<div style="font-size:0.8rem; color:var(--text-muted); padding:8px;">Sin chats guardados</div>';
                return;
            }

            chatIds.forEach(id => {
                const item = document.createElement('div');
                item.className = `history-item ${id === currentChatId ? 'active' : ''}`;
                item.onclick = () => cargarChat(id);
                
                item.innerHTML = `
                    <i class="fa-regular fa-message"></i>
                    <span>${chats[id].title || 'Nuevo chat'}</span>
                    <i class="fa-solid fa-trash btn-delete" onclick="eliminarChat(event, '${id}')"></i>
                `;
                list.appendChild(item);
            });
        }

        function nuevoChat() {
            currentChatId = null;
            document.getElementById("chat").innerHTML = `
                <div class="msg-wrapper bot">
                    <div class="avatar"><i class="fa-solid fa-robot"></i></div>
                    <div class="msg-content">
                        ¡Hola! Soy <b>EdgarAI</b>. ¿En qué te ayudo hoy?
                    </div>
                </div>`;
            renderHistory();
            if (window.innerWidth <= 768) toggleSidebar();
        }

        function guardarMensaje(role, text) {
            if (!currentChatId) {
                currentChatId = 'chat_' + Date.now();
                chats[currentChatId] = {
                    title: text.length > 25 ? text.substring(0, 25) + '...' : text,
                    messages: []
                };
            }
            chats[currentChatId].messages.push({ role, text });
            localStorage.setItem('edgarai_chats', JSON.stringify(chats));
            renderHistory();
        }

        function cargarChat(id) {
            currentChatId = id;
            const chatData = chats[id];
            const chatBox = document.getElementById("chat");
            chatBox.innerHTML = '';

            chatData.messages.forEach(m => {
                if (m.role === 'user') {
                    chatBox.innerHTML += `
                        <div class="msg-wrapper user">
                            <div class="avatar"><i class="fa-solid fa-user"></i></div>
                            <div class="msg-content">${escapeHTML(m.text)}</div>
                        </div>`;
                } else {
                    let htmlRespuesta = marked.parse(m.text);
                    chatBox.innerHTML += `
                        <div class="msg-wrapper bot">
                            <div class="avatar"><i class="fa-solid fa-robot"></i></div>
                            <div class="msg-content">${htmlRespuesta}</div>
                        </div>`;
                }
            });

            document.querySelectorAll('pre code').forEach((block) => {
                hljs.highlightElement(block);
            });

            chatBox.scrollTop = chatBox.scrollHeight;
            renderHistory();
            if (window.innerWidth <= 768) toggleSidebar();
        }

        function eliminarChat(e, id) {
            e.stopPropagation();
            delete chats[id];
            localStorage.setItem('edgarai_chats', JSON.stringify(chats));
            if (currentChatId === id) {
                nuevoChat();
            } else {
                renderHistory();
            }
        }

        async function enviar() {
            let input = document.getElementById("msg");
            let texto = input.value.trim();
            if (!texto) return;

            let chat = document.getElementById("chat");
            let typing = document.getElementById("typing");

            chat.innerHTML += `
                <div class="msg-wrapper user">
                    <div class="avatar"><i class="fa-solid fa-user"></i></div>
                    <div class="msg-content">${escapeHTML(texto)}</div>
                </div>`;
            
            input.value = "";
            chat.scrollTop = chat.scrollHeight;

            guardarMensaje('user', texto);

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

                chat.innerHTML += `
                    <div class="msg-wrapper bot">
                        <div class="avatar"><i class="fa-solid fa-robot"></i></div>
                        <div class="msg-content">${htmlRespuesta}</div>
                    </div>`;

                guardarMensaje('bot', data.respuesta);

                document.querySelectorAll('pre code').forEach((block) => {
                    hljs.highlightElement(block);
                });

            } catch (e) {
                typing.style.display = "none";
                chat.innerHTML += `
                    <div class="msg-wrapper bot">
                        <div class="avatar"><i class="fa-solid fa-triangle-exclamation"></i></div>
                        <div class="msg-content">Error al conectar con la IA.</div>
                    </div>`;
            }
            chat.scrollTop = chat.scrollHeight;
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