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

// NUEVA: Función para formatear el texto de soluciones
function formatSolutionsText(textContent) {
    // Si el texto contiene "Solution", reformatearlo
    if (textContent.includes('Solution')) {
        return textContent
            .replace(/Solution \d+:/g, '\n$&') // Añadir salto de línea antes de cada "Solution X:"
            .replace(/^\n/, '') // Quitar salto de línea inicial si existe
            .trim();
    }
    return textContent;
}

// NUEVA: Función para actualizar con simulación (MEJORADA para formato)
function updateLoadingMessageWithSimulation(loadingMessageDiv, textContent, simulationHtml) {
    const messageContent = loadingMessageDiv.querySelector('.message-content');
    messageContent.className = 'message-content simulation-message';
    
    // Formatear el texto de soluciones
    const formattedText = formatSolutionsText(textContent);
    
    // Crear estructura con texto formateado y simulación
    messageContent.innerHTML = `
        <div class="text-response" style="white-space: pre-line; font-family: monospace;">${formattedText}</div>
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
    
    // Resto del código igual...
    setTimeout(() => {
        const simViewer = messageContent.querySelector('.simulation-viewer');
        const statusSpan = messageContent.querySelector('.simulation-status');
        
        try {
            const iframe = document.createElement('iframe');
            iframe.style.width = '100%';
            iframe.style.height = '500px';
            iframe.style.border = 'none';
            iframe.srcdoc = simulationHtml;
            
            simViewer.innerHTML = '';
            simViewer.appendChild(iframe);
            
            statusSpan.textContent = 'Interactive';
            statusSpan.style.background = '#28a745';
            
            console.log('✅ Simulación cargada en iframe con anchura fija');
            
        } catch (error) {
            console.log('⚠️ Iframe fallido, intentando inyección directa');
            
            simViewer.innerHTML = `
                <div class="plotly-container-wrapper" style="width: 100%; height: 500px; overflow: auto;">
                    ${simulationHtml}
                </div>
            `;
            
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