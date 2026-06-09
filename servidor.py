# servidor.py
from flask import Flask, render_template, request, redirect, url_for
from extensions import db
from DAOs.servidor_DAO import ServidorDAO
from modelosDB.modelos import Veiculo, Motorista
from Blueprints.bp_admin import admin_bp
from Blueprints.bp_servidor import servidor_bp

app = Flask(__name__)
app.secret_key = "secret_key_expresso_federal"

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///meubanco.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Inicializa o banco com a estratégia correta de desacoplamento
db.init_app(app)

# Registra o Blueprint do Admin de forma limpa
app.register_blueprint(admin_bp)
app.register_blueprint(servidor_bp)

with app.app_context():
    db.create_all()


@app.route('/')
def inicial():
    return render_template('principal.html')


@app.route('/cadastrar', methods=['POST'])
def cadastro():
    nome = request.form.get('nome')
    email = request.form.get('email')
    matri = request.form.get('matri')
    senha = request.form.get('sen')
    senha1 = request.form.get('sen1')

    if senha != senha1:
        return render_template('cadastro.html', msg='As senhas não coincidem!')

    ServidorDAO.salvar(nome=nome, email=email, matricula=matri, senha=senha)
    return render_template('principal.html', msg='Servidor cadastrado com sucesso!')


@app.route('/logar', methods=['POST'])
def login():
    login_mat = request.form.get('mat')
    senha = request.form.get('senha')

    servidor = ServidorDAO.autenticar(matricula=login_mat, senha=senha)

    if not servidor:
        return render_template('principal.html', msg='Matrícula ou senha incorretos.')

    if servidor.status != 'Ativo':
        return render_template('principal.html', msg='Cadastro aguardando aprovação administrativa.')

    return render_template('homepage.html', servidor=servidor)


@app.route('/cadastrolink')
def cadastrolink():
    return render_template('cadastro.html')


@app.route('/logarlink')
def logarlink():
    return render_template('principal.html')


@app.route('/login_adm', methods=['GET', 'POST'])
def login_adm():
    if request.method == 'POST':
        login_mat = request.form.get('mat')
        senha = request.form.get('senha')

        if senha == '123' and login_mat == 'sales':
            return redirect(url_for('bp_admin.index'))
        else:
            return render_template('login_adm.html', msg='Admin não encontrado ou senha incorreta')
    return render_template('login_adm.html')


@app.route('/logarlink_adm')
def logarlink_adm():
    return render_template('login_adm.html')


@app.route('/lista_servidores')
def listar_servidores():
    lista = ServidorDAO.listar()
    return render_template('lista_servidores.html', servidores=lista)


@app.route('/cad_motor', methods=['GET', 'POST'])
def listar_motoristas():
    if request.method == 'POST':
        matricula = request.form.get('matricula')
        nome = request.form.get('nome')
        cnh = request.form.get('cnh')
        categoria = request.form.get('categoria')
        validade = request.form.get('validade_cnh')

        novo_motorista = Motorista(matricula=matricula, nome=nome, cnh=cnh, categoria=categoria, validade_cnh=validade)
        db.session.add(novo_motorista)
        db.session.commit()
        return redirect(url_for('listar_motoristas'))

    motoristas = Motorista.query.all()
    return render_template('cadastrar_motorista.html', motoristas=motoristas)


@app.route('/cad_veiculos', methods=['GET', 'POST'])
def cadastrar_vei():
    if request.method == 'POST':
        prefixo = request.form.get('prefixo')
        modelo = request.form.get('modelo')
        placa = request.form.get('placa')
        capacidade = int(request.form.get('capacidade', 0))
        status = request.form.get('status')

        novo_veiculo = Veiculo(prefixo=prefixo, modelo=modelo, placa=placa, capacidade=capacidade, status=status)
        db.session.add(novo_veiculo)
        db.session.commit()
        return redirect(url_for('cadastrar_vei'))

    lista_veiculos = Veiculo.query.all()
    return render_template('cad_veiculos.html', lista_veiculos=lista_veiculos)


if __name__ == '__main__':
    app.run(debug=True)