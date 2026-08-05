from datetime import datetime
from src.database import BaseDatos

class BodegaModel:
    def __init__(self):
        self.db = BaseDatos()
        
    # --- MÓDULO HERRAMIENTAS ---
    def registrar_herramienta(self, nombre, descripcion, foto_path):
        conn = self.db.obtener_conexion()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO Herramientas (nombre, descripcion, foto_path, estado_id) VALUES (?, ?, ?, 1)",
            (nombre, descripcion, foto_path)
        )
        conn.commit()
        conn.close()

    def obtener_inventario(self):
        conn = self.db.obtener_conexion()
        cursor = conn.cursor()
        query = '''
            SELECT h.id, h.nombre, h.descripcion, e.nombre, h.foto_path
            FROM Herramientas h
            JOIN EstadoHerramienta e ON h.estado_id = e.id
        '''
        cursor.execute(query)
        filas = cursor.fetchall()
        conn.close()
        return filas

    def eliminar_herramienta(self, herramienta_id):
        conn = self.db.obtener_conexion()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM Herramientas WHERE id = ?", (herramienta_id,))
        conn.commit()
        conn.close()
        
    def obtener_herramientas_disponibles(self):
        conn = self.db.obtener_conexion()
        cursor = conn.cursor()
        cursor.execute("SELECT id, nombre FROM Herramientas WHERE estado_id = 1")
        filas = cursor.fetchall()
        conn.close()
        return filas

    # --- MÓDULO TRABAJADORES ---
    def registrar_trabajador(self, nombre, puesto, telefono):
        conn = self.db.obtener_conexion()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO Trabajadores (nombre, puesto, telefono) VALUES (?, ?, ?)",
            (nombre, puesto, telefono)
        )
        conn.commit()
        conn.close()

    def obtener_trabajadores(self):
        conn = self.db.obtener_conexion()
        cursor = conn.cursor()
        # Se agregan las 4 columnas incluyendo el teléfono
        cursor.execute("SELECT id, nombre, puesto, telefono FROM Trabajadores")
        filas = cursor.fetchall()
        conn.close()
        return filas

    def eliminar_trabajador(self, trabajador_id):
        conn = self.db.obtener_conexion()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM Trabajadores WHERE id = ?", (trabajador_id,))
        conn.commit()
        conn.close()

    # --- MÓDULO PRÉSTAMOS ---
    def registrar_prestamo(self, herramienta_id, trabajador_id, fecha_devolucion):
        conn = self.db.obtener_conexion()
        cursor = conn.cursor()
        fecha_hoy = datetime.now().strftime("%Y-%m-%d")

        cursor.execute(
            "INSERT INTO Prestamos (herramienta_id, trabajador_id, fecha_prestamo, fecha_devolucion_esperada) VALUES (?, ?, ?, ?)",
            (herramienta_id, trabajador_id, fecha_hoy, fecha_devolucion)
        )
        cursor.execute("UPDATE Herramientas SET estado_id = 2 WHERE id = ?", (herramienta_id,))
        conn.commit()
        conn.close()

    def obtener_prestamos_activos(self):
        conn = self.db.obtener_conexion()
        cursor = conn.cursor()
        query = '''
            SELECT p.id, h.nombre, t.nombre, p.fecha_prestamo, p.fecha_devolucion_esperada
            FROM Prestamos p
            JOIN Herramientas h ON p.herramienta_id = h.id
            JOIN Trabajadores t ON p.trabajador_id = t.id
            WHERE p.devuelto = 0
        '''
        cursor.execute(query)
        filas = cursor.fetchall()
        conn.close()
        return filas

    def registrar_devolucion(self, prestamo_id):
        conn = self.db.obtener_conexion()
        cursor = conn.cursor()
        
        cursor.execute("SELECT herramienta_id FROM Prestamos WHERE id = ?", (prestamo_id,))
        res = cursor.fetchone()
        if res:
            herramienta_id = res[0]
            cursor.execute("UPDATE Prestamos SET devuelto = 1 WHERE id = ?", (prestamo_id,))
            cursor.execute("UPDATE Herramientas SET estado_id = 1 WHERE id = ?", (herramienta_id,))
            conn.commit()
        
        conn.close()
