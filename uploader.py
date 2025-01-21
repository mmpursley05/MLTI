import tkinter as tk
from tkinter import filedialog, messagebox
import pandas as pd

workflow = input("Workflow: ").strip().lower()  # Ensure case insensitivity
df = pd.DataFrame()  # Initialize an empty DataFrame

def upload_csv():
    """Opens a file dialog to select a CSV file and reads it into a Pandas DataFrame."""
    global df  # Use the global keyword to modify the global df variable
    filepath = filedialog.askopenfilename(
        defaultextension=".csv", filetypes=[("CSV Files", "*.csv")]
    )
    if filepath:
        try:
            df = pd.read_csv(filepath)
            messagebox.showinfo("Success", "CSV file loaded successfully!")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to read CSV: {e}")

if workflow == "populator":
    root = tk.Tk()
    root.title("CSV Uploader")
    
    upload_button = tk.Button(root, text="Upload Income Statement", command=upload_csv)
    upload_button.pack(pady=20)
    
    root.mainloop()

elif workflow == "editor":
    print("No GUI needed for editor workflow.")

else:
    print("Invalid workflow. Please choose 'populator' or 'editor'.")