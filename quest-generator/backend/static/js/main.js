document.addEventListener('DOMContentLoaded', () => {
    const generateBtn = document.getElementById('generate-btn');
    const settingInput = document.getElementById('setting-input');
    const apiKeyInput = document.getElementById('api-key-input');
    const resultBox = document.getElementById('result-box');
    const llmSelect = document.getElementById('llm-select');
    const apiKeyGroup = document.getElementById('api-key-group');

    llmSelect.addEventListener('change', () => {
        apiKeyGroup.style.display = llmSelect.value === 'groq' ? 'block' : 'none';
    });

    generateBtn.addEventListener('click', async () => {
        const setting = settingInput.value.trim();
        const apiKey = apiKeyInput.value.trim();
        const llm_type = llmSelect.value;

        if (!setting) {
            alert('Пожалуйста, заполните описание сеттинга.');
            return;
        }

        if (llm_type === 'groq' && !apiKey) {
            alert('Пожалуйста, введите ваш Groq API ключ.');
            return;
        }

        resultBox.textContent = 'Генерация... Пожалуйста, подождите.';
        generateBtn.disabled = true;

        try {
            const body = {
                setting: setting,
                llm_type: llm_type
            };

            if (llm_type === 'groq') {
                body.api_key = apiKey;
            }

            const response = await fetch('/generate', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(body),
            });

            const data = await response.json();

            if (response.ok) {
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
