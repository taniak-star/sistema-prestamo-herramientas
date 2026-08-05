import sqlite3

class BaseDatos:
    def __init__(self, db_name="bodega.db"):
        self.db_name = db_name
        self.conexion = sqlite3.connect(self.db_name)
        self.cursor = self.conexion.cursor()
        self.cursor.execute("PRAGMA foreign_keys = ON;")
        self.crear_tablas()

    def crear_tablas(self):
        # 1. Tabla EstadoHerramienta
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS EstadoHerramienta (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre TEXT NOT NULL UNIQUE
            )
        ''')

        # Insertar estados base
        self.cursor.execute("SELECT COUNT(*) FROM EstadoHerramienta")
        if self.cursor.fetchone()[0] == 0:
            self.cursor.executemany(
                "INSERT INTO EstadoHerramienta (nombre) VALUES (?)",
                [('Disponible',), ('Prestada',), ('En Reparación',)]
            )

        # 2. Tabla Trabajadores
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS Trabajadores (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre TEXT NOT NULL,
                puesto TEXT NOT NULL,
                telefono TEXT
            )
        ''')

        # Insertar trabajadores de prueba
        self.cursor.execute("SELECT COUNT(*) FROM Trabajadores")
        if self.cursor.fetchone()[0] == 0:
            self.cursor.executemany(
                "INSERT INTO Trabajadores (nombre, puesto, telefono) VALUES (?, ?, ?)",
                [
                    ("Juan Pérez", "Maestro Obra", "555-0101"),
                    ("Carlos López", "Electricista", "555-0202"),
                    ("Ana Gómez", "Carpintera", "555-0303")
                ]
            )

        # 3. Tabla Herramientas
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS Herramientas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre TEXT NOT NULL,
                descripcion TEXT,
                foto_path TEXT,
                estado_id INTEGER DEFAULT 1,
                FOREIGN KEY (estado_id) REFERENCES EstadoHerramienta(id)
            )
        ''')

        # 4. Tabla Prestamos
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS Prestamos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                herramienta_id INTEGER NOT NULL,
                trabajador_id INTEGER NOT NULL,
                fecha_prestamo TEXT NOT NULL,
                fecha_devolucion_esperada TEXT NOT NULL,
                devuelto INTEGER DEFAULT 0,
                FOREIGN KEY (herramienta_id) REFERENCES Herramientas(id),
                FOREIGN KEY (trabajador_id) REFERENCES Trabajadores(id)
            )
        ''')

        self.conexion.commit()

    def obtener_conexion(self):
        return sqlite3.connect(self.db_name)
