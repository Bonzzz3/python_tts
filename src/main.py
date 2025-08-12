import tkinter as tk
from tkinter import ttk
from controllers.main_controller import MainController

def main():
    root = tk.Tk()
    
    # Set window sizes
    root.minsize(600, 800)
    root.geometry("600x800")
    root.resizable(True, True)
    
    # Configure style
    style = ttk.Style()
    style.configure('Accent.TButton', font=('Arial', 11, 'bold'), foreground='white')
    
    app = MainController(root)
    root.mainloop()

if __name__ == "__main__":
    main()