// Main JavaScript for TerraAgent

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
    
    // Document ingestion elements
    const sidebarDocForm = document.getElementById('sidebar-document-form');
    const sidebarIngestStatus = document.getElementById('sidebar-ingest-status');
    
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
    
    // Set up document ingestion form
    if (sidebarDocForm) {
        sidebarDocForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            
            const url = document.getElementById('sidebar-doc-url').value;
            const title = document.getElementById('sidebar-doc-title').value;
            
            // Show status
            sidebarIngestStatus.classList.remove('d-none', 'text-success', 'text-danger');
            sidebarIngestStatus.classList.add('text-info');
            sidebarIngestStatus.textContent = 'Processing document...';
            
            try {
                // Send API request
                const response = await fetch('/api/ingest_document', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({
                        url,
                        title: title || null,
                        type: 'webpage'
                    })
                });
                
                const result = await response.json();
                
                if (response.ok) {
                    // Success
                    sidebarIngestStatus.classList.remove('text-info', 'text-danger');
                    sidebarIngestStatus.classList.add('text-success');
                    sidebarIngestStatus.textContent = `Document added successfully!`;
                    
                    // Add message to chat
                    addMessage(`I've added a new document "${result.title}" to my knowledge base. You can now ask me questions about it!`, 'assistant');
                    
                    // Clear form
                    sidebarDocForm.reset();
                } else {
                    // Error
                    sidebarIngestStatus.classList.remove('text-info', 'text-success');
                    sidebarIngestStatus.classList.add('text-danger');
                    sidebarIngestStatus.textContent = `Error: ${result.error}`;
                }
            } catch (error) {
                // Network error
                sidebarIngestStatus.classList.remove('text-info', 'text-success');
                sidebarIngestStatus.classList.add('text-danger');
                sidebarIngestStatus.textContent = `Network error`;
                console.error('Document ingestion error:', error);
            }
        });
    }
    
    // Hide loading indicator initially
    if (loadingIndicator) {
        loadingIndicator.style.display = 'none';
    }
    
    // Add welcome message
    addMessage('Hello, I\'m Agent Smith from TerraAgent. Ask me anything about property assessment, CAMA data, levy calculations, or database information. You can also add documents to my knowledge base using the form in the sidebar.', 'assistant');
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
        addMessage('Chat history has been reset. I\'m Agent Smith - how can I assist with your property assessment needs today?', 'assistant');
    })
    .catch(error => {
        console.error('Error resetting chat:', error);
    });
}
