import pandas as pd

# workflow = input("Workflow: ").strip().lower()  # Ensure case insensitivity
workflow = ""
df = pd.DataFrame()  # Initialize an empty DataFrame

def upload_csv():
    """Opens a file dialog to select a CSV file and reads it into a Pandas DataFrame."""
    global df  # Use the global keyword to modify the global df variable
    df = pd.read_csv("~/Downloads/real_estate.csv")
    if workflow == "populator":
        print("populator?")
    elif workflow == "editor":
        print("No GUI needed for editor workflow.")

    else:
        print("Invalid workflow. Please choose 'populator' or 'editor'.")
