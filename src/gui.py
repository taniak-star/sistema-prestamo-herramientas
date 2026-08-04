import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import datetime
import os
import shutil
from PIL import Image, ImageTk
from src.models import BodegaModel

class SistemaBodegaGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Sistema de Préstamo de Herramientas")
        self.root.geometry("1050x650")

        self.model = BodegaModel()
        self.ruta_foto_seleccionada = ""
        self.imagen_preview_tk = None

        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill="both", expand=True, padx=10, pady=10)

        self._crear_pestana_inventario()
        self._crear_pestana_trabajadores()
        self._crear_pestana_prestamos()
        self._crear_pestana_devoluciones()

        self.actualizar_todo()

    def actualizar_todo(self):
        self.cargar_inventario()
        self.cargar_combos_prestamo()
        self.cargar_prestamos_activos()
        self.cargar_trabajadores_tabla()

    # ---------------------------------------------------------
    # PESTAÑA 1: INVENTARIO DE HERRAMIENTAS
    # ---------------------------------------------------------
    def _crear_pestana_inventario(self):
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="Inventario de Herramientas")

        frame_form = ttk.LabelFrame(tab, text=" Registrar Nueva Herramienta ")
        frame_form.pack(side="left", fill="y", padx=10, pady=10)

        ttk.Label(frame_form, text="Nombre:").pack(anchor="w", padx=5, pady=2)
        self.ent_nombre = ttk.Entry(frame_form, width=28)
        self.ent_nombre.pack(padx=5, pady=2)

        ttk.Label(frame_form, text="Descripción:").pack(anchor="w", padx=5, pady=2)
        self.ent_desc = ttk.Entry(frame_form, width=28)
        self.ent_desc.pack(padx=5, pady=2)

        btn_foto = ttk.Button(frame_form, text="Seleccionar Imagen", command=self.seleccionar_foto)
        btn_foto.pack(padx=5, pady=10)

        self.lbl_foto_status = ttk.Label(frame_form, text="Sin foto seleccionada", foreground="gray")
        self.lbl_foto_status.pack(padx=5, pady=2)

        btn_guardar = ttk.Button(frame_form, text="Guardar Herramienta", command=self.guardar_herramienta)
        btn_guardar.pack(padx=5, pady=15, fill="x")

        frame_tabla = ttk.Frame(tab)
        frame_tabla.pack(side="left", fill="both", expand=True, padx=5, pady=10)

        self.tree_inv = ttk.Treeview(frame_tabla, columns=("ID", "Nombre", "Descripción", "Estado"), show="headings")
        self.tree_inv.heading("ID", text="ID")
        self.tree_inv.heading("Nombre", text="Nombre")
        self.tree_inv.heading("Descripción", text="Descripción")
        self.tree_inv.heading("Estado", text="Estado")

        self.tree_inv.column("ID", width=40, anchor="center")
        self.tree_inv.column("Nombre", width=130)
        self.tree_inv.column("Descripción", width=180)
        self.tree_inv.column("Estado", width=90, anchor="center")
        
        self.tree_inv.pack(fill="both", expand=True)
        self.tree_inv.bind("<<TreeviewSelect>>", self.mostrar_foto_detalle)

        # Botón eliminar debajo de la tabla
        btn_eliminar_h = ttk.Button(frame_tabla, text="Eliminar Herramienta Seleccionada", command=self.eliminar_herramienta)
        btn_eliminar_h.pack(pady=5, fill="x")

        # Visor de foto
        frame_visor = ttk.LabelFrame(tab, text=" Fotografía ")
        frame_visor.pack(side="right", fill="y", padx=10, pady=10)

        self.lbl_imagen_visor = ttk.Label(frame_visor, text="Selecciona una herramienta\npara ver su foto", anchor="center")
        self.lbl_imagen_visor.pack(padx=20, pady=40)

    def seleccionar_foto(self):
        filepath = filedialog.askopenfilename(filetypes=[("Imágenes", "*.png *.jpg *.jpeg")])
        if filepath:
            os.makedirs("uploads", exist_ok=True)
            nombre_archivo = f"{int(datetime.now().timestamp())}_{os.path.basename(filepath)}"
            destino = os.path.join("uploads", nombre_archivo)
            shutil.copy(filepath, destino)
            
            self.ruta_foto_seleccionada = destino
            self.lbl_foto_status.config(text=os.path.basename(destino), foreground="black")

    def guardar_herramienta(self):
        nombre = self.ent_nombre.get().strip()
        desc = self.ent_desc.get().strip()

        if not nombre:
            messagebox.showwarning("Atención", "Escriba el nombre de la herramienta.")
            return

        self.model.registrar_herramienta(nombre, desc, self.ruta_foto_seleccionada)
        messagebox.showinfo("Éxito", "Herramienta registrada correctamente.")
        
        self.ent_nombre.delete(0, tk.END)
        self.ent_desc.delete(0, tk.END)
        self.ruta_foto_seleccionada = ""
        self.lbl_foto_status.config(text="Sin foto seleccionada", foreground="gray")
        self.actualizar_todo()

    def eliminar_herramienta(self):
        sel = self.tree_inv.selection()
        if not sel:
            messagebox.showwarning("Atención", "Seleccione una herramienta de la lista para eliminar.")
            return

        item = self.tree_inv.item(sel[0])
        h_id = item['values'][0]
        h_nombre = item['values'][1]

        if messagebox.askyesno("Confirmar", f"¿Está seguro de eliminar la herramienta '{h_nombre}'?"):
            try:
                self.model.eliminar_herramienta(h_id)
                messagebox.showinfo("Éxito", "Herramienta eliminada correctamente.")
                self.lbl_imagen_visor.config(image="", text="Selecciona una herramienta\npara ver su foto")
                self.actualizar_todo()
            except Exception as e:
                messagebox.showerror("Error", "No se puede eliminar la herramienta si tiene un historial de préstamos asociado.")

    def cargar_inventario(self):
        for row in self.tree_inv.get_children():
            self.tree_inv.delete(row)
        for h in self.model.obtener_inventario():
            self.tree_inv.insert("", tk.END, values=(h[0], h[1], h[2], h[3]), tags=(h[4],))

    def mostrar_foto_detalle(self, event):
        sel = self.tree_inv.selection()
        if not sel:
            return
        
        item = self.tree_inv.item(sel[0])
        foto_path = item['tags'][0] if item['tags'] else ""

        if foto_path and os.path.exists(foto_path):
            try:
                img = Image.open(foto_path)
                img = img.resize((180, 180), Image.Resampling.LANCZOS)
                self.imagen_preview_tk = ImageTk.PhotoImage(img)
                self.lbl_imagen_visor.config(image=self.imagen_preview_tk, text="")
            except Exception:
                self.lbl_imagen_visor.config(image="", text="Error al cargar imagen")
        else:
            self.lbl_imagen_visor.config(image="", text="[ Sin Fotografía ]")

    # ---------------------------------------------------------
    # PESTAÑA 2: TRABAJADORES
    # ---------------------------------------------------------
    def _crear_pestana_trabajadores(self):
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="Trabajadores")

        frame_form = ttk.LabelFrame(tab, text=" Registrar Nuevo Trabajador ")
        frame_form.pack(side="left", fill="y", padx=10, pady=10)

        ttk.Label(frame_form, text="Nombre Completo:").pack(anchor="w", padx=5, pady=2)
        self.ent_t_nombre = ttk.Entry(frame_form, width=30)
        self.ent_t_nombre.pack(padx=5, pady=2)

        ttk.Label(frame_form, text="Puesto / Cargo:").pack(anchor="w", padx=5, pady=2)
        self.ent_t_puesto = ttk.Entry(frame_form, width=30)
        self.ent_t_puesto.pack(padx=5, pady=2)

        ttk.Label(frame_form, text="Teléfono:").pack(anchor="w", padx=5, pady=2)
        self.ent_t_tel = ttk.Entry(frame_form, width=30)
        self.ent_t_tel.pack(padx=5, pady=2)

        btn_guardar_t = ttk.Button(frame_form, text="Guardar Trabajador", command=self.guardar_trabajador)
        btn_guardar_t.pack(padx=5, pady=15, fill="x")

        frame_tabla = ttk.Frame(tab)
        frame_tabla.pack(side="right", fill="both", expand=True, padx=10, pady=10)

        self.tree_trab = ttk.Treeview(frame_tabla, columns=("ID", "Nombre", "Puesto", "Teléfono"), show="headings")
        self.tree_trab.heading("ID", text="ID")
        self.tree_trab.heading("Nombre", text="Nombre")
        self.tree_trab.heading("Puesto", text="Puesto")
        self.tree_trab.heading("Teléfono", text="Teléfono")

        self.tree_trab.column("ID", width=40, anchor="center")
        self.tree_trab.column("Nombre", width=180)
        self.tree_trab.column("Puesto", width=150)
        self.tree_trab.column("Teléfono", width=120)

        self.tree_trab.pack(fill="both", expand=True)

        # Botón eliminar debajo de la tabla
        btn_eliminar_t = ttk.Button(frame_tabla, text="Eliminar Trabajador Seleccionado", command=self.eliminar_trabajador)
        btn_eliminar_t.pack(pady=5, fill="x")

    def guardar_trabajador(self):
        nombre = self.ent_t_nombre.get().strip()
        puesto = self.ent_t_puesto.get().strip()
        telefono = self.ent_t_tel.get().strip()

        if not nombre or not puesto:
            messagebox.showwarning("Atención", "Nombre y puesto son obligatorios.")
            return

        self.model.registrar_trabajador(nombre, puesto, telefono if telefono else "N/A")
        messagebox.showinfo("Éxito", "Trabajador registrado correctamente.")
        
        self.ent_t_nombre.delete(0, tk.END)
        self.ent_t_puesto.delete(0, tk.END)
        self.ent_t_tel.delete(0, tk.END)

        self.actualizar_todo()

    def eliminar_trabajador(self):
        sel = self.tree_trab.selection()
        if not sel:
            messagebox.showwarning("Atención", "Seleccione un trabajador de la lista para eliminar.")
            return

        item = self.tree_trab.item(sel[0])
        t_id = item['values'][0]
        t_nombre = item['values'][1]

        if messagebox.askyesno("Confirmar", f"¿Está seguro de eliminar al trabajador '{t_nombre}'?"):
            try:
                self.model.eliminar_trabajador(t_id)
                messagebox.showinfo("Éxito", "Trabajador eliminado correctamente.")
                self.actualizar_todo()
            except Exception:
                messagebox.showerror("Error", "No se puede eliminar el trabajador si tiene registros de préstamos vinculados.")

    def cargar_trabajadores_tabla(self):
        for item in self.tree_trab.get_children():
            self.tree_trab.delete(item)
        for t in self.model.obtener_trabajadores():
            self.tree_trab.insert("", tk.END, values=(t[0], t[1], t[2], t[3]))

    # ---------------------------------------------------------
    # PESTAÑA 3: PRÉSTAMOS
    # ---------------------------------------------------------
    def _crear_pestana_prestamos(self):
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="Registrar Préstamo")

        frame = ttk.LabelFrame(tab, text=" Nuevo Préstamo ")
        frame.pack(fill="both", expand=True, padx=20, pady=20)

        ttk.Label(frame, text="Herramienta Disponible:").grid(row=0, column=0, sticky="w", padx=10, pady=10)
        self.combo_herramientas = ttk.Combobox(frame, state="readonly", width=40)
        self.combo_herramientas.grid(row=0, column=1, padx=10, pady=10)

        ttk.Label(frame, text="Trabajador:").grid(row=1, column=0, sticky="w", padx=10, pady=10)
        self.combo_trabajadores = ttk.Combobox(frame, state="readonly", width=40)
        self.combo_trabajadores.grid(row=1, column=1, padx=10, pady=10)

        ttk.Label(frame, text="Fecha Devolución (AAAA-MM-DD):").grid(row=2, column=0, sticky="w", padx=10, pady=10)
        self.ent_fecha_dev = ttk.Entry(frame, width=20)
        self.ent_fecha_dev.insert(0, datetime.now().strftime("%Y-%m-%d"))
        self.ent_fecha_dev.grid(row=2, column=1, sticky="w", padx=10, pady=10)

        btn = ttk.Button(frame, text="Realizar Préstamo", command=self.realizar_prestamo)
        btn.grid(row=3, column=0, columnspan=2, pady=20)

    def cargar_combos_prestamo(self):
        h_disponibles = self.model.obtener_herramientas_disponibles()
        self.combo_herramientas['values'] = [f"{h[0]} - {h[1]}" for h in h_disponibles]

        trabajadores = self.model.obtener_trabajadores()
        self.combo_trabajadores['values'] = [f"{t[0]} - {t[1]} ({t[2]})" for t in trabajadores]

    def realizar_prestamo(self):
        h_sel = self.combo_herramientas.get()
        t_sel = self.combo_trabajadores.get()
        fecha_dev = self.ent_fecha_dev.get().strip()

        if not h_sel or not t_sel or not fecha_dev:
            messagebox.showwarning("Atención", "Complete todos los campos.")
            return

        h_id = h_sel.split(" - ")[0]
        t_id = t_sel.split(" - ")[0]

        self.model.registrar_prestamo(h_id, t_id, fecha_dev)
        messagebox.showinfo("Éxito", "Préstamo registrado.")
        self.actualizar_todo()

    # ---------------------------------------------------------
    # PESTAÑA 4: DEVOLUCIONES Y ALERTAS
    # ---------------------------------------------------------
    def _crear_pestana_devoluciones(self):
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="Devoluciones y Alertas de Retraso")

        self.tree_dev = ttk.Treeview(tab, columns=("ID", "Herramienta", "Trabajador", "F. Préstamo", "F. Límite", "Estado"), show="headings")
        self.tree_dev.heading("ID", text="ID Préstamo")
        self.tree_dev.heading("Herramienta", text="Herramienta")
        self.tree_dev.heading("Trabajador", text="Trabajador")
        self.tree_dev.heading("F. Préstamo", text="Fecha Préstamo")
        self.tree_dev.heading("F. Límite", text="Fecha Límite")
        self.tree_dev.heading("Estado", text="Estatus")

        self.tree_dev.tag_configure("retrasado", background="#FFCCCC", foreground="#8B0000")
        self.tree_dev.tag_configure("a_tiempo", background="#E6FFFA", foreground="#006600")

        self.tree_dev.pack(fill="both", expand=True, padx=10, pady=10)

        btn_dev = ttk.Button(tab, text="Marcar Selección como Devuelto", command=self.devolver_herramienta)
        btn_dev.pack(pady=10)

    def cargar_prestamos_activos(self):
        for item in self.tree_dev.get_children():
            self.tree_dev.delete(item)

        hoy = datetime.now().strftime("%Y-%m-%d")
        for p in self.model.obtener_prestamos_activos():
            p_id, h_nom, t_nom, f_prest, f_limite = p
            
            if f_limite < hoy:
                estatus = "⚠️ ATRASADO"
                tag = "retrasado"
            else:
                estatus = "En Regla"
                tag = "a_tiempo"

            self.tree_dev.insert("", tk.END, values=(p_id, h_nom, t_nom, f_prest, f_limite, estatus), tags=(tag,))

    def devolver_herramienta(self):
        sel = self.tree_dev.selection()
        if not sel:
            messagebox.showwarning("Atención", "Seleccione un préstamo activo de la lista.")
            return

        p_id = self.tree_dev.item(sel)['values'][0]
        self.model.registrar_devolucion(p_id)
        messagebox.showinfo("Éxito", "Herramienta devuelta a bodega.")
        self.actualizar_todo()