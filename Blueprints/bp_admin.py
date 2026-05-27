from flask  import Blueprint, render_template
from modelosDB.servidoresDB import *
admin = Blueprint('bp_aluno', __name__)

@admin.route('/')
def index():
    return render_template('admin.html')


#rotas para ver servidores aprovados pelo admin no sistema
@admin.route('/listar')
def listar_servidores():
    return render_template('listarservidores.html')

@admin.route('/excluir')
def remover_servidores():
    pass


#rotas para permitir os servidores a entrar



