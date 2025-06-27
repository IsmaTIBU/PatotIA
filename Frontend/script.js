// Elementos del DOM
const chatMessages = document.getElementById('chatMessages');
const messageInput = document.getElementById('messageInput');
const sendButton = document.getElementById('sendButton');

// URL de la API
const API_URL = 'http://localhost:5000';

// Función para agregar mensaje al chat
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

// Función para actualizar mensaje de carga con respuesta real
function updateLoadingMessage(loadingMessageDiv, content) {
    const messageContent = loadingMessageDiv.querySelector('.message-content');
    messageContent.className = 'message-content'; // Quitar clase loading
    messageContent.style.whiteSpace = 'pre-wrap';
    messageContent.style.fontFamily = 'monospace';
    messageContent.textContent = content;
}

// Función para enviar mensaje
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
        
        // ACTUALIZAR BURBUJA DE CARGA CON RESPUESTA REAL
        if (data.error) {
            updateLoadingMessage(loadingMessage, `❌ Error: ${data.error}`);
        } else {
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

// Event listeners
sendButton.addEventListener('click', sendMessage);

messageInput.addEventListener('keypress', function(e) {
    if (e.key === 'Enter') {
        sendMessage();
    }
});