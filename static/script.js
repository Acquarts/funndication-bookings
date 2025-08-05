class ChatInterface {
    constructor() {
        this.sessionId = null;
        this.messageInput = document.getElementById('messageInput');
        this.sendButton = document.getElementById('sendButton');
        this.messagesContainer = document.getElementById('messagesContainer');
        this.loadingOverlay = document.getElementById('loadingOverlay');
        
        this.initializeEventListeners();
        this.focusInput();
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
        
        // Auto-resize input (optional enhancement)
        this.messageInput.addEventListener('input', () => {
            this.adjustInputHeight();
        });
    }
    
    adjustInputHeight() {
        this.messageInput.style.height = 'auto';
        this.messageInput.style.height = Math.min(this.messageInput.scrollHeight, 120) + 'px';
    }
    
    focusInput() {
        setTimeout(() => this.messageInput.focus(), 100);
    }
    
    async sendMessage() {
        const message = this.messageInput.value.trim();
        
        if (!message || this.sendButton.disabled) {
            return;
        }
        
        // Add user message immediately
        this.addMessage(message, 'user');
        
        // Clear and reset input
        this.messageInput.value = '';
        this.adjustInputHeight();
        
        // Disable input during processing
        this.setInputState(false);
        
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
                throw new Error(`Request failed with status ${response.status}`);
            }
            
            const data = await response.json();
            
            // Update session ID
            this.sessionId = data.session_id;
            
            // Add assistant response
            this.addMessage(data.response, 'assistant');
            
            // Handle conversation end
            if (data.status === 'completed') {
                this.handleConversationEnd();
            }
            
        } catch (error) {
            console.error('Error sending message:', error);
            this.addMessage(
                'Lo siento, ocurrió un error técnico. Por favor, intenta de nuevo.',
                'assistant'
            );
        } finally {
            // Hide loading and re-enable input
            this.showLoading(false);
            this.setInputState(true);
            this.focusInput();
        }
    }
    
    addMessage(content, sender) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${sender}-message`;
        
        // Create message header
        const headerDiv = document.createElement('div');
        headerDiv.className = 'message-header';
        
        const senderSpan = document.createElement('span');
        senderSpan.className = 'sender-name';
        senderSpan.textContent = sender === 'user' ? 'Tú' : 'Funndication';
        
        const timeSpan = document.createElement('span');
        timeSpan.className = 'message-time';
        timeSpan.textContent = this.formatTime(new Date());
        
        headerDiv.appendChild(senderSpan);
        headerDiv.appendChild(timeSpan);
        
        // Create message content
        const contentDiv = document.createElement('div');
        contentDiv.className = 'message-content';
        
        if (sender === 'assistant') {
            contentDiv.innerHTML = this.formatAssistantMessage(content);
        } else {
            contentDiv.textContent = content;
        }
        
        messageDiv.appendChild(headerDiv);
        messageDiv.appendChild(contentDiv);
        
        this.messagesContainer.appendChild(messageDiv);
        this.scrollToBottom();
    }
    
    formatAssistantMessage(content) {
        // Format the assistant message content
        return content
            .replace(/\n/g, '<br>')
            .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
            .replace(/\*(.*?)\*/g, '<em>$1</em>')
            .replace(/`(.*?)`/g, '<code>$1</code>');
    }
    
    formatTime(date) {
        return date.toLocaleTimeString('en-US', {
            hour: '2-digit',
            minute: '2-digit',
            hour12: false
        });
    }
    
    setInputState(enabled) {
        this.messageInput.disabled = !enabled;
        this.sendButton.disabled = !enabled;
        
        // Update button appearance
        if (enabled) {
            this.sendButton.style.opacity = '1';
        } else {
            this.sendButton.style.opacity = '0.5';
        }
    }
    
    showLoading(show) {
        this.loadingOverlay.style.display = show ? 'flex' : 'none';
    }
    
    scrollToBottom() {
        setTimeout(() => {
            this.messagesContainer.scrollTop = this.messagesContainer.scrollHeight;
        }, 50);
    }
    
    handleConversationEnd() {
        setTimeout(() => {
            this.addMessage(
                'Gracias por usar nuestro servicio. Puedes iniciar una nueva conversación cuando quieras.',
                'assistant'
            );
            
            // Reset session for new conversation
            this.sessionId = null;
        }, 1500);
    }
}

// Utility functions
const utils = {
    // Debounce function for performance
    debounce(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    },
    
    // Check if device is mobile
    isMobile() {
        return /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent);
    }
};

// Initialize the chat interface when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    const chatInterface = new ChatInterface();
    
    // Add some mobile-specific optimizations
    if (utils.isMobile()) {
        document.body.classList.add('mobile-device');
        
        // Adjust viewport on mobile keyboard show/hide
        const viewport = document.querySelector('meta[name=viewport]');
        if (viewport) {
            viewport.setAttribute('content', 
                'width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no'
            );
        }
    }
    
    // Handle visibility change (tab focus/blur)
    document.addEventListener('visibilitychange', () => {
        if (!document.hidden) {
            chatInterface.focusInput();
        }
    });
});

// Error handling for uncaught errors
window.addEventListener('error', (event) => {
    console.error('Uncaught error:', event.error);
});

window.addEventListener('unhandledrejection', (event) => {
    console.error('Unhandled promise rejection:', event.reason);
});