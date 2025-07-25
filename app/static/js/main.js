document.addEventListener('DOMContentLoaded', () => {
    const generateBtn = document.getElementById('generate-btn');
    const settingInput = document.getElementById('setting-input');
    const resultBox = document.getElementById('result-box');

    generateBtn.addEventListener('click', async () => {
        const setting = settingInput.value.trim();
        const selectedProvider = document.querySelector('input[name="api_provider"]:checked').value;

        let apiKey;
        const apiProvider = selectedProvider;

        switch (apiProvider) {
            case 'groq':
                apiKey = localStorage.getItem('groq_api_key');
                break;
            case 'openai':
                apiKey = localStorage.getItem('openai_api_key');
                break;
            case 'gemini':
                apiKey = localStorage.getItem('gemini_api_key');
                break;
            default:
                apiKey = null;
        }

        if (!setting) {
            alert('Пожалуйста, введите сеттинг.');
            return;
        }
        
        if (!apiKey) {
            alert(`API-ключ для провайдера "${apiProvider}" не найден. Пожалуйста, добавьте его на странице настройки ключей.`);
            window.location.href = '/api_keys'; // Перенаправляем на страницу ключей
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