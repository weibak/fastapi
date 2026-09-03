const sessionDiv = document.getElementById('ai-session');
const sessionId = sessionDiv.getAttribute('data-session-id');
const messagesDiv = document.getElementById('messages');

function appendMessage(text, fromAI = false) {
    const msg = document.createElement('div');
    msg.className = fromAI ? 'p-2 my-1 bg-gray-200 text-black rounded-md self-start max-w-xs' : 'p-2 my-1 bg-blue-500 text-white rounded-md self-end max-w-xs ml-auto';
    msg.textContent = text;
    messagesDiv.appendChild(msg);
    messagesDiv.scrollTop = messagesDiv.scrollHeight;
}

async function sendQuestion() {
    const input = document.getElementById('questionInput');
    const modelSelect = document.getElementById('modelSelect');
    const question = input.value.trim();
    if (!question) return;

    // Показываем сообщение пользователя
    appendMessage(question, false);
    input.value = '';

    try {
        const res = await fetch('/ai/chat', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ question: question, session_id: sessionId, model: modelSelect.value })
        });

        if (!res.ok) {
            const text = await res.text();
            appendMessage('Ошибка: ' + text, true);
            return;
        }

        const data = await res.json();
        if (data && data.answer) {
            appendMessage(data.answer, true);
        } else {
            appendMessage('AI вернул пустой ответ', true);
        }
    } catch (err) {
        appendMessage('Ошибка сети: ' + err.message, true);
    }
}

document.getElementById('questionInput').addEventListener('keypress', (e) => {
    if (e.key === 'Enter') {
        e.preventDefault();
        sendQuestion();
    }
});
