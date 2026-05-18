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