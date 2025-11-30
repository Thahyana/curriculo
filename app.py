from flask import Flask, request, jsonify
from flask_cors import CORS
import os
from datetime import datetime
import google.generativeai as genai
from google.generativeai import types
import json
from pydantic import BaseModel, Field
import PyPDF2

app = Flask(__name__)
CORS(app)
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

api_key = os.environ.get("GEMINI_API_KEY")
if not api_key:
    print("ERRO: GEMINI_API_KEY não encontrada nas variáveis de ambiente.")
    print("Obtenha sua chave em aistudio.google.com")
    exit(1)

genai.configure(api_key=api_key)

class DadosCurriculo(BaseModel):
    nome_completo: str = Field(description="O nome completo da pessoa.")
    email: str = Field(description="O endereço de e-mail principal da pessoa.")
    telefone: str = Field(description="O número de telefone principal da pessoa, incluindo o código de área, se disponível.")
    cargo_desejado: str = Field(description="O cargo que o candidato está procurando.")
    experiencia_anos: int = Field(description="Total de anos de experiência profissional relevante (arredondado para o número inteiro mais próximo).")
    principais_habilidades: list[str] = Field(description="Lista das habilidades técnicas e comportamentais mais relevantes.")
    formacao_academica: str = Field(description="O nível de educação mais alto ou curso principal.")

def extract_text_from_pdf(pdf_path):
    with open(pdf_path, 'rb') as file:
        reader = PyPDF2.PdfReader(file)
        text = ""
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
    return text

def analyze_resume_with_ai(pdf_text):
    try:
        model_name = 'gemini-2.5-flash'

        prompt = f"""
        Analise o texto do currículo abaixo. Extraia as informações solicitadas no formato JSON definido pelo schema.
        Se um campo não for encontrado, use valores padrões apropriados (por exemplo, "Não especificado" ou 0 para anos).

        Texto do Currículo:
        {pdf_text[:15000]}
        """

        response = genai.Client().models.generate_content(
            model=model_name,
            contents=[prompt],
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=DadosCurriculo,
            ),
        )

        return json.loads(response.text)

    except Exception as e:
        print(f"Erro na análise de IA com structured output: {e}")
        return None

@app.route('/api/resumes', methods=['POST'])
def upload_resume():
    try:
        if 'resume' not in request.files:
            return jsonify({'error': 'Nenhum arquivo enviado'}), 400

        file = request.files['resume']
        name = request.form.get('name')
        email = request.form.get('email')
        phone = request.form.get('phone')

        if not file:
            return jsonify({'error': 'Arquivo não enviado'}), 400

        if not file.filename.endswith(('.pdf', '.doc', '.docx')):
            return jsonify({'error': 'Formato de arquivo inválido. Apenas PDF, DOC e DOCX são aceitos.'}), 400

        safe_email = email.replace('@', '_') if email else 'unknown'
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"{timestamp}_{safe_email}_{file.filename.split('/')[-1]}"
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        file.save(filepath)

        additional_data = {}
        if file.filename.endswith('.pdf'):
            try:
                pdf_text = extract_text_from_pdf(filepath)

                ai_analysis = analyze_resume_with_ai(pdf_text)
                print(f"DEBUG - Resposta da IA: {ai_analysis}")

                if ai_analysis:
                    additional_data['ai_extracted_data'] = ai_analysis

                    if not name and ai_analysis.get('nome_completo') not in ["Não especificado", ""]:
                        name = ai_analysis.get('nome_completo')
                    if not email and ai_analysis.get('email') not in ["Não especificado", ""]:
                        email = ai_analysis.get('email')
                    if not phone and ai_analysis.get('telefone') not in ["Não especificado", ""]:
                        phone = ai_analysis.get('telefone')

            except Exception as e:
                print(f"Erro ao processar PDF: {e}")
                additional_data['processing_error'] = str(e)

        resume_data = {
            'name': name,
            'email': email,
            'phone': phone,
            'filename': filename,
            'filepath': filepath,
            'uploaded_at': datetime.now().isoformat(),
            **additional_data
        }

        print(f"Currículo recebido: {resume_data}")

        return jsonify({
            'success': True,
            'message': 'Currículo enviado com sucesso',
            'data': {
                'id': 'resume_123',
                'name': name,
                'email': email,
                'ai_data': additional_data.get('ai_extracted_data')
            }
        }), 201

    except Exception as e:
        print(f"Erro ao processar requisição: {e}")
        return jsonify({'error': f'Erro ao processar currículo: {str(e)}'}), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'ok'}), 200

if __name__ == '__main__':
    app.run(debug=True, port=5000)
