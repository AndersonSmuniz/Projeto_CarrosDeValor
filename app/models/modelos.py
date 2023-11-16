from app import db
from flask_login import UserMixin

class Usuario(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False)
    senha = db.Column(db.String(255), nullable=False)

    def __init__(self, nome, email, senha):
        self.nome = nome
        self.email = email
        self.senha = senha


class Carro(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    modelo = db.Column(db.String(255), nullable=False)
    ano = db.Column(db.Integer, nullable=False)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=False)
    usuario = db.relationship('Usuario', backref=db.backref('carros', lazy=True))

    def __init__(self, modelo, ano, usuario):
        self.modelo = modelo
        self.ano = ano
        self.usuario = usuario


class PostDeVenda(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    descricao = db.Column(db.Text, nullable=False)
    preco = db.Column(db.Float, nullable=False)
    negociavel = db.Column(db.Boolean, nullable=False)
    vendido = db.Column(db.Boolean, nullable=False, default=False)
    carro_id = db.Column(db.Integer, db.ForeignKey('carro.id'), nullable=False)
    carro = db.relationship('Carro', backref=db.backref('posts_de_venda', lazy=True))
    tempo_duracao = db.Column(db.Integer, nullable=False)
    ativo = db.Column(db.Boolean, nullable=False, default=True)

    def __init__(self, descricao, preco, negociavel, carro, tempo_duracao):
        self.descricao = descricao
        self.preco = preco
        self.negociavel = negociavel
        self.carro = carro
        self.tempo_duracao = tempo_duracao


class Lance(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    valor = db.Column(db.Float, nullable=True)
    tempo_expiracao = db.Column(db.DateTime, nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey('post_de_venda.id'), nullable=False)
    post = db.relationship('PostDeVenda', backref=db.backref('lances', lazy=True))
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=False)
    usuario = db.relationship('Usuario', backref=db.backref('lances', lazy=True))
    secreto = db.Column(db.Boolean, nullable=False)
    valor_real = db.Column(db.Float)

    def __init__(self, valor, tempo_expiracao, post, usuario, secreto):
        self.valor = valor
        self.tempo_expiracao = tempo_expiracao
        self.post = post
        self.usuario = usuario
        self.secreto = secreto

