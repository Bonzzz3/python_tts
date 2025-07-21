import tkinter as tk
from tkinter import ttk
from controllers.main_controller import MainController

def main():
    root = tk.Tk()
    style = ttk.Style()
    style.configure('Accent.TButton', font=('Arial', 11, 'bold'), foreground='white')
    app = MainController(root)
    root.mainloop()

if __name__ == "__main__":
    main()