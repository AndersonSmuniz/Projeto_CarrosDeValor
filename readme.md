# Instruções

Execute o comando abaixo para instalar as dependências:

```
pip install -r requirements.txt
``` 
Depois, rode seu banco de dados. Se for a primeira vez:

* Criar o Banco de Dados:
```
flask db init
``` 
* Criar Migração Inicial
```
flask db migrate -m "Inicialização"
``` 
* Aplicar Migrações
```
flask db upgrade
``` 

Se você já tem o banco de dados e atualizou alguma tabela:
```
flask db upgrade
``` 

Depois, execute o run.py

Para ver as dependências:
pip freeze