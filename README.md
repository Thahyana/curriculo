# Sistema de Upload de Currículos

Sistema completo para upload e processamento de currículos com frontend em HTML/CSS/JavaScript e backend em Python Flask.

## 📋 Funcionalidades

- ✅ Upload de currículos (PDF, DOC, DOCX)
- ✅ Drag and drop de arquivos
- ✅ Validação de tamanho (máx. 5MB)
- ✅ Extração de texto de PDFs
- ✅ API REST para processamento
- ✅ Integração opcional com IA (Claude) para análise de currículos

## 🚀 Como Usar

### 1. Instalar Dependências Python

```bash
pip install -r requirements.txt
```

### 2. Iniciar o Backend

```bash
python app.py
```

O servidor Flask estará rodando em `http://localhost:5000`

### 3. Abrir o Frontend

Abra o arquivo `index.html` no seu navegador ou use um servidor local:

```bash
# Opção 1: Python
python -m http.server 8000

# Opção 2: Node.js (se tiver instalado)
npx serve
```

Acesse: `http://localhost:8000`

## 📁 Estrutura do Projeto

```
projeto curriculo/
├── index.html          # Página principal
├── style.css           # Estilos
├── script.js           # Lógica do frontend
├── app.py              # Backend Flask
├── requirements.txt    # Dependências Python
├── .env.example        # Exemplo de variáveis de ambiente
├── README.md           # Este arquivo
└── uploads/            # Pasta onde os currículos são salvos (criada automaticamente)
```

## 🔧 Configuração Opcional

### Usar IA para Análise de Currículos

1. Crie uma conta em [Anthropic](https://www.anthropic.com/)
2. Obtenha sua API key
3. Copie `.env.example` para `.env`
4. Adicione sua chave: `ANTHROPIC_API_KEY=sua_chave_aqui`
5. Descomente as linhas relacionadas ao Claude no `app.py`

### Integrar com Banco de Dados

O código já está preparado para integração com banco de dados. Exemplos incluídos:

- **SQLite** (mais simples)
- **PostgreSQL**
- **MongoDB**

Descomente o código relevante em `app.py` na função `upload_resume()`.

## 📝 API Endpoints

### POST `/api/resumes`

Envia um currículo.

**Body (multipart/form-data):**
- `resume`: arquivo (PDF, DOC, DOCX)
- `name`: nome completo
- `email`: email
- `phone`: telefone

**Resposta de Sucesso (201):**
```json
{
  "success": true,
  "message": "Currículo enviado com sucesso",
  "data": {
    "id": "resume_123",
    "name": "João Silva",
    "email": "joao@email.com"
  }
}
```

### GET `/api/health`

Verifica se o servidor está funcionando.

**Resposta (200):**
```json
{
  "status": "ok"
}
```

## 🛠️ Tecnologias Utilizadas

### Frontend
- HTML5
- CSS3 (com animações e gradientes modernos)
- JavaScript (ES6+)
- Fetch API

### Backend
- Python 3.x
- Flask
- Flask-CORS
- PyPDF2 (extração de texto de PDFs)
- Anthropic API (opcional, para IA)

## 📄 Licença

Este projeto possui licença MIT.
