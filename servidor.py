from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from sqlalchemy import inspect, text
from extensions import db
from DAOs.servidor_DAO import ServidorDAO
from modelosDB.modelos import Veiculo, Motorista
from Blueprints.bp_admin import admin_bp
from Blueprints.bp_servidor import servidor_bp
from Blueprints.bp_motorista import bp_motorista

app = Flask(__name__)
app.secret_key = "klnhgcxs65d7fgohivyes3aerty98hgfxze5aws4e5df6g9yitres5df6giyvcxzas4e5r68gigfhdszadddfgfxgdzfxgchgchxgdzl.ko,mijhuggybtrfaludopix"

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///meubanco.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Inicializa o banco com a estratégia correta de desacoplamento
db.init_app(app)

# Registra o Blueprint do Admin de forma limpa
app.register_blueprint(admin_bp)
app.register_blueprint(servidor_bp)
app.register_blueprint(bp_motorista)

# Cria as tabelas de forma segura dentro do contexto correto
with app.app_context():
    db.create_all()
    # create_all não altera tabelas SQLite já existentes. Esta migração pequena
    # preserva o banco atual e permite vincular cada viagem ao seu motorista.
    colunas = {col['name'] for col in inspect(db.engine).get_columns('solicitacoes_viagem')}
    if 'motorista_id' not in colunas:
        db.session.execute(text('ALTER TABLE solicitacoes_viagem ADD COLUMN motorista_id INTEGER'))
        db.session.commit()


@app.route('/')
def inicial():
    return render_template('auth/principal.html')


@app.route('/cadastrar', methods=['POST'])
def cadastro():
    nome = request.form.get('nome')
    email = request.form.get('email')
    matri = request.form.get('matri')
    senha = request.form.get('sen')
    senha1 = request.form.get('sen1')

    if senha != senha1:
        return render_template('auth/cadastro.html', msg='As senhas não coincidem!')

    ServidorDAO.salvar(nome=nome, email=email, matricula=matri, senha=senha)
    return render_template('auth/principal.html', msg='Servidor cadastrado com sucesso!')


@app.route('/cadastrolink')
def cadastrolink():
    return render_template('auth/cadastro.html')


@app.route('/logarlink')
def logarlink():
    return render_template('auth/principal.html')


@app.route('/logar', methods=['POST'])
def login():
    login_mat = request.form.get('mat')
    senha = request.form.get('senha')

    print(f"\n--- DETETIVE DO LOGIN ---")
    print(f"Recebido do HTML -> Matrícula: '{login_mat}', Senha: '{senha}'")

    servidor = ServidorDAO.autenticar(matricula=login_mat, senha=senha)
    print(f"Busca no Banco (Servidor encontrado?): {servidor}")

    if not servidor:
        print("❌ Barrado no Portão 1: Usuário ou senha inválidos.")
        return render_template('auth/principal.html', msg='Matrícula ou senha incorretos.')

    print(f"Status do usuário no banco: '{servidor.status}'")
    if servidor.status != 'Ativo':
        print("❌ Barrado no Portão 2: Usuário encontrado, mas status não é 'Ativo'.")
        return render_template('auth/principal.html', msg='Cadastro aguardando aprovação administrativa.')

    session['servidor'] = login_mat
    print("✅ SUCESSO! Indo para a homepage.html")
    return render_template('servidor/homepage.html', servidor=servidor)


@app.route('/login_adm', methods=['GET', 'POST'])
def login_adm():
    if request.method == 'POST':
        login_mat = request.form.get('mat')
        senha = request.form.get('senha')

        if senha == '123' and login_mat == 'sales':
            session['admin'] = login_mat
            return redirect(url_for('bp_admin.index'))
        else:
            return render_template('auth/login_adm.html', msg='Admin não encontrado ou senha incorreta')
    return render_template('auth/login_adm.html')


@app.route('/logarlink_adm')
def logarlink_adm():
    return render_template('auth/login_adm.html')


@app.route('/lista_servidores')
def listar_servidores():
    lista = ServidorDAO.listar()
    return render_template('admin/lista_servidores.html', servidores=lista)


@app.route('/cad_motor', methods=['GET', 'POST'])
def listar_motoristas():
    if request.method == 'POST':
        matricula = request.form.get('matricula')
        nome = request.form.get('nome')
        cnh = request.form.get('cnh')
        categoria = request.form.get('categoria')
        validade = request.form.get('validade_cnh')

        # Agora o construtor mapeia os campos opcionais sem falhar por falta de parâmetro
        novo_motorista = Motorista(
            matricula=matricula,
            nome=nome,
            cnh=cnh,
            categoria=categoria,
            validade_cnh=validade
        )
        db.session.add(novo_motorista)
        db.session.commit()
        return redirect(url_for('listar_motoristas'))

    motoristas = Motorista.query.all()
    return render_template('admin/cadastrar_motorista.html', motoristas=motoristas)


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
    return render_template('admin/cad_veiculos.html', lista_veiculos=lista_veiculos)


@app.route('/motora', methods=['GET', 'POST'])
def pagina_motorista():
    return render_template('motorista/login_motorista.html')




if __name__ == '__main__':
    app.run(debug=True)
