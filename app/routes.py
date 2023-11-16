from flask import request, jsonify, render_template, url_for, flash, redirect
from app import app, db
from sqlalchemy.exc import IntegrityError
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, login_required, current_user
from datetime import datetime
from app.models.modelos import Carro, Lance, PostDeVenda, Usuario
from flask_bcrypt import Bcrypt

bcrypt = Bcrypt(app)

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/login', methods=['GET', 'POST'])
def login_post():
    if current_user.is_authenticated:
        # Se o usuário já estiver autenticado, redirecione para a página desejada
        return redirect(url_for('profile'))

    if request.method == 'POST':
        # Lógica de login aqui
        email = request.form.get('email')
        password = request.form.get('password')
        remember = True if request.form.get('remember') else False

        usuario = Usuario.query.filter_by(email=email).first()

        if usuario and bcrypt.check_password_hash(usuario.senha, password):
            login_user(usuario, remember=remember)
            return redirect(url_for('profile'))
        else:
            flash('Login falhou. Verifique seu nome de usuário e senha.', 'danger')

    return render_template('login.html')
    

@app.route('/signup', methods=['GET', 'POST'])
def signup_post():
    if request.method == 'POST':
        email = request.form.get('email')
        nome = request.form.get('name')
        password = request.form.get('password')

        if not email or not nome or not password:
            flash('Por favor, preencha todos os campos.', 'danger')
            return redirect(url_for('signup'))

        usuario = Usuario.query.filter_by(email=email).first()

        if usuario:
            flash('Email já cadastrado', 'danger')
            return redirect(url_for('signup'))

        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
        new_usuario = Usuario(email=email, nome=nome, senha=hashed_password)

        db.session.add(new_usuario)
        db.session.commit()

        flash('Registro bem-sucedido! Faça o login para continuar.', 'success')
        return redirect(url_for('login_post'))

    return render_template('signup.html')

@app.route('/logout')
def logout():
    return redirect(url_for('login_post'))


@app.route('/profile')
@login_required
def profile():
    return render_template('profile.html', name=current_user.nome)

