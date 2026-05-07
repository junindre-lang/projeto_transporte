from flask import*
from modelos.usuario import Usuario

app = Flask(__name__)

@app.route('/')
def inicial():
    render_template('principal.html')

if __name__ == '__main__':
    app.run()