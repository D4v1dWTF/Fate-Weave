# main.py
from ui import GameApp
import tkinter as tk

if __name__ == "__main__":
    root = tk.Tk()
    app = GameApp(root)
    app.run()