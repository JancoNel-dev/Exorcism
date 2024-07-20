import os
import subprocess
import tkinter as tk
from tkinter import messagebox, filedialog
import winreg as reg
import ctypes
import sys

def is_admin() -> bool:
    return ctypes.windll.shell32.IsUserAnAdmin() == 1

def run_as_admin():
    script = os.path.abspath(sys.argv[0])
    params = ' '.join([script] + sys.argv[1:])
    try:
        ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, params, None, 1)
    except Exception as e:
        root = tk.Tk()
        root.withdraw()  # Hide the main window
        messagebox.showerror("Error", f"Failed to elevate privileges: {e}")
        root.destroy()
        sys.exit()

if not is_admin():
    root = tk.Tk()
    root.withdraw()  # Hide the main window
    messagebox.showinfo("Info", "This application requires administrative privileges.")
    root.destroy()
    run_as_admin()
    sys.exit()

if is_admin():
    print('Got damn admin')
else:
    print('Sorry will get them next time')

# Define dark Twilight theme colors
BG_COLOR = "#2e3440"
FG_COLOR = "#d8dee9"
BTN_COLOR = "#5e81ac"
ENTRY_COLOR = "#4c566a"

class ExorcismApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Exorcism - Malware Removal Tool")
        self.root.geometry("500x300")
        self.root.configure(bg=BG_COLOR)

        # Load whitelist
        self.whitelist = self.load_whitelist()

        # Create UI elements
        self.create_widgets()

    def load_whitelist(self):
        if os.path.exists("whitelist.txt"):
            with open("whitelist.txt", "r") as file:
                return [line.strip() for line in file.readlines()]
        return []

    def save_whitelist(self):
        try:
            with open("whitelist.txt", "w") as file:
                for item in self.whitelist:
                    file.write(f"{item}\n")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save whitelist: {e}")

    def add_to_whitelist(self):
        file_path = filedialog.askopenfilename(title="Select Executable")
        if file_path:
            normalized_path = os.path.normpath(file_path)
            if normalized_path not in self.whitelist:
                self.whitelist.append(normalized_path)
                self.save_whitelist()
                self.update_whitelist_display()
            else:
                messagebox.showinfo("Info", "File already in whitelist")

    def remove_from_whitelist(self):
        selected_item = self.whitelist_listbox.curselection()
        if selected_item:
            self.whitelist.pop(selected_item[0])
            self.save_whitelist()
            self.update_whitelist_display()
        else:
            messagebox.showinfo("Info", "No item selected")

    def update_whitelist_display(self):
        self.whitelist_listbox.delete(0, tk.END)
        for item in self.whitelist:
            self.whitelist_listbox.insert(tk.END, item)

    def remove_non_whitelisted(self):
        try:
            # Define registry paths
            registry_paths = [
                r"SOFTWARE\Microsoft\Windows\CurrentVersion\Run",
                r"SOFTWARE\Microsoft\Windows\CurrentVersion\RunOnce",
                r"SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\Explorer\Run",
                r"SOFTWARE\Wow6432Node\Microsoft\Windows\CurrentVersion\Run",
                r"SOFTWARE\Wow6432Node\Microsoft\Windows\CurrentVersion\RunOnce",
                r"SOFTWARE\Wow6432Node\Microsoft\Windows\CurrentVersion\Policies\Explorer\Run"
            ]
            # Define startup folder paths
            startup_paths = [
                os.path.join(os.getenv("APPDATA"), r"Microsoft\Windows\Start Menu\Programs\Startup"),
                os.path.join(os.getenv("PROGRAMDATA"), r"Microsoft\Windows\Start Menu\Programs\Startup")
            ]

            # Remove non-whitelisted executables from registry
            for path in registry_paths:
                self.clean_registry(path)

            # Remove non-whitelisted executables from startup folders
            for path in startup_paths:
                self.clean_startup_folder(path)

            # Restart the computer
            subprocess.call(["shutdown", "/r", "/t", "0"])
            
        except Exception as e:
            messagebox.showerror("Exorcism", f"An error occurred: {e}")

    def clean_registry(self, path):
        try:
            with reg.OpenKey(reg.HKEY_LOCAL_MACHINE, path, 0, reg.KEY_READ | reg.KEY_WRITE) as key:
                for i in range(reg.QueryInfoKey(key)[1]):
                    value_name, value_data, _ = reg.EnumValue(key, i)
                    if os.path.normpath(value_data) not in self.whitelist:
                        reg.DeleteValue(key, value_name)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to clean registry path {path}: {e}")

    def clean_startup_folder(self, path):
        try:
            for item in os.listdir(path):
                item_path = os.path.join(path, item)
                if os.path.isfile(item_path) and os.path.normpath(item_path) not in self.whitelist:
                    os.remove(item_path)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to clean startup folder {path}: {e}")

    def create_widgets(self):
        tk.Label(self.root, text="Exorcism", bg=BG_COLOR, fg=FG_COLOR, font=("Helvetica", 16)).pack(pady=10)

        frame = tk.Frame(self.root, bg=BG_COLOR)
        frame.pack(pady=10)

        self.whitelist_listbox = tk.Listbox(frame, bg=ENTRY_COLOR, fg=FG_COLOR, width=50, height=10)
        self.whitelist_listbox.pack(side=tk.LEFT, padx=10)
        self.update_whitelist_display()

        scrollbar = tk.Scrollbar(frame, command=self.whitelist_listbox.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.whitelist_listbox.config(yscrollcommand=scrollbar.set)

        btn_frame = tk.Frame(self.root, bg=BG_COLOR)
        btn_frame.pack(pady=10)

        tk.Button(btn_frame, text="Add to Whitelist", bg=BTN_COLOR, fg=FG_COLOR, command=self.add_to_whitelist).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="Remove from Whitelist", bg=BTN_COLOR, fg=FG_COLOR, command=self.remove_from_whitelist).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="Exorcise", bg=BTN_COLOR, fg=FG_COLOR, command=self.remove_non_whitelisted).pack(side=tk.LEFT, padx=5)

if __name__ == "__main__":
    root = tk.Tk()
    app = ExorcismApp(root)
    root.mainloop()
