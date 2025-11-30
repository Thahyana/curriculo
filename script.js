const uploadArea = document.getElementById('uploadArea');
const fileInput = document.getElementById('fileInput');
const fileInfo = document.getElementById('fileInfo');
const fileName = document.getElementById('fileName');
const form = document.getElementById('uploadForm');
const successMessage = document.getElementById('successMessage');
const submitBtn = document.getElementById('submitBtn');

uploadArea.addEventListener('click', () => fileInput.click());

uploadArea.addEventListener('dragover', (e) => {
    e.preventDefault();
    uploadArea.classList.add('dragover');
});

uploadArea.addEventListener('dragleave', () => {
    uploadArea.classList.remove('dragover');
});

uploadArea.addEventListener('drop', (e) => {
    e.preventDefault();
    uploadArea.classList.remove('dragover');
    const files = e.dataTransfer.files;
    if (files.length > 0) {
        fileInput.files = files;
        displayFileName(files[0]);
    }
});

fileInput.addEventListener('change', (e) => {
    if (e.target.files.length > 0) {
        displayFileName(e.target.files[0]);
    }
});

function displayFileName(file) {
    fileName.textContent = `✓ ${file.name} (${(file.size / 1024).toFixed(2)} KB)`;
    fileInfo.classList.add('show');

    uploadArea.classList.add('uploaded');
    uploadArea.querySelector('.upload-icon').textContent = '✅';
    uploadArea.querySelector('.upload-text').textContent = 'Currículo adicionado com sucesso!';
    uploadArea.querySelector('.upload-hint').textContent = 'Clique para alterar o arquivo';

    // Esconder resultados anteriores se houver
    const resultsContainer = document.getElementById('resultsContainer');
    if (resultsContainer) {
        resultsContainer.style.display = 'none';
    }
}

form.addEventListener('submit', async (e) => {
    e.preventDefault();

    // Validar se há arquivo selecionado
    if (!fileInput.files || fileInput.files.length === 0) {
        alert('Por favor, selecione um arquivo antes de enviar.');
        return;
    }

    // Validar tamanho do arquivo (5MB)
    const maxSize = 5 * 1024 * 1024; // 5MB em bytes
    if (fileInput.files[0].size > maxSize) {
        alert('O arquivo é muito grande. Tamanho máximo: 5MB');
        return;
    }

    submitBtn.disabled = true;
    submitBtn.textContent = 'Enviando...';

    try {
        // Preparar dados do formulário
        const formData = new FormData();
        formData.append('resume', fileInput.files[0]);
        // name, email, phone agora são extraídos pelo backend

        // Enviar para o backend
        const response = await fetch('http://localhost:5000/api/resumes', {
            method: 'POST',
            body: formData
        });

        const result = await response.json();

        if (response.ok && result.success) {
            // Sucesso
            form.style.display = 'none';
            successMessage.classList.add('show');

            // Mostrar dados extraídos pela IA
            if (result.data && result.data.ai_data) {
                const aiData = result.data.ai_data;
                const resultsContainer = document.getElementById('resultsContainer');
                const extractedData = document.getElementById('extractedData');

                let html = '<ul style="list-style: none; padding: 0;">';
                html += `<li><strong>Nome:</strong> ${aiData.nome_completo || 'Não encontrado'}</li>`;
                html += `<li><strong>Email:</strong> ${aiData.email || 'Não encontrado'}</li>`;
                html += `<li><strong>Telefone:</strong> ${aiData.telefone || 'Não encontrado'}</li>`;

                if (aiData.principais_habilidades) {
                    html += `<li><strong>Habilidades:</strong> ${Array.isArray(aiData.principais_habilidades) ? aiData.principais_habilidades.join(', ') : aiData.principais_habilidades}</li>`;
                }

                html += '</ul>';

                extractedData.innerHTML = html;
                resultsContainer.style.display = 'block';
            }

            setTimeout(() => {
                form.reset();
                fileInfo.classList.remove('show');
                form.style.display = 'block';
                successMessage.classList.remove('show');
                submitBtn.disabled = false;
                submitBtn.textContent = 'Enviar Currículo';

                uploadArea.classList.remove('uploaded');
                uploadArea.querySelector('.upload-icon').textContent = '📄';
                uploadArea.querySelector('.upload-text').textContent = 'Clique ou arraste seu currículo aqui';
                uploadArea.querySelector('.upload-hint').textContent = 'PDF, DOC ou DOCX (máx. 5MB)';
            }, 3000);
        } else {
            // Erro do servidor
            alert(result.error || 'Erro ao enviar currículo. Tente novamente.');
            submitBtn.disabled = false;
            submitBtn.textContent = 'Enviar Currículo';
        }
    } catch (error) {
        // Erro de conexão
        console.error('Erro:', error);
        alert('Erro ao conectar com o servidor. Verifique se o backend está rodando.');
        submitBtn.disabled = false;
        submitBtn.textContent = 'Enviar Currículo';
    }
});