from flask import *
from Blueprints.bp_aluno import aluno
from modelos.usuario import Usuario

usuarios = []

app = Flask(__name__)
app.register_blueprint(aluno, url_prefix='/')


@app.route('/')
def inicial():
    return render_template('principal.html')

@app.route('/cadastrar', methods=['GET','POST'])
def cadastro():
    nome = request.form.get('nome')
    email = request.form.get('email')
    matri = request.form.get('matri')
    senha = request.form.get('sen')
    senha1 = request.form.get('sen1')
    if senha != senha1:
        return render_template('cadastro.html', msg='As senhas não coincidem!')
    else:
        novo_user = Usuario(nome=nome, matricula=matri, email=email, senha=senha, senha1=senha1)
        usuarios.append(novo_user)
        texto = 'aluno cadastrado com sucesso!'
        return render_template('principal.html', msg=texto)


@app.route('/logar', methods=['GET','POST'])
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



@app.route('/cadastrolink')
def cadastrolink():
    return render_template('cadastro.html')

@app.route('/logarlink')
def logarlink():
    return render_template('principal.html')

@app.route('/login_adm')
def login_adm():
    login = request.form.get('matricula')
    senha = request.form.get('senha')

    if senha == '123' and login == 'sales':
        texto = 'bem vindo Sales!'
        return render_template('admin.html', msg=texto)
    else:
        texto = 'admin não encontrado'
        return render_template('login_adm.html', msg = texto)

if __name__ == '__main__':
        app.run(debug=True)

