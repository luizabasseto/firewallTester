import json
import tkinter as tk
from tkinter import ttk, filedialog

SETTINGS_FILE = "settings.json"
DEFAULT_SETTINGS = {
    "firewall_directory": "",
    "reset_rules_file": "",
    "firewall_rules_file": "",
    "show_container_id": False,
    "docker_image": "",
    "include_mangle_table": False
}

def load_settings():
    try:
        with open(SETTINGS_FILE, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return DEFAULT_SETTINGS.copy()

def save_settings():
    settings = {
        "firewall_directory": firewall_dir_var.get(),
        "reset_rules_file": reset_rules_var.get(),
        "firewall_rules_file": firewall_rules_var.get(),
        "show_container_id": show_container_id_var.get(),
        "docker_image": docker_image_var.get(),
        "include_mangle_table": include_mangle_var.get()
    }
    with open(SETTINGS_FILE, "w") as f:
        json.dump(settings, f, indent=4)

def restore_default_settings():
    firewall_dir_var.set(DEFAULT_SETTINGS["firewall_directory"])
    reset_rules_var.set(DEFAULT_SETTINGS["reset_rules_file"])
    firewall_rules_var.set(DEFAULT_SETTINGS["firewall_rules_file"])
    show_container_id_var.set(DEFAULT_SETTINGS["show_container_id"])
    docker_image_var.set(DEFAULT_SETTINGS["docker_image"])
    include_mangle_var.set(DEFAULT_SETTINGS["include_mangle_table"])
    save_settings()

def browse_directory():
    directory = filedialog.askdirectory()
    if directory:
        firewall_dir_var.set(directory)

def browse_file(entry_var):
    file_path = filedialog.askopenfilename()
    if file_path:
        entry_var.set(file_path)

# Load existing settings
settings = load_settings()

# Create main window
root = tk.Tk()
root.title("Firewall Configuration")

notebook = ttk.Notebook(root)
settings_tab = ttk.Frame(notebook)
notebook.add(settings_tab, text="Settings")
notebook.pack(expand=True, fill="both")

# Variables
firewall_dir_var = tk.StringVar(value=settings.get("firewall_directory", ""))
reset_rules_var = tk.StringVar(value=settings.get("reset_rules_file", ""))
firewall_rules_var = tk.StringVar(value=settings.get("firewall_rules_file", ""))
show_container_id_var = tk.BooleanVar(value=settings.get("show_container_id", False))
docker_image_var = tk.StringVar(value=settings.get("docker_image", ""))
include_mangle_var = tk.BooleanVar(value=settings.get("include_mangle_table", False))

# UI Elements
ttk.Label(settings_tab, text="Firewall Directory:").grid(row=0, column=0, sticky="w")
ttk.Entry(settings_tab, textvariable=firewall_dir_var, width=40).grid(row=0, column=1)
ttk.Button(settings_tab, text="Browse", command=browse_directory).grid(row=0, column=2)

ttk.Label(settings_tab, text="Reset Rules File:").grid(row=1, column=0, sticky="w")
ttk.Entry(settings_tab, textvariable=reset_rules_var, width=40).grid(row=1, column=1)
ttk.Button(settings_tab, text="Browse", command=lambda: browse_file(reset_rules_var)).grid(row=1, column=2)

ttk.Label(settings_tab, text="Firewall Rules File:").grid(row=2, column=0, sticky="w")
ttk.Entry(settings_tab, textvariable=firewall_rules_var, width=40).grid(row=2, column=1)
ttk.Button(settings_tab, text="Browse", command=lambda: browse_file(firewall_rules_var)).grid(row=2, column=2)

ttk.Checkbutton(settings_tab, text="Show Container ID Column", variable=show_container_id_var).grid(row=3, column=0, columnspan=2, sticky="w")

ttk.Label(settings_tab, text="Docker Image Name:").grid(row=4, column=0, sticky="w")
ttk.Entry(settings_tab, textvariable=docker_image_var, width=40).grid(row=4, column=1)

ttk.Checkbutton(settings_tab, text="Include Mangle Table in Listing", variable=include_mangle_var).grid(row=5, column=0, columnspan=2, sticky="w")

ttk.Button(settings_tab, text="Save Settings", command=save_settings).grid(row=6, column=0, columnspan=3, pady=5)
ttk.Button(settings_tab, text="Restore Defaults", command=restore_default_settings).grid(row=7, column=0, columnspan=3, pady=5)

root.mainloop()

