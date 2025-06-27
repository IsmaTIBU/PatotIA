// Elementos del DOM
const chatMessages = document.getElementById('chatMessages');
const messageInput = document.getElementById('messageInput');
const sendButton = document.getElementById('sendButton');

// Función para agregar mensaje al chat
function addMessage(content, isUser = false) {
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${isUser ? 'user' : 'robot'}`;
    
    const avatar = document.createElement('div');
    avatar.className = 'message-avatar';
    avatar.textContent = isUser ? '👤' : '🤖';
    
    const messageContent = document.createElement('div');
    messageContent.className = 'message-content';
    messageContent.textContent = content;
    
    messageDiv.appendChild(avatar);
    messageDiv.appendChild(messageContent);
    
    chatMessages.appendChild(messageDiv);
    
    // Scroll hacia abajo
    chatMessages.scrollTop = chatMessages.scrollHeight;
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
    
    try {
        // AQUÍ VA LA LLAMADA A LA API (por ahora simulamos)
        // await fetch('/chat', { ... })
        
        // SIMULACIÓN temporal - borrar cuando tengas Flask
        setTimeout(() => {
            const responses = [
                "I understand you want to calculate robotics operations. Please provide specific angles or coordinates.",
                "For forward kinematics, I need three joint angles (q1, q2, q3).",
                "For inverse kinematics, provide target coordinates (x, y, z).",
                "For Jacobian calculations, I need joint angles and optionally joint velocities.",
                "I can also generate 3D simulations of the robot configuration."
            ];
            
            const randomResponse = responses[Math.floor(Math.random() * responses.length)];
            addMessage(randomResponse, false);
            
            // Rehabilitar botón
            sendButton.disabled = false;
            sendButton.textContent = 'Send';
        }, 1000);
        
    } catch (error) {
        addMessage('Error: Could not connect to Robot AI. Please check if the server is running.', false);
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

// Mensaje de bienvenida adicional
setTimeout(() => {
    addMessage("Type 'help' if you need guidance on how to use me!", false);
}, 500);