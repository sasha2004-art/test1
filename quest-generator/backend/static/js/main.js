// quest-generator/backend/static/js/main.js

document.addEventListener('DOMContentLoaded', () => {
    const generateBtn = document.getElementById('generate-btn');
    const settingInput = document.getElementById('setting-input');
    const apiKeyInput = document.getElementById('api-key-input');
    const resultBox = document.getElementById('result-box');
    const modelSelect = document.getElementById('model-select');
    const apiKeyGroup = document.getElementById('api-key-group');

    // Показываем/скрываем поле ключа в зависимости от выбора
    modelSelect.addEventListener('change', () => {
        apiKeyGroup.style.display = modelSelect.value === 'groq' ? 'block' : 'none';
    });

    generateBtn.addEventListener('click', async () => {
        const setting = settingInput.value.trim();
        const model = modelSelect.value;
        const apiKey = apiKeyInput.value.trim();

        if (!setting) {
            alert('Пожалуйста, заполните описание сеттинга.');
            return;
        }
        if (model === 'groq' && !apiKey) {
            alert('Пожалуйста, введите API-ключ для модели Groq.');
            return;
        }

        resultBox.textContent = 'Генерация... Пожалуйста, подождите.';
        generateBtn.disabled = true;

        try {
            // Обновляем тело запроса
            const requestBody = {
                setting: setting,
                model: model,
            };
            if (model === 'groq') {
                requestBody.api_key = apiKey;
            }

            const response = await fetch('/generate', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(requestBody),
            });

            const data = await response.json();

            if (response.ok) {
                // Форматируем JSON для красивого отображения
                resultBox.textContent = JSON.stringify(data, null, 2);
            } else {
                resultBox.textContent = `Ошибка: ${data.error || 'Неизвестная ошибка сервера'}`;
            }
        } catch (error) {
            console.error('Fetch Error:', error);
            resultBox.textContent = 'Сетевая ошибка или не удалось обработать запрос. Проверьте консоль (F12).';
        } finally {
            generateBtn.disabled = false;
        }
    });
});
