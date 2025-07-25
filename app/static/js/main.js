document.addEventListener('DOMContentLoaded', () => {
    const generateBtn = document.getElementById('generate-btn');
    const settingInput = document.getElementById('setting-input');
    const resultBox = document.getElementById('result-box');
    const providerRadios = document.querySelectorAll('input[name="api_provider"]');
    const modelSelectorGroup = document.getElementById('model-selector-group');
    const modelSelector = document.getElementById('model-selector');

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

    // Initial model load
    updateModels();

    generateBtn.addEventListener('click', async () => {
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