import pandas as pd
import tkinter as tk
from tkinter import ttk
import os

# Archivos CSV
voltage_ascending_sweep_results = 'voltage_ascending_sweep_results.csv'
voltage_descending_sweep_results = 'voltage_descending_sweep_results.csv'
function_table_file = 'function_table.csv'

# Crear ventana principal
root = tk.Tk()
root.title("Sweep Results Viewer")
root.geometry("800x600")

# Crear un notebook (pestañas)
notebook = ttk.Notebook(root)
notebook.pack(expand=True, fill='both')

# Función para agregar una tabla a una pestaña
def create_table_tab(dataframe, tab_name):
    frame = ttk.Frame(notebook)
    notebook.add(frame, text=tab_name)

    tree = ttk.Treeview(frame, columns=list(dataframe.columns), show='headings')
    tree.pack(expand=True, fill='both')

    # Configurar columnas
    for col in dataframe.columns:
        tree.heading(col, text=col)
        tree.column(col, anchor='center')

    # Agregar filas
    for _, row in dataframe.iterrows():
        tree.insert('', 'end', values=list(row))

# Cargar y mostrar los datos si existen
if os.path.exists(voltage_ascending_sweep_results):
    a = pd.read_csv(voltage_ascending_sweep_results)
    create_table_tab(a, "Ascending Sweep")

if os.path.exists(voltage_descending_sweep_results):
    b = pd.read_csv(voltage_descending_sweep_results)
    create_table_tab(b, "Descending Sweep")

if os.path.exists(function_table_file):
    c = pd.read_csv(function_table_file)
    create_table_tab(c, "Function Table")

# Mensaje si no se encontró ningún archivo
if not any([
    os.path.exists(voltage_ascending_sweep_results),
    os.path.exists(voltage_descending_sweep_results),
    os.path.exists(function_table_file)
]):
    label = tk.Label(root, text="⚠️ No se encontraron archivos CSV para mostrar.", font=("Arial", 14))
    label.pack(pady=20)

# Ejecutar ventana
root.mainloop()
