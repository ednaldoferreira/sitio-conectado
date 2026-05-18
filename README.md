# Sítio Conectado — Portal do Pequeno Produtor Rural
## UNITINS — TADS 3º Período 2026.1 — Polo Sítio Novo TO

---

## Instalação e execução

### 1. Instalar dependências Python
```bash
pip install -r requirements.txt
```

### 2. Configurar o banco de dados
- Abra o MySQL Workbench
- Execute o script SQL do documento de Banco de Dados
- Edite o arquivo `app.py` e altere a senha do MySQL se necessário:
  ```python
  password = "SUA_SENHA_AQUI"
  ```

### 3. Executar o sistema
```bash
python app.py
```

### 4. Acessar no navegador
```
http://localhost:5000
```

---

## Estrutura do projeto
```
sitio_conectado/
├── app.py                      ← Backend Flask (rotas e lógica)
├── requirements.txt            ← Dependências Python
├── README.md                   ← Este arquivo
└── templates/                  ← Páginas HTML
    ├── base.html               ← Template base (navbar, footer)
    ├── login.html              ← Página de login
    ├── cadastro.html           ← Página de cadastro
    ├── produtos.html           ← Listagem de produtos
    ├── produto_detalhe.html    ← Detalhe + interesse + comentários
    ├── produto_form.html       ← Formulário cadastro/edição
    ├── meus_produtos.html      ← Painel do produtor
    ├── interessados.html       ← Lista de interessados
    └── perfil.html             ← Perfil do usuário
```

---

## Funcionalidades implementadas
- [x] Cadastro de usuários (produtor e consumidor)
- [x] Login e logout com senha criptografada
- [x] Edição de perfil
- [x] Cadastro, edição e remoção de produtos (produtor)
- [x] Listagem de produtos disponíveis
- [x] Busca por nome/descrição
- [x] Filtro por categoria
- [x] Demonstrar interesse em produto (consumidor)
- [x] Visualizar interessados por produto (produtor)
- [x] Comentários em produtos
