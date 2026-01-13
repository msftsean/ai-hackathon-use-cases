/**
 * Constituent Services Agent - Chat Interface
 * Handles session management, API integration, and accessibility
 */

// Configuration
const API_BASE = '/api/v1';
const MAX_MESSAGE_LENGTH = 10000;

// State
let sessionId = null;
let isWaitingForResponse = false;

// DOM Elements
const messagesContainer = document.getElementById('messages-container');
const welcomeSection = document.getElementById('welcome-section');
const typingIndicator = document.getElementById('typing-indicator');
const chatForm = document.getElementById('chat-form');
const messageInput = document.getElementById('message-input');
const sendBtn = document.getElementById('send-btn');
const newChatBtn = document.getElementById('new-chat-btn');
const srAnnouncements = document.getElementById('sr-announcements');

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    initSession();
    setupEventListeners();
    setupAutoResize();
});

/**
 * Initialize or restore session
 */
function initSession() {
    // Try to restore session from storage
    const savedSession = sessionStorage.getItem('chat-session-id');
    if (savedSession) {
        sessionId = savedSession;
        // Could restore conversation history here
    } else {
        sessionId = generateUUID();
        sessionStorage.setItem('chat-session-id', sessionId);
    }
}

/**
 * Set up event listeners
 */
function setupEventListeners() {
    // Form submission
    chatForm.addEventListener('submit', handleSubmit);

    // New chat button
    newChatBtn.addEventListener('click', startNewChat);

    // Service card quick actions
    document.querySelectorAll('.service-card').forEach(card => {
        card.addEventListener('click', () => {
            const query = card.dataset.query;
            if (query) {
                messageInput.value = query;
                handleSubmit(new Event('submit'));
            }
        });
    });

    // Keyboard shortcuts
    messageInput.addEventListener('keydown', (e) => {
        // Submit on Enter (without Shift)
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            handleSubmit(new Event('submit'));
        }
    });
}

/**
 * Auto-resize textarea
 */
function setupAutoResize() {
    messageInput.addEventListener('input', () => {
        messageInput.style.height = 'auto';
        messageInput.style.height = Math.min(messageInput.scrollHeight, 200) + 'px';
    });
}

/**
 * Handle form submission
 */
async function handleSubmit(e) {
    e.preventDefault();

    const message = messageInput.value.trim();
    if (!message || isWaitingForResponse) return;

    if (message.length > MAX_MESSAGE_LENGTH) {
        showError(`Message too long. Maximum ${MAX_MESSAGE_LENGTH} characters.`);
        return;
    }

    // Hide welcome section
    if (welcomeSection) {
        welcomeSection.style.display = 'none';
    }

    // Add user message
    addMessage('user', message);

    // Clear input
    messageInput.value = '';
    messageInput.style.height = 'auto';

    // Show typing indicator
    showTypingIndicator();
    isWaitingForResponse = true;
    sendBtn.disabled = true;

    try {
        const response = await sendMessage(message);
        hideTypingIndicator();
        addAssistantMessage(response);
        announce('Response received');
    } catch (error) {
        hideTypingIndicator();
        addErrorMessage(error.message || 'Failed to get response. Please try again.');
        announce('Error: ' + (error.message || 'Failed to get response'));
    } finally {
        isWaitingForResponse = false;
        sendBtn.disabled = false;
        messageInput.focus();
    }
}

/**
 * Send message to API
 */
async function sendMessage(message) {
    const response = await fetch(`${API_BASE}/chat`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            session_id: sessionId,
            message: message,
        }),
    });

    if (!response.ok) {
        const error = await response.json().catch(() => ({}));
        throw new Error(error.message || `Error: ${response.status}`);
    }

    return response.json();
}

/**
 * Add user message to chat
 */
function addMessage(role, content) {
    const messageDiv = document.createElement('div');
    messageDiv.className = `message message-${role}`;
    messageDiv.setAttribute('role', 'article');

    const bubble = document.createElement('div');
    bubble.className = 'message-bubble';
    bubble.textContent = content;

    messageDiv.appendChild(bubble);
    messagesContainer.appendChild(messageDiv);
    scrollToBottom();
}

/**
 * Add assistant message with citations
 */
function addAssistantMessage(response) {
    const messageDiv = document.createElement('div');
    messageDiv.className = 'message message-assistant';
    messageDiv.setAttribute('role', 'article');

    // Message bubble
    const bubble = document.createElement('div');
    bubble.className = 'message-bubble';

    // Format response text (preserve line breaks)
    const responseText = document.createElement('div');
    responseText.className = 'response-text';
    responseText.innerHTML = formatResponse(response.response);
    bubble.appendChild(responseText);

    // Disclaimer
    if (response.disclaimer) {
        const disclaimer = document.createElement('div');
        disclaimer.className = 'message-disclaimer';
        disclaimer.textContent = response.disclaimer;
        bubble.appendChild(disclaimer);
    }

    // Citations
    if (response.citations && response.citations.length > 0) {
        const citations = document.createElement('div');
        citations.className = 'citations';
        citations.innerHTML = `
            <div class="citations-title">Sources:</div>
            ${response.citations.map((cite, i) => `
                <div class="citation-item">
                    <span>[${i + 1}]</span>
                    <div>
                        <a href="${escapeHtml(cite.url)}" target="_blank" rel="noopener noreferrer">
                            ${escapeHtml(cite.title)}
                        </a>
                        <span class="citation-agency">(${escapeHtml(cite.agency)})</span>
                    </div>
                </div>
            `).join('')}
        `;
        bubble.appendChild(citations);
    }

    // Suggested actions
    if (response.suggested_actions && response.suggested_actions.length > 0) {
        const actions = document.createElement('div');
        actions.className = 'suggested-actions';
        response.suggested_actions.forEach(action => {
            const btn = document.createElement('button');
            btn.className = 'action-btn';
            btn.textContent = action.label;
            btn.addEventListener('click', () => handleAction(action));
            actions.appendChild(btn);
        });
        bubble.appendChild(actions);
    }

    messageDiv.appendChild(bubble);

    // Meta info (confidence)
    const meta = document.createElement('div');
    meta.className = 'message-meta';

    const confidence = response.confidence || 0;
    const confidenceClass = confidence >= 0.7 ? 'high' : confidence >= 0.5 ? 'medium' : 'low';
    const confidenceText = confidence >= 0.7 ? 'High confidence' : confidence >= 0.5 ? 'Medium confidence' : 'Low confidence';

    meta.innerHTML = `
        <span class="confidence-badge confidence-${confidenceClass}">${confidenceText}</span>
    `;
    messageDiv.appendChild(meta);

    messagesContainer.appendChild(messageDiv);
    scrollToBottom();
}

/**
 * Add error message
 */
function addErrorMessage(message) {
    const messageDiv = document.createElement('div');
    messageDiv.className = 'message message-assistant';
    messageDiv.setAttribute('role', 'alert');

    const bubble = document.createElement('div');
    bubble.className = 'message-bubble';
    bubble.innerHTML = `
        <p style="color: var(--danger);">⚠️ ${escapeHtml(message)}</p>
        <p>Please try again or <button class="action-btn" onclick="handleAction({type: 'escalate'})">talk to a human agent</button>.</p>
    `;

    messageDiv.appendChild(bubble);
    messagesContainer.appendChild(messageDiv);
    scrollToBottom();
}

/**
 * Handle suggested action
 */
async function handleAction(action) {
    if (action.type === 'escalate') {
        try {
            const response = await fetch(`${API_BASE}/conversations/${sessionId}/escalate`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ reason: 'User requested human assistance' }),
            });

            if (response.ok) {
                const data = await response.json();
                addMessage('assistant',
                    `You've been connected to our support queue. ` +
                    `Estimated wait time: ${data.estimated_wait_time} minutes. ` +
                    `Queue position: ${data.queue_position}. ` +
                    `Your conversation history will be available to the agent.`
                );
            }
        } catch (error) {
            addErrorMessage('Failed to connect to support queue. Please try again.');
        }
    } else if (action.type === 'link') {
        window.open(action.value, '_blank', 'noopener,noreferrer');
    } else if (action.type === 'follow_up') {
        messageInput.value = action.value;
        messageInput.focus();
    }
}

/**
 * Start new chat
 */
function startNewChat() {
    // Clear messages
    messagesContainer.innerHTML = '';

    // Show welcome section
    if (welcomeSection) {
        welcomeSection.style.display = 'block';
    }

    // Generate new session
    sessionId = generateUUID();
    sessionStorage.setItem('chat-session-id', sessionId);

    // Focus input
    messageInput.focus();
    announce('Started new conversation');
}

/**
 * Show typing indicator
 */
function showTypingIndicator() {
    typingIndicator.classList.add('visible');
    scrollToBottom();
}

/**
 * Hide typing indicator
 */
function hideTypingIndicator() {
    typingIndicator.classList.remove('visible');
}

/**
 * Scroll chat to bottom
 */
function scrollToBottom() {
    messagesContainer.scrollTop = messagesContainer.scrollHeight;
}

/**
 * Format response text
 */
function formatResponse(text) {
    // Convert markdown-style formatting
    let formatted = escapeHtml(text);

    // Bold text (**text**)
    formatted = formatted.replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>');

    // Numbered lists
    formatted = formatted.replace(/^(\d+\.)\s+(.+)$/gm, '<li>$2</li>');
    formatted = formatted.replace(/(<li>.*<\/li>\n?)+/g, '<ol>$&</ol>');

    // Bullet points
    formatted = formatted.replace(/^[-•]\s+(.+)$/gm, '<li>$1</li>');

    // Line breaks
    formatted = formatted.replace(/\n/g, '<br>');

    return formatted;
}

/**
 * Escape HTML
 */
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

/**
 * Announce for screen readers
 */
function announce(message) {
    srAnnouncements.textContent = message;
    setTimeout(() => {
        srAnnouncements.textContent = '';
    }, 1000);
}

/**
 * Show error notification
 */
function showError(message) {
    announce('Error: ' + message);
    // Could also show visual toast notification
}

/**
 * Generate UUID v4
 */
function generateUUID() {
    return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
        const r = Math.random() * 16 | 0;
        const v = c === 'x' ? r : (r & 0x3 | 0x8);
        return v.toString(16);
    });
}
