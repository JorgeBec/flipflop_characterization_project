import tkinter as tk
from tkinter import scrolledtext
import subprocess
import os
import sys
import threading

# Base path where your scripts are located
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PYTHON_EXECUTABLE = sys.executable  # Use the same Python that runs the GUI

# Function to execute scripts and display real-time output
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
            text_area.insert(tk.END, f"\n--- Running {script_name} ---\n")
            for line in process.stdout:
                text_area.insert(tk.END, line)
                text_area.see(tk.END)
            process.wait()
            text_area.insert(tk.END, f"\n{script_name} finished\n")
            text_area.see(tk.END)
        except Exception as ex:
            text_area.insert(tk.END, f"\nError running {script_name}:\n{str(ex)}\n")
            text_area.see(tk.END)

    threading.Thread(target=task).start()

# Function to delete previously generated CSV files
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
                text_area.insert(tk.END, f"Deleted file: {filename}\n")
                deleted_any = True
            except Exception as e:
                text_area.insert(tk.END, f"Error deleting {filename}: {str(e)}\n")
    if not deleted_any:
        text_area.insert(tk.END, "No files found to delete.\n")
    text_area.see(tk.END)

# GUI
root = tk.Tk()
root.title("Test Station - FlipFlop JK 74LS73")

frame = tk.Frame(root)
frame.pack(padx=10, pady=10)

# Buttons corresponding to image boxes
btn1 = tk.Button(frame, text="Detect 0 to 1", command=lambda: run_script('sweep_voltage_detect1.py'))  # Box 1
btn1.grid(row=0, column=0, padx=5, pady=5)

btn2 = tk.Button(frame, text="Detect 1 to 0", command=lambda: run_script('sweep_voltage_detect0.py'))  # Box 2
btn2.grid(row=0, column=1, padx=5, pady=5)

btn3 = tk.Button(frame, text="Function Table", command=lambda: run_script('function_table.py'))  # Box 3
btn3.grid(row=0, column=2, padx=5, pady=5)

btn4 = tk.Button(frame, text="Show Results", command=lambda: run_script('deploy_tables.py'), bg='light green')  # Box 4
btn4.grid(row=0, column=3, padx=5, pady=5)

btn_delete = tk.Button(frame, text="Delete Data", command=delete_previous_data, bg='tomato')  # Box 5
btn_delete.grid(row=1, column=3, padx=5, pady=5)

btn5 = tk.Button(frame, text="tdHL", command=lambda: run_script('osc_tpHL.py'), bg='light blue')
btn5.grid(row=1, column=0, padx=5, pady=5)

btn5 = tk.Button(frame, text="tdLH", command=lambda: run_script('osc_tpLH.py'), bg='light blue')
btn5.grid(row=1, column=1, padx=5, pady=5)


# Text area to display output
text_area = scrolledtext.ScrolledText(root, width=100, height=25)
text_area.pack(padx=10, pady=10)

root.mainloop()
