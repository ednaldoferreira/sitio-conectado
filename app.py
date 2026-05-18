from flask import Flask, render_template, request, redirect, url_for, session, flash
import mysql.connector
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import os
from functools import wraps

app = Flask(__name__)
app.secret_key = 'sitio_conectado_2026'

# ─── Configurações para upload de imagens ─────────────────────────────────────
UPLOAD_FOLDER = 'static/uploads/produtos'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_FILE_SIZE

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# ─── Conexão com o banco ───────────────────────────────────────────────────────
def get_db():
    return mysql.connector.connect(
        host     = "localhost",
        user     = "root",
        password = "163676",          # coloque sua senha aqui se tiver
        database = "sitio_conectado"
    )

# ─── Decorador de login obrigatório ───────────────────────────────────────────
def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'usuario_id' not in session:
            flash('Você precisa estar logado para acessar essa página.', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated

def produtor_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if session.get('tipo') != 'produtor':
            flash('Apenas produtores podem acessar essa área.', 'danger')
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated

# ══════════════════════════════════════════════════════════════════════════════
#  ROTAS DE AUTENTICAÇÃO
# ══════════════════════════════════════════════════════════════════════════════

@app.route('/')
def index():
    return redirect(url_for('produtos'))

# ── Cadastro
@app.route('/cadastro', methods=['GET', 'POST'])
def cadastro():
    if request.method == 'POST':
        nome     = request.form['nome'].strip()
        email    = request.form['email'].strip()
        senha    = request.form['senha']
        tipo     = request.form['tipo']
        telefone = request.form.get('telefone', '').strip()

        if not nome or not email or not senha or not tipo:
            flash('Preencha todos os campos obrigatórios.', 'danger')
            return render_template('cadastro.html')

        senha_hash = generate_password_hash(senha)

        try:
            db  = get_db()
            cur = db.cursor()
            cur.execute(
                "INSERT INTO usuario (nome, email, senha_hash, tipo, telefone) VALUES (%s, %s, %s, %s, %s)",
                (nome, email, senha_hash, tipo, telefone)
            )
            db.commit()
            flash('Cadastro realizado com sucesso! Faça login.', 'success')
            return redirect(url_for('login'))
        except mysql.connector.IntegrityError:
            flash('Este e-mail já está cadastrado.', 'danger')
        finally:
            cur.close(); db.close()

    return render_template('cadastro.html')

# ── Login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email'].strip()
        senha = request.form['senha']

        db  = get_db()
        cur = db.cursor(dictionary=True)
        cur.execute("SELECT * FROM usuario WHERE email = %s", (email,))
        usuario = cur.fetchone()
        cur.close(); db.close()

        if usuario and check_password_hash(usuario['senha_hash'], senha):
            session['usuario_id'] = usuario['id']
            session['nome']       = usuario['nome']
            session['tipo']       = usuario['tipo']
            flash(f'Bem-vindo, {usuario["nome"]}!', 'success')
            return redirect(url_for('produtos'))
        else:
            flash('E-mail ou senha incorretos.', 'danger')

    return render_template('login.html')

# ── Logout
@app.route('/logout')
def logout():
    session.clear()
    flash('Você saiu do sistema.', 'info')
    return redirect(url_for('login'))

# ── Perfil
@app.route('/perfil', methods=['GET', 'POST'])
@login_required
def perfil():
    db  = get_db()
    cur = db.cursor(dictionary=True)

    if request.method == 'POST':
        nome     = request.form['nome'].strip()
        telefone = request.form.get('telefone', '').strip()
        cur.execute(
            "UPDATE usuario SET nome=%s, telefone=%s WHERE id=%s",
            (nome, telefone, session['usuario_id'])
        )
        db.commit()
        session['nome'] = nome
        flash('Perfil atualizado com sucesso!', 'success')

    cur.execute("SELECT * FROM usuario WHERE id = %s", (session['usuario_id'],))
    usuario = cur.fetchone()
    cur.close(); db.close()
    return render_template('perfil.html', usuario=usuario)

# ══════════════════════════════════════════════════════════════════════════════
#  ROTAS DE PRODUTOS
# ══════════════════════════════════════════════════════════════════════════════

@app.route('/produtos')
def produtos():
    db  = get_db()
    cur = db.cursor(dictionary=True)

    busca     = request.args.get('busca', '').strip()
    categoria = request.args.get('categoria', '')

    # Carrega categorias para o filtro
    cur.execute("SELECT * FROM categoria ORDER BY nome")
    categorias = cur.fetchall()

    # Monta a query dinamicamente
    sql    = """
        SELECT p.*, c.nome AS categoria_nome, u.nome AS produtor_nome, u.telefone AS produtor_tel
        FROM produto p
        JOIN categoria c ON c.id = p.categoria_id
        JOIN usuario   u ON u.id = p.produtor_id
        WHERE p.status = 'disponivel'
    """
    params = []

    if busca:
        sql += " AND (p.nome LIKE %s OR p.descricao LIKE %s)"
        params += [f'%{busca}%', f'%{busca}%']

    if categoria:
        sql += " AND p.categoria_id = %s"
        params.append(categoria)

    sql += " ORDER BY p.criado_em DESC"

    cur.execute(sql, params)
    produtos = cur.fetchall()
    cur.close(); db.close()

    return render_template('produtos.html',
                           produtos=produtos,
                           categorias=categorias,
                           busca=busca,
                           categoria_selecionada=categoria)

# ── Detalhe do produto
@app.route('/produto/<int:id>')
def produto_detalhe(id):
    db  = get_db()
    cur = db.cursor(dictionary=True)

    cur.execute("""
        SELECT p.*, c.nome AS categoria_nome, u.nome AS produtor_nome, u.telefone AS produtor_tel
        FROM produto p
        JOIN categoria c ON c.id = p.categoria_id
        JOIN usuario   u ON u.id = p.produtor_id
        WHERE p.id = %s
    """, (id,))
    produto = cur.fetchone()

    if not produto:
        flash('Produto não encontrado.', 'danger')
        return redirect(url_for('produtos'))

    # Comentários
    cur.execute("""
        SELECT cm.texto, cm.criado_em, u.nome AS autor, u.tipo
        FROM comentario cm
        JOIN usuario u ON u.id = cm.usuario_id
        WHERE cm.produto_id = %s
        ORDER BY cm.criado_em ASC
    """, (id,))
    comentarios = cur.fetchall()

    # Verifica se o usuário já demonstrou interesse
    ja_interessou = False
    if 'usuario_id' in session:
        cur.execute(
            "SELECT id FROM interesse WHERE usuario_id=%s AND produto_id=%s",
            (session['usuario_id'], id)
        )
        ja_interessou = cur.fetchone() is not None

    # Total de interessados
    cur.execute("SELECT COUNT(*) AS total FROM interesse WHERE produto_id=%s", (id,))
    total_interesse = cur.fetchone()['total']

    cur.close(); db.close()
    return render_template('produto_detalhe.html',
                           produto=produto,
                           comentarios=comentarios,
                           ja_interessou=ja_interessou,
                           total_interesse=total_interesse)

# ── Demonstrar interesse
@app.route('/produto/<int:id>/interesse', methods=['POST'])
@login_required
def demonstrar_interesse(id):
    mensagem = request.form.get('mensagem', '').strip()
    db  = get_db()
    cur = db.cursor()
    try:
        cur.execute(
            "INSERT INTO interesse (usuario_id, produto_id, mensagem) VALUES (%s, %s, %s)",
            (session['usuario_id'], id, mensagem)
        )
        db.commit()
        flash('Interesse registrado! O produtor poderá ver seu contato.', 'success')
    except mysql.connector.IntegrityError:
        flash('Você já demonstrou interesse neste produto.', 'warning')
    finally:
        cur.close(); db.close()
    return redirect(url_for('produto_detalhe', id=id))

# ── Adicionar comentário
@app.route('/produto/<int:id>/comentario', methods=['POST'])
@login_required
def adicionar_comentario(id):
    texto = request.form.get('texto', '').strip()
    if not texto:
        flash('O comentário não pode estar vazio.', 'warning')
        return redirect(url_for('produto_detalhe', id=id))

    db  = get_db()
    cur = db.cursor()
    cur.execute(
        "INSERT INTO comentario (usuario_id, produto_id, texto) VALUES (%s, %s, %s)",
        (session['usuario_id'], id, texto)
    )
    db.commit()
    cur.close(); db.close()
    flash('Comentário adicionado!', 'success')
    return redirect(url_for('produto_detalhe', id=id))

# ══════════════════════════════════════════════════════════════════════════════
#  ROTAS DO PRODUTOR
# ══════════════════════════════════════════════════════════════════════════════

@app.route('/meus-produtos')
@login_required
@produtor_required
def meus_produtos():
    db  = get_db()
    cur = db.cursor(dictionary=True)
    cur.execute("""
        SELECT p.*, c.nome AS categoria_nome,
               COUNT(i.id) AS total_interesse
        FROM produto p
        JOIN categoria c ON c.id = p.categoria_id
        LEFT JOIN interesse i ON i.produto_id = p.id
        WHERE p.produtor_id = %s
        GROUP BY p.id
        ORDER BY p.criado_em DESC
    """, (session['usuario_id'],))
    produtos = cur.fetchall()
    cur.close(); db.close()
    return render_template('meus_produtos.html', produtos=produtos)

@app.route('/produto/novo', methods=['GET', 'POST'])
@login_required
@produtor_required
def novo_produto():
    db  = get_db()
    cur = db.cursor(dictionary=True)
    cur.execute("SELECT * FROM categoria ORDER BY nome")
    categorias = cur.fetchall()

    if request.method == 'POST':
        nome         = request.form['nome'].strip()
        descricao    = request.form.get('descricao', '').strip()
        categoria_id = request.form['categoria_id']
        quantidade   = request.form['quantidade']
        unidade      = request.form.get('unidade', 'kg').strip()

        # Upload de imagem
        imagem_path = None
        if 'imagem' in request.files:
            file = request.files['imagem']
            if file and file.filename != '':
                if not allowed_file(file.filename):
                    flash('Tipo de arquivo não permitido. Use apenas PNG, JPG, JPEG ou GIF.', 'danger')
                    cur.close(); db.close()
                    return render_template('produto_form.html', categorias=categorias, produto=None)
                
                # Verificar tamanho do arquivo
                file.seek(0, os.SEEK_END)
                file_size = file.tell()
                file.seek(0)
                
                if file_size > MAX_FILE_SIZE:
                    flash('Arquivo muito grande. Máximo permitido: 5MB.', 'danger')
                    cur.close(); db.close()
                    return render_template('produto_form.html', categorias=categorias, produto=None)
                
                filename = secure_filename(file.filename)
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                
                # Evitar sobrescrever arquivos existentes
                counter = 1
                while os.path.exists(file_path):
                    name, ext = os.path.splitext(filename)
                    filename = f"{name}_{counter}{ext}"
                    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                    counter += 1
                
                try:
                    file.save(file_path)
                    imagem_path = f'uploads/produtos/{filename}'
                except Exception as e:
                    flash('Erro ao salvar a imagem. Tente novamente.', 'danger')
                    cur.close(); db.close()
                    return render_template('produto_form.html', categorias=categorias, produto=None)

        if not nome or not categoria_id or not quantidade:
            flash('Preencha todos os campos obrigatórios.', 'danger')
        else:
            cur.execute(
                "INSERT INTO produto (produtor_id, categoria_id, nome, descricao, quantidade, unidade, imagem) VALUES (%s,%s,%s,%s,%s,%s,%s)",
                (session['usuario_id'], categoria_id, nome, descricao, quantidade, unidade, imagem_path)
            )
            db.commit()
            flash('Produto cadastrado com sucesso!', 'success')
            cur.close(); db.close()
            return redirect(url_for('meus_produtos'))

    cur.close(); db.close()
    return render_template('produto_form.html', categorias=categorias, produto=None)

@app.route('/produto/<int:id>/editar', methods=['GET', 'POST'])
@login_required
@produtor_required
def editar_produto(id):
    db  = get_db()
    cur = db.cursor(dictionary=True)

    cur.execute("SELECT * FROM produto WHERE id=%s AND produtor_id=%s", (id, session['usuario_id']))
    produto = cur.fetchone()
    if not produto:
        flash('Produto não encontrado.', 'danger')
        return redirect(url_for('meus_produtos'))

    cur.execute("SELECT * FROM categoria ORDER BY nome")
    categorias = cur.fetchall()

    if request.method == 'POST':
        nome         = request.form['nome'].strip()
        descricao    = request.form.get('descricao', '').strip()
        categoria_id = request.form['categoria_id']
        quantidade   = request.form['quantidade']
        unidade      = request.form.get('unidade', 'kg').strip()
        status       = request.form.get('status', 'disponivel')

        # Upload de imagem
        imagem_path = produto['imagem']  # Manter a imagem atual por padrão
        
        # Verificar se o produtor quer remover a imagem atual
        if request.form.get('remover_imagem') == '1':
            imagem_path = None
        elif 'imagem' in request.files:
            file = request.files['imagem']
            if file and file.filename != '':
                if not allowed_file(file.filename):
                    flash('Tipo de arquivo não permitido. Use apenas PNG, JPG, JPEG ou GIF.', 'danger')
                    cur.close(); db.close()
                    return render_template('produto_form.html', categorias=categorias, produto=produto)
                
                # Verificar tamanho do arquivo
                file.seek(0, os.SEEK_END)
                file_size = file.tell()
                file.seek(0)
                
                if file_size > MAX_FILE_SIZE:
                    flash('Arquivo muito grande. Máximo permitido: 5MB.', 'danger')
                    cur.close(); db.close()
                    return render_template('produto_form.html', categorias=categorias, produto=produto)
                
                filename = secure_filename(file.filename)
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                
                # Evitar sobrescrever arquivos existentes
                counter = 1
                while os.path.exists(file_path):
                    name, ext = os.path.splitext(filename)
                    filename = f"{name}_{counter}{ext}"
                    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                    counter += 1
                
                try:
                    file.save(file_path)
                    imagem_path = f'uploads/produtos/{filename}'
                except Exception as e:
                    flash('Erro ao salvar a imagem. Tente novamente.', 'danger')
                    cur.close(); db.close()
                    return render_template('produto_form.html', categorias=categorias, produto=produto)

        cur.execute("""
            UPDATE produto SET nome=%s, descricao=%s, categoria_id=%s,
            quantidade=%s, unidade=%s, status=%s, imagem=%s WHERE id=%s AND produtor_id=%s
        """, (nome, descricao, categoria_id, quantidade, unidade, status, imagem_path, id, session['usuario_id']))
        db.commit()
        flash('Produto atualizado!', 'success')
        cur.close(); db.close()
        return redirect(url_for('meus_produtos'))

    cur.close(); db.close()
    return render_template('produto_form.html', categorias=categorias, produto=produto)

@app.route('/produto/<int:id>/remover', methods=['POST'])
@login_required
@produtor_required
def remover_produto(id):
    db  = get_db()
    cur = db.cursor()
    cur.execute("DELETE FROM produto WHERE id=%s AND produtor_id=%s", (id, session['usuario_id']))
    db.commit()
    cur.close(); db.close()
    flash('Produto removido.', 'info')
    return redirect(url_for('meus_produtos'))

@app.route('/produto/<int:id>/interessados')
@login_required
@produtor_required
def interessados(id):
    db  = get_db()
    cur = db.cursor(dictionary=True)

    cur.execute("SELECT nome FROM produto WHERE id=%s AND produtor_id=%s",
                (id, session['usuario_id']))
    produto = cur.fetchone()
    if not produto:
        flash('Produto não encontrado.', 'danger')
        return redirect(url_for('meus_produtos'))

    cur.execute("""
        SELECT u.nome, u.email, u.telefone, i.mensagem, i.criado_em
        FROM interesse i
        JOIN usuario u ON u.id = i.usuario_id
        WHERE i.produto_id = %s
        ORDER BY i.criado_em DESC
    """, (id,))
    interessados = cur.fetchall()
    cur.close(); db.close()
    return render_template('interessados.html', produto=produto, interessados=interessados)

if __name__ == '__main__':
    app.run(debug=True)
