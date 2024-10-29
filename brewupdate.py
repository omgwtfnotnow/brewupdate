import subprocess
import tkinter as tk
from tkinter import messagebox, ttk

def list_installed_packages():
    for widget in scrollable_frame.winfo_children():
        widget.destroy()
    
    result = subprocess.run(["brew", "list"], capture_output=True, text=True)
    packages = result.stdout.splitlines()
    
    for idx, package in enumerate(packages):
        row = idx // 4
        col = idx % 4   
        
        button = tk.Button(scrollable_frame, text=package, relief="groove", padx=5, pady=5, command=lambda p=package: display_package_options(p))
        button.grid(row=row, column=col, padx=5, pady=5, sticky="nsew")

    canvas.update_idletasks()
    canvas.config(scrollregion=canvas.bbox("all"))

def display_package_options(package_name):
    for widget in options_frame.winfo_children():
        widget.destroy()

    label = tk.Label(options_frame, text=f"Options for {package_name}", font=("Arial", 12, "bold"))
    label.pack(pady=5)

    def check_for_update():
        status_label = tk.Label(options_frame, text="Checking", font=("Arial", 10))
        status_label.pack(pady=5)

        def update_status(dots):
            if dots > 3:
                dots = 1  
            status_label.config(text="Checking" + "." * dots)
            root.after(500, update_status, dots + 1)

        update_status(1) 


        root.after(1000, lambda: perform_update_check(package_name, status_label))


    def perform_update_check(package_name, status_label):
        result = subprocess.run(["brew", "outdated", package_name], capture_output=True, text=True)
        status_label.destroy()  
        if result.stdout.strip():
            messagebox.showinfo("Update Status", f"{package_name} has an update available.")
        else:
            messagebox.showinfo("Update Status", f"{package_name} is up-to-date.")


    def list_permissions():
        result = subprocess.run(["ls", "-l", f"$(brew --prefix {package_name})"], capture_output=True, text=True, shell=True)
        if result.stdout:
            permissions = result.stdout.strip().splitlines()
           
            open_permissions_window(permissions)
        else:
            messagebox.showinfo("Permissions", f"No permissions found for {package_name}.")

    
    def open_permissions_window(permissions):
        perm_window = tk.Toplevel(root)
        perm_window.title("Permissions for Selected Package")
        perm_window.geometry("400x300")

        
        listbox = tk.Listbox(perm_window, selectmode=tk.MULTIPLE)
        listbox.pack(pady=10, fill=tk.BOTH, expand=True)

        for permission in permissions:
            listbox.insert(tk.END, permission)

        btn_delete_selected = tk.Button(perm_window, text="Delete Selected Permissions", command=lambda: delete_selected_permissions(listbox.get(listbox.curselection())))
        btn_delete_selected.pack(pady=5)

    def delete_selected_permissions(selected_permissions):
        for permission in selected_permissions:
            confirm = messagebox.askyesno("Delete Permission", f"Are you sure you want to delete permission for:\n{permission}?")
            if confirm:
                subprocess.run(["chmod", "u-x", permission])  
                messagebox.showinfo("Delete Permission", f"Permission for {permission} has been deleted.")

    def delete_package():
        confirm = messagebox.askyesno("Delete", f"Are you sure you want to delete {package_name}?")
        if confirm:
            subprocess.run(["brew", "uninstall", package_name])
            list_installed_packages()
            messagebox.showinfo("Delete", f"{package_name} has been deleted.")

    btn_check_update = tk.Button(options_frame, text="Check for Updates", command=check_for_update)
    btn_check_update.pack(fill=tk.X, padx=10, pady=5)

    btn_list_permissions = tk.Button(options_frame, text="Show Permissions Granted", command=list_permissions)
    btn_list_permissions.pack(fill=tk.X, padx=10, pady=5)

    btn_delete = tk.Button(options_frame, text="Delete Package", command=delete_package)
    btn_delete.pack(fill=tk.X, padx=10, pady=5)

def on_mouse_wheel(event):
    canvas.yview_scroll(-1 if event.delta > 0 else 1, "units")

root = tk.Tk()
root.title("Homebrew Package Manager")
root.geometry("600x500")

package_frame = tk.Frame(root, padx=10, pady=10, bd=2, relief="groove")
package_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

canvas = tk.Canvas(package_frame)
scrollbar = ttk.Scrollbar(package_frame, orient="vertical", command=canvas.yview)
scrollable_frame = ttk.Frame(canvas)

scrollable_frame.bind(
    "<Configure>",
    lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
)

canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
canvas.configure(yscrollcommand=scrollbar.set)

canvas.pack(side="left", fill="both", expand=True)
scrollbar.pack(side="right", fill="y")

canvas.bind_all("<MouseWheel>", on_mouse_wheel)  

list_installed_packages()

options_frame = tk.Frame(root)
options_frame.pack(pady=10)

root.mainloop()
