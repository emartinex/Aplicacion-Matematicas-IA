"""Prueba de integración de la interfaz, con ventana oculta."""

from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from matematicas_ia.catalog import LESSONS
from matematicas_ia.ui import Application


def main():
    app = Application()
    app.withdraw()
    try:
        app.update_idletasks()
        for lesson in LESSONS:
            app.tree.selection_set(lesson.id)
            app.select_lesson()
            app.load_example()
            app.compute()
            app.update_idletasks()
            assert app.last_report and "APLICACIÓN EN IA" in app.last_report, lesson.id
            assert "Revisa los valores" not in app.result_text.get("1.0", "end"), lesson.id
            assert str(app.export_button.cget("state")) == "normal", lesson.id
            app.clear()
            assert app.last_report is None, lesson.id
            app.compute()
            assert "Revisa los valores" in app.result_text.get("1.0", "end"), lesson.id
        app.tree.selection_set("v_dot")
        app.select_lesson()
        app.load_example()
        app.compute()
        app.inputs["a"].insert(0, "1 ")
        assert app.last_report is None, "Editar debe invalidar el resultado"
        print(f"Interfaz verificada: {len(LESSONS)} operaciones, ejemplos, errores, limpieza y edición.")
    finally:
        app.destroy()


if __name__ == "__main__":
    main()
