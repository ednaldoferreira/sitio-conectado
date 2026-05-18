# 🌿 Sítio Conectado — Portal de Apoio ao Pequeno Produtor Rural

> Projeto desenvolvido como parte da Atividade Multidisciplinar Integradora - 3º Período  
> Tecnologia em Análise e Desenvolvimento de Sistemas - TADS  
> Universidade Estadual do Tocantins - UNITINS - Polo Sítio Novo, TO - 2026.1

---

## 📋 Descrição do Projeto

O **Sítio Conectado** é um portal web que conecta pequenos produtores rurais de Sítio Novo — TO diretamente a consumidores locais, sem intermediários comerciais. O sistema funciona como um **mural digital comunitário**, onde produtores divulgam seus produtos (frutas, verduras, grãos, mel, ovos, entre outros) e consumidores demonstram interesse, combinando a negociação diretamente fora da plataforma.

O projeto integra na prática os conhecimentos das disciplinas de:
- Engenharia de Requisitos
- Banco de Dados I
- Programação para Web I
- Redes de Computadores I

---

## 🛠️ Tecnologias Utilizadas

| Camada | Tecnologia |
|---|---|
| Back-end | Python 3 + Flask |
| Front-end | HTML5 + CSS3 + JavaScript |
| Banco de dados | MySQL |
| Servidor web | Nginx + Gunicorn (produção) |
| Virtualização | VirtualBox + Ubuntu (Redes) |
| Versionamento | Git + GitHub |

---

## 📁 Estrutura de Pastas

```
sitio_conectado/
│
├── app.py                      ← Arquivo principal — rotas e lógica do back-end
├── requirements.txt            ← Dependências Python
├── README.md                   ← Este arquivo
│
└── templates/                  ← Páginas HTML (front-end)
    ├── base.html               ← Template base com navbar e footer
    ├── login.html              ← Tela de login
    ├── cadastro.html           ← Tela de cadastro de usuário
    ├── produtos.html           ← Listagem de produtos com busca e filtros
    ├── produto_detalhe.html    ← Detalhe do produto + interesse + comentários
    ├── produto_form.html       ← Formulário de cadastro e edição de produto
    ├── meus_produtos.html      ← Painel do produtor
    ├── interessados.html       ← Lista de consumidores interessados
    └── perfil.html             ← Perfil do usuário
```

---

## ⚙️ Como Executar o Sistema Localmente

### Pré-requisitos

- Python 3.10 ou superior instalado
- MySQL instalado e rodando
- Git instalado

### Passo 1 — Clonar o repositório

```bash
git clone https://github.com/SEU_USUARIO/sitio-conectado.git
cd sitio-conectado
```

### Passo 2 — Criar e ativar o ambiente virtual

```bash
# Windows
python -m venv .venv
.venv\Scripts\activate

# Linux/Mac
python3 -m venv .venv
source .venv/bin/activate
```

### Passo 3 — Instalar as dependências

```bash
pip install -r requirements.txt
```

### Passo 4 — Configurar o banco de dados

Abra o MySQL Workbench (ou terminal MySQL) e execute os scripts abaixo:

```sql
CREATE DATABASE IF NOT EXISTS sitio_conectado
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;

USE sitio_conectado;

CREATE TABLE categoria (
  id        INT AUTO_INCREMENT PRIMARY KEY,
  nome      VARCHAR(100) NOT NULL UNIQUE,
  descricao TEXT,
  criado_em DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE usuario (
  id         INT AUTO_INCREMENT PRIMARY KEY,
  nome       VARCHAR(150) NOT NULL,
  email      VARCHAR(150) NOT NULL UNIQUE,
  senha_hash VARCHAR(255) NOT NULL,
  tipo       ENUM('produtor','consumidor') NOT NULL,
  telefone   VARCHAR(20),
  criado_em  DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE produto (
  id           INT AUTO_INCREMENT PRIMARY KEY,
  produtor_id  INT NOT NULL,
  categoria_id INT NOT NULL,
  nome         VARCHAR(150) NOT NULL,
  descricao    TEXT,
  quantidade   INT NOT NULL DEFAULT 0,
  unidade      VARCHAR(30) DEFAULT 'kg',
  status       ENUM('disponivel','indisponivel') DEFAULT 'disponivel',
  criado_em    DATETIME DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (produtor_id)  REFERENCES usuario(id)   ON DELETE CASCADE,
  FOREIGN KEY (categoria_id) REFERENCES categoria(id) ON DELETE RESTRICT
);

CREATE TABLE interesse (
  id         INT AUTO_INCREMENT PRIMARY KEY,
  usuario_id INT NOT NULL,
  produto_id INT NOT NULL,
  mensagem   TEXT,
  criado_em  DATETIME DEFAULT CURRENT_TIMESTAMP,
  UNIQUE KEY unico_interesse (usuario_id, produto_id),
  FOREIGN KEY (usuario_id) REFERENCES usuario(id) ON DELETE CASCADE,
  FOREIGN KEY (produto_id) REFERENCES produto(id) ON DELETE CASCADE
);

CREATE TABLE comentario (
  id         INT AUTO_INCREMENT PRIMARY KEY,
  usuario_id INT NOT NULL,
  produto_id INT NOT NULL,
  texto      TEXT NOT NULL,
  criado_em  DATETIME DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (usuario_id) REFERENCES usuario(id) ON DELETE CASCADE,
  FOREIGN KEY (produto_id) REFERENCES produto(id) ON DELETE CASCADE
);

INSERT INTO categoria (nome, descricao) VALUES
  ('Frutas',     'Frutas frescas da região'),
  ('Verduras',   'Hortaliças e verduras'),
  ('Grãos',      'Feijão, milho, arroz e outros'),
  ('Mel',        'Mel puro e derivados'),
  ('Ovos',       'Ovos caipira e orgânicos'),
  ('Laticínios', 'Queijo, manteiga e derivados'),
  ('Outros',     'Demais produtos rurais');
```

### Passo 5 — Configurar a conexão com o banco

Abra o arquivo `app.py` e edite as linhas de conexão com suas credenciais:

```python
def get_db():
    return mysql.connector.connect(
        host     = "localhost",
        user     = "root",
        password = "SUA_SENHA_AQUI",  # altere para sua senha
        database = "sitio_conectado"
    )
```

### Passo 6 — Executar o sistema

```bash
python app.py
```

### Passo 7 — Acessar no navegador

```
http://127.0.0.1:5000
```

---

## ✅ Funcionalidades Implementadas

### Gerenciamento de Usuários
- [x] Cadastro de usuário (nome, e-mail, senha, tipo: produtor ou consumidor)
- [x] Login com autenticação via e-mail e senha
- [x] Logout com encerramento de sessão
- [x] Edição de perfil (nome e telefone)
- [x] Senhas armazenadas com hash seguro (bcrypt)

### Gerenciamento de Produtos (Produtor)
- [x] Cadastro de produto (nome, descrição, categoria, quantidade, unidade)
- [x] Edição de produto
- [x] Remoção de produto
- [x] Listagem dos próprios produtos no painel

### Busca e Filtros (Consumidor e Produtor)
- [x] Listagem de todos os produtos disponíveis
- [x] Busca por nome ou descrição
- [x] Filtro por categoria

### Interações
- [x] Demonstrar interesse em produto (consumidor)
- [x] Visualizar lista de consumidores interessados (produtor)
- [x] Comentários em produtos (todos os usuários autenticados)

---

## 🗄️ Banco de Dados

O banco de dados relacional `sitio_conectado` é composto por 5 tabelas:

| Tabela | Descrição |
|---|---|
| `usuario` | Armazena todos os usuários do sistema |
| `categoria` | Categorias de produtos disponíveis |
| `produto` | Produtos cadastrados pelos produtores |
| `interesse` | Registro de interesse de consumidores em produtos |
| `comentario` | Comentários de usuários em produtos |

---

## 👥 Integrantes do Grupo

| Nome | Função |
|---|---|
| Ednaldo Conceição Ferreira | Desenvolvimento |
| _(adicionar demais integrantes)_ | _(função)_ |

**Polo:** Sítio Novo — TO  
**Curso:** Tecnologia em Análise e Desenvolvimento de Sistemas — TADS  
**Instituição:** Universidade Estadual do Tocantins — UNITINS  
**Período:** 3º Período — 2026.1
