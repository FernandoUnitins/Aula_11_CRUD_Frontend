
from flask import Flask, request, jsonify, render_template, redirect, url_for, flash
import mysql.connector
from config import Config

app = Flask(__name__)
app.config.from_object(Config)


def get_connection():
    return mysql.connector.connect(
        host=app.config['MYSQL_DATABASE_HOST'],
        user=app.config['MYSQL_DATABASE_USER'],
        password=app.config['MYSQL_DATABASE_PASSWORD'],
        database=app.config['MYSQL_DATABASE_DB']
    )

# ------------------- API JSON -------------------------

# Rota para verificar se o servidor está ativo
@app.route('/api/usuario', methods=['POST'])
def api_cadastrar_usuario():
    #Cadastra um novo usuário via requisição JSON.
    #Espera um JSON com 'nome', 'email' e 'senha'.
    if not request.is_json:
        return jsonify({'erro': 'Conteúdo deve ser JSON'}), 415

    dados = request.get_json()
    nome = dados.get('nome')
    email = dados.get('email')
    senha = dados.get('senha')

    if not nome or not email or not senha:
        return jsonify({'erro': 'Campos obrigatórios ausentes'}), 400

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO usuario (nome, email, senha) VALUES (%s, %s, %s)", (nome, email, senha))
    conn.commit()
    cursor.close()
    conn.close()

    return jsonify({'mensagem': 'Usuário cadastrado com sucesso!'}), 201


@app.route('/api/usuarios', methods=['GET'])
#Lista todos os usuários cadastrados.
#Retorna JSON com 'id', 'nome' e 'email'.

def api_listar_usuarios():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, nome, email FROM usuario")
    dados = cursor.fetchall()
    cursor.close()
    conn.close()

    usuarios = [{'id': id, 'nome': nome, 'email': email} for id, nome, email in dados]
    return jsonify(usuarios), 200


@app.route('/api/usuario/<int:id>', methods=['PUT'])

def api_editar_usuario(id):

    #Atualiza os dados de um usuário a partir de seu ID.
    #Permite atualização de nome, email e senha.
    if not request.is_json:
        return jsonify({'erro': 'Conteúdo deve ser JSON'}), 415

    dados = request.get_json()
    nome = dados.get('nome')
    email = dados.get('email')
    senha = dados.get('senha')

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM usuario WHERE id = %s", (id,))
    if not cursor.fetchone():
        return jsonify({'erro': 'Usuário não encontrado'}), 404

    if senha:
        cursor.execute("UPDATE usuario SET nome = %s, email = %s, senha = %s WHERE id = %s",
                       (nome, email, senha, id))
    else:
        cursor.execute("UPDATE usuario SET nome = %s, email = %s WHERE id = %s",
                       (nome, email, id))

    conn.commit()
    cursor.close()
    conn.close()

    return jsonify({'mensagem': 'Usuário atualizado com sucesso'}), 200


@app.route('/api/usuario/<int:id>', methods=['DELETE'])
def api_deletar_usuario(id):

    # Exclui um usuário com base no ID.
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM usuario WHERE id = %s", (id,))
    if not cursor.fetchone():
        return jsonify({'erro': 'Usuário não encontrado'}), 404

    cursor.execute("DELETE FROM usuario WHERE id = %s", (id,))
    conn.commit()
    cursor.close()
    conn.close()

    return jsonify({'mensagem': 'Usuário deletado com sucesso'}), 200


# ------------------- ROTAS HTML -------------------------
@app.route('/')

#Página inicial que lista todos os usuários.
def index():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, nome, email FROM usuario")
    dados = cursor.fetchall()
    cursor.close()
    conn.close()

    usuarios = [{'id': id, 'nome': nome, 'email': email} for id, nome, email in dados]
    return render_template('index.html', usuarios=usuarios)


@app.route('/usuario/form', methods=['POST'])
def form_cadastrar_usuario():
    #Cadastra um novo usuário via formulário HTML.
    nome = request.form['nome']
    email = request.form['email']
    senha = request.form['senha']

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO usuario (nome, email, senha) VALUES (%s, %s, %s)", (nome, email, senha))
    conn.commit()
    cursor.close()
    conn.close()

    flash('Usuário cadastrado com sucesso!', 'success')
    return redirect(url_for('index'))

@app.route('/usuario/editar', methods=['POST'])
def form_editar_usuario():
    
    # Atualiza os dados de um usuário via formulário HTML.
    id = request.form.get('id')
    nome = request.form.get('nome').strip()
    email = request.form.get('email').strip()
    senha = request.form.get('senha').strip()

    # Verificação do ID
    if not id:
        flash('ID do usuário é obrigatório.', 'danger')
        return redirect(url_for('index'))

    # Verificação se ao menos um campo está preenchido
    if not nome and not email and not senha:
        flash('Informe pelo menos um dos campos: Nome, Email ou Senha.', 'warning')
        return redirect(url_for('index'))

    # Construção dinâmica da query
    campos = []
    valores = []

    if nome:
        campos.append("nome = %s")
        valores.append(nome)
    if email:
        campos.append("email = %s")
        valores.append(email)
    if senha:
        campos.append("senha = %s")
        valores.append(senha)

    valores.append(id)  

    conn = get_connection()
    cursor = conn.cursor()
    sql = f"UPDATE usuario SET {', '.join(campos)} WHERE id = %s"
    cursor.execute(sql, tuple(valores))
    conn.commit()
    cursor.close()
    conn.close()

    flash('Usuário atualizado com sucesso!', 'success')
    return redirect(url_for('index'))


@app.route('/usuario/deletar', methods=['POST'])
def form_deletar_usuario():

    # Exclui um usuário via formulário HTML.
    id = request.form['id']

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM usuario WHERE id = %s", (id,))
    conn.commit()
    cursor.close()
    conn.close()

    flash('Usuário deletado com sucesso!', 'success')
    return redirect(url_for('index'))

# Executa a aplicação
if __name__ == '__main__':
    app.run(debug=True)