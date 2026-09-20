"""Interfaz de escritorio Tkinter, íntegramente en español y sin red."""

from pathlib import Path
import tkinter as tk
from tkinter import ttk, filedialog, messagebox

from .catalog import LESSONS, BY_ID
from .core import InputError, calculate, display


BG = "#f2f5f8"
INK = "#172c40"
MUTED = "#50657a"
ACCENT = "#007c78"
NAV = "#122b3e"


class Application(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Álgebra para IA · Laboratorio de aprendizaje")
        width = min(1260, self.winfo_screenwidth() - 80)
        height = min(880, self.winfo_screenheight() - 110)
        self.geometry(f"{max(1000, width)}x{max(740, height)}")
        self.minsize(1000, 740)
        self.configure(bg=BG)
        self.lesson = None
        self.inputs = {}
        self.last_report = None
        self._styles()
        self._layout()
        self.bind("<Control-Return>", lambda event: self.compute())
        self.tree.selection_set("v_dot")
        self.select_lesson()

    def _styles(self):
        style = ttk.Style(self)
        style.theme_use("clam")
        style.configure(".", font=("Segoe UI", 10))
        style.configure("TFrame", background=BG)
        style.configure("Card.TFrame", background="white")
        style.configure("TLabel", background=BG, foreground=INK)
        style.configure("Title.TLabel", font=("Segoe UI", 23, "bold"))
        style.configure("Small.TLabel", foreground=MUTED, font=("Segoe UI", 10))
        style.configure("TButton", padding=(12, 8), font=("Segoe UI", 10))
        style.configure("Primary.TButton", background=ACCENT, foreground="white", font=("Segoe UI", 11, "bold"))
        style.map("Primary.TButton", background=[("active", "#005d59")])
        style.configure("TNotebook", background=BG, borderwidth=0)
        style.configure("TNotebook.Tab", padding=(15, 10), background="#e4ebf0")
        style.map("TNotebook.Tab", background=[("selected", "white")], foreground=[("selected", ACCENT)])
        style.configure("Nav.Treeview", background=NAV, fieldbackground=NAV, foreground="#e1ecf3", borderwidth=0, rowheight=32, font=("Segoe UI", 10))
        style.map("Nav.Treeview", background=[("selected", "#24536a")], foreground=[("selected", "white")])
        style.configure("TEntry", padding=7)

    def _layout(self):
        self.columnconfigure(1, weight=1)
        self.rowconfigure(0, weight=1)
        sidebar = tk.Frame(self, bg=NAV, width=282)
        sidebar.grid(row=0, column=0, sticky="nsew")
        sidebar.grid_propagate(False)
        sidebar.columnconfigure(0, weight=1)
        sidebar.rowconfigure(2, weight=1)
        tk.Label(sidebar, text="ÁLGEBRA / IA", bg=NAV, fg="white", font=("Segoe UI", 21, "bold"), anchor="w").grid(row=0, column=0, sticky="ew", padx=20, pady=(25, 4))
        tk.Label(sidebar, text="LABORATORIO DE APRENDIZAJE", bg=NAV, fg="#8eb8c9", font=("Segoe UI", 8, "bold"), anchor="w").grid(row=1, column=0, sticky="ew", padx=21, pady=(0, 20))
        navigation = tk.Frame(sidebar, bg=NAV)
        navigation.grid(row=2, column=0, sticky="nsew", padx=8)
        navigation.columnconfigure(0, weight=1)
        navigation.rowconfigure(0, weight=1)
        self.tree = ttk.Treeview(navigation, show="tree", selectmode="browse", style="Nav.Treeview", takefocus=True)
        self.tree.grid(row=0, column=0, sticky="nsew")
        nav_scroll = ttk.Scrollbar(navigation, orient="vertical", command=self.tree.yview)
        nav_scroll.grid(row=0, column=1, sticky="ns")
        self.tree.configure(yscrollcommand=nav_scroll.set)
        for index, group in enumerate(dict.fromkeys(lesson.group for lesson in LESSONS), 1):
            self.tree.insert("", "end", iid=group, text=f"{index:02d}   {group.upper()}", open=True, tags=("group",))
            for lesson in LESSONS:
                if lesson.group == group:
                    self.tree.insert(group, "end", iid=lesson.id, text=lesson.title)
        self.tree.tag_configure("group", foreground="#7fcac6", font=("Segoe UI", 9, "bold"))
        self.tree.bind("<<TreeviewSelect>>", self.select_lesson)
        tk.Label(sidebar, text=f"{len(LESSONS)} operaciones · ejemplos incluidos\nPython · cálculo local", justify="left", bg=NAV, fg="#9db7c8", font=("Segoe UI", 9)).grid(row=3, column=0, sticky="w", padx=20, pady=18)
        body = ttk.Frame(self, padding=(26, 22, 26, 12))
        body.grid(row=0, column=1, sticky="nsew")
        body.columnconfigure(0, weight=1)
        body.rowconfigure(3, weight=1)
        self.section = ttk.Label(body, style="Small.TLabel")
        self.section.grid(row=0, column=0, sticky="w")
        self.heading = ttk.Label(body, style="Title.TLabel")
        self.heading.grid(row=1, column=0, sticky="w", pady=(4, 15))
        body.bind("<Configure>", lambda event: self.heading.configure(wraplength=max(350, event.width-52)))
        intro = ttk.Frame(body, style="Card.TFrame", padding=16)
        intro.grid(row=2, column=0, sticky="ew", pady=(0, 18))
        intro.columnconfigure(0, weight=1)
        self.formula = tk.Label(intro, bg="white", fg=ACCENT, font=("Segoe UI", 15, "bold"), anchor="w", justify="left")
        self.formula.grid(row=0, column=0, sticky="ew")
        self.theory = tk.Label(intro, bg="white", fg=INK, justify="left", anchor="w", font=("Segoe UI", 11))
        self.theory.grid(row=1, column=0, sticky="ew", pady=(10, 0))
        intro.bind("<Configure>", lambda event: (self.theory.configure(wraplength=max(350, event.width-34)), self.formula.configure(wraplength=max(350, event.width-34))))
        work = ttk.Frame(body)
        work.grid(row=3, column=0, sticky="nsew")
        work.columnconfigure(0, weight=4, minsize=290)
        work.columnconfigure(1, weight=6, minsize=365)
        work.rowconfigure(1, weight=1)
        ttk.Label(work, text="01  INGRESA LOS VALORES", font=("Segoe UI", 10, "bold")).grid(row=0, column=0, sticky="w", pady=(0, 12))
        ttk.Label(work, text="02  EXPLORA EL RESULTADO", font=("Segoe UI", 10, "bold")).grid(row=0, column=1, sticky="w", padx=(20, 0), pady=(0, 12))
        left = ttk.Frame(work)
        left.grid(row=1, column=0, sticky="nsew")
        left.columnconfigure(0, weight=1)
        left.rowconfigure(1, weight=1)
        tk.Label(left, text="Números separados por espacios.\nMatrices: una fila por línea.\nUsa punto decimal (0.5) o fracciones (1/3).\nMáximo: 8 componentes o matriz de 8 × 8.", bg=BG, fg=MUTED, justify="left", anchor="w", font=("Segoe UI", 9)).grid(row=0, column=0, sticky="ew", pady=(0, 10))
        viewport = ttk.Frame(left)
        viewport.grid(row=1, column=0, sticky="nsew")
        viewport.rowconfigure(0, weight=1)
        viewport.columnconfigure(0, weight=1)
        self.canvas = tk.Canvas(viewport, bg=BG, highlightthickness=0, width=300)
        self.canvas.grid(row=0, column=0, sticky="nsew")
        scrollbar = ttk.Scrollbar(viewport, orient="vertical", command=self.canvas.yview)
        scrollbar.grid(row=0, column=1, sticky="ns")
        self.canvas.configure(yscrollcommand=scrollbar.set)
        self.fields_frame = ttk.Frame(self.canvas)
        self.fields_frame.columnconfigure(0, weight=1)
        self.fields_window = self.canvas.create_window((0, 0), window=self.fields_frame, anchor="nw")
        self.fields_frame.bind("<Configure>", lambda event: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        self.canvas.bind("<Configure>", self._resize_fields)
        actions = ttk.Frame(left)
        actions.grid(row=2, column=0, sticky="ew", pady=(10, 0))
        actions.columnconfigure(0, weight=1)
        ttk.Button(actions, text="Calcular y comprender", style="Primary.TButton", command=self.compute).grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, 8))
        ttk.Button(actions, text="Cargar ejemplo", command=self.load_example).grid(row=1, column=0, sticky="ew")
        ttk.Button(actions, text="Limpiar", command=self.clear).grid(row=1, column=1, sticky="ew", padx=(6, 0))
        self.notebook = ttk.Notebook(work)
        self.notebook.grid(row=1, column=1, sticky="nsew", padx=(20, 0))
        self.result_text = self._text_tab("Resultado")
        self.steps_text = self._text_tab("Paso a paso")
        self.context_text = self._text_tab("Aplicación en IA")
        footer = ttk.Frame(body)
        footer.grid(row=4, column=0, sticky="ew", pady=(14, 0))
        footer.columnconfigure(0, weight=1)
        self.status = ttk.Label(footer, text="Elige una operación para empezar.", style="Small.TLabel", wraplength=520)
        self.status.grid(row=0, column=0, sticky="w")
        self.export_button = ttk.Button(footer, text="Guardar explicación…", command=self.export, state="disabled")
        self.export_button.grid(row=0, column=1, sticky="e", padx=(8, 0))

    def _resize_fields(self, event):
        self.canvas.itemconfigure(self.fields_window, width=event.width)
        for widget in self.fields_frame.winfo_children():
            if isinstance(widget, tk.Label):
                widget.configure(wraplength=max(180, event.width-12))

    def _text_tab(self, title):
        frame = ttk.Frame(self.notebook, style="Card.TFrame")
        frame.rowconfigure(0, weight=1)
        frame.columnconfigure(0, weight=1)
        text = tk.Text(frame, wrap="word", bg="white", fg=INK, relief="flat", padx=20, pady=20, font=("Segoe UI", 11), spacing1=4, spacing3=8, width=34, height=12, state="disabled")
        text.grid(row=0, column=0, sticky="nsew")
        scrollbar = ttk.Scrollbar(frame, command=text.yview)
        scrollbar.grid(row=0, column=1, sticky="ns")
        text.configure(yscrollcommand=scrollbar.set)
        text.tag_configure("title", font=("Segoe UI", 15, "bold"), foreground=ACCENT, spacing3=16)
        text.tag_configure("value", font=("Consolas", 14), background="#edf8f6", spacing1=10, spacing3=15)
        text.tag_configure("heading", font=("Segoe UI", 11, "bold"), spacing1=14)
        text.tag_configure("matrix", font=("Consolas", 10))
        self.notebook.add(frame, text=title)
        return text

    @staticmethod
    def _write(widget, sections):
        widget.configure(state="normal")
        widget.delete("1.0", "end")
        for content, tag in sections:
            widget.insert("end", content + "\n", tag)
        widget.configure(state="disabled")
        widget.yview_moveto(0)

    def select_lesson(self, event=None):
        selected = self.tree.selection()
        if not selected or selected[0] not in BY_ID:
            return
        lesson = BY_ID[selected[0]]
        if self.lesson == lesson:
            return
        self.lesson = lesson
        self.tree.see(lesson.id)
        self.section.configure(text=f"{lesson.group.upper()}   /   COMPRENDE → CALCULA → APLICA")
        self.heading.configure(text=lesson.title)
        self.formula.configure(text=lesson.formula)
        self.theory.configure(text=lesson.theory)
        for child in self.fields_frame.winfo_children():
            child.destroy()
        self.inputs = {}
        for i, field in enumerate(lesson.fields):
            label = tk.Label(self.fields_frame, text=field.label, bg=BG, fg=INK, font=("Segoe UI", 11, "bold"), anchor="w")
            label.grid(row=i*3, column=0, sticky="ew", pady=(6, 3))
            description = tk.Label(self.fields_frame, text=field.description, bg=BG, fg=MUTED, justify="left", anchor="w", font=("Segoe UI", 9), wraplength=290)
            description.grid(row=i*3+1, column=0, sticky="ew", pady=(0, 6))
            if field.kind == "matrix":
                widget = tk.Text(self.fields_frame, height=4, width=20, wrap="none", font=("Consolas", 12), relief="solid", borderwidth=1, padx=9, pady=7, undo=True)
                widget.bind("<Tab>", self._next_field)
                widget.bind("<Shift-Tab>", self._previous_field)
                widget.bind("<KeyRelease>", self._edited)
            else:
                variable = tk.StringVar()
                variable.trace_add("write", self._edited)
                widget = ttk.Entry(self.fields_frame, textvariable=variable, font=("Consolas", 12))
                widget.variable = variable
            widget.grid(row=i*3+2, column=0, sticky="ew", pady=(0, 10), padx=(0, 5))
            self.inputs[field.key] = widget
        self.canvas.yview_moveto(0)
        self._reset_output()
        self.notebook.select(0)
        self.status.configure(text="Lee la definición, escribe tus datos o carga el ejemplo.")

    @staticmethod
    def _next_field(event):
        event.widget.tk_focusNext().focus_set()
        return "break"

    @staticmethod
    def _previous_field(event):
        event.widget.tk_focusPrev().focus_set()
        return "break"

    def _edited(self, *args):
        if self.last_report is not None:
            self._reset_output()
            self.status.configure(text="Los datos cambiaron. Calcula de nuevo para actualizar la explicación.")

    def _reset_output(self):
        self.last_report = None
        self.export_button.configure(state="disabled")
        self._write(self.result_text, [("Tu próximo descubrimiento", "title"), ("Introduce los valores y pulsa «Calcular y comprender». Aquí verás el resultado y cómo interpretarlo.", ""), ("Atajo: Ctrl + Enter para calcular.", ""), ("Los cálculos racionales se muestran como fracciones exactas. Las raíces no racionales y los pares de autovalor/autovector numéricos se indican como aproximados.", "")])
        self._write(self.steps_text, [("Sigue el procedimiento", "title"), ("Después de calcular aparecerán las operaciones, componente por componente, o los pasos de Gauss–Jordan.", "")])
        self._write(self.context_text, [("¿Dónde se utiliza?", "title"), (self.lesson.scenario, ""), ("Para reflexionar", "heading"), (self.lesson.question, ""), ("Origen del contenido", "heading"), (self.lesson.source, "")])

    def _set_input(self, widget, value):
        if isinstance(widget, tk.Text):
            widget.delete("1.0", "end")
            widget.insert("1.0", value)
        else:
            widget.delete(0, "end")
            widget.insert(0, value)

    def load_example(self):
        self._reset_output()
        for field in self.lesson.fields:
            self._set_input(self.inputs[field.key], field.example)
        self.status.configure(text="Ejemplo cargado. Puedes modificarlo antes de calcular.")

    def clear(self):
        self._reset_output()
        for widget in self.inputs.values():
            self._set_input(widget, "")
        self.status.configure(text="Campos vacíos. Introduce nuevos valores.")
        next(iter(self.inputs.values())).focus_set()

    def compute(self):
        data = {key: widget.get("1.0", "end-1c") if isinstance(widget, tk.Text) else widget.get() for key, widget in self.inputs.items()}
        try:
            result = calculate(self.lesson.id, data)
        except InputError as error:
            self._reset_output()
            self._write(self.result_text, [("Revisa los valores", "title"), (str(error), ""), ("Corrige los campos y vuelve a calcular.", "")])
            self.notebook.select(0)
            self.status.configure(text="No se realizó el cálculo: revisa el mensaje del resultado.")
            return
        self._write(self.result_text, [(result.summary, "title"), (display(result.value), "value"), ("Cómo leer el resultado", "heading"), (result.interpretation, ""), ("Continúa aprendiendo", "heading"), ("Abre «Paso a paso» para revisar el procedimiento y «Aplicación en IA» para conectar la operación con un caso real.", "")])
        sections = [("El procedimiento", "title")]
        for i, step in enumerate(result.steps, 1):
            lines = step.split("\n", 1)
            sections.append((f"{i}. {lines[0]}", ""))
            if len(lines) == 2:
                sections.append((lines[1], "matrix"))
        self._write(self.steps_text, sections)
        self._write(self.context_text, [("De la ecuación a la IA", "title"), (self.lesson.scenario, ""), ("Con tus resultados", "heading"), (result.interpretation, ""), ("Para reflexionar", "heading"), (self.lesson.question, ""), ("Origen del contenido", "heading"), (self.lesson.source, "")])
        report = ["ÁLGEBRA PARA IA", self.lesson.title, self.lesson.formula, "\nDEFINICIÓN", self.lesson.theory, "\nVALORES"]
        for field in self.lesson.fields:
            report.append(f"{field.label}:\n{data[field.key]}")
        report.extend(["\nRESULTADO", result.summary, display(result.value), "\nPASO A PASO"])
        report.extend(f"{i}. {step}" for i, step in enumerate(result.steps, 1))
        report.extend(["\nINTERPRETACIÓN", result.interpretation, "\nAPLICACIÓN EN IA", self.lesson.scenario, "\nPARA REFLEXIONAR", self.lesson.question, "\nBASE", self.lesson.source])
        self.last_report = "\n".join(report) + "\n"
        self.export_button.configure(state="normal")
        self.notebook.select(0)
        self.status.configure(text="Cálculo listo. Explora los pasos y su aplicación en IA.")

    def export(self):
        if not self.last_report:
            return
        path = filedialog.asksaveasfilename(parent=self, title="Guardar explicación", defaultextension=".txt", initialfile=f"{self.lesson.id}.txt", filetypes=[("Texto UTF-8", "*.txt")])
        if path:
            try:
                Path(path).write_text(self.last_report, encoding="utf-8")
            except OSError as error:
                messagebox.showerror("No se pudo guardar", str(error), parent=self)
                return
            self.status.configure(text=f"Explicación guardada en {Path(path).name}.")


def main():
    Application().mainloop()
