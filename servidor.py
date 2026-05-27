from flask import *
from Blueprints.bp_aluno import aluno
from modelosDB.servidoresDB import *
from flask_sqlalchemy import SQLAlchemy
from DAOs.servidor_DAO import ServidorDAO



app = Flask(__name__)
app.register_blueprint(aluno, url_prefix='/')

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///meubanco.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

with app.app_context():
    db.create_all()

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
        ServidorDAO.salvar(matricula=matri, senha=senha1)
        texto = 'aluno cadastrado com sucesso!'
        return render_template('principal.html', msg=texto)


@app.route('/logar', methods=['GET','POST'])
def login():

    if request.method == 'POST':
        login = request.form.get('mat')
        senha = request.form.get('senha')

        servidor = ServidorDAO.autenticar(matricula=login, senha=senha)

        if not servidor:
            return render_template('principal.html')

        if not servidor.aprovado:
            return render_template('principal.html')

        return render_template('')





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

