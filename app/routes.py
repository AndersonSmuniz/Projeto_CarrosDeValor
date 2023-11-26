from flask import request, jsonify, render_template, url_for, flash, redirect
from app import app, db, allowed_file
from sqlalchemy.exc import IntegrityError
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, login_required, current_user, logout_user
from app.models.modelos import Carro, Lance, Usuario, Favorito
from werkzeug.utils import secure_filename
import os
from datetime import datetime
from flask_bcrypt import Bcrypt

bcrypt = Bcrypt(app)

@app.route('/')
def index():
    carros = Carro.query.all()
    
    return render_template('dashboard.html', carros=carros)


@app.route('/login', methods=['GET', 'POST'])
def login_post():
    if current_user.is_authenticated:  
        return redirect(url_for('index'))

    elif request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        usuario = Usuario.query.filter_by(email=email).first()
        
        if usuario and bcrypt.check_password_hash(usuario.senha, password):
            login_user(usuario)
            return redirect(url_for('index'))
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
            return redirect(url_for('signup_post'))

        usuario = Usuario.query.filter_by(email=email).first()

        if usuario:
            flash('Email já cadastrado', 'danger')
            return redirect(url_for('signup_post'))

        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
        new_usuario = Usuario(email=email, nome=nome, senha=hashed_password)

        db.session.add(new_usuario)
        db.session.commit()

        flash('Registro bem-sucedido! Faça o login para continuar.', 'success')
        return redirect(url_for('login_post'))

    return render_template('signup.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login_post'))


@app.route('/profile')
@login_required
def profile():
    return render_template('profile.html', name=current_user.nome)

########### Carro ##############

@app.route('/cadastrar_carro', methods=['GET', 'POST'])
@login_required
def cadastrar_carro():
    if request.method == 'POST':
        modelo = request.form['modelo']
        ano = request.form['ano']
        imagem = request.files['imagem']
        descricao = request.form['descricao']
        preco = request.form['preco']
        negociavel = bool(request.form['negociavel'])
        tempo_duracao = request.form['tempo_duracao']

        usuario_id = current_user.id
        usuario = Usuario.query.get(usuario_id)

        if not usuario:
            return redirect(url_for('login_post'))

        if imagem and allowed_file(imagem.filename):
            filename = secure_filename(imagem.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)

            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            imagem.save(file_path)

            carro = Carro(modelo=modelo, ano=ano, usuario=usuario, imagem='imagens/' + filename, descricao=descricao,
                          preco=preco, negociavel=negociavel, tempo_duracao=tempo_duracao)
        else:
            carro = Carro(modelo=modelo, ano=ano, usuario=usuario, imagem=None, descricao=descricao, preco=preco,
                          negociavel=negociavel, tempo_duracao=tempo_duracao)

        db.session.add(carro)
        db.session.commit()

        return redirect(url_for('minhas_vendas'))

    return render_template('cadastrar_carro.html')


@app.route('/atualizar_carro/<int:carro_id>', methods=['GET', 'POST'])
@login_required
def atualizar_carro(carro_id):
    carro = Carro.query.get(carro_id)

    if not carro:
        flash('Carro não encontrado', 'danger')
        return redirect(url_for('minhas_vendas'))

    if request.method == 'POST':
        modelo = request.form['modelo']
        ano = request.form['ano']
        nova_imagem = request.files['imagem']
        descricao = request.form['descricao']
        preco = request.form['preco']
        negociavel = (request.form['negociavel'] == True)
        tempo_duracao = request.form['tempo_duracao']

        print(negociavel) 
        if not carro.usuario_id == current_user.id:
            flash('Você não tem permissão para acessar este carro', 'danger')
            return redirect(url_for('minhas_vendas'))

        if nova_imagem and allowed_file(nova_imagem.filename):
            filename = secure_filename(nova_imagem.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], str(carro_id) + filename)
            nova_imagem.save(file_path)
            carro.imagem = 'imagens/' + str(carro_id) + filename

        carro.modelo = modelo
        carro.ano = ano
        carro.descricao = descricao
        carro.preco = preco
        carro.negociavel = negociavel
        carro.tempo_duracao = tempo_duracao
        db.session.commit()

        return redirect(url_for('minhas_vendas'))

    return render_template('cadastrar_carro.html', carro=carro)

@app.route('/excluir_carro/int:<id>', methods=['GET','POST'])
@login_required
def excluir_carro():
    if request.method == 'POST':
        carro_id = request.form['carro_id']
        
        carro = Carro.query.get(carro_id)
        if not carro:
            return redirect(url_for('minhas_vendas'))
        
        if not carro.usuario_id == current_user.id:
            flash('Você não tem permissão para acessar este carro', 'danger')
            return redirect(url_for('minhas_vendas'))
        
        db.session.delete(carro)
        db.session.commit()
        
        return redirect(url_for('minhas_vendas'))
    
    carro = Carro.query.get(carro_id)
    return render_template('excluir_carro.html', carro= carro)


######### Paginas ###############
@app.route('/minhas_vendas')
@login_required
def minhas_vendas():
    usuario_id = current_user.id

    usuario = Usuario.query.get(usuario_id)
    if not usuario:
        return redirect(url_for('login_post'))
    
    carros = Carro.query.filter_by(usuario_id=usuario_id).all()
    
    return render_template('minhas_vendas.html', carros=carros)

@app.route('/carro/<int:carro_id>')
@login_required
def exibir_carro(carro_id):
    carro = Carro.query.get(carro_id)
    if not carro:
        return redirect(url_for('index'))
    
    if carro.usuario_id == current_user.id:
        print(carro_id, Lance.query.filter_by(carro_id=carro_id).all())
        
        lances_recebidos = Lance.query.filter_by(carro_id=carro_id).all()
        return render_template('info.html', carro=carro, usuario_logado=current_user, lances_recebidos=lances_recebidos)
        
    else:
        lances_dados = Lance.query.filter_by(usuario_id=current_user.id).all()    
        return render_template('info.html', carro=carro, usuario_logado=current_user, lances_dados=lances_dados)

#######Lance########

@app.route('/realizar_lance/<int:carro_id>', methods=['POST'])
@login_required
def realizar_lance(carro_id):
    carro = Carro.query.get(carro_id)
    if not carro:
        return jsonify({'status': 'error', 'message': 'Carro não encontrado.'}), 404

    if not carro.negociavel:
        return jsonify({'status': 'error', 'message': 'Este carro não é negociável.'}), 400

    valor_lance = float(request.form['valor'])
    novo_lance = Lance(valor=valor_lance, carro=carro, usuario=current_user)
    db.session.add(novo_lance)
    db.session.commit()

    return redirect(url_for('exibir_carro', carro_id=carro_id))

@app.route('/parar_lances/<int:carro_id>', methods=['POST'])
@login_required
def parar_lances(carro_id):
    carro = Carro.query.get(carro_id)
    if not carro:
        return jsonify({'status': 'error', 'message': 'Carro não encontrado.'}), 404

    if carro.usuario_id != current_user.id:
        return jsonify({'status': 'error', 'message': 'Você não é o proprietário deste carro.'}), 403

    carro.tempo_termino = datetime.utcnow()
    db.session.commit()

    return jsonify({'status': 'success', 'message': 'Lances parados com sucesso.'})

@app.route('/meus_lances')
@login_required
def meus_lances():
    lances_dados = Lance.query.filter_by(usuario_id=current_user.id).all()
    return render_template('lances_dados.html', lances_dados=lances_dados)

@app.route('/lances_recebidos')
@login_required
def lances_recebidos():
    lances_recebidos = Lance.query.filter_by(carro_id=current_user.carros.first().id).all()
    return render_template('lances_recebidos.html', lances_recebidos=lances_recebidos)
    

#####Favoritos#############

@app.route('/favoritos')
@login_required
def favoritos():
    usuario_id = current_user.id
    usuario = Usuario.query.get(usuario_id)

    if not usuario:
        flash('Usuário não encontrado.', 'danger')
        return redirect(url_for('login_post'))

    carros_favoritos = usuario.carros_favoritos()

    return render_template('favoritos.html', carros_favoritos=carros_favoritos)


@app.route('/adicionar_favorito/<int:carro_id>')
@login_required
def adicionar_favorito(carro_id):
    usuario_id = current_user.id
    usuario = Usuario.query.get(usuario_id)
    carro = Carro.query.get(carro_id)
    if carro:
        usuario.adicionar_favorito(carro)
        flash('Carro adicionado aos favoritos!', 'success')
    else:
        flash('Carro não encontrado.', 'danger')

    return redirect(url_for('exibir_carro', carro_id=carro_id))


@app.route('/remover_favorito/<int:carro_id>')
@login_required
def remover_favorito(carro_id):
    usuario_id = current_user.id
    usuario = Usuario.query.get(usuario_id)
    carro = Carro.query.get(carro_id)
    if carro:
        usuario.remover_favorito(carro)
        flash('Carro removido dos favoritos.', 'success')
    else:
        flash('Carro não encontrado.', 'danger')

    return redirect(url_for('exibir_carro', carro_id=carro_id))
