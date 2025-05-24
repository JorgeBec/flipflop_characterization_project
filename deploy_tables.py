import pandas as pd
import tkinter as tk
from tkinter import ttk
import os
import matplotlib.pyplot as plt

# CSV files
voltage_ascending_sweep_results = 'voltage_ascending_sweep_results.csv'
voltage_descending_sweep_results = 'voltage_descending_sweep_results.csv'
function_table_file = 'function_table.csv'

# Create main window
root = tk.Tk()
root.title("Test Results Viewer")
root.geometry("800x600")

# Create notebook (tabs)
notebook = ttk.Notebook(root)
notebook.pack(expand=True, fill='both')

# Function to add a table to a tab
def create_table_tab(dataframe, tab_name):
    frame = ttk.Frame(notebook)
    notebook.add(frame, text=tab_name)

    tree = ttk.Treeview(frame, columns=list(dataframe.columns), show='headings')
    tree.pack(expand=True, fill='both')

    # Set up columns
    for col in dataframe.columns:
        tree.heading(col, text=col)
        tree.column(col, anchor='center')

    # Insert rows
    for _, row in dataframe.iterrows():
        tree.insert('', 'end', values=list(row))

# DataFrames
a = b = c = None

# Load and display CSV files if they exist
if os.path.exists(voltage_ascending_sweep_results):
    a = pd.read_csv(voltage_ascending_sweep_results)
    create_table_tab(a, "Ascending Sweep")

if os.path.exists(voltage_descending_sweep_results):
    b = pd.read_csv(voltage_descending_sweep_results)
    create_table_tab(b, "Descending Sweep")

if os.path.exists(function_table_file):
    c = pd.read_csv(function_table_file)
    create_table_tab(c, "Function Table")

# Message if no files were found
if not any([a is not None, b is not None, c is not None]):
    label = tk.Label(root, text="No CSV files found to display.", font=("Arial", 14))
    label.pack(pady=20)

def apply_step_hold(df, q_column):
    """Modifica Q para mantener su valor hasta que detecte un cambio real"""
    q = df[q_column].values
    held_q = [q[0]]
    for i in range(1, len(q)):
        if q[i] != q[i-1]:
            held_q.append(q[i])
        else:
            held_q.append(held_q[-1])
    df[q_column + " (Held)"] = held_q
    return df

# Show plots
def show_plots():
    if a is not None:
        a_mod = apply_step_hold(a.copy(), 'Q Voltage (V)')
        plt.figure()
        plt.step(a_mod['J Voltage (V)'], a_mod['Q Voltage (V) (Held)'], where='post', marker='o')
        plt.title('Ascending Sweep')
        plt.xlabel('J Voltage (V)')
        plt.ylabel('Q Voltage (V)')
        plt.grid(True)

    if b is not None:
        b_mod = apply_step_hold(b.copy(), 'Q Voltage (V)')
        plt.figure()
        plt.step(b_mod['J Voltage (V)'], b_mod['Q Voltage (V) (Held)'], where='post', marker='o', color='red')
        plt.title('Descending Sweep')
        plt.xlabel('J Voltage (V)')
        plt.ylabel('Q Voltage (V)')
        plt.grid(True)

    plt.show()


# Display the plots when the script runs
show_plots()

# Run the window
root.mainloop()
