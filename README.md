"# projeto_transporte"  

## PostgreSQL

A aplicação usa PostgreSQL por meio da variável de ambiente `DATABASE_URL`.
O valor padrão local é:

```text
postgresql+psycopg2://postgres:postgres@localhost:5432/projeto_transporte
```

Crie o banco e configure a conexão antes de iniciar:

```powershell
createdb projeto_transporte
$env:DATABASE_URL = "postgresql+psycopg2://usuario:senha@localhost:5432/projeto_transporte"
pip install -r requirements.txt
python servidor.py
```

As tabelas são criadas automaticamente pelo Flask-SQLAlchemy na primeira
execução. O arquivo SQLite antigo não é mais utilizado."
