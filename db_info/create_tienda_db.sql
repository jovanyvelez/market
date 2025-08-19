-- =============================================================================
-- SCRIPT PARA FASTAPI + SUPABASE (Solo DB + Storage)
-- =============================================================================
-- Arquitectura: FastAPI (Backend) → Supabase (PostgreSQL + Storage)
-- Este script está optimizado para usar con FastAPI como backend principal
-- =============================================================================

-- Las extensiones están disponibles en Supabase por defecto

-- =============================================================================
-- TABLA: CATEGORÍA DE PRODUCTOS (CON JERARQUÍA)
-- =============================================================================
CREATE TABLE categoria (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL UNIQUE,
    descripcion TEXT,
    padre INTEGER REFERENCES categoria(id) ON DELETE SET NULL,
    imagen_url VARCHAR(255),
    activo BOOLEAN DEFAULT TRUE,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    fecha_actualizacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Índices para categoria
CREATE INDEX idx_categoria_padre ON categoria(padre);
CREATE INDEX idx_categoria_activo ON categoria(activo);
CREATE INDEX idx_categoria_nombre ON categoria(nombre);

-- =============================================================================
-- TABLA: PROVEEDOR
-- =============================================================================
CREATE TABLE proveedor (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(150) NOT NULL,
    contacto VARCHAR(100),
    telefono VARCHAR(20),
    email VARCHAR(100),
    direccion TEXT,
    rfc VARCHAR(15),
    activo BOOLEAN DEFAULT TRUE,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    fecha_actualizacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- =============================================================================
-- TABLA: PRODUCTO
-- =============================================================================
CREATE TYPE unidad_medida_enum AS ENUM ('pieza', 'kg', 'litro', 'gramo', 'metro', 'caja', 'paquete');

CREATE TABLE producto (
    id SERIAL PRIMARY KEY,
    codigo_barras VARCHAR(50) UNIQUE,
    nombre VARCHAR(200) NOT NULL,
    descripcion TEXT,
    categoria_id INTEGER REFERENCES categoria(id) ON DELETE SET NULL,
    proveedor_id INTEGER REFERENCES proveedor(id) ON DELETE SET NULL,
    precio_compra DECIMAL(10,2) NOT NULL,
    precio_venta DECIMAL(10,2) NOT NULL,
    stock_actual INTEGER DEFAULT 0,
    stock_minimo INTEGER DEFAULT 0,
    stock_maximo INTEGER DEFAULT 1000,
    unidad_medida unidad_medida_enum DEFAULT 'pieza',
    imagen_url VARCHAR(255),
    fecha_vencimiento DATE,
    activo BOOLEAN DEFAULT TRUE,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    fecha_actualizacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Índices para producto
CREATE INDEX idx_producto_codigo_barras ON producto(codigo_barras);
CREATE INDEX idx_producto_nombre ON producto(nombre);
CREATE INDEX idx_producto_categoria ON producto(categoria_id);
CREATE INDEX idx_producto_stock ON producto(stock_actual);

-- =============================================================================
-- TABLA: CLIENTE
-- =============================================================================
CREATE TYPE tipo_cliente_enum AS ENUM ('regular', 'vip', 'mayorista');

CREATE TABLE cliente (
    id SERIAL PRIMARY KEY,
    numero_cliente VARCHAR(20) UNIQUE,
    nombre VARCHAR(100) NOT NULL,
    apellidos VARCHAR(100),
    telefono VARCHAR(20),
    email VARCHAR(100),
    direccion TEXT,
    fecha_nacimiento DATE,
    tipo_cliente tipo_cliente_enum DEFAULT 'regular',
    descuento_aplicable DECIMAL(5,2) DEFAULT 0.00,
    limite_credito DECIMAL(10,2) DEFAULT 0.00,
    activo BOOLEAN DEFAULT TRUE,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    fecha_actualizacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Índices para cliente
CREATE INDEX idx_cliente_numero_cliente ON cliente(numero_cliente);
CREATE INDEX idx_cliente_nombre_completo ON cliente(nombre, apellidos);
CREATE INDEX idx_cliente_telefono ON cliente(telefono);

-- =============================================================================
-- TABLA: USUARIO DEL SISTEMA
-- =============================================================================
CREATE TYPE rol_usuario_enum AS ENUM ('admin', 'cajero', 'vendedor', 'almacenista');

CREATE TABLE usuario (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    email VARCHAR(100) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    nombre VARCHAR(100) NOT NULL,
    apellidos VARCHAR(100),
    rol rol_usuario_enum NOT NULL,
    telefono VARCHAR(20),
    ultimo_acceso TIMESTAMP,
    activo BOOLEAN DEFAULT TRUE,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    fecha_actualizacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Índices para usuario
CREATE INDEX idx_usuario_username ON usuario(username);
CREATE INDEX idx_usuario_email ON usuario(email);
CREATE INDEX idx_usuario_rol ON usuario(rol);

-- =============================================================================
-- TABLA: VENTA (ENCABEZADO)
-- =============================================================================
CREATE TYPE metodo_pago_enum AS ENUM ('efectivo', 'tarjeta', 'transferencia', 'credito');
CREATE TYPE estado_venta_enum AS ENUM ('pendiente', 'completada', 'cancelada', 'devuelta');

CREATE TABLE venta (
    id SERIAL PRIMARY KEY,
    numero_venta VARCHAR(20) UNIQUE NOT NULL,
    cliente_id INTEGER REFERENCES cliente(id) ON DELETE SET NULL,
    usuario_id INTEGER NOT NULL REFERENCES usuario(id),
    fecha_venta TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    subtotal DECIMAL(10,2) NOT NULL DEFAULT 0.00,
    descuento DECIMAL(10,2) DEFAULT 0.00,
    impuestos DECIMAL(10,2) DEFAULT 0.00,
    total DECIMAL(10,2) NOT NULL,
    metodo_pago metodo_pago_enum NOT NULL,
    estado estado_venta_enum DEFAULT 'completada',
    observaciones TEXT
);

-- Índices para venta
CREATE INDEX idx_venta_numero_venta ON venta(numero_venta);
CREATE INDEX idx_venta_fecha_venta ON venta(fecha_venta);
CREATE INDEX idx_venta_cliente ON venta(cliente_id);
CREATE INDEX idx_venta_usuario ON venta(usuario_id);
CREATE INDEX idx_venta_estado ON venta(estado);

-- =============================================================================
-- TABLA: DETALLE DE VENTA
-- =============================================================================
CREATE TABLE detalle_venta (
    id SERIAL PRIMARY KEY,
    venta_id INTEGER NOT NULL REFERENCES venta(id) ON DELETE CASCADE,
    producto_id INTEGER NOT NULL REFERENCES producto(id),
    cantidad DECIMAL(10,2) NOT NULL,
    precio_unitario DECIMAL(10,2) NOT NULL,
    descuento_unitario DECIMAL(10,2) DEFAULT 0.00,
    subtotal DECIMAL(10,2) NOT NULL
);

-- Índices para detalle_venta
CREATE INDEX idx_detalle_venta_venta ON detalle_venta(venta_id);
CREATE INDEX idx_detalle_venta_producto ON detalle_venta(producto_id);

-- =============================================================================
-- TABLA: COMPRA (ENCABEZADO)
-- =============================================================================
CREATE TYPE estado_compra_enum AS ENUM ('pendiente', 'recibida', 'cancelada');

CREATE TABLE compra (
    id SERIAL PRIMARY KEY,
    numero_compra VARCHAR(20) UNIQUE NOT NULL,
    proveedor_id INTEGER NOT NULL REFERENCES proveedor(id),
    usuario_id INTEGER NOT NULL REFERENCES usuario(id),
    fecha_compra TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    subtotal DECIMAL(10,2) NOT NULL DEFAULT 0.00,
    impuestos DECIMAL(10,2) DEFAULT 0.00,
    total DECIMAL(10,2) NOT NULL,
    estado estado_compra_enum DEFAULT 'pendiente',
    observaciones TEXT
);

-- Índices para compra
CREATE INDEX idx_compra_numero_compra ON compra(numero_compra);
CREATE INDEX idx_compra_fecha_compra ON compra(fecha_compra);
CREATE INDEX idx_compra_proveedor ON compra(proveedor_id);
CREATE INDEX idx_compra_estado ON compra(estado);

-- =============================================================================
-- TABLA: DETALLE DE COMPRA
-- =============================================================================
CREATE TABLE detalle_compra (
    id SERIAL PRIMARY KEY,
    compra_id INTEGER NOT NULL REFERENCES compra(id) ON DELETE CASCADE,
    producto_id INTEGER NOT NULL REFERENCES producto(id),
    cantidad DECIMAL(10,2) NOT NULL,
    precio_unitario DECIMAL(10,2) NOT NULL,
    subtotal DECIMAL(10,2) NOT NULL
);

-- Índices para detalle_compra
CREATE INDEX idx_detalle_compra_compra ON detalle_compra(compra_id);
CREATE INDEX idx_detalle_compra_producto ON detalle_compra(producto_id);

-- =============================================================================
-- TABLA: MOVIMIENTO DE INVENTARIO
-- =============================================================================
CREATE TYPE tipo_movimiento_enum AS ENUM ('entrada', 'salida', 'ajuste', 'merma');

CREATE TABLE movimiento_inventario (
    id SERIAL PRIMARY KEY,
    producto_id INTEGER NOT NULL REFERENCES producto(id),
    tipo_movimiento tipo_movimiento_enum NOT NULL,
    cantidad DECIMAL(10,2) NOT NULL,
    stock_anterior INTEGER NOT NULL,
    stock_nuevo INTEGER NOT NULL,
    referencia VARCHAR(100), -- Referencia a venta, compra, etc.
    motivo TEXT,
    usuario_id INTEGER NOT NULL REFERENCES usuario(id),
    fecha_movimiento TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Índices para movimiento_inventario
CREATE INDEX idx_movimiento_producto ON movimiento_inventario(producto_id);
CREATE INDEX idx_movimiento_tipo ON movimiento_inventario(tipo_movimiento);
CREATE INDEX idx_movimiento_fecha ON movimiento_inventario(fecha_movimiento);

-- =============================================================================
-- TABLA: CAJA (CONTROL DE EFECTIVO)
-- =============================================================================
CREATE TYPE estado_caja_enum AS ENUM ('abierta', 'cerrada');

CREATE TABLE caja (
    id SERIAL PRIMARY KEY,
    usuario_id INTEGER NOT NULL REFERENCES usuario(id),
    fecha_apertura TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    fecha_cierre TIMESTAMP,
    monto_inicial DECIMAL(10,2) NOT NULL,
    monto_final DECIMAL(10,2),
    total_ventas_efectivo DECIMAL(10,2) DEFAULT 0.00,
    total_gastos DECIMAL(10,2) DEFAULT 0.00,
    diferencia DECIMAL(10,2) DEFAULT 0.00,
    estado estado_caja_enum DEFAULT 'abierta',
    observaciones TEXT
);

-- Índices para caja
CREATE INDEX idx_caja_usuario ON caja(usuario_id);
CREATE INDEX idx_caja_fecha_apertura ON caja(fecha_apertura);
CREATE INDEX idx_caja_estado ON caja(estado);

-- =============================================================================
-- TABLA: GASTO
-- =============================================================================
CREATE TYPE categoria_gasto_enum AS ENUM ('servicios', 'mercancia', 'mantenimiento', 'administrativo', 'otros');

CREATE TABLE gasto (
    id SERIAL PRIMARY KEY,
    concepto VARCHAR(200) NOT NULL,
    monto DECIMAL(10,2) NOT NULL,
    categoria categoria_gasto_enum NOT NULL,
    fecha_gasto DATE NOT NULL,
    usuario_id INTEGER NOT NULL REFERENCES usuario(id),
    caja_id INTEGER REFERENCES caja(id) ON DELETE SET NULL,
    observaciones TEXT
);

-- Índices para gasto
CREATE INDEX idx_gasto_fecha ON gasto(fecha_gasto);
CREATE INDEX idx_gasto_categoria ON gasto(categoria);
CREATE INDEX idx_gasto_usuario ON gasto(usuario_id);

-- =============================================================================
-- TABLA: CONFIGURACIÓN DEL SISTEMA
-- =============================================================================
CREATE TYPE tipo_config_enum AS ENUM ('string', 'number', 'boolean', 'json');

CREATE TABLE configuracion (
    id SERIAL PRIMARY KEY,
    clave VARCHAR(100) NOT NULL UNIQUE,
    valor TEXT NOT NULL,
    descripcion TEXT,
    tipo tipo_config_enum DEFAULT 'string',
    fecha_actualizacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- =============================================================================
-- FUNCIONES Y TRIGGERS PARA ACTUALIZAR STOCK AUTOMÁTICAMENTE
-- =============================================================================

-- Función para actualizar timestamp
CREATE OR REPLACE FUNCTION update_timestamp()
RETURNS TRIGGER AS $$
BEGIN
    NEW.fecha_actualizacion = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Triggers para actualizar timestamp automáticamente
CREATE TRIGGER trigger_categoria_timestamp
    BEFORE UPDATE ON categoria
    FOR EACH ROW EXECUTE FUNCTION update_timestamp();

CREATE TRIGGER trigger_proveedor_timestamp
    BEFORE UPDATE ON proveedor
    FOR EACH ROW EXECUTE FUNCTION update_timestamp();

CREATE TRIGGER trigger_producto_timestamp
    BEFORE UPDATE ON producto
    FOR EACH ROW EXECUTE FUNCTION update_timestamp();

CREATE TRIGGER trigger_cliente_timestamp
    BEFORE UPDATE ON cliente
    FOR EACH ROW EXECUTE FUNCTION update_timestamp();

CREATE TRIGGER trigger_usuario_timestamp
    BEFORE UPDATE ON usuario
    FOR EACH ROW EXECUTE FUNCTION update_timestamp();

CREATE TRIGGER trigger_configuracion_timestamp
    BEFORE UPDATE ON configuracion
    FOR EACH ROW EXECUTE FUNCTION update_timestamp();

-- Función para actualizar stock después de una venta
CREATE OR REPLACE FUNCTION actualizar_stock_venta()
RETURNS TRIGGER AS $$
DECLARE
    stock_anterior INTEGER;
BEGIN
    -- Obtener stock actual
    SELECT stock_actual INTO stock_anterior 
    FROM producto 
    WHERE id = NEW.producto_id;
    
    -- Actualizar stock del producto
    UPDATE producto 
    SET stock_actual = stock_actual - NEW.cantidad 
    WHERE id = NEW.producto_id;
    
    -- Registrar movimiento de inventario
    INSERT INTO movimiento_inventario (
        producto_id, tipo_movimiento, cantidad, stock_anterior, 
        stock_nuevo, referencia, usuario_id
    ) VALUES (
        NEW.producto_id, 'salida', NEW.cantidad, stock_anterior,
        stock_anterior - NEW.cantidad::INTEGER, 'VENTA-' || NEW.venta_id, 
        (SELECT usuario_id FROM venta WHERE id = NEW.venta_id)
    );
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Función para actualizar stock después de una compra
CREATE OR REPLACE FUNCTION actualizar_stock_compra()
RETURNS TRIGGER AS $$
DECLARE
    stock_anterior INTEGER;
BEGIN
    -- Obtener stock actual
    SELECT stock_actual INTO stock_anterior 
    FROM producto 
    WHERE id = NEW.producto_id;
    
    -- Actualizar stock del producto
    UPDATE producto 
    SET stock_actual = stock_actual + NEW.cantidad 
    WHERE id = NEW.producto_id;
    
    -- Registrar movimiento de inventario
    INSERT INTO movimiento_inventario (
        producto_id, tipo_movimiento, cantidad, stock_anterior, 
        stock_nuevo, referencia, usuario_id
    ) VALUES (
        NEW.producto_id, 'entrada', NEW.cantidad, stock_anterior,
        stock_anterior + NEW.cantidad::INTEGER, 'COMPRA-' || NEW.compra_id,
        (SELECT usuario_id FROM compra WHERE id = NEW.compra_id)
    );
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Triggers para control de stock
CREATE TRIGGER trigger_detalle_venta_stock
    AFTER INSERT ON detalle_venta
    FOR EACH ROW EXECUTE FUNCTION actualizar_stock_venta();

CREATE TRIGGER trigger_detalle_compra_stock
    AFTER INSERT ON detalle_compra
    FOR EACH ROW EXECUTE FUNCTION actualizar_stock_compra();

-- =============================================================================
-- DATOS INICIALES
-- =============================================================================

-- Insertar categorías principales colombianas (categorías padre)
INSERT INTO categoria (nombre, descripcion, padre) VALUES
('Alimentos y despensa', 'Productos alimenticios básicos y despensa', NULL),
('Aseo Hogar', 'Productos de limpieza y cuidado del hogar', NULL),
('Aseo y cuidado personal', 'Productos de higiene y cuidado personal', NULL),
('Bebé', 'Productos para el cuidado del bebé', NULL),
('Lácteos', 'Leche, quesos, yogurt y derivados lácteos', NULL),
('Mascotas', 'Alimentos y productos para mascotas', NULL),
('Bebidas', 'Refrescos, jugos, agua y bebidas en general', NULL);

-- Insertar subcategorías de Alimentos y despensa (id: 1)
INSERT INTO categoria (nombre, descripcion, padre) VALUES
('Granos y cereales', 'Arroz, lentejas, fríjoles, avena', 1),
('Aceites y vinagres', 'Aceites vegetales, vinagres y aderezos', 1),
('Enlatados y conservas', 'Productos enlatados y conservas', 1),
('Condimentos y especias', 'Sal, pimienta, condimentos varios', 1);

-- Insertar subcategorías de Aseo Hogar (id: 2)
INSERT INTO categoria (nombre, descripcion, padre) VALUES
('Detergentes', 'Detergentes para ropa y lavado', 2),
('Limpiadores', 'Limpiadores multiusos y especializados', 2),
('Papelería hogar', 'Papel higiénico, servilletas, toallas', 2);

-- Insertar subcategorías de Lácteos (id: 5)
INSERT INTO categoria (nombre, descripcion, padre) VALUES
('Leches', 'Leche fresca, deslactosada, en polvo', 5),
('Yogures', 'Yogurt natural, griego, con frutas', 5),
('Quesos', 'Quesos frescos, maduros, procesados', 5),
('Mantequillas', 'Mantequilla, margarina, cremas', 5);

-- Insertar subcategorías de Bebidas (id: 7)
INSERT INTO categoria (nombre, descripcion, padre) VALUES
('Gaseosas', 'Refrescos carbonatados', 7),
('Aguas', 'Agua natural, con gas, saborizada', 7),
('Jugos', 'Jugos naturales, néctares, concentrados', 7),
('Bebidas calientes', 'Café, té, chocolate, aromáticas', 7);

-- Insertar subcategorías de Mascotas (id: 6)
INSERT INTO categoria (nombre, descripcion, padre) VALUES
('Comida perros', 'Alimento balanceado para perros', 6),
('Comida gatos', 'Alimento balanceado para gatos', 6),
('Accesorios mascotas', 'Correas, juguetes, camas', 6);

-- Insertar proveedores colombianos
INSERT INTO proveedor (nombre, contacto, telefono, email, direccion) VALUES
('Grupo Nutresa', 'Carlos Rodriguez', '601-3130000', 'ventas@nutresa.com', 'Calle 104 No. 14A-45, Bogotá'),
('Alpina S.A.', 'Maria Gonzalez', '601-4271010', 'comercial@alpina.com', 'Carrera 23 No. 99-54, Bogotá'),
('Colgate-Palmolive', 'Juan Martinez', '601-6542100', 'ventas@colgate.com', 'Zona Franca Bogotá'),
('Unilever Andina', 'Ana Torres', '601-4262828', 'comercial@unilever.com', 'Carrera 68A No. 24B-10, Bogotá'),
('Grupo Bimbo Colombia', 'Luis Herrera', '601-7441020', 'ventas@bimbo.com.co', 'Calle 26 No. 92-32, Bogotá'),
('Bavaria S.A.', 'Sofia Castro', '601-4266000', 'comercial@bavaria.co', 'Carrera 53A No. 127-35, Bogotá'),
('Colombina S.A.', 'Diego Morales', '602-3399500', 'ventas@colombina.com', 'Calle 8 No. 3-65, La Paila, Valle');

-- Insertar usuario administrador por defecto (password: admin123)
INSERT INTO usuario (username, email, password_hash, nombre, apellidos, rol) VALUES
('admin', 'admin@market.com', crypt('admin123', gen_salt('bf')), 'Administrador', 'Sistema', 'admin');

-- Insertar productos de prueba con marcas colombianas

-- GRANOS Y CEREALES (subcategoría de Alimentos y despensa)
INSERT INTO producto (codigo_barras, nombre, descripcion, categoria_id, proveedor_id, precio_compra, precio_venta, stock_actual, stock_minimo, unidad_medida, imagen_url) VALUES
('7702001012345', 'Arroz Diana Selecto x 500g', 'Arroz blanco de grano largo premium marca Diana', 8, 1, 2500.00, 3200.00, 50, 10, 'paquete', 'https://images.unsplash.com/photo-1586201375761-83865001e31c?w=400&h=400&fit=crop');

-- ACEITES Y VINAGRES (subcategoría de Alimentos y despensa)
INSERT INTO producto (codigo_barras, nombre, descripcion, categoria_id, proveedor_id, precio_compra, precio_venta, stock_actual, stock_minimo, unidad_medida, imagen_url) VALUES
('7702001098765', 'Aceite Gourmet Girasol x 900ml', 'Aceite de girasol refinado marca Gourmet', 9, 1, 4800.00, 6200.00, 30, 8, 'litro', 'https://images.unsplash.com/photo-1474979266404-7eaacbcd87c5?w=400&h=400&fit=crop');

-- DETERGENTES (subcategoría de Aseo Hogar)
INSERT INTO producto (codigo_barras, nombre, descripcion, categoria_id, proveedor_id, precio_compra, precio_venta, stock_actual, stock_minimo, unidad_medida, imagen_url) VALUES
('7891024567890', 'Detergente Ariel Poder x 2kg', 'Detergente en polvo para ropa blanca y de color', 12, 3, 15800.00, 19500.00, 25, 5, 'kg', 'https://images.unsplash.com/photo-1556909114-f6e7ad7d3136?w=400&h=400&fit=crop');

-- LIMPIADORES (subcategoría de Aseo Hogar)
INSERT INTO producto (codigo_barras, nombre, descripcion, categoria_id, proveedor_id, precio_compra, precio_venta, stock_actual, stock_minimo, unidad_medida, imagen_url) VALUES
('7891024123456', 'Limpiapisos Fabuloso Lavanda x 900ml', 'Limpiador multiusos aroma lavanda', 13, 4, 3200.00, 4100.00, 40, 10, 'litro', 'https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=400&h=400&fit=crop');

-- ASEO Y CUIDADO PERSONAL (categoría padre)
INSERT INTO producto (codigo_barras, nombre, descripcion, categoria_id, proveedor_id, precio_compra, precio_venta, stock_actual, stock_minimo, unidad_medida, imagen_url) VALUES
('7702425789012', 'Shampoo Sedal Ceramidas x 350ml', 'Shampoo reparación total con ceramidas', 3, 4, 8500.00, 11200.00, 35, 8, 'pieza', 'https://images.unsplash.com/photo-1571781926291-c477ebfd024b?w=400&h=400&fit=crop'),
('7702425345678', 'Jabón Protex Avena x 110g', 'Jabón antibacterial con avena', 3, 3, 2100.00, 2800.00, 60, 15, 'pieza', 'https://images.unsplash.com/photo-1556228578-dd603d5ce7d3?w=400&h=400&fit=crop');

-- BEBÉ (categoría padre)
INSERT INTO producto (codigo_barras, nombre, descripcion, categoria_id, proveedor_id, precio_compra, precio_venta, stock_actual, stock_minimo, unidad_medida, imagen_url) VALUES
('7703186456789', 'Pañales Pequeñín Etapa 3 x 32 unidades', 'Pañales desechables talla M (6-10 kg)', 4, 1, 28500.00, 35200.00, 20, 5, 'paquete', 'https://images.unsplash.com/photo-1545558014-8692077e9b5c?w=400&h=400&fit=crop'),
('7703186987654', 'Toallas Húmedas Pequeñín Aloe x 80 unidades', 'Toallitas húmedas con aloe vera', 4, 1, 8200.00, 10500.00, 45, 10, 'paquete', 'https://images.unsplash.com/photo-1544367567-0f2fcb009e0b?w=400&h=400&fit=crop');

-- LECHES (subcategoría de Lácteos)
INSERT INTO producto (codigo_barras, nombre, descripcion, categoria_id, proveedor_id, precio_compra, precio_venta, stock_actual, stock_minimo, unidad_medida, imagen_url) VALUES
('7702001234567', 'Leche Alpina Entera x 1100ml', 'Leche entera pasteurizada', 16, 2, 3800.00, 4900.00, 80, 20, 'litro', 'https://images.unsplash.com/photo-1550583724-b2692b85b150?w=400&h=400&fit=crop');

-- YOGURES (subcategoría de Lácteos)
INSERT INTO producto (codigo_barras, nombre, descripcion, categoria_id, proveedor_id, precio_compra, precio_venta, stock_actual, stock_minimo, unidad_medida, imagen_url) VALUES
('7702001876543', 'Yogurt Alpina Griego Natural x 150g', 'Yogurt griego natural cremoso', 17, 2, 2400.00, 3100.00, 55, 12, 'pieza', 'https://images.unsplash.com/photo-1571212515416-bb89a2b0f71e?w=400&h=400&fit=crop');

-- COMIDA PERROS (subcategoría de Mascotas)
INSERT INTO producto (codigo_barras, nombre, descripcion, categoria_id, proveedor_id, precio_compra, precio_venta, stock_actual, stock_minimo, unidad_medida, imagen_url) VALUES
('7702048123456', 'Comida Dog Chow Adultos x 2kg', 'Alimento balanceado para perros adultos', 24, 1, 18500.00, 23800.00, 15, 4, 'kg', 'https://images.unsplash.com/photo-1589924691995-400dc9ecc119?w=400&h=400&fit=crop');

-- COMIDA GATOS (subcategoría de Mascotas)
INSERT INTO producto (codigo_barras, nombre, descripcion, categoria_id, proveedor_id, precio_compra, precio_venta, stock_actual, stock_minimo, unidad_medida, imagen_url) VALUES
('7702048789012', 'Arena Sanitaria Cat Chow x 4kg', 'Arena aglomerante para gatos', 25, 1, 12200.00, 15900.00, 20, 5, 'kg', 'https://images.unsplash.com/photo-1574158622682-e40e69881006?w=400&h=400&fit=crop');

-- GASEOSAS (subcategoría de Bebidas)
INSERT INTO producto (codigo_barras, nombre, descripcion, categoria_id, proveedor_id, precio_compra, precio_venta, stock_actual, stock_minimo, unidad_medida, imagen_url) VALUES
('7702103456789', 'Coca-Cola Original x 350ml', 'Gaseosa sabor original', 20, 6, 1200.00, 1800.00, 100, 25, 'pieza', 'https://images.unsplash.com/photo-1561758033-d89a9ad46330?w=400&h=400&fit=crop');

-- AGUAS (subcategoría de Bebidas)
INSERT INTO producto (codigo_barras, nombre, descripcion, categoria_id, proveedor_id, precio_compra, precio_venta, stock_actual, stock_minimo, unidad_medida, imagen_url) VALUES
('7702103987654', 'Agua Cristal Sin Gas x 600ml', 'Agua natural purificada', 21, 6, 800.00, 1200.00, 120, 30, 'pieza', 'https://images.unsplash.com/photo-1559839734-2b71ea197ec2?w=400&h=400&fit=crop');

-- Insertar configuraciones básicas
INSERT INTO configuracion (clave, valor, descripcion, tipo) VALUES
('nombre_negocio', 'Market El Buen Precio', 'Nombre del negocio', 'string'),
('direccion_negocio', 'Calle Principal #123', 'Dirección del negocio', 'string'),
('telefono_negocio', '555-1234', 'Teléfono del negocio', 'string'),
('iva_porcentaje', '16', 'Porcentaje de IVA aplicable', 'number'),
('moneda', 'MXN', 'Moneda utilizada', 'string'),
('decimales_precio', '2', 'Cantidad de decimales para precios', 'number'),
('stock_bajo_notificacion', 'true', 'Activar notificaciones de stock bajo', 'boolean'),
('permitir_venta_sin_stock', 'false', 'Permitir ventas con stock insuficiente', 'boolean');

-- =============================================================================
-- FUNCIONES ÚTILES
-- =============================================================================

-- Función para generar número de venta automático
CREATE OR REPLACE FUNCTION generar_numero_venta()
RETURNS VARCHAR(20) AS $$
DECLARE
    nuevo_numero VARCHAR(20);
    contador INTEGER;
BEGIN
    -- Obtener el último número de venta del día
    SELECT COALESCE(MAX(CAST(SUBSTRING(numero_venta FROM 12) AS INTEGER)), 0) + 1
    INTO contador
    FROM venta
    WHERE DATE(fecha_venta) = CURRENT_DATE;
    
    -- Generar nuevo número con formato: V-YYYYMMDD-NNNN
    nuevo_numero := 'V-' || TO_CHAR(CURRENT_DATE, 'YYYYMMDD') || '-' || LPAD(contador::TEXT, 4, '0');
    
    RETURN nuevo_numero;
END;
$$ LANGUAGE plpgsql;

-- Función para generar número de compra automático
CREATE OR REPLACE FUNCTION generar_numero_compra()
RETURNS VARCHAR(20) AS $$
DECLARE
    nuevo_numero VARCHAR(20);
    contador INTEGER;
BEGIN
    -- Obtener el último número de compra del día
    SELECT COALESCE(MAX(CAST(SUBSTRING(numero_compra FROM 12) AS INTEGER)), 0) + 1
    INTO contador
    FROM compra
    WHERE DATE(fecha_compra) = CURRENT_DATE;
    
    -- Generar nuevo número con formato: C-YYYYMMDD-NNNN
    nuevo_numero := 'C-' || TO_CHAR(CURRENT_DATE, 'YYYYMMDD') || '-' || LPAD(contador::TEXT, 4, '0');
    
    RETURN nuevo_numero;
END;
$$ LANGUAGE plpgsql;

-- =============================================================================
-- FUNCIONES PARA JERARQUÍA DE CATEGORÍAS
-- =============================================================================

-- Función para obtener todas las categorías descendientes de una categoría padre
CREATE OR REPLACE FUNCTION obtener_categorias_descendientes(categoria_padre_id INTEGER)
RETURNS TABLE(id INTEGER, nombre VARCHAR, nivel INTEGER) AS $$
BEGIN
    RETURN QUERY
    WITH RECURSIVE categoria_tree AS (
        -- Caso base: categoría padre
        SELECT c.id, c.nombre, 0 as nivel
        FROM categoria c
        WHERE c.id = categoria_padre_id AND c.activo = true
        
        UNION ALL
        
        -- Caso recursivo: hijos
        SELECT c.id, c.nombre, ct.nivel + 1
        FROM categoria c
        INNER JOIN categoria_tree ct ON c.padre = ct.id
        WHERE c.activo = true
    )
    SELECT ct.id, ct.nombre, ct.nivel
    FROM categoria_tree ct
    ORDER BY ct.nivel, ct.nombre;
END;
$$ LANGUAGE plpgsql;

-- Función para obtener la ruta completa de una categoría (breadcrumb)
CREATE OR REPLACE FUNCTION obtener_ruta_categoria(categoria_id INTEGER)
RETURNS TABLE(id INTEGER, nombre VARCHAR, nivel INTEGER) AS $$
BEGIN
    RETURN QUERY
    WITH RECURSIVE categoria_path AS (
        -- Caso base: categoría actual
        SELECT c.id, c.nombre, c.padre, 0 as nivel
        FROM categoria c
        WHERE c.id = categoria_id
        
        UNION ALL
        
        -- Caso recursivo: padres
        SELECT c.id, c.nombre, c.padre, cp.nivel + 1
        FROM categoria c
        INNER JOIN categoria_path cp ON c.id = cp.padre
        WHERE c.id IS NOT NULL
    )
    SELECT cp.id, cp.nombre, cp.nivel
    FROM categoria_path cp
    ORDER BY cp.nivel DESC;
END;
$$ LANGUAGE plpgsql;

-- Función para verificar si una categoría tiene productos
CREATE OR REPLACE FUNCTION categoria_tiene_productos(categoria_id INTEGER)
RETURNS BOOLEAN AS $$
DECLARE
    producto_count INTEGER;
BEGIN
    SELECT COUNT(*)
    INTO producto_count
    FROM producto p
    WHERE p.categoria_id = categoria_id AND p.activo = true;
    
    RETURN producto_count > 0;
END;
$$ LANGUAGE plpgsql;

-- Función para obtener el total de productos de una categoría y sus descendientes
CREATE OR REPLACE FUNCTION contar_productos_categoria_tree(categoria_padre_id INTEGER)
RETURNS INTEGER AS $$
DECLARE
    total_productos INTEGER;
BEGIN
    WITH RECURSIVE categoria_tree AS (
        -- Caso base: categoría padre
        SELECT id FROM categoria
        WHERE id = categoria_padre_id AND activo = true
        
        UNION ALL
        
        -- Caso recursivo: descendientes
        SELECT c.id FROM categoria c
        INNER JOIN categoria_tree ct ON c.padre = ct.id
        WHERE c.activo = true
    )
    SELECT COUNT(p.id)
    INTO total_productos
    FROM categoria_tree ct
    LEFT JOIN producto p ON ct.id = p.categoria_id
    WHERE p.activo = true;
    
    RETURN COALESCE(total_productos, 0);
END;
$$ LANGUAGE plpgsql;

-- =============================================================================
-- VISTAS ÚTILES CON JERARQUÍA
-- =============================================================================

-- Vista de productos con información completa incluyendo jerarquía de categorías
CREATE OR REPLACE VIEW vista_productos_completa AS
SELECT 
    p.id,
    p.codigo_barras,
    p.nombre,
    p.descripcion,
    c.nombre AS categoria,
    cp.nombre AS categoria_padre,
    pr.nombre AS proveedor,
    p.precio_compra,
    p.precio_venta,
    p.stock_actual,
    p.stock_minimo,
    p.unidad_medida,
    p.fecha_vencimiento,
    p.activo,
    CASE 
        WHEN p.stock_actual <= p.stock_minimo THEN 'BAJO'
        WHEN p.stock_actual = 0 THEN 'AGOTADO'
        ELSE 'NORMAL'
    END AS estado_stock
FROM producto p
LEFT JOIN categoria c ON p.categoria_id = c.id
LEFT JOIN categoria cp ON c.padre = cp.id
LEFT JOIN proveedor pr ON p.proveedor_id = pr.id;

-- Vista de categorías con información jerárquica
CREATE OR REPLACE VIEW vista_categorias_jerarquia AS
SELECT 
    c.id,
    c.nombre,
    c.descripcion,
    c.padre,
    cp.nombre AS categoria_padre,
    c.activo,
    CASE 
        WHEN c.padre IS NULL THEN 'RAIZ'
        ELSE 'SUBCATEGORIA'
    END AS tipo_categoria,
    (SELECT COUNT(*) FROM categoria ch WHERE ch.padre = c.id AND ch.activo = true) AS total_subcategorias,
    (SELECT COUNT(*) FROM producto p WHERE p.categoria_id = c.id AND p.activo = true) AS total_productos_directos,
    c.fecha_creacion
FROM categoria c
LEFT JOIN categoria cp ON c.padre = cp.id
WHERE c.activo = true
ORDER BY 
    CASE WHEN c.padre IS NULL THEN c.id ELSE c.padre END,
    c.padre NULLS FIRST,
    c.nombre;

-- Vista de ventas del día
CREATE OR REPLACE VIEW vista_ventas_hoy AS
SELECT 
    v.id,
    v.numero_venta,
    CONCAT(c.nombre, ' ', COALESCE(c.apellidos, '')) AS cliente,
    u.nombre AS vendedor,
    v.total,
    v.metodo_pago,
    v.fecha_venta
FROM venta v
LEFT JOIN cliente c ON v.cliente_id = c.id
LEFT JOIN usuario u ON v.usuario_id = u.id
WHERE DATE(v.fecha_venta) = CURRENT_DATE
AND v.estado = 'completada';

-- Vista de productos con stock bajo
CREATE OR REPLACE VIEW vista_productos_stock_bajo AS
SELECT 
    p.id,
    p.codigo_barras,
    p.nombre,
    c.nombre AS categoria,
    cp.nombre AS categoria_padre,
    p.stock_actual,
    p.stock_minimo,
    p.precio_venta
FROM producto p
LEFT JOIN categoria c ON p.categoria_id = c.id
LEFT JOIN categoria cp ON c.padre = cp.id
WHERE p.stock_actual <= p.stock_minimo
AND p.activo = TRUE
ORDER BY p.stock_actual ASC;

-- Vista de resumen de ventas diarias
CREATE OR REPLACE VIEW vista_resumen_ventas_diarias AS
SELECT 
    DATE(fecha_venta) AS fecha,
    COUNT(*) AS total_ventas,
    SUM(total) AS total_ingresos,
    AVG(total) AS promedio_venta,
    COUNT(CASE WHEN metodo_pago = 'efectivo' THEN 1 END) AS ventas_efectivo,
    COUNT(CASE WHEN metodo_pago = 'tarjeta' THEN 1 END) AS ventas_tarjeta
FROM venta
WHERE estado = 'completada'
GROUP BY DATE(fecha_venta)
ORDER BY fecha DESC;

-- Vista de categorías raíz con estadísticas
CREATE OR REPLACE VIEW vista_categorias_raiz_estadisticas AS
SELECT 
    c.id,
    c.nombre,
    c.descripcion,
    c.activo,
    (SELECT COUNT(*) FROM categoria ch WHERE ch.padre = c.id AND ch.activo = true) AS total_subcategorias,
    (SELECT COUNT(*) FROM producto p 
     WHERE p.categoria_id = c.id AND p.activo = true) AS productos_directos,
    contar_productos_categoria_tree(c.id) AS total_productos_tree,
    c.fecha_creacion
FROM categoria c
WHERE c.padre IS NULL AND c.activo = true
ORDER BY c.nombre;

-- =============================================================================
-- ÍNDICES ADICIONALES PARA OPTIMIZACIÓN
-- =============================================================================

-- Índices compuestos para consultas frecuentes
CREATE INDEX idx_producto_categoria_activo ON producto(categoria_id, activo);
CREATE INDEX idx_venta_fecha_estado ON venta(fecha_venta, estado);
CREATE INDEX idx_cliente_tipo_activo ON cliente(tipo_cliente, activo);
CREATE INDEX idx_movimientos_fecha_tipo ON movimiento_inventario(fecha_movimiento, tipo_movimiento);

-- =============================================================================
-- FUNCIONES ÚTILES
-- =============================================================================

-- Función para generar número de venta automático
CREATE OR REPLACE FUNCTION generar_numero_venta()
RETURNS VARCHAR(20) AS $$
DECLARE
    nuevo_numero VARCHAR(20);
    contador INTEGER;
BEGIN
    -- Obtener el último número de venta del día
    SELECT COALESCE(MAX(CAST(SUBSTRING(numero_venta FROM 12) AS INTEGER)), 0) + 1
    INTO contador
    FROM venta
    WHERE DATE(fecha_venta) = CURRENT_DATE;
    
    -- Generar nuevo número con formato: V-YYYYMMDD-NNNN
    nuevo_numero := 'V-' || TO_CHAR(CURRENT_DATE, 'YYYYMMDD') || '-' || LPAD(contador::TEXT, 4, '0');
    
    RETURN nuevo_numero;
END;
$$ LANGUAGE plpgsql;

-- Función para generar número de compra automático
CREATE OR REPLACE FUNCTION generar_numero_compra()
RETURNS VARCHAR(20) AS $$
DECLARE
    nuevo_numero VARCHAR(20);
    contador INTEGER;
BEGIN
    -- Obtener el último número de compra del día
    SELECT COALESCE(MAX(CAST(SUBSTRING(numero_compra FROM 12) AS INTEGER)), 0) + 1
    INTO contador
    FROM compra
    WHERE DATE(fecha_compra) = CURRENT_DATE;
    
    -- Generar nuevo número con formato: C-YYYYMMDD-NNNN
    nuevo_numero := 'C-' || TO_CHAR(CURRENT_DATE, 'YYYYMMDD') || '-' || LPAD(contador::TEXT, 4, '0');
    
    RETURN nuevo_numero;
END;
$$ LANGUAGE plpgsql;

-- =============================================================================
-- FUNCIONES PARA JERARQUÍA DE CATEGORÍAS
-- =============================================================================

-- Función para obtener todas las categorías descendientes de una categoría padre
CREATE OR REPLACE FUNCTION obtener_categorias_descendientes(categoria_padre_id INTEGER)
RETURNS TABLE(id INTEGER, nombre VARCHAR, nivel INTEGER) AS $$
BEGIN
    RETURN QUERY
    WITH RECURSIVE categoria_tree AS (
        -- Caso base: categoría padre
        SELECT c.id, c.nombre, 0 as nivel
        FROM categoria c
        WHERE c.id = categoria_padre_id AND c.activo = true
        
        UNION ALL
        
        -- Caso recursivo: hijos
        SELECT c.id, c.nombre, ct.nivel + 1
        FROM categoria c
        INNER JOIN categoria_tree ct ON c.padre = ct.id
        WHERE c.activo = true
    )
    SELECT ct.id, ct.nombre, ct.nivel
    FROM categoria_tree ct
    ORDER BY ct.nivel, ct.nombre;
END;
$$ LANGUAGE plpgsql;

-- Función para obtener la ruta completa de una categoría (breadcrumb)
CREATE OR REPLACE FUNCTION obtener_ruta_categoria(categoria_id INTEGER)
RETURNS TABLE(id INTEGER, nombre VARCHAR, nivel INTEGER) AS $$
BEGIN
    RETURN QUERY
    WITH RECURSIVE categoria_path AS (
        -- Caso base: categoría actual
        SELECT c.id, c.nombre, c.padre, 0 as nivel
        FROM categoria c
        WHERE c.id = categoria_id
        
        UNION ALL
        
        -- Caso recursivo: padres
        SELECT c.id, c.nombre, c.padre, cp.nivel + 1
        FROM categoria c
        INNER JOIN categoria_path cp ON c.id = cp.padre
        WHERE c.id IS NOT NULL
    )
    SELECT cp.id, cp.nombre, cp.nivel
    FROM categoria_path cp
    ORDER BY cp.nivel DESC;
END;
$$ LANGUAGE plpgsql;

-- Función para verificar si una categoría tiene productos
CREATE OR REPLACE FUNCTION categoria_tiene_productos(categoria_id INTEGER)
RETURNS BOOLEAN AS $$
DECLARE
    producto_count INTEGER;
BEGIN
    SELECT COUNT(*)
    INTO producto_count
    FROM producto p
    WHERE p.categoria_id = categoria_id AND p.activo = true;
    
    RETURN producto_count > 0;
END;
$$ LANGUAGE plpgsql;

-- Función para obtener el total de productos de una categoría y sus descendientes
CREATE OR REPLACE FUNCTION contar_productos_categoria_tree(categoria_padre_id INTEGER)
RETURNS INTEGER AS $$
DECLARE
    total_productos INTEGER;
BEGIN
    WITH RECURSIVE categoria_tree AS (
        -- Caso base: categoría padre
        SELECT id FROM categoria
        WHERE id = categoria_padre_id AND activo = true
        
        UNION ALL
        
        -- Caso recursivo: descendientes
        SELECT c.id FROM categoria c
        INNER JOIN categoria_tree ct ON c.padre = ct.id
        WHERE c.activo = true
    )
    SELECT COUNT(p.id)
    INTO total_productos
    FROM categoria_tree ct
    LEFT JOIN producto p ON ct.id = p.categoria_id
    WHERE p.activo = true;
    
    RETURN COALESCE(total_productos, 0);
END;
$$ LANGUAGE plpgsql;

-- =============================================================================
-- CONFIGURACIÓN PARA FASTAPI + SUPABASE
-- =============================================================================

-- Para conectar FastAPI con Supabase PostgreSQL:
-- 1. Obtén la CONNECTION STRING desde Supabase Dashboard → Settings → Database
-- 2. Usa SQLAlchemy o asyncpg en FastAPI
-- 3. Para Storage: Usa la API REST de Supabase Storage

-- Ejemplo de connection string:
-- postgresql://postgres:[PASSWORD]@db.[REF].supabase.co:5432/postgres

-- NO necesitas RLS ya que FastAPI manejará toda la autenticación y autorización
-- Comentamos las políticas RLS para FastAPI

-- =============================================================================
-- RECOMENDACIONES PARA FASTAPI
-- =============================================================================

-- =============================================================================
-- COMENTARIOS FINALES PARA SUPABASE
-- =============================================================================

-- =============================================================================
-- RECOMENDACIONES PARA FASTAPI CON JERARQUÍA DE CATEGORÍAS
-- =============================================================================

-- Este script es ideal para FastAPI + Supabase porque:
-- ✅ PostgreSQL puro sin dependencias de Supabase Auth
-- ✅ Triggers automáticos para lógica de negocio
-- ✅ Vistas optimizadas para APIs REST
-- ✅ Funciones para generar IDs automáticos
-- ✅ Estructura perfecta para modelos Pydantic
-- ✅ JERARQUÍA DE CATEGORÍAS con consultas CTE recursivas
-- ✅ Funciones especializadas para árboles de categorías

-- STACK TECNOLÓGICO RECOMENDADO:
-- 🐍 FastAPI + SQLAlchemy + Alembic (migraciones)
-- 🗄️ Supabase PostgreSQL (base de datos)
-- 📸 Supabase Storage (imágenes de productos)
-- 🔐 JWT tokens manejados por FastAPI
-- 📱 Frontend: React/Vue (web) + React Native/Flutter (mobile)

-- FUNCIONALIDADES DE JERARQUÍA IMPLEMENTADAS:
-- 🌳 Categorías padre e hijas ilimitadas
-- 📊 Funciones para obtener descendientes
-- 🧭 Función de breadcrumb/ruta de categoría
-- 📈 Conteo de productos por árbol de categorías
-- 👀 Vistas optimizadas con información jerárquica

-- EJEMPLOS DE USO DE JERARQUÍA:

-- 1. Obtener todas las subcategorías de "Lácteos" (id: 5):
-- SELECT * FROM obtener_categorias_descendientes(5);

-- 2. Obtener la ruta completa de "Yogures" (breadcrumb):
-- SELECT * FROM obtener_ruta_categoria(17);

-- 3. Contar productos totales en "Bebidas" y subcategorías:
-- SELECT contar_productos_categoria_tree(7);

-- 4. Ver categorías raíz con estadísticas:
-- SELECT * FROM vista_categorias_raiz_estadisticas;

-- 5. Consulta CTE para productos de una categoría y descendientes:
-- WITH RECURSIVE categoria_tree AS (
--     SELECT id FROM categoria WHERE id = 5 AND activo = true
--     UNION ALL
--     SELECT c.id FROM categoria c
--     INNER JOIN categoria_tree ct ON c.padre = ct.id
--     WHERE c.activo = true
-- )
-- SELECT p.* FROM categoria_tree ct
-- INNER JOIN producto p ON ct.id = p.categoria_id
-- WHERE p.activo = true;

-- CONEXIÓN FASTAPI → SUPABASE:
-- 1. Instalar: pip install sqlalchemy asyncpg python-dotenv
-- 2. Obtener connection string de Supabase
-- 3. Configurar DATABASE_URL en .env
-- 4. Crear modelos SQLAlchemy basados en estas tablas
-- 5. Implementar endpoints para jerarquía de categorías

-- PARA STORAGE DE IMÁGENES:
-- 1. Crear bucket "productos" en Supabase Storage
-- 2. Configurar políticas públicas para lectura
-- 3. Usar FastAPI para subir/gestionar archivos
-- 4. URLs de imágenes: https://[proyecto].supabase.co/storage/v1/object/public/productos/[imagen]

-- ESTRUCTURA DE CATEGORÍAS DE EJEMPLO:
-- Alimentos y despensa (1)
--   ├── Granos y cereales (8)
--   ├── Aceites y vinagres (9) 
--   ├── Enlatados y conservas (10)
--   └── Condimentos y especias (11)
-- Lácteos (5)
--   ├── Leches (16)
--   ├── Yogures (17)
--   ├── Quesos (18)
--   └── Mantequillas (19)
-- Bebidas (7)
--   ├── Gaseosas (20)
--   ├── Aguas (21)
--   ├── Jugos (22)
--   └── Bebidas calientes (23)

-- VENTAJAS DE ESTA ARQUITECTURA CON JERARQUÍA:
-- ✅ Control total de la lógica de negocio en FastAPI
-- ✅ Base de datos PostgreSQL robusta y escalable
-- ✅ Storage gratuito hasta 1GB
-- ✅ APIs REST automáticas con OpenAPI/Swagger
-- ✅ Consultas CTE recursivas optimizadas
-- ✅ Fácil testing y deployment
-- ✅ Sin vendor lock-in (puedes migrar PostgreSQL fácilmente)
-- ✅ Soporte completo para categorías anidadas
-- ✅ Funciones especializadas para árboles de datos

-- INSTRUCCIONES DE USO:
-- 1. Ejecuta este script completo en Supabase SQL Editor
-- 2. Configura un bucket "productos" en Storage
-- 3. Obtén la connection string de PostgreSQL
-- 4. Desarrolla tu FastAPI usando estos modelos
-- 5. Implementa endpoints para jerarquía (categorías padre/hijas)
-- 6. ¡A construir tu market con categorías organizadas! 🚀

-- Usuario admin inicial:
-- username: admin
-- password: admin123 (CAMBIAR EN PRODUCCIÓN)

-- PRÓXIMOS PASOS PARA FASTAPI CON JERARQUÍA:
-- 1. Crear modelos Pydantic para requests/responses jerárquicos
-- 2. Implementar autenticación JWT
-- 3. Crear endpoints CRUD para categorías con jerarquía
-- 4. Endpoint para obtener categorías descendientes
-- 5. Endpoint para breadcrumb de categorías
-- 6. Implementar lógica de ventas y inventario
-- 7. Integrar Supabase Storage para imágenes
-- 8. API para productos por categoría y subcategorías