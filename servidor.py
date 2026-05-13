from flask import *
from Blueprints.bp_aluno import aluno

usuarios = []

app = Flask(__name__)
app.register_blueprint(aluno, url_prefix='/')


@app.route('/')
def inicial():
    render_template('principal.html')

@app.route('/logar', methods=['POST'])
def login():
    login = request.form.get('mat')
    senha = request.form.get('senha')
    logado = False
    for u in usuarios:
        if login == u.get_matricula() and senha == u.get_senha():
            logado = True
            break
    if logado:
        return render_template('homepage.html')
    else:
        texto = 'matrícula ou senha incorretos'
        return render_template('principal.html' , msg = texto)

if __name__ == '__main__':
    app.run()