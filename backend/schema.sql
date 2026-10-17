-- Executar conectado a devops_lab como devops_app.
-- Laboratório: não executar repetidamente os INSERTs sem considerar duplicatas.
CREATE TABLE IF NOT EXISTS tasks (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    completed BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Carga demonstrativa inicial (opcional)
INSERT INTO tasks (name) VALUES
    ('Configure AWS VPC'),
    ('Deploy Backend API'),
    ('Install PostgreSQL');
