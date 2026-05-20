from flask  import Blueprint, render_template
admin = Blueprint('bp_aluno', __name__)

@admin.route('/')
def index():
    return render_template('admin.html')

