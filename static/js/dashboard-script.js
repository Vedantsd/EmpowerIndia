const themeToggle = document.getElementById('themeToggle');
const body = document.body;
const chatMessages = document.getElementById('chatMessages');
const userInput = document.getElementById('userInput');
const sendBtn = document.getElementById('sendBtn');
const moonIcon = document.getElementById('moonIcon');
const sunIcon = document.getElementById('sunIcon');

themeToggle.addEventListener('click', () => {
    if (body.getAttribute('data-theme') === 'dark') {
        body.removeAttribute('data-theme');
        moonIcon.style.display = 'block';
        sunIcon.style.display = 'none';
        localStorage.setItem('theme', 'light');
    } else {
        body.setAttribute('data-theme', 'dark');
        moonIcon.style.display = 'none';
        sunIcon.style.display = 'block';
        localStorage.setItem('theme', 'dark');
    }
});

const savedTheme = localStorage.getItem('theme');
if (savedTheme === 'dark') {
    body.setAttribute('data-theme', 'dark');
    moonIcon.style.display = 'none';
    sunIcon.style.display = 'block';
    themeText.textContent = 'Light Mode';
}

function addMessage(content, isUser) {
    const welcomeMsg = chatMessages.querySelector('.welcome-message');
    if (welcomeMsg) {
        welcomeMsg.remove();
    }

    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${isUser ? 'user' : 'bot'}`;

    const formattedContent = isUser ? content : formatMarkdown(content);
    
    messageDiv.innerHTML = `
        <div class="message-avatar">${isUser ? 'U' : '⚖️'}</div>
        <div class="message-content">${formattedContent}</div>
    `;
    
    chatMessages.appendChild(messageDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

function addLoadingIndicator() {
    const loadingDiv = document.createElement('div');
    loadingDiv.className = 'message bot';
    loadingDiv.id = 'loadingIndicator';
    loadingDiv.innerHTML = `
        <div class="message-avatar">⚖️</div>
        <div class="message-content loading">
            <span></span>
            <span></span>
            <span></span>
        </div>
    `;
    chatMessages.appendChild(loadingDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

function removeLoadingIndicator() {
    const loadingIndicator = document.getElementById('loadingIndicator');
    if (loadingIndicator) {
        loadingIndicator.remove();
    }
}

async function sendMessage() {
    const message = userInput.value.trim();
    if (!message) return;

    addMessage(message, true);
    userInput.value = '';
    sendBtn.disabled = true;
    addLoadingIndicator();

    try {
        const response = await fetch('/chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ message: message })
        });

        const data = await response.json();
        removeLoadingIndicator();
        
        if (data.response) {
            addMessage(data.response, false);
        } else {
            addMessage('Sorry, I encountered an error. Please try again.', false);
        }
    } catch (error) {
        removeLoadingIndicator();
        addMessage('Sorry, I could not connect to the server. Please try again later.', false);
    } finally {
        sendBtn.disabled = false;
        userInput.focus();
    }
}



function formatMarkdown(text) {
    text = text.replace(/&/g, '&amp;')
               .replace(/</g, '&lt;')
               .replace(/>/g, '&gt;');
    
    text = text.replace(/^### (.*$)/gim, '<h3>$1</h3>');
    text = text.replace(/^## (.*$)/gim, '<h2>$1</h2>');
    text = text.replace(/^# (.*$)/gim, '<h1>$1</h1>');
    
    text = text.replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>');
    text = text.replace(/__(.+?)__/g, '<strong>$1</strong>');
    
    text = text.replace(/\*([^*]+?)\*/g, '<em>$1</em>');
    text = text.replace(/_([^_]+?)_/g, '<em>$1</em>');
    
    text = text.replace(/```([\s\S]*?)```/g, '<pre><code>$1</code></pre>');
    
    text = text.replace(/`([^`]+)`/g, '<code>$1</code>');
    
    let lines = text.split('\n');
    let inList = false;
    let listType = null;
    let processedLines = [];
    
    for (let i = 0; i < lines.length; i++) {
        let line = lines[i];
        
        if (line.match(/^[\*\-]\s+(.+)/)) {
            if (!inList || listType !== 'ul') {
                if (inList) processedLines.push(`</${listType}>`);
                processedLines.push('<ul>');
                inList = true;
                listType = 'ul';
            }
            processedLines.push(line.replace(/^[\*\-]\s+(.+)/, '<li>$1</li>'));
        }

        else if (line.match(/^\d+\.\s+(.+)/)) {
            if (!inList || listType !== 'ol') {
                if (inList) processedLines.push(`</${listType}>`);
                processedLines.push('<ol>');
                inList = true;
                listType = 'ol';
            }
            processedLines.push(line.replace(/^\d+\.\s+(.+)/, '<li>$1</li>'));
        }


        else {
            if (inList) {
                processedLines.push(`</${listType}>`);
                inList = false;
                listType = null;
            }
            processedLines.push(line);
        }
    }
    
    if (inList) {
        processedLines.push(`</${listType}>`);
    }
    
    text = processedLines.join('\n');
    
    text = text.replace(/\n\n+/g, '</p><p>');
    text = text.replace(/\n/g, '<br>');
    


    if (!text.startsWith('<h') && !text.startsWith('<ul') && !text.startsWith('<ol') && !text.startsWith('<pre')) {
        text = '<p>' + text + '</p>';
    }
    
    return text;
}