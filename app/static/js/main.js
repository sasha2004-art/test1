document.addEventListener('DOMContentLoaded', () => {
    const generateBtn = document.getElementById('generate-btn');
    const settingInput = document.getElementById('setting-input');
    const resultBox = document.getElementById('result-box');
    const providerRadios = document.querySelectorAll('input[name="api_provider"]');
    const modelSelectorGroup = document.getElementById('model-selector-group');
    const modelSelector = document.getElementById('model-selector');
    const newChatBtn = document.getElementById('new-chat-btn');
    const chatList = document.getElementById('chat-list');

    let chats = {};
    let activeChatId = null;

    function saveChats() {
        localStorage.setItem('chats', JSON.stringify(chats));
    }

    function loadChats() {
        const savedChats = localStorage.getItem('chats');
        if (savedChats) {
            chats = JSON.parse(savedChats);
        }
    }

    function renderChatList() {
        chatList.innerHTML = '';
        for (const id in chats) {
            const chat = chats[id];
            const chatDiv = document.createElement('div');
            chatDiv.classList.add('chat-item');
            if (id === activeChatId) {
                chatDiv.classList.add('active');
            }
            chatDiv.textContent = chat.title;
            chatDiv.dataset.chatId = id;
            chatDiv.addEventListener('click', () => {
                switchChat(id);
            });
            chatList.appendChild(chatDiv);
        }
    }

    function switchChat(chatId) {
        activeChatId = chatId;
        const chat = chats[chatId];
        settingInput.value = chat.setting;
        resultBox.textContent = chat.result;
        renderChatList();
    }

    function createNewChat() {
        const newChatId = `chat_${Date.now()}`;
        chats[newChatId] = {
            id: newChatId,
            title: `Чат ${Object.keys(chats).length + 1}`,
            setting: '',
            result: 'Здесь появится сгенерированный JSON...'
        };
        activeChatId = newChatId;
        saveChats();
        renderChatList();
        switchChat(newChatId);
    }

    newChatBtn.addEventListener('click', createNewChat);

    async function updateModels() {
        const selectedProvider = document.querySelector('input[name="api_provider"]:checked').value;
        const apiKey = localStorage.getItem(`${selectedProvider}_api_key`);

        if (!apiKey) {
            modelSelectorGroup.style.display = 'none';
            return;
        }

        try {
            const response = await fetch('/api/models', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    api_provider: selectedProvider,
                    api_key: apiKey,
                }),
            });

            const data = await response.json();

            if (response.ok && data.models) {
                modelSelector.innerHTML = '';
                data.models.forEach(model => {
                    const option = document.createElement('option');
                    option.value = model;
                    option.textContent = model;
                    modelSelector.appendChild(option);
                });
                modelSelectorGroup.style.display = 'block';
            } else {
                modelSelectorGroup.style.display = 'none';
                console.error('Failed to fetch models:', data.error);
            }
        } catch (error) {
            modelSelectorGroup.style.display = 'none';
            console.error('Error fetching models:', error);
        }
    }

    providerRadios.forEach(radio => {
        radio.addEventListener('change', updateModels);
    });

    generateBtn.addEventListener('click', async () => {
        if (!activeChatId) {
            createNewChat();
        }

        const setting = settingInput.value.trim();
        const selectedProvider = document.querySelector('input[name="api_provider"]:checked').value;
        const selectedModel = modelSelector.value;
        const apiKey = localStorage.getItem(`${selectedProvider}_api_key`);

        if (!setting) {
            alert('Пожалуйста, введите сеттинг.');
            return;
        }

        if (!apiKey) {
            alert(`API-ключ для провайдера "${selectedProvider}" не найден. Пожалуйста, добавьте его на странице настройки ключей.`);
            window.location.href = '/api_keys';
            return;
        }

        if (!selectedModel) {
            alert('Пожалуйста, выберите модель.');
            return;
        }

        resultBox.textContent = 'Генерация... Пожалуйста, подождите.';
        generateBtn.disabled = true;

        chats[activeChatId].setting = setting;

        try {
            const response = await fetch('/generate', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    setting: setting,
                    api_key: apiKey,
                    api_provider: selectedProvider,
                    model: selectedModel,
                }),
            });

            const data = await response.json();

            if (response.ok) {
                const result = JSON.stringify(data, null, 2);
                resultBox.textContent = result;
                chats[activeChatId].result = result;
            } else {
                const error = `Ошибка: ${data.error || 'Неизвестная ошибка сервера'}`;
                resultBox.textContent = error;
                chats[activeChatId].result = error;
            }
        } catch (error) {
            console.error('Fetch Error:', error);
            const errorMsg = 'Сетевая ошибка или не удалось обработать запрос. Проверьте консоль (F12).';
            resultBox.textContent = errorMsg;
            chats[activeChatId].result = errorMsg;
        } finally {
            generateBtn.disabled = false;
            saveChats();
        }
    });

    loadChats();
    if (Object.keys(chats).length === 0) {
        createNewChat();
    } else {
        activeChatId = Object.keys(chats)[0];
        switchChat(activeChatId);
    }
    renderChatList();
    updateModels();
});