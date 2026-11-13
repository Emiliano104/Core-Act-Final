"""Interfaz gráfica del rastreador de síntomas (Tkinter + matplotlib).

La ventana tiene cuatro pestañas: Registro, Historial, Patrones y Recomendaciones.
Toda la lógica de datos vive en los otros módulos (almacenamiento, analisis y
recomendaciones); este archivo solo se encarga de mostrar y pedir información.
"""

import textwrap
import tkinter as tk
from datetime import date
from tkinter import font as tkfont
from tkinter import messagebox, ttk

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

import almacenamiento
import analisis
import recomendaciones

# Colores de la aplicación
COLOR_PRINCIPAL = "#2a6f64"
COLOR_OSCURO = "#235c53"
COLOR_FONDO = "#f2f6f5"
COLOR_TEXTO = "#1f2d2b"
COLOR_SUAVE = "#5b6b68"
COLOR_ALERTA = "#c0563d"

AVISO = "Esta app no sustituye a un médico. Si tus síntomas son fuertes o no se van, consulta a un profesional."

# Columnas de la tabla del historial: (clave, título, ancho)
COLUMNAS_TABLA = [
    ("fecha", "Fecha", 110),
    ("sintoma", "Síntoma", 190),
    ("intensidad", "Intensidad", 90),
    ("sueno", "Sueño (h)", 90),
    ("comidas", "Comidas", 80),
    ("agua", "Agua (vasos)", 100),
    ("ejercicio", "Ejercicio", 90),
]


class RastreadorApp(tk.Tk):
    """Ventana principal de la aplicación."""

    def __init__(self):
        super().__init__()
        self.title("Rastreador de síntomas")
        self.geometry("980x740")
        self.minsize(860, 640)
        self.configure(bg=COLOR_FONDO)

        self.registros = almacenamiento.leer_registros()  # copia de los datos en pantalla

        self._configurar_estilos()
        self._crear_encabezado()
        self._crear_barra_estado()
        self._crear_pestanas()
        self.actualizar_todo()

    # ------------------------------------------------------------------
    # Construcción de la ventana
    # ------------------------------------------------------------------

    def _configurar_estilos(self):
        """Define colores y estilos de los widgets."""
        fuente = tkfont.nametofont("TkDefaultFont")
        fuente.configure(size=11)
        self.fuente_negrita = fuente.copy()
        self.fuente_negrita.configure(weight="bold")
        self.fuente_titulo = fuente.copy()
        self.fuente_titulo.configure(size=20, weight="bold")

        estilo = ttk.Style(self)
        estilo.theme_use("clam")
        estilo.configure(".", background=COLOR_FONDO, foreground=COLOR_TEXTO)
        estilo.configure("TNotebook", background=COLOR_FONDO, borderwidth=0)
        estilo.configure("TNotebook.Tab", padding=(18, 8), background="#dbe6e3")
        estilo.map("TNotebook.Tab", background=[("selected", "#ffffff")])
        estilo.configure("Treeview", rowheight=26, background="#ffffff", fieldbackground="#ffffff")
        estilo.configure("Treeview.Heading", font=self.fuente_negrita)
        estilo.configure("Suave.TLabel", foreground=COLOR_SUAVE)
        estilo.configure("Titulo.TLabel", font=self.fuente_titulo, foreground=COLOR_PRINCIPAL)
        estilo.configure("Principal.TButton", background=COLOR_PRINCIPAL, foreground="#ffffff",
                         padding=(16, 8), font=self.fuente_negrita)
        estilo.map("Principal.TButton", background=[("active", COLOR_OSCURO)])
        estilo.configure("TButton", padding=(12, 6))

    def _crear_encabezado(self):
        """Título, aviso y botones de datos de ejemplo."""
        encabezado = ttk.Frame(self, padding=(20, 16, 20, 4))
        encabezado.pack(fill="x")

        # Primera fila: título a la izquierda y botones de ejemplo a la derecha
        fila_superior = ttk.Frame(encabezado)
        fila_superior.pack(fill="x")
        ttk.Label(fila_superior, text="Rastreador de síntomas", style="Titulo.TLabel").pack(side="left")
        ttk.Button(fila_superior, text="Borrar datos de ejemplo", command=self.borrar_ejemplos).pack(side="right")
        ttk.Button(fila_superior, text="Cargar datos de ejemplo", command=self.cargar_ejemplo).pack(
            side="right", padx=6)

        # Segunda fila: aviso de que la app no sustituye a un médico
        ttk.Label(encabezado, text=AVISO, style="Suave.TLabel").pack(anchor="w")

    def _crear_barra_estado(self):
        """Barra inferior con el número de registros y la ubicación del archivo."""
        self.var_estado = tk.StringVar()
        ttk.Label(self, textvariable=self.var_estado, style="Suave.TLabel", padding=(20, 6)).pack(
            side="bottom", fill="x")

    def _crear_pestanas(self):
        """Crea el Notebook con las cuatro pestañas."""
        self.pestanas = ttk.Notebook(self)
        self.pestanas.pack(fill="both", expand=True, padx=20, pady=(8, 0))

        marco_registro = ttk.Frame(self.pestanas, padding=24)
        marco_historial = ttk.Frame(self.pestanas, padding=16)
        marco_patrones = ttk.Frame(self.pestanas, padding=16)
        marco_recomendaciones = ttk.Frame(self.pestanas, padding=16)

        self.pestanas.add(marco_registro, text="Registro diario")
        self.pestanas.add(marco_historial, text="Historial")
        self.pestanas.add(marco_patrones, text="Patrones")
        self.pestanas.add(marco_recomendaciones, text="Recomendaciones")

        self._crear_pestana_registro(marco_registro)
        self._crear_pestana_historial(marco_historial)
        self._crear_pestana_patrones(marco_patrones)
        self._crear_pestana_recomendaciones(marco_recomendaciones)

    def _crear_texto(self, marco, alto):
        """Crea un cuadro de texto de solo lectura con estilos para títulos y notas."""
        texto = tk.Text(marco, height=alto, wrap="word", relief="flat", bg="#ffffff",
                        fg=COLOR_TEXTO, padx=16, pady=12, state="disabled", cursor="arrow",
                        font="TkDefaultFont")
        texto.tag_configure("titulo", font=self.fuente_negrita, foreground=COLOR_PRINCIPAL, spacing1=8)
        texto.tag_configure("alerta", font=self.fuente_negrita, foreground=COLOR_ALERTA, spacing1=8)
        texto.tag_configure("suave", foreground=COLOR_SUAVE, spacing1=6)
        return texto

    # ------------------------------------------------------------------
    # Pestaña 1: Registro diario
    # ------------------------------------------------------------------

    def _crear_pestana_registro(self, marco):
        """Formulario para registrar el día."""
        self.var_fecha = tk.StringVar(value=date.today().isoformat())
        self.var_sintoma = tk.StringVar(value="ninguno")
        self.var_intensidad = tk.DoubleVar(value=3)
        self.var_texto_intensidad = tk.StringVar()
        self.var_sueno = tk.StringVar()
        self.var_comidas = tk.StringVar()
        self.var_agua = tk.StringVar()
        self.var_ejercicio = tk.BooleanVar(value=False)
        self.var_mensaje = tk.StringVar()

        formulario = ttk.Frame(marco)
        formulario.pack(anchor="n", pady=8)

        ttk.Label(formulario, text="Fecha (AAAA-MM-DD)").grid(row=0, column=0, sticky="w", pady=8)
        ttk.Entry(formulario, textvariable=self.var_fecha, width=14).grid(row=0, column=1, sticky="w", padx=16)

        ttk.Label(formulario, text="¿Qué sentiste hoy?").grid(row=1, column=0, sticky="w", pady=8)
        selector = ttk.Combobox(formulario, textvariable=self.var_sintoma, values=almacenamiento.SINTOMAS,
                                state="readonly", width=24)
        selector.grid(row=1, column=1, sticky="w", padx=16)
        selector.bind("<<ComboboxSelected>>", self._al_cambiar_sintoma)

        ttk.Label(formulario, text="Intensidad").grid(row=2, column=0, sticky="w", pady=8)
        zona_intensidad = ttk.Frame(formulario)
        zona_intensidad.grid(row=2, column=1, sticky="w", padx=16)
        self.barra_intensidad = ttk.Scale(zona_intensidad, from_=1, to=5, orient="horizontal", length=220,
                                          variable=self.var_intensidad, command=self._al_mover_intensidad)
        self.barra_intensidad.pack(side="left")
        ttk.Label(zona_intensidad, textvariable=self.var_texto_intensidad, width=22).pack(side="left", padx=10)

        ttk.Label(formulario, text="Horas de sueño").grid(row=3, column=0, sticky="w", pady=8)
        ttk.Spinbox(formulario, from_=0, to=24, increment=0.5, textvariable=self.var_sueno,
                    width=8).grid(row=3, column=1, sticky="w", padx=16)

        ttk.Label(formulario, text="Comidas al día").grid(row=4, column=0, sticky="w", pady=8)
        ttk.Spinbox(formulario, from_=0, to=8, increment=1, textvariable=self.var_comidas,
                    width=8).grid(row=4, column=1, sticky="w", padx=16)

        ttk.Label(formulario, text="Vasos de agua").grid(row=5, column=0, sticky="w", pady=8)
        ttk.Spinbox(formulario, from_=0, to=30, increment=1, textvariable=self.var_agua,
                    width=8).grid(row=5, column=1, sticky="w", padx=16)

        ttk.Checkbutton(formulario, text="Hice ejercicio hoy", variable=self.var_ejercicio).grid(
            row=6, column=1, sticky="w", padx=16, pady=8)

        ttk.Button(formulario, text="Guardar registro", style="Principal.TButton",
                   command=self.guardar_registro).grid(row=7, column=0, columnspan=2, pady=(16, 8))
        ttk.Label(formulario, textvariable=self.var_mensaje, foreground=COLOR_PRINCIPAL).grid(
            row=8, column=0, columnspan=2)

        self._al_cambiar_sintoma()
        self._al_mover_intensidad()

    def _al_mover_intensidad(self, _valor=None):
        """Redondea la barra a un número entero y actualiza el texto que la acompaña."""
        nivel = int(round(self.var_intensidad.get()))
        self.var_intensidad.set(nivel)
        etiquetas = {1: "1 (leve)", 5: "5 (muy fuerte)"}
        self.var_texto_intensidad.set(etiquetas.get(nivel, str(nivel)))

    def _al_cambiar_sintoma(self, _evento=None):
        """Si no hubo síntoma, la intensidad no se usa y se desactiva la barra."""
        if self.var_sintoma.get() == "ninguno":
            self.barra_intensidad.state(["disabled"])
        else:
            self.barra_intensidad.state(["!disabled"])

    def _leer_numero(self, variable, nombre, minimo, maximo, tipo):
        """Convierte el texto de un campo a número. Lanza ValueError con un mensaje claro."""
        texto = variable.get().strip().replace(",", ".")
        try:
            valor = tipo(texto)
        except ValueError:
            descripcion = "un número entero" if tipo is int else "un número"
            raise ValueError(f"{nombre}: escribe {descripcion}.") from None
        if not minimo <= valor <= maximo:
            raise ValueError(f"{nombre}: el valor debe estar entre {minimo} y {maximo}.")
        return valor

    def _leer_formulario(self):
        """Valida los campos del formulario y regresa el registro como diccionario."""
        try:
            fecha = date.fromisoformat(self.var_fecha.get().strip())
        except ValueError:
            raise ValueError("La fecha debe tener el formato AAAA-MM-DD, por ejemplo 2026-11-04.") from None
        if fecha > date.today():
            raise ValueError("La fecha no puede ser futura.")

        sintoma = self.var_sintoma.get()
        if sintoma not in almacenamiento.SINTOMAS:
            raise ValueError("Elige un síntoma de la lista.")
        intensidad = 0 if sintoma == "ninguno" else int(round(self.var_intensidad.get()))

        return {
            "fecha": fecha.isoformat(),
            "sintoma": sintoma,
            "intensidad": intensidad,
            "sueno": self._leer_numero(self.var_sueno, "Horas de sueño", 0, 24, float),
            "comidas": self._leer_numero(self.var_comidas, "Comidas al día", 0, 8, int),
            "agua": self._leer_numero(self.var_agua, "Vasos de agua", 0, 30, int),
            "ejercicio": "si" if self.var_ejercicio.get() else "no",
            "ejemplo": "no",
        }

    def guardar_registro(self):
        """Valida el formulario, guarda el registro y actualiza la pantalla."""
        try:
            registro = self._leer_formulario()
        except ValueError as error:
            messagebox.showwarning("Revisa los datos", str(error))
            return

        try:
            reemplazo = almacenamiento.agregar_registro(registro)
        except OSError:
            messagebox.showerror("No se pudo guardar",
                                 "No se pudo escribir el archivo. Si lo tienes abierto en otro programa, ciérralo.")
            return

        self.var_mensaje.set("Actualizamos tu registro de esa fecha." if reemplazo
                             else "Registro guardado. ¡Gracias por llevar tu seguimiento!")
        self._limpiar_formulario()
        self.actualizar_todo()

    def _limpiar_formulario(self):
        """Deja el formulario listo para el siguiente registro."""
        self.var_fecha.set(date.today().isoformat())
        self.var_sintoma.set("ninguno")
        self.var_intensidad.set(3)
        self.var_sueno.set("")
        self.var_comidas.set("")
        self.var_agua.set("")
        self.var_ejercicio.set(False)
        self._al_cambiar_sintoma()
        self._al_mover_intensidad()

    # ------------------------------------------------------------------
    # Pestaña 2: Historial (con filtro por síntoma)
    # ------------------------------------------------------------------

    def _crear_pestana_historial(self, marco):
        """Tabla de registros con filtro por síntoma."""
        self.var_filtro = tk.StringVar(value="Todos")
        self.var_resumen = tk.StringVar()

        barra = ttk.Frame(marco)
        barra.pack(fill="x", pady=(0, 10))
        ttk.Label(barra, text="Filtrar por síntoma:").pack(side="left")
        filtro = ttk.Combobox(barra, textvariable=self.var_filtro, values=["Todos"] + almacenamiento.SINTOMAS,
                              state="readonly", width=24)
        filtro.pack(side="left", padx=10)
        filtro.bind("<<ComboboxSelected>>", lambda _evento: self._actualizar_historial())
        ttk.Button(barra, text="Eliminar registro seleccionado", command=self.eliminar_seleccionado).pack(side="right")

        zona_tabla = ttk.Frame(marco)
        zona_tabla.pack(fill="both", expand=True)
        claves = [clave for clave, _titulo, _ancho in COLUMNAS_TABLA]
        self.tabla = ttk.Treeview(zona_tabla, columns=claves, show="headings", selectmode="browse")
        for clave, titulo, ancho in COLUMNAS_TABLA:
            self.tabla.heading(clave, text=titulo)
            self.tabla.column(clave, width=ancho, anchor="center")
        desplazador = ttk.Scrollbar(zona_tabla, orient="vertical", command=self.tabla.yview)
        self.tabla.configure(yscrollcommand=desplazador.set)
        self.tabla.pack(side="left", fill="both", expand=True)
        desplazador.pack(side="right", fill="y")

        ttk.Label(marco, textvariable=self.var_resumen, style="Suave.TLabel", wraplength=860).pack(
            anchor="w", pady=(10, 0))

    def _actualizar_historial(self):
        """Llena la tabla con los registros (del más reciente al más antiguo) y el resumen."""
        datos = analisis.filtrar_por_sintoma(self.registros, self.var_filtro.get())
        self.tabla.delete(*self.tabla.get_children())

        if datos.empty:
            self.var_resumen.set("No hay registros para mostrar.")
            return

        for _, fila in datos.sort_values("fecha", ascending=False).iterrows():
            intensidad = int(fila["intensidad"]) if fila["intensidad"] > 0 else "-"
            ejercicio = "Sí" if fila["ejercicio"] == "si" else "No"
            self.tabla.insert("", "end", values=(fila["fecha"], fila["sintoma"], intensidad,
                                                 fila["sueno"], int(fila["comidas"]), int(fila["agua"]), ejercicio))

        resumen = analisis.resumen(datos)
        self.var_resumen.set(
            f"Días: {resumen['dias']} (con síntomas: {resumen['dias_con_sintoma']})   |   "
            f"Sueño promedio: {resumen['sueno_promedio']} h   |   "
            f"Comidas promedio: {resumen['comidas_promedio']}   |   "
            f"Agua promedio: {resumen['agua_promedio']} vasos   |   "
            f"Días con ejercicio: {resumen['dias_ejercicio']}")

    def eliminar_seleccionado(self):
        """Elimina el registro que esté seleccionado en la tabla."""
        seleccion = self.tabla.selection()
        if not seleccion:
            messagebox.showinfo("Eliminar registro", "Primero selecciona un registro de la tabla.")
            return

        fecha = str(self.tabla.item(seleccion[0], "values")[0])
        if not messagebox.askyesno("Eliminar registro", f"¿Seguro que quieres eliminar el registro del {fecha}?"):
            return
        self._ejecutar_cambio_de_datos(lambda: almacenamiento.eliminar_registro(fecha))

    # ------------------------------------------------------------------
    # Pestaña 3: Patrones (gráfica + explicación)
    # ------------------------------------------------------------------

    def _crear_pestana_patrones(self, marco):
        """Gráfica de barras y texto con los patrones detectados."""
        # El texto se coloca primero (abajo) para que conserve su altura; la gráfica usa el espacio restante
        self.texto_patrones = self._crear_texto(marco, alto=11)
        self.texto_patrones.pack(side="bottom", fill="x", pady=(10, 0))

        self.figura = Figure(figsize=(8, 3.6), dpi=100, layout="constrained", facecolor="#ffffff")
        self.lienzo = FigureCanvasTkAgg(self.figura, master=marco)
        self.lienzo.get_tk_widget().pack(fill="both", expand=True)

    def _mostrar_mensaje_en_grafica(self, mensaje):
        """Muestra un mensaje centrado en lugar de la gráfica."""
        self.figura.clear()
        self.figura.text(0.5, 0.5, mensaje, ha="center", va="center", fontsize=12, color=COLOR_SUAVE)
        self.lienzo.draw()

    def _dibujar_grafica(self, patrones):
        """Dibuja, para cada hábito, el % de días con síntomas cuando se cumple y cuando no."""
        self.figura.clear()
        eje = self.figura.add_subplot(111)

        posiciones = list(range(len(patrones)))
        ancho = 0.38
        barras_cumple = eje.bar([p - ancho / 2 for p in posiciones], [p["p_cumple"] for p in patrones],
                                ancho, color=COLOR_ALERTA, label="Cuando se cumple")
        barras_no_cumple = eje.bar([p + ancho / 2 for p in posiciones], [p["p_no_cumple"] for p in patrones],
                                   ancho, color=COLOR_PRINCIPAL, label="Cuando no se cumple")
        eje.bar_label(barras_cumple, fmt="%d%%", padding=2)
        eje.bar_label(barras_no_cumple, fmt="%d%%", padding=2)

        eje.set_xticks(posiciones)
        eje.set_xticklabels([textwrap.fill(p["cumple"].capitalize(), 18) for p in patrones])
        eje.set_ylim(0, 115)
        eje.set_yticks([0, 25, 50, 75, 100])
        eje.set_ylabel("% de días con síntomas")
        eje.set_title("¿Cuándo aparecen más síntomas?", loc="left", fontweight="bold")
        eje.spines[["top", "right"]].set_visible(False)
        eje.legend(loc="upper center", bbox_to_anchor=(0.5, -0.22), ncol=2, frameon=False)
        self.lienzo.draw()

    def _actualizar_patrones(self, patrones):
        """Actualiza la gráfica y el texto de la pestaña Patrones."""
        total = len(self.registros)
        if total < analisis.MIN_REGISTROS:
            self._mostrar_mensaje_en_grafica(
                f"Necesitas al menos {analisis.MIN_REGISTROS} registros para ver patrones.\n"
                f"Tienes {total}. Registra más días o carga datos de ejemplo.")
            self._escribir_texto(self.texto_patrones, [])
            return

        if not patrones:
            self._mostrar_mensaje_en_grafica("Todavía no hay suficientes días comparables en tus hábitos.\n"
                                             "Sigue registrando para que haya más variedad.")
            self._escribir_texto(self.texto_patrones, [])
            return

        self._dibujar_grafica(patrones)

        lineas = []
        claros = [p for p in patrones if p["es_patron"]]
        if claros:
            lineas.append(("Posibles patrones", "alerta"))
            for patron in claros:
                extra = f" Más común: {patron['sintoma_comun']}." if patron["sintoma_comun"] else ""
                lineas.append((f"• Cuando {patron['cumple']}: síntomas el {patron['p_cumple']}% de los días "
                               f"(contra {patron['p_no_cumple']}% cuando {patron['no_cumple']}).{extra}", None))
        else:
            lineas.append(("Por ahora no se ve ningún patrón claro.", "titulo"))
        lineas.append(("Son patrones simples basados en tus registros, no son un diagnóstico.", "suave"))
        self._escribir_texto(self.texto_patrones, lineas)

    # ------------------------------------------------------------------
    # Pestaña 4: Recomendaciones
    # ------------------------------------------------------------------

    def _crear_pestana_recomendaciones(self, marco):
        """Cuadro de texto con las recomendaciones."""
        self.texto_recomendaciones = self._crear_texto(marco, alto=20)
        self.texto_recomendaciones.pack(fill="both", expand=True)

    def _actualizar_recomendaciones(self, patrones):
        """Escribe las recomendaciones según los patrones detectados."""
        total = len(self.registros)
        lineas = []

        if total < analisis.MIN_REGISTROS:
            lineas.append((f"Necesitas al menos {analisis.MIN_REGISTROS} registros para dar recomendaciones. "
                           f"Tienes {total}.", "titulo"))
            lineas.append(("Registra más días o carga datos de ejemplo.", None))
        else:
            consejos = recomendaciones.generar_recomendaciones(patrones)
            if not consejos:
                lineas.append(("Por ahora no se ve ningún patrón claro en tus registros.", "titulo"))
                lineas.append(("Sigue registrando tus días y vuelve a revisar en unos días.", None))
            else:
                lineas.append(("Según tus registros, estos hábitos podrían ayudarte:", None))
                for numero, (situacion, consejo) in enumerate(consejos, start=1):
                    lineas.append((f"{numero}. Cuando {situacion} aparecen más síntomas", "titulo"))
                    lineas.append((consejo, None))

        lineas.append(("Son sugerencias generales de hábitos, no un diagnóstico. Si tus síntomas son fuertes, "
                       "frecuentes o no se van, consulta a un profesional de la salud.", "suave"))
        self._escribir_texto(self.texto_recomendaciones, lineas)

    # ------------------------------------------------------------------
    # Utilidades compartidas
    # ------------------------------------------------------------------

    def _escribir_texto(self, widget, lineas):
        """Reemplaza el contenido de un cuadro de texto. `lineas` es una lista de (texto, estilo)."""
        widget.configure(state="normal")
        widget.delete("1.0", "end")
        for texto, estilo in lineas:
            widget.insert("end", texto + "\n", estilo or "")
        widget.configure(state="disabled")

    def _ejecutar_cambio_de_datos(self, accion):
        """Ejecuta una acción que modifica el CSV, avisa si falla y actualiza la pantalla."""
        try:
            accion()
        except OSError:
            messagebox.showerror("No se pudo guardar",
                                 "No se pudo escribir el archivo. Si lo tienes abierto en otro programa, ciérralo.")
            return
        self.actualizar_todo()

    def cargar_ejemplo(self):
        """Agrega 14 días de datos simulados después de pedir confirmación."""
        if not messagebox.askyesno("Datos de ejemplo",
                                   "Esto agregará 14 días de datos de ejemplo.\n"
                                   "Si ya tenías un registro en alguna de esas fechas, se conserva el tuyo.\n\n"
                                   "¿Quieres continuar?"):
            return
        self._ejecutar_cambio_de_datos(almacenamiento.cargar_ejemplo)

    def borrar_ejemplos(self):
        """Elimina los datos de ejemplo (tus registros reales no se tocan)."""
        if not (self.registros["ejemplo"] == "si").any():
            messagebox.showinfo("Datos de ejemplo", "No hay datos de ejemplo para borrar.")
            return
        if not messagebox.askyesno("Datos de ejemplo",
                                   "Se borrarán solo los datos de ejemplo. Tus registros no se tocan.\n\n"
                                   "¿Quieres continuar?"):
            return
        self._ejecutar_cambio_de_datos(almacenamiento.borrar_ejemplos)

    def actualizar_todo(self):
        """Vuelve a leer el CSV y actualiza todas las pestañas."""
        self.registros = almacenamiento.leer_registros()

        patrones = []
        if len(self.registros) >= analisis.MIN_REGISTROS:
            patrones = analisis.detectar_patrones(self.registros)

        self._actualizar_historial()
        self._actualizar_patrones(patrones)
        self._actualizar_recomendaciones(patrones)
        self.var_estado.set(f"Registros guardados: {len(self.registros)}   |   "
                            f"Archivo: datos/{almacenamiento.ARCHIVO_CSV.name}")


def iniciar():
    """Crea la ventana y arranca la aplicación."""
    app = RastreadorApp()
    app.mainloop()
