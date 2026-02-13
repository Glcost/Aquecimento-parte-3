from flask import Flask, render_template, redirect, request, flash, send_file, session
import requests
import io

app = Flask(__name__)
app.secret_key = 'chave_secreta_do_jaime' # SEMPRE necessária para session

ENDPOINT_API = 'https://api.thecatapi.com/v1/images/search'

@app.route('/', methods=['GET'])
def index():
    # Aqui o Flask apenas lê o que está guardado
    nome = session.get('nome')
    url_imagem = session.get('url_imagem')
    return render_template('index.html', nome=nome, url_imagem=url_imagem)

@app.route("/gato", methods=['POST'])
def gato():
    nome = request.form.get('nome')
    
    if not nome:
        flash("ERRO! Digite um nome")
        return redirect("/")

    resposta = requests.get(ENDPOINT_API, timeout=5)
    
    if resposta.status_code == 200:
        dados = resposta.json()
        
        # SALVAMOS NA SESSÃO
        session['nome'] = nome
        session['url_imagem'] = dados[0]['url']
        
        # O PULO DO GATO: Não use render_template aqui!
        # Use o redirect para a home. Isso "limpa" o envio do formulário.
        return redirect('/')
    
    return redirect('/')

@app.route("/baixar")
def baixar():
    # Pegamos a URL direto da sessão para não ter erro
    url = session.get('url_imagem')
    nome_usuario = session.get('nome', 'gatinho')

    if not url:
        return redirect('/')

    resposta_imagem = requests.get(url)
    if resposta_imagem.status_code == 200:
        imagem_memoria = io.BytesIO(resposta_imagem.content)
        imagem_memoria.seek(0) 
        
        return send_file(
            imagem_memoria,
            mimetype=resposta_imagem.headers.get('Content-Type', 'image/jpeg'),
            as_attachment=True,
            download_name=f"gatinho_do_{nome_usuario}.jpg"
        )
    return "Erro", 500

# Rota para quando quiser trocar de gato de propósito
@app.route("/limpar")
def limpar():
    session.clear()
    return redirect("/")

if __name__ == '__main__':
    app.run(debug=True)