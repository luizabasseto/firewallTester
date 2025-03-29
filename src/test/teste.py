import tkinter as tk
from tkinter import ttk
from tkinter import messagebox

class HostnameContainerPopup:
    def __init__(self, master, failed_hostname, available_hostnames, callback):
        self.top = tk.Toplevel(master)
        self.top.title("Relate Hostname to Container")

        self.failed_hostname = failed_hostname
        self.available_hostnames = available_hostnames
        self.selected_hostname = tk.StringVar()
        self.result = None  # Variable to store the result
        self.callback = callback  # Callback function to continue processing

        self.create_widgets()

    def create_widgets(self):
        message = f"Failed to relate hostname '{self.failed_hostname}' to a container. Select the correct hostname:"
        tk.Label(self.top, text=message).pack(padx=10, pady=10)

        self.hostname_combobox = ttk.Combobox(self.top, textvariable=self.selected_hostname, values=self.available_hostnames)
        self.hostname_combobox.pack(padx=10, pady=5)

        button_frame = tk.Frame(self.top)
        button_frame.pack(padx=10, pady=10)

        tk.Button(button_frame, text="Save", command=self.save).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="Ignore", command=self.ignore).pack(side=tk.LEFT, padx=5)

    def save(self):
        selected_hostname = self.selected_hostname.get()
        if selected_hostname:
            self.result = selected_hostname  # Store the selected hostname
            self.top.destroy()
            self.callback(self.result)  # Continue processing
        else:
            messagebox.showerror("Error", "Select a hostname.")

    def ignore(self):
        self.result = False  # Indicate that the user ignored the relation
        self.top.destroy()
        self.callback(self.result)  # Continue processing

def process_hostnames(root, failed_hostnames, available_hostnames):
    if not failed_hostnames:
        return  # All hostnames processed

    failed_hostname = failed_hostnames[0]
    remaining_hostnames = failed_hostnames[1:]

    def continue_processing(result):
        if result:
            if result != False:
                print(f"Hostname '{failed_hostname}' related to '{result}'.")
            else:
                print(f"Relation for '{failed_hostname}' ignored.")

        process_hostnames(root, remaining_hostnames, available_hostnames)

    HostnameContainerPopup(root, failed_hostname, available_hostnames, continue_processing)

# Example usage
root = tk.Tk()

failed_hostnames = ["hostname1", "hostname2", "hostname3"]
available_hostnames = ["host1", "host2", "host3", "host4"]

tk.Button(root, text="Process Hostnames", command=lambda: process_hostnames(root, failed_hostnames, available_hostnames)).pack(padx=10, pady=10)

root.mainloop()
