document.addEventListener('DOMContentLoaded', () => {
    const generateBtn = document.getElementById('generate-btn');
    const settingInput = document.getElementById('setting-input');
    const resultBox = document.getElementById('result-box');

    generateBtn.addEventListener('click', async () => {
        const setting = settingInput.value.trim();

        const groqApiKey = localStorage.getItem('groq_api_key');
        const openaiApiKey = localStorage.getItem('openai_api_key');
        const geminiApiKey = localStorage.getItem('gemini_api_key');

        let apiKey = groqApiKey || openaiApiKey || geminiApiKey;
        let apiProvider = '';

        if (groqApiKey) {
            apiKey = groqApiKey;
            apiProvider = 'groq';
        } else if (openaiApiKey) {
            apiKey = openaiApiKey;
            apiProvider = 'openai';
        } else if (geminiApiKey) {
            apiKey = geminiApiKey;
            apiProvider = 'gemini';
        }

        if (!setting || !apiKey) {
            alert('Пожалуйста, введите сеттинг и настройте хотя бы один API-ключ.');
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
                    api_key: apiKey,
                    api_provider: apiProvider
                }),
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
