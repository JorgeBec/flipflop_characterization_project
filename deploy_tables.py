import pandas as pd
import tkinter as tk
from tkinter import ttk

# Archivos CSV
voltage_ascending_sweep_results = 'voltage_ascending_sweep_results_3.csv'
voltage_descending_sweep_results = 'voltage_descending_sweep_results_3.csv'
function_table_file = 'function_table.csv'

# Cargar los datos
a = pd.read_csv(voltage_ascending_sweep_results)
b = pd.read_csv(voltage_descending_sweep_results)
c = pd.read_csv(function_table_file)

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

# Crear las pestañas
create_table_tab(a, "Ascending Sweep")
create_table_tab(b, "Descending Sweep")
create_table_tab(c, "Function Table")

# Ejecutar ventana
root.mainloop()
