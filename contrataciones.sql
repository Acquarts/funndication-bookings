-- Base de datos para contrataciones de DJs de Funndication
-- Tabla para almacenar todas las contrataciones realizadas

CREATE TABLE IF NOT EXISTS contrataciones (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    dj_nombre TEXT NOT NULL,
    cliente_nombre TEXT NOT NULL,
    cliente_telefono TEXT NOT NULL,
    cliente_email TEXT NOT NULL,
    localizacion TEXT NOT NULL,
    fecha_evento TEXT NOT NULL,
    duracion TEXT NOT NULL,
    precio_total REAL NOT NULL,
    fecha_contratacion DATETIME DEFAULT CURRENT_TIMESTAMP,
    estado TEXT DEFAULT 'confirmada'
);

-- Índice para búsquedas rápidas por DJ y fecha
CREATE INDEX IF NOT EXISTS idx_dj_fecha ON contrataciones(dj_nombre, fecha_evento);

-- Insertar datos de ejemplo (opcional)
-- INSERT INTO contrataciones (dj_nombre, cliente_nombre, cliente_telefono, cliente_email, localizacion, fecha_evento, duracion, precio_total)
-- VALUES ('The Brainkiller', 'Juan Pérez', '123456789', 'juan@email.com', 'Madrid', '2024-12-25', '2 horas', 1600.00);