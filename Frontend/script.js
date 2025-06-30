// Elementos del DOM
const chatMessages = document.getElementById('chatMessages');
const messageInput = document.getElementById('messageInput');
const sendButton = document.getElementById('sendButton');

// URL de la API
const API_URL = 'http://localhost:5000';

// Función para agregar mensaje al chat (ORIGINAL + mejora pequeña)
function addMessage(content, isUser = false, isLoading = false) {
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${isUser ? 'user' : 'robot'}`;
    
    const avatar = document.createElement('div');
    avatar.className = 'message-avatar';
    avatar.textContent = isUser ? '👤' : '🤖';
    
    const messageContent = document.createElement('div');
    messageContent.className = 'message-content';
    
    if (isLoading) {
        messageContent.className += ' loading-message';
        messageContent.innerHTML = `
            <div class="loading-container">
                <div class="loading-text">
                    Processing
                    <span class="text-dots">
                        <span class="text-dot">.</span>
                        <span class="text-dot">.</span>
                        <span class="text-dot">.</span>
                    </span>
                </div>
            </div>
        `;
    } else {
        // Preservar saltos de línea y formato
        messageContent.style.whiteSpace = 'pre-wrap';
        messageContent.style.fontFamily = 'monospace';
        messageContent.textContent = content;
    }
    
    messageDiv.appendChild(avatar);
    messageDiv.appendChild(messageContent);
    
    chatMessages.appendChild(messageDiv);
    
    // Scroll hacia abajo
    chatMessages.scrollTop = chatMessages.scrollHeight;
    
    return messageDiv; // Retornar para poder modificarlo después
}

// Función para actualizar mensaje de carga con respuesta real (ORIGINAL)
function updateLoadingMessage(loadingMessageDiv, content) {
    const messageContent = loadingMessageDiv.querySelector('.message-content');
    messageContent.className = 'message-content'; // Quitar clase loading
    messageContent.style.whiteSpace = 'pre-wrap';
    messageContent.style.fontFamily = 'monospace';
    messageContent.textContent = content;
}

// NUEVA: Función para actualizar con simulación (CORREGIDA para Plotly)
function updateLoadingMessageWithSimulation(loadingMessageDiv, textContent, simulationHtml) {
    const messageContent = loadingMessageDiv.querySelector('.message-content');
    messageContent.className = 'message-content'; // Quitar clase loading
    
    // Crear estructura con texto y simulación SIEMPRE con altura fija
    messageContent.innerHTML = `
        <div class="text-response">${textContent}</div>
        <div class="media-container">
            <div class="simulation-header">
                <h4>🤖 3D Robot Simulation</h4>
                <span class="simulation-status">Loading...</span>
            </div>
            <div class="simulation-viewer simulation-viewer-fixed" id="sim-${Date.now()}">
                <div class="simulation-loading">
                    <div class="spinner-large"></div>
                    <p>Rendering 3D simulation...</p>
                </div>
            </div>
        </div>
    `;
    
    // Inyectar HTML de Plotly de forma correcta
    setTimeout(() => {
        const simViewer = messageContent.querySelector('.simulation-viewer');
        const statusSpan = messageContent.querySelector('.simulation-status');
        
        try {
            // MÉTODO 1: Crear iframe con el HTML de Plotly
            const iframe = document.createElement('iframe');
            iframe.style.width = '100%';
            iframe.style.height = '500px'; // ← ALTURA FIJA SIEMPRE
            iframe.style.border = 'none';
            iframe.srcdoc = simulationHtml;
            
            // Limpiar y agregar iframe
            simViewer.innerHTML = '';
            simViewer.appendChild(iframe);
            
            statusSpan.textContent = 'Interactive';
            statusSpan.style.background = '#28a745';
            
            console.log('✅ Simulación cargada en iframe con altura fija');
            
        } catch (error) {
            // MÉTODO 2: Fallback - inyección directa con scripts
            console.log('⚠️ Iframe fallido, intentando inyección directa');
            
            // Envolver el HTML en un contenedor con altura fija
            simViewer.innerHTML = `
                <div class="plotly-container-wrapper" style="width: 100%; height: 500px; overflow: auto;">
                    ${simulationHtml}
                </div>
            `;
            
            // Ejecutar scripts de Plotly manualmente
            const scripts = simViewer.querySelectorAll('script');
            scripts.forEach(script => {
                try {
                    const newScript = document.createElement('script');
                    newScript.textContent = script.textContent;
                    document.head.appendChild(newScript);
                    setTimeout(() => document.head.removeChild(newScript), 100);
                } catch (e) {
                    console.log('Script execution error:', e);
                }
            });
            
            // Forzar altura en todos los elementos Plotly dentro del wrapper
            setTimeout(() => {
                const plotlyDivs = simViewer.querySelectorAll('.plotly-graph-div');
                plotlyDivs.forEach(div => {
                    div.style.height = '480px'; // Un poco menos para el scroll
                    div.style.width = '100%';
                });
            }, 1000);
            
            statusSpan.textContent = 'Loaded';
            statusSpan.style.background = '#17a2b8';
        }
        
    }, 500);
}

// Función para enviar mensaje (TU ORIGINAL + pequeña mejora)
async function sendMessage() {
    const message = messageInput.value.trim();
    
    if (message === '') return;
    
    // Agregar mensaje del usuario
    addMessage(message, true);
    
    // Limpiar input
    messageInput.value = '';
    
    // Deshabilitar botón mientras procesa
    sendButton.disabled = true;
    sendButton.textContent = 'Processing...';
    
    // MOSTRAR BURBUJA DE CARGA INMEDIATAMENTE
    const loadingMessage = addMessage('', false, true);
    
    try {
        // LLAMADA REAL A LA API (asíncrona)
        const response = await fetch(`${API_URL}/chat`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ message: message })
        });
        
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }
        
        const data = await response.json();
        
        // DEBUG: Ver qué respuesta recibimos
        console.log('📨 Respuesta de la API:', data);
        
        // ACTUALIZAR BURBUJA DE CARGA CON RESPUESTA REAL
        if (data.error) {
            console.log('❌ Error detectado');
            updateLoadingMessage(loadingMessage, `❌ Error: ${data.error}`);
        } else if (data.has_simulation && data.simulations_html) {
            console.log('✅ Simulación detectada con HTML');
            updateLoadingMessageWithSimulation(loadingMessage, data.response, data.simulations_html);
        } else if (data.has_simulation) {
            console.log('⚠️ Simulación detectada PERO sin HTML');
            updateLoadingMessage(loadingMessage, data.response + '\n\n[Simulación abierta en ventana externa]');
        } else {
            console.log('📝 Respuesta normal');
            updateLoadingMessage(loadingMessage, data.response);
        }
        
    } catch (error) {
        console.error('API Error:', error);
        updateLoadingMessage(loadingMessage, `❌ Connection error: ${error.message}\n\n💡 Make sure the Robot AI server is running:\n   python api.py`);
    } finally {
        // Rehabilitar botón
        sendButton.disabled = false;
        sendButton.textContent = 'Send';
    }
}

// Event listeners (ORIGINALES - NO TOCAR)
sendButton.addEventListener('click', sendMessage);

messageInput.addEventListener('keypress', function(e) {
    if (e.key === 'Enter') {
        sendMessage();
    }
});