from flask import Flask, request, jsonify
from flask_cors import CORS
import os
from datetime import datetime
import PyPDF2
import google.generativeai as genai  # Gemini API para extrair dados do PDF
import json

app = Flask(__name__)
CORS(app)  # Permitir requisições do frontend

# Configurações
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Inicializar cliente Gemini
api_key = os.environ.get("GEMINI_API_KEY")
if not api_key:
    print("AVISO: GEMINI_API_KEY não encontrada no arquivo .env")

genai.configure(api_key=api_key)
model = genai.GenerativeModel('gemini-pro')

def extract_text_from_pdf(pdf_path):
    """Extrai texto do PDF"""
    with open(pdf_path, 'rb') as file:
        reader = PyPDF2.PdfReader(file)
        text = ""
        for page in reader.pages:
            text += page.extract_text()
    return text



def analyze_resume_with_ai(pdf_text):
    """
    Usa Gemini para extrair informações estruturadas do currículo
    """
    try:
        prompt = f"""Analise este currículo e extraia as seguintes informações em formato JSON:
        - nome_completo
        - email
        - telefone
        - cargo_desejado
        - experiencia_anos
        - principais_habilidades (lista)
        - formacao_academica
        
        Currículo:
        {pdf_text}
        
        Retorne APENAS o JSON, sem explicações, sem blocos de código (```json ... ```). Apenas o objeto JSON cru."""

        response = model.generate_content(prompt)
        text_response = response.text
        
        # Limpar possíveis blocos de código markdown
        if "```json" in text_response:
            text_response = text_response.replace("```json", "").replace("```", "")
        elif "```" in text_response:
             text_response = text_response.replace("```", "")
             
        # Tentar fazer o parse do JSON
        try:
            return json.loads(text_response.strip())
        except json.JSONDecodeError:
            print(f"Erro ao decodificar JSON da IA: {text_response}")
            return None
            
    except Exception as e:
        print(f"Erro na análise de IA: {e}")
        return None

@app.route('/api/resumes', methods=['POST'])
def upload_resume():
    try:
        # Verificar se o arquivo foi enviado
        if 'resume' not in request.files:
            return jsonify({'error': 'Nenhum arquivo enviado'}), 400
        
        file = request.files['resume']
        name = request.form.get('name')
        email = request.form.get('email')
        phone = request.form.get('phone')
        
        # Validar dados
        # Validar dados (apenas arquivo é obrigatório agora)
        if not file:
            return jsonify({'error': 'Arquivo não enviado'}), 400
        
        # Validar tipo de arquivo
        if not file.filename.endswith(('.pdf', '.doc', '.docx')):
            return jsonify({'error': 'Formato de arquivo inválido'}), 400
        
        # Salvar arquivo com nome único
        # Se não tiver email, usa 'unknown' no nome do arquivo
        safe_email = email.replace('@', '_') if email else 'unknown'
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"{timestamp}_{safe_email}_{file.filename}"
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        file.save(filepath)
        
        # Extrair texto do PDF (se for PDF)
        additional_data = {}
        if file.filename.endswith('.pdf'):
            try:
                pdf_text = extract_text_from_pdf(filepath)
                
                # Usar IA para extrair dados estruturados
                ai_analysis = analyze_resume_with_ai(pdf_text)
                print(f"DEBUG - Resposta da IA: {ai_analysis}")
                
                if ai_analysis:
                    additional_data['ai_extracted_data'] = ai_analysis
                    
                    # Se os campos não vieram do form, tentar pegar da IA
                    if not name and ai_analysis.get('nome_completo'):
                        name = ai_analysis.get('nome_completo')
                    if not email and ai_analysis.get('email'):
                        email = ai_analysis.get('email')
                    if not phone and ai_analysis.get('telefone'):
                        phone = ai_analysis.get('telefone')
                
            except Exception as e:
                print(f"Erro ao processar PDF: {e}")
        
        # Salvar no banco de dados
        resume_data = {
            'name': name,
            'email': email,
            'phone': phone,
            'filename': filename,
            'filepath': filepath,
            'uploaded_at': datetime.now().isoformat(),
            **additional_data
        }
        
        # AQUI: Salvar no seu banco de dados (MongoDB, PostgreSQL, etc)
        # ...
        
        print(f"Currículo recebido: {resume_data}")
        
        return jsonify({
            'success': True,
            'message': 'Currículo enviado com sucesso',
            'data': {
                'id': 'resume_123',  # ID gerado pelo banco
                'name': name,
                'email': email,
                'ai_data': additional_data.get('ai_extracted_data')
            }
        }), 201
        
    except Exception as e:
        print(f"Erro ao processar requisição: {e}")
        return jsonify({'error': 'Erro ao processar currículo'}), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'ok'}), 200

if __name__ == '__main__':
    app.run(debug=True, port=5000)