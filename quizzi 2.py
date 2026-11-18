"""Quiz de Historia de México (Independencia y Revolución) con Tkinter."""
import csv
import os
import random
import tkinter as tk
from tkinter import messagebox

ARCHIVO_CSV = "preguntas.csv"
# Busca el CSV junto al programa, sin importar desde donde se ejecute
RUTA_CSV = os.path.join(os.path.dirname(os.path.abspath(__file__)), ARCHIVO_CSV)
NUM_PREGUNTAS = 3
VIDAS_INICIALES = 3
PUNTOS_ACIERTO = 10

FUENTE_PREGUNTA = ("Times New Roman", 16, "bold")
FUENTE_TEXTO = ("Times New Roman", 12)
COLOR_TEXTO = "#000000" 


def leer_texto(ruta):
    """Lee el archivo probando UTF-8 y, si falla, la codificacion de Excel en Windows."""
    for codificacion in ("utf-8-sig", "cp1252"):
        try:
            with open(ruta, newline="", encoding=codificacion) as f:
                return f.read()
        except UnicodeDecodeError:
            continue
    return ""


def cargar_preguntas(ruta=RUTA_CSV):
    """Lee TODAS las preguntas del CSV. Devuelve lista de dicts o None si falta el archivo."""
    try:
        texto = leer_texto(ruta)
    except FileNotFoundError:
        return None

    
    primera_linea = texto.splitlines()[0] if texto.strip() else ""
    delimitador = ";" if primera_linea.count(";") > primera_linea.count(",") else ","

    preguntas = []
    lector = csv.reader(texto.splitlines(), delimiter=delimitador)
    next(lector, None)  # saltar encabezado
    for fila in lector:
        if len(fila) < 6:
            continue
        preguntas.append({
            "pregunta": fila[0].strip(),
            "opciones": [o.strip() for o in fila[1:5]],
            "correcta": fila[5].strip(),
        })
    return preguntas


class QuizApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Quiz de Historia de México")
        self.root.geometry("640x420")
        self.root.resizable(False, False)

        self.nombre = tk.StringVar()
        self.seleccion = tk.StringVar()
        self.frame_actual = None

        self.mostrar_inicio()

    #  utilidades 
    def cambiar_vista(self):
        if self.frame_actual is not None:
            self.frame_actual.destroy()
        self.frame_actual = tk.Frame(self.root, padx=20, pady=20)
        self.frame_actual.pack(fill="both", expand=True)
        return self.frame_actual

    # Inicio 
    def mostrar_inicio(self):
        f = self.cambiar_vista()
        tk.Label(f, text="Quiz de Historia",
                 font=("Times New Roman", 22, "bold"), fg=COLOR_TEXTO).pack(pady=(30, 5))
        tk.Label(f, text="Independencia y Revolución Mexicana",
                 font=FUENTE_TEXTO, fg=COLOR_TEXTO).pack(pady=(0, 30))
        tk.Label(f, text="Nombre del jugador:", font=FUENTE_TEXTO,
                 fg=COLOR_TEXTO).pack()
        entrada = tk.Entry(f, textvariable=self.nombre, font=FUENTE_TEXTO, width=28)
        entrada.pack(pady=8)
        entrada.focus()
        tk.Button(f, text="Comenzar", font=FUENTE_TEXTO, width=14,
                  command=self.comenzar).pack(pady=20)

    def comenzar(self):
        if not self.nombre.get().strip():
            messagebox.showwarning("Falta el nombre", "Escribe tu nombre para comenzar.")
            return

        todas = cargar_preguntas()
        if todas is None:
            messagebox.showerror(
                "Archivo no encontrado",
                f"No se encontró el archivo '{ARCHIVO_CSV}'.\n"
                "Colócalo en la misma carpeta que el programa e inténtalo de nuevo.")
            return
        if len(todas) < NUM_PREGUNTAS:
            messagebox.showerror(
                "Pocas preguntas",
                f"El archivo tiene {len(todas)} preguntas y se necesitan al menos "
                f"{NUM_PREGUNTAS}. No se puede iniciar el juego.")
            return

        self.preguntas = random.sample(todas, NUM_PREGUNTAS)
        self.indice = 0
        self.vidas = VIDAS_INICIALES
        self.puntaje = 0
        self.mostrar_juego()

    # Juego 
    def mostrar_juego(self):
        f = self.cambiar_vista()
        p = self.preguntas[self.indice]
        self.seleccion.set("")
        self.respondida = False

        self.lbl_vidas = tk.Label(f, text=f"Vidas: {'❤️ ' * self.vidas}".strip(),
                                  font=FUENTE_TEXTO, fg="#b00020")
        self.lbl_vidas.grid(row=0, column=0, sticky="w")
        self.lbl_puntaje = tk.Label(f, text=f"Puntaje: {self.puntaje}",
                                    font=FUENTE_TEXTO, fg=COLOR_TEXTO)
        self.lbl_puntaje.grid(row=0, column=1, sticky="e")
        f.columnconfigure(0, weight=1)
        f.columnconfigure(1, weight=1)

        tk.Label(f, text=f"Pregunta {self.indice + 1} de {NUM_PREGUNTAS}",
                 font=FUENTE_TEXTO, fg=COLOR_TEXTO).grid(row=1, column=0, columnspan=2,
                                                         sticky="w", pady=(10, 0))
        tk.Label(f, text=p["pregunta"], font=FUENTE_PREGUNTA, fg=COLOR_TEXTO,
                 wraplength=580, justify="left").grid(row=2, column=0, columnspan=2,
                                                      sticky="w", pady=10)

        self.radios = []
        for i, opcion in enumerate(p["opciones"]):
            rb = tk.Radiobutton(f, text=opcion, variable=self.seleccion, value=opcion,
                                font=FUENTE_TEXTO, fg=COLOR_TEXTO, anchor="w")
            rb.grid(row=3 + i, column=0, columnspan=2, sticky="w", padx=20, pady=2)
            self.radios.append(rb)

        self.lbl_feedback = tk.Label(f, text="", font=FUENTE_TEXTO)
        self.lbl_feedback.grid(row=7, column=0, columnspan=2, pady=8)

        self.btn_responder = tk.Button(f, text="Responder", font=FUENTE_TEXTO,
                                       width=12, command=self.responder)
        self.btn_responder.grid(row=8, column=0, pady=5)
        self.btn_siguiente = tk.Button(f, text="Siguiente", font=FUENTE_TEXTO,
                                       width=12, state="disabled", command=self.siguiente)
        self.btn_siguiente.grid(row=8, column=1, pady=5)

    def responder(self):
        if self.respondida:
            return
        elegida = self.seleccion.get()
        if not elegida:
            messagebox.showwarning("Sin respuesta", "Selecciona una opción.")
            return

        self.respondida = True
        correcta = self.preguntas[self.indice]["correcta"]
        if elegida == correcta:
            self.puntaje += PUNTOS_ACIERTO
            self.lbl_feedback.config(text="¡Correcto! +10 puntos", fg="#1b7f3b")
        else:
            self.vidas -= 1
            self.lbl_feedback.config(text=f"Incorrecto. La respuesta era: {correcta}",
                                     fg="#b00020")

        self.lbl_vidas.config(text=f"Vidas: {'❤️' * self.vidas}".strip())
        self.lbl_puntaje.config(text=f"Puntaje: {self.puntaje}")
        for rb in self.radios:
            rb.config(state="disabled")
        self.btn_responder.config(state="disabled")
        self.btn_siguiente.config(state="normal")

    def siguiente(self):
        self.indice += 1
        if self.vidas == 0 or self.indice >= NUM_PREGUNTAS:
            self.mostrar_resultados()
        else:
            self.mostrar_juego()

    #  Resultados
    def mostrar_resultados(self):
        f = self.cambiar_vista()
        nombre = self.nombre.get().strip()
        if self.vidas == 0:
            titulo, color = "¡Te quedaste sin vidas!", "#ff0000"
        else:
            titulo, color = "¡Juego terminado!", "#00ff00"

        tk.Label(f, text=titulo, font=("Times New Roman", 22, "bold"),
                 fg=color).pack(pady=(40, 10))
        tk.Label(f, text=f"Jugador: {nombre}", font=FUENTE_TEXTO,
                 fg=COLOR_TEXTO).pack()
        tk.Label(f, text=f"Puntaje final: {self.puntaje} / {NUM_PREGUNTAS * PUNTOS_ACIERTO}",
                 font=("Times New Roman", 18), fg=COLOR_TEXTO).pack(pady=15)
        tk.Button(f, text="Reiniciar", font=FUENTE_TEXTO, width=14,
                  command=self.mostrar_inicio).pack(pady=20)

        messagebox.showinfo("Resultado", f"{nombre}, obtuviste {self.puntaje} puntos.")


if __name__ == "__main__":
    ventana = tk.Tk()
    QuizApp(ventana)
    ventana.mainloop()