// Main JavaScript for PACS-Training Assistant

// DOM Elements
let chatContainer, messageInput, sendButton, queryTypeSelect;
let resetChatButton, loadingIndicator;

// Initialize application when DOM is fully loaded
document.addEventListener('DOMContentLoaded', () => {
    // Get DOM elements
    chatContainer = document.getElementById('chat-container');
    messageInput = document.getElementById('message-input');
    sendButton = document.getElementById('send-button');
    queryTypeSelect = document.getElementById('query-type');
    resetChatButton = document.getElementById('reset-chat');
    loadingIndicator = document.getElementById('loading-indicator');
    
    // Set up event listeners
    sendButton.addEventListener('click', sendMessage);
    messageInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            sendMessage();
        }
    });
    
    if (resetChatButton) {
        resetChatButton.addEventListener('click', resetChat);
    }
    
    // Hide loading indicator initially
    if (loadingIndicator) {
        loadingIndicator.style.display = 'none';
    }
    
    // Add welcome message
    addMessage('Welcome to PACS-Training Assistant! Ask me anything about CAMA data, levy calculations, or database information.', 'assistant');
});

// Send message to backend
function sendMessage() {
    const message = messageInput.value.trim();
    
    // Skip if message is empty
    if (!message) {
        return;
    }
    
    // Get selected query type
    const queryType = queryTypeSelect ? queryTypeSelect.value : 'general';
    
    // Add user message to chat
    addMessage(message, 'user');
    
    // Clear input
    messageInput.value = '';
    
    // Show loading indicator
    if (loadingIndicator) {
        loadingIndicator.style.display = 'inline-block';
    }
    
    // Disable send button while processing
    sendButton.disabled = true;
    
    // Send to backend
    fetch('/api/query', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            query: message,
            type: queryType
        })
    })
    .then(response => response.json())
    .then(data => {
        // Hide loading indicator
        if (loadingIndicator) {
            loadingIndicator.style.display = 'none';
        }
        
        // Re-enable send button
        sendButton.disabled = false;
        
        // Handle error
        if (data.error) {
            addMessage(`Error: ${data.error}`, 'assistant error');
            return;
        }
        
        // Add assistant response to chat
        addMessage(data.result, 'assistant');
        
        // Scroll to bottom
        scrollToBottom();
    })
    .catch(error => {
        // Hide loading indicator
        if (loadingIndicator) {
            loadingIndicator.style.display = 'none';
        }
        
        // Re-enable send button
        sendButton.disabled = false;
        
        // Show error
        addMessage(`Error: ${error.message}`, 'assistant error');
        console.error('Error:', error);
    });
}

// Add a message to the chat container
function addMessage(text, role) {
    // Create message element
    const messageElement = document.createElement('div');
    messageElement.className = `message ${role}-message`;
    
    // Process markdown-like formatting in the message
    const formattedText = formatText(text);
    messageElement.innerHTML = formattedText;
    
    // Add to chat container
    chatContainer.appendChild(messageElement);
    
    // Scroll to bottom
    scrollToBottom();
}

// Format text with simple markdown-like syntax
function formatText(text) {
    // Convert code blocks
    text = text.replace(/```([^`]+)```/g, '<pre><code>$1</code></pre>');
    
    // Convert inline code
    text = text.replace(/`([^`]+)`/g, '<code>$1</code>');
    
    // Convert bold text
    text = text.replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>');
    
    // Convert italic text
    text = text.replace(/\*([^*]+)\*/g, '<em>$1</em>');
    
    // Convert line breaks
    text = text.replace(/\n/g, '<br>');
    
    return text;
}

// Scroll chat container to bottom
function scrollToBottom() {
    chatContainer.scrollTop = chatContainer.scrollHeight;
}

// Reset chat history
function resetChat() {
    // Clear chat container
    while (chatContainer.firstChild) {
        chatContainer.removeChild(chatContainer.firstChild);
    }
    
    // Send reset request to backend
    fetch('/api/reset_chat', {
        method: 'POST'
    })
    .then(response => response.json())
    .then(data => {
        // Add welcome message
        addMessage('Chat history has been reset. How can I help you today?', 'assistant');
    })
    .catch(error => {
        console.error('Error resetting chat:', error);
    });
}
