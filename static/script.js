class ChatBot {
    constructor() {
        this.sessionId = null;
        this.messageInput = document.getElementById('messageInput');
        this.sendButton = document.getElementById('sendButton');
        this.chatMessages = document.getElementById('chatMessages');
        this.loading = document.getElementById('loading');
        
        this.initializeEventListeners();
    }
    
    initializeEventListeners() {
        // Enter key to send message
        this.messageInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                this.sendMessage();
            }
        });
        
        // Send button click
        this.sendButton.addEventListener('click', () => {
            this.sendMessage();
        });
        
        // Auto-focus input
        this.messageInput.focus();
    }
    
    async sendMessage() {
        const message = this.messageInput.value.trim();
        
        if (!message) {
            return;
        }
        
        // Disable input while processing
        this.setInputState(false);
        
        // Add user message to chat
        this.addMessage(message, 'user');
        
        // Clear input
        this.messageInput.value = '';
        
        try {
            // Show loading
            this.showLoading(true);
            
            // Send request to API
            const response = await fetch('/chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    message: message,
                    session_id: this.sessionId
                })
            });
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            const data = await response.json();
            
            // Update session ID
            this.sessionId = data.session_id;
            
            // Add bot response to chat
            this.addMessage(data.response, 'bot');
            
            // Check if conversation ended
            if (data.status === 'completed') {
                this.handleConversationEnd();
            }
            
        } catch (error) {
            console.error('Error:', error);
            this.addMessage('Lo siento, ocurrió un error al procesar tu mensaje. Por favor, intenta de nuevo.', 'bot');
        } finally {
            // Hide loading and re-enable input
            this.showLoading(false);
            this.setInputState(true);
            this.messageInput.focus();
        }
    }
    
    addMessage(content, sender) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${sender}-message`;
        
        const messageContent = document.createElement('div');
        messageContent.className = 'message-content';
        
        if (sender === 'bot') {
            messageContent.innerHTML = `<strong>Funndication DJ Bookings:</strong><br>${this.formatBotMessage(content)}`;
        } else {
            messageContent.textContent = content;
        }
        
        messageDiv.appendChild(messageContent);
        this.chatMessages.appendChild(messageDiv);
        
        // Scroll to bottom
        this.scrollToBottom();
    }
    
    formatBotMessage(content) {
        // Convert newlines to <br> and preserve formatting
        return content
            .replace(/\n/g, '<br>')
            .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
            .replace(/\*(.*?)\*/g, '<em>$1</em>');
    }
    
    setInputState(enabled) {
        this.messageInput.disabled = !enabled;
        this.sendButton.disabled = !enabled;
        
        if (enabled) {
            this.sendButton.innerHTML = '<span>Enviar</span>';
        } else {
            this.sendButton.innerHTML = '<span>...</span>';
        }
    }
    
    showLoading(show) {
        this.loading.style.display = show ? 'flex' : 'none';
    }
    
    scrollToBottom() {
        setTimeout(() => {
            this.chatMessages.scrollTop = this.chatMessages.scrollHeight;
        }, 100);
    }
    
    handleConversationEnd() {
        // Add a restart button or message
        setTimeout(() => {
            const restartDiv = document.createElement('div');
            restartDiv.className = 'message bot-message';
            restartDiv.innerHTML = `
                <div class="message-content">
                    <strong>¿Necesitas algo más?</strong><br>
                    Puedes empezar una nueva conversación escribiendo otro mensaje.
                </div>
            `;
            this.chatMessages.appendChild(restartDiv);
            this.scrollToBottom();
            
            // Reset session
            this.sessionId = null;
        }, 2000);
    }
}

// Initialize chat when page loads
document.addEventListener('DOMContentLoaded', () => {
    const chatBot = new ChatBot();
    
    // Global function for inline onclick (backup)
    window.sendMessage = () => chatBot.sendMessage();
});

// Service Worker registration (optional, for PWA features)
if ('serviceWorker' in navigator) {
    window.addEventListener('load', () => {
        navigator.serviceWorker.register('/static/sw.js')
            .then((registration) => {
                console.log('SW registered: ', registration);
            })
            .catch((registrationError) => {
                console.log('SW registration failed: ', registrationError);
            });
    });
}