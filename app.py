from flask import Flask, request, render_template, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_required, login_user, logout_user
from werkzeug.security import generate_password_hash, check_password_hash
import secrets

app = Flask(__name__)
#ENDEREÇO DO BANCO
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///app.db"
#CONECTANDO MINHA APLICAÇÃO AO GERENCIADOR DE LOGINS
login_manager = LoginManager(app)
#CONECTANDO A CLASSE SQL ALCHEMY A MINHA APLICAÇÃO
db = SQLAlchemy(app)
#Traz o contexto atual
app.app_context().push()
#Gera uma chave aleatória de sessão
app.config['SECRET_KEY'] = secrets.token_hex(16)
# app.config['PERMANENT_SESSION_LIFETIME'] = False

@login_manager.user_loader
def current_user(user_id):
    return Usuario.query.get(user_id)


class Usuario(db.Model, UserMixin):
    __tablename__ = "usuario"
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(84), nullable=False)
    email = db.Column(db.String(84), nullable=False, unique=True, index=True)
    senha = db.Column(db.String(84), nullable=False)    

    def __str__(self):
        return self.nome
db.create_all()    


@app.route("/cadastro", methods=['GET','POST'])
def cadastro():
    if request.method == "POST":
        usuario = Usuario()
        usuario.nome = request.form['nome']
        usuario.email = request.form['email']
        usuario.senha = generate_password_hash(request.form['senha'])    

        db.session.add(usuario)
        db.session.commit()
    return render_template('cadastro.html')

@app.route("/login", methods=['GET','POST'])
def login():
    if request.method == "POST":
        email= request.form['email']
        senha = request.form['senha']
        usuario = Usuario.query.filter_by(email=email).first()
    
        if not usuario:
            return redirect(url_for("login"))
        
        if not check_password_hash(usuario.senha, senha):
            return redirect(url_for('login'))
        
        login_user(usuario)
        return redirect(url_for("index"))
    return render_template('login.html')   

@app.route("/")
@login_required
def index():
    usuarios = Usuario.query.all()
    return render_template('index.html', usuarios=usuarios)  
@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('login'))

if __name__ == "__main__":
    app.run(debug=True)