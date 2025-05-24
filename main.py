import tkinter as tk
from tkinter import scrolledtext
import subprocess
import os
import sys
import threading

# Ruta base donde están tus scripts
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PYTHON_EXECUTABLE = sys.executable  # Usa el mismo Python que ejecuta la GUI

# Función para ejecutar scripts y mostrar salida en tiempo real
def run_script(script_name):
    def task():
        try:
            script_path = os.path.join(BASE_DIR, script_name)
            process = subprocess.Popen(
                [PYTHON_EXECUTABLE, script_path],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1
            )
            text_area.insert(tk.END, f"\n--- Ejecutando {script_name} ---\n")
            for line in process.stdout:
                text_area.insert(tk.END, line)
                text_area.see(tk.END)
            process.wait()
            text_area.insert(tk.END, f"\n{script_name} terminado\n")
            text_area.see(tk.END)
        except Exception as ex:
            text_area.insert(tk.END, f"\nError ejecutando {script_name}:\n{str(ex)}\n")
            text_area.see(tk.END)

    threading.Thread(target=task).start()

# Función para eliminar archivos CSV generados previamente
def delete_previous_data():
    files_to_delete = [
        'function_table.csv',
        'voltage_ascending_sweep_results.csv',
        'voltage_descending_sweep_results.csv'
    ]
    deleted_any = False
    for filename in files_to_delete:
        file_path = os.path.join(BASE_DIR, filename)
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
                text_area.insert(tk.END, f"Archivo eliminado: {filename}\n")
                deleted_any = True
            except Exception as e:
                text_area.insert(tk.END, f"Error al eliminar {filename}: {str(e)}\n")
    if not deleted_any:
        text_area.insert(tk.END, "No se encontraron archivos para eliminar.\n")
    text_area.see(tk.END)

# Interfaz gráfica
root = tk.Tk()
root.title("Estación de Pruebas - FlipFlop JK 74LS73")

frame = tk.Frame(root)
frame.pack(padx=10, pady=10)

# Botones individuales
btn1 = tk.Button(frame, text="Detectar cambio 0 a 1", command=lambda: run_script('sweep_voltage_detect1.py'))
btn1.grid(row=0, column=0, padx=5, pady=5)

btn2 = tk.Button(frame, text="Detectar cambio 1 a 0", command=lambda: run_script('sweep_voltage_detect0.py'))
btn2.grid(row=0, column=1, padx=5, pady=5)

btn3 = tk.Button(frame, text="Tabla de función", command=lambda: run_script('function_table.py'))
btn3.grid(row=1, column=0, padx=5, pady=5)

btn4 = tk.Button(frame, text="Mostrar resultados", command=lambda: run_script('deploy_tables.py'))
btn4.grid(row=1, column=1, padx=5, pady=5)

# Botón para eliminar datos anteriores
btn_delete = tk.Button(frame, text="Eliminar datos anteriores", command=delete_previous_data, bg='tomato')
btn_delete.grid(row=2, column=0, columnspan=2, pady=10)

# Área de texto para mostrar salida
text_area = scrolledtext.ScrolledText(root, width=100, height=25)
text_area.pack(padx=10, pady=10)

root.mainloop()
