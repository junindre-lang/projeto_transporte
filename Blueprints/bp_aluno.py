from flask import Blueprint, render_template

aluno = Blueprint('bp_aluno', __name__)

@aluno.route('/')
def index():
    return render_template('principal.html')
