from flask import *
from modelosDB.servidoresDB import *
from flask_sqlalchemy import SQLAlchemy
from DAOs.servidor_DAO import ServidorDAO
from modelos.admin import Admin
from modelos.usuario import Usuario
from modelos.veiculos import *


app = Flask(__name__)


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
        ServidorDAO.salvar(nome=nome, email=email, matricula=matri, senha=senha, senha1=senha1)
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

@app.route('/login_adm', methods=['POST', 'GET'])
def login_adm():
    login = request.form.get('mat')
    senha = request.form.get('senha')

    if senha == '123' and login == 'sales':
        texto = 'bem vindo Sales!'
        return render_template('admin.html', msg=texto)
    else:
        texto = 'admin não encontrado'
        return render_template('login_adm.html', msg = texto)
@app.route('/logarlink_adm')
def logarlink_adm():
    return render_template('login_adm.html')

@app.route('/lista_servidores')
def listar_sevidores():
    return render_template('lista_servidores.html')

@app.route('/cad_motor')
def listar_motoristas ():
    return render_template('cadastrar_motorista.html')

@app.route('/cad_veiculos')
def cadastrar_vei():
    prefixo = request.form.get('prefixo')
    modelo = request.form.get('modelo')
    placa = request.form.get('placa')
    capacidade = request.form.get('capacidade')
    status = request.form.get('status')

    return render_template('cad_veiculos.html')

@app.route('/pag_admin')
def principal():
    return render_template('admin.html')

if __name__ == '__main__':
        app.run(debug=True)
