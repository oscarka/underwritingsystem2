CREATE TABLE disease_categories (
    id INTEGER PRIMARY KEY,
    code VARCHAR(50) NOT NULL UNIQUE,
    name VARCHAR(100) NOT NULL,
    parent_id INTEGER,
    level INTEGER NOT NULL,
    sort_order INTEGER NOT NULL,
    description TEXT,
    status INTEGER NOT NULL,
    created_at DATETIME NOT NULL,
    updated_at DATETIME NOT NULL
);

CREATE TABLE diseases (
    id INTEGER PRIMARY KEY,
    code VARCHAR(50) NOT NULL UNIQUE,
    name VARCHAR(100) NOT NULL,
    category_id INTEGER NOT NULL,
    description TEXT,
    status INTEGER NOT NULL,
    created_at DATETIME NOT NULL,
    updated_at DATETIME NOT NULL,
    FOREIGN KEY (category_id) REFERENCES disease_categories(id)
);

CREATE TABLE questions (
    id INTEGER PRIMARY KEY,
    code VARCHAR(50) NOT NULL UNIQUE,
    content TEXT NOT NULL,
    sort_order INTEGER NOT NULL,
    next_question_code VARCHAR(50),
    disease_id INTEGER,
    status INTEGER NOT NULL,
    created_at DATETIME NOT NULL,
    updated_at DATETIME NOT NULL,
    FOREIGN KEY (disease_id) REFERENCES diseases(id)
);

CREATE TABLE conclusion_types (
    id INTEGER PRIMARY KEY,
    code VARCHAR(50) NOT NULL UNIQUE,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    input_type VARCHAR(50) NOT NULL DEFAULT 'text',
    options JSON,
    validation_rules JSON,
    status INTEGER NOT NULL,
    created_at DATETIME NOT NULL,
    updated_at DATETIME NOT NULL
);

CREATE TABLE conclusions (
    id INTEGER PRIMARY KEY,
    code VARCHAR(50) NOT NULL UNIQUE,
    content TEXT NOT NULL,
    decision VARCHAR(50) NOT NULL,
    em_value DECIMAL(10,2),
    type_id INTEGER NOT NULL,
    status INTEGER NOT NULL,
    created_at DATETIME NOT NULL,
    updated_at DATETIME NOT NULL,
    FOREIGN KEY (type_id) REFERENCES conclusion_types(id)
);

CREATE TABLE tenant (
    id INTEGER PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE,
    status VARCHAR(20) DEFAULT 'enabled'
);

CREATE TABLE user (
    id INTEGER PRIMARY KEY,
    username VARCHAR(64) NOT NULL UNIQUE,
    password_hash VARCHAR(128) NOT NULL,
    is_admin BOOLEAN DEFAULT FALSE,
    status VARCHAR(20) DEFAULT 'enabled',
    tenant_id INTEGER,
    FOREIGN KEY (tenant_id) REFERENCES tenant(id)
);

INSERT INTO tenant (id, name) VALUES (1, 'default');

INSERT INTO user (username, password_hash, is_admin, tenant_id) 
VALUES ('admin', 'pbkdf2:sha256:260000$8eUcuVEqQxE2vRXV$d91c8c6a2d664c8db6f9e8a86c3f1c0c6d0c8c6a2d664c8db6f9e8a86c3f1c0c', TRUE, 1); 