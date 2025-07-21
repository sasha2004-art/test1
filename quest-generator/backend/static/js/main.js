// quest-generator/backend/static/js/main.js

document.addEventListener('DOMContentLoaded', () => {
    const generateBtn = document.getElementById('generate-btn');
    const settingInput = document.getElementById('setting-input');
    const apiKeyInput = document.getElementById('api-key-input');
    const resultBox = document.getElementById('result-box');

    generateBtn.addEventListener('click', async () => {
        const setting = settingInput.value.trim();
        const apiKey = apiKeyInput.value.trim();

        if (!setting || !apiKey) {
            alert('Пожалуйста, заполните описание сеттинга и API-ключ.');
            return;
        }

        resultBox.textContent = 'Генерация... Пожалуйста, подождите.';
        generateBtn.disabled = true;

        try {
            const response = await fetch('/generate', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    setting: setting,
                    api_key: apiKey
                }),
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
