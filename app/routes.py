from flask import request, jsonify, render_template, url_for, flash, redirect
from app import app, db, allowed_file
from sqlalchemy import desc
from flask_login import login_user, login_required, current_user, logout_user
from app.models.modelos import Carro, Lance, Usuario, Favorito
from werkzeug.utils import secure_filename
import os
from datetime import datetime
from flask_bcrypt import Bcrypt


bcrypt = Bcrypt(app)

@app.route('/')
def index():
    carros = Carro.query.filter_by(vendido=False).all()
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

    if carro.vendido or carro.lances:
        flash('Não é possível atualizar um carro vendido ou com lances', 'danger')
        return redirect(url_for('exibir_carro', carro_id=carro_id))

    if request.method == 'POST':
        modelo = request.form['modelo']
        ano = request.form['ano']
        nova_imagem = request.files['imagem']
        descricao = request.form['descricao']
        preco = request.form['preco']
        negociavel = (request.form['negociavel'] == 'True')  # Converta para booleano
        tempo_duracao = request.form['tempo_duracao']

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

        flash('Carro atualizado com sucesso', 'success')
        return redirect(url_for('minhas_vendas'))

    return render_template('cadastrar_carro.html', carro=carro)


@app.route('/excluir_carro/<int:carro_id>', methods=['GET'])
@login_required
def excluir_carro(carro_id):
    print('aqui')
    carro = Carro.query.get(carro_id)
    if not carro:
        return redirect(url_for('minhas_vendas'))
        
    if carro.vendido or carro.lances:
        flash('Não é possível excluir um carro vendido ou com lances', 'danger')
        return redirect(url_for('exibir_carro', carro_id=carro_id))

    if not carro.usuario_id == current_user.id:
        flash('Você não tem permissão para acessar este carro', 'danger')
        return redirect(url_for('minhas_vendas'))
        
    db.session.delete(carro)
    db.session.commit()
        
    return redirect(url_for('minhas_vendas'))


######### Paginas ###############
@app.route('/minhas_vendas')
@login_required
def minhas_vendas():
    usuario_id = current_user.id

    usuario = Usuario.query.get(usuario_id)
    if not usuario:
        return redirect(url_for('login_post'))
    
    carros = Carro.query.filter_by(usuario_id=usuario_id).all()

    for carro in carros:
        vender_carro(carro)
    
    return render_template('minhas_vendas.html', carros=carros)

@app.route('/carro/<int:carro_id>')
@login_required
def exibir_carro(carro_id):
    carro = Carro.query.get(carro_id)
    if not carro:
        return redirect(url_for('index'))

    if carro.usuario_id == current_user.id:
        lances_recebidos = Lance.query.filter_by(carro_id=carro.id).all()


        # Calcular tempo restante
        tempo_restante = max(0, (carro.tempo_termino - datetime.utcnow()).total_seconds())

        return render_template('info.html', carro=carro, usuario_logado=current_user,
                               lances_recebidos=lances_recebidos, tempo_restante=tempo_restante, e_favorito=e_favorito(carro))
    else:
        lances_dados = Lance.query.filter_by(usuario_id=current_user.id, carro_id=carro.id).all()
        
        # Calcular tempo restante
        tempo_restante = max(0, (carro.tempo_termino - datetime.utcnow()).total_seconds())

        return render_template('info.html', carro=carro, usuario_logado=current_user,
                               lances_dados=lances_dados, tempo_restante=tempo_restante, e_favorito=e_favorito( carro))
#######Lance########

@app.route('/realizar_lance/<int:carro_id>', methods=['POST'])
@login_required
def realizar_lance(carro_id):
    carro = Carro.query.get(carro_id)
    if not carro:
        flash('Você não tem permissão para acessar este carro', 'danger')
        return redirect(url_for('index'))

    if not carro.negociavel:
        flash('Este carro não é negociável.', 'danger')
        return redirect(url_for('exibir_carro', carro_id=carro_id))

    valor_lance = float(request.form['valor'])

    if valor_lance < carro.preco:
        flash('O valor do lance deve ser igual ou maior que o valor do carro.', 'danger')
        return redirect(url_for('exibir_carro', carro_id=carro_id))

    novo_lance = Lance(valor=valor_lance, carro=carro, usuario=current_user)
    db.session.add(novo_lance)
    db.session.commit()

    verificar_venda_carro(carro)

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


@app.route('/favoritar_carro/<int:carro_id>')
@login_required
def favoritar_carro(carro_id):
    usuario_id = current_user.id
    usuario = Usuario.query.get(usuario_id)
    carro = Carro.query.get(carro_id)

    if not carro:
        flash('Carro não encontrado.', 'danger')
    else:
        if carro in usuario.carros_favoritos():
            usuario.remover_favorito(carro)
            flash('Carro removido dos favoritos.', 'success')
        else:
            usuario.adicionar_favorito(carro)
            flash('Carro adicionado aos favoritos!', 'success')

    return redirect(url_for('exibir_carro', carro_id=carro_id))


####funcões###
def allowed_file(filename):
    # Adicione sua lógica para verificar se a extensão do arquivo é permitida
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def verificar_venda_carro(carro):
    if not carro.negociavel:
        carro.vendido = True
        db.session.commit()
        flash('O carro foi vendido!', 'success')
    elif datetime.utcnow() > carro.tempo_termino:
        melhor_lance = Lance.query.filter_by(carro_id=carro.id, ativo=True).order_by(Lance.valor.desc()).first()
        if melhor_lance:
            carro.vendido = True
            db.session.commit()
            flash(f'O carro foi vendido para o lance de R$ {melhor_lance.valor}!', 'success')
            

def vender_carro(carro):
    if not carro.ativo or carro.vendido:
        return

    if carro.negociavel:
        if carro.tempo_termino <= datetime.utcnow():
            maior_lance = Lance.query.filter_by(carro_id=carro.id, ativo=True).order_by(desc(Lance.valor)).first()
            if maior_lance:
                carro.vendido = True
                carro.tempo_termino = datetime.utcnow()
                db.session.commit()
        else:
            
            pass
    else:
        
        primeiro_lance = Lance.query.filter_by(carro_id=carro.id, ativo=True).order_by(Lance.tempo_lance).first()
        if primeiro_lance:
            carro.vendido = True
            carro.tempo_termino = datetime.utcnow()
            db.session.commit()
            

def e_favorito(carro):
    return Favorito.query.filter_by(usuario_id=current_user.id, carro_id=carro.id).first() is not None if current_user.is_authenticated else False