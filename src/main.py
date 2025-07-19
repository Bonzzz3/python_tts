import tkinter as tk
from tkinter import ttk
from controllers.tts_app_controller import TTSAppController

def main():
    root = tk.Tk()
    style = ttk.Style()
    style.configure('Accent.TButton', font=('Arial', 11, 'bold'), foreground='white')
    app = TTSAppController(root)
    root.mainloop()

if __name__ == "__main__":
    main()