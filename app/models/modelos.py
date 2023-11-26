from app import db
from flask_login import UserMixin
from datetime import datetime, timedelta

class Usuario(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False)
    senha = db.Column(db.String(255), nullable=False)

    def __init__(self, nome, email, senha):
        self.nome = nome
        self.email = email
        self.senha = senha

    def adicionar_favorito(self, carro):
        if carro not in self.favoritos:
            favorito = Favorito(usuario=self, carro=carro)
            db.session.add(favorito)
            db.session.commit()

    def remover_favorito(self, carro):
        favorito = Favorito.query.filter_by(usuario_id=self.id, carro_id=carro.id).first()
        if favorito:
            db.session.delete(favorito)
            db.session.commit()

    def carros_favoritos(self):
        return Carro.query.join(Favorito).filter(Favorito.usuario_id == self.id).all()

class Carro(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    modelo = db.Column(db.String(255), nullable=False)
    ano = db.Column(db.Integer, nullable=False)
    imagem = db.Column(db.String(255))
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=False)
    usuario = db.relationship('Usuario', backref=db.backref('carros', lazy=True))
    descricao = db.Column(db.Text, nullable=False)
    preco = db.Column(db.Float, nullable=False)
    negociavel = db.Column(db.Boolean, nullable=False)
    vendido = db.Column(db.Boolean, nullable=False, default=False)
    tempo_duracao = db.Column(db.Integer, nullable=False)
    ativo = db.Column(db.Boolean, nullable=False, default=True)
    tempo_inicio = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    tempo_termino = db.Column(db.DateTime, nullable=False)


    def __init__(self, modelo, ano, usuario, imagem, descricao, preco, negociavel, tempo_duracao):
        self.modelo = modelo
        self.ano = ano
        self.usuario = usuario
        self.imagem = imagem
        self.descricao = descricao
        self.preco = preco
        self.negociavel = negociavel
        self.tempo_duracao = tempo_duracao
        self.tempo_inicio = datetime.utcnow()
        self.tempo_termino = self.tempo_inicio + timedelta(minutes=int(tempo_duracao))


class Lance(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    valor = db.Column(db.Float, nullable=False)
    tempo_lance = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    carro_id = db.Column(db.Integer, db.ForeignKey('carro.id'), nullable=False)
    carro = db.relationship('Carro', backref=db.backref('lances', lazy=True))
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=False)
    usuario = db.relationship('Usuario', backref=db.backref('lances', lazy=True))
    ativo = db.Column(db.Boolean, nullable=False, default=True)

    def __init__(self, valor, carro, usuario):
        self.valor = valor
        self.carro = carro
        self.usuario = usuario
        

class Favorito(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=False)
    usuario = db.relationship('Usuario', backref=db.backref('favoritos', lazy=True))
    carro_id = db.Column(db.Integer, db.ForeignKey('carro.id'), nullable=False)
    carro = db.relationship('Carro', backref=db.backref('favoritos', lazy=True))

    def __init__(self, usuario, carro):
        self.usuario = usuario
        self.carro = carro