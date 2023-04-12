from flask import Flask, request, render_template, redirect, url_for, flash, get_flashed_messages
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_required, login_user, logout_user
from werkzeug.security import generate_password_hash, check_password_hash
import secrets
from datetime import date

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
    
class Tarefas(db.Model):
    __tablename__ = "tarefas"
    id_tarefa = db.Column(db.Integer, primary_key=True)
    titulo_tarefa = db.Column(db.String(84), nullable=False)
    hora_tarefa = db.Column(db.String(84), nullable=False)
    prazo_tarefa = db.Column(db.String(84), nullable=False)
    prioridade = db.Column(db.String(84), nullable=False)
    
    def __str__(self):
        return self.titulo_tarefa
    

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

@app.route("/", methods=['GET','POST'])
def login():
    if request.method == "POST":
        email= request.form['email']
        senha = request.form['senha']
        usuario = Usuario.query.filter_by(email=email).first()
    
        if not usuario:
            flash('Usuário não encontrado!')
            return redirect(url_for("login"))
        
        if not check_password_hash(usuario.senha, senha):
            flash('Senha incorreta!')
            return redirect(url_for('login'))
        
        login_user(usuario)
        return redirect(url_for("tarefas"))
    return render_template('login.html')   

@app.route("/usuarios")
@login_required
def usuarios():
    usuarios = Usuario.query.all()
    return render_template('usuarios.html', usuarios=usuarios)  
@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route("/tarefas", methods=['GET', 'POST'])
@login_required
def tarefas():
    if request.method == "POST":
        tarefa= Tarefas()
        tarefa.titulo_tarefa = request.form['tarefa']
        tarefa.hora_tarefa = (date.today()).strftime("%d/%m/%Y")
        tarefa.prazo_tarefa = request.form['prazo']
        tarefa.prioridade = request.form['prioridade']
        db.session.add(tarefa)
        db.session.commit()
        return redirect(url_for('tarefas'))
    tarefas = Tarefas.query.all()
    return render_template('tarefas.html', tarefas=tarefas)

@app.route("/deletar/<int:id>")
@login_required
def deletar_tarefa(id):
    tarefa = Tarefas.query.filter_by(id_tarefa=id).first()
    db.session.delete(tarefa)
    db.session.commit()
    return redirect(url_for('tarefas'))

if __name__ == "__main__":
    app.run(debug=True)