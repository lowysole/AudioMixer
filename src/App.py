import tkinter as tk
from tkinter import ttk

import os
import sys

LOCKFILE = "app.lock"

class Application:
    def __init__(self):
        self.finished = False
        self.app = None

    def start(self):
        if not check_lock():
            return
        
        self.app = tk.Tk()
        self.app.title("Audio Mixer")
        self.app.geometry("720x480")
        self.app.protocol("WM_DELETE_WINDOW", self.on_close)

    def update(self):
        if self.finished:
            return False
        
        return True

    def start_main_loop(self):
        self.app.mainloop()

    def on_close(self):
        self.finished = True
        release_lock()
        self.app.destroy()


def check_lock():
    if os.path.exists(LOCKFILE):
        print("The app is already running!")
        return False
    # Create lock file
    with open(LOCKFILE, "w") as f:
        f.write("locked")
    return True

def release_lock():
    if os.path.exists(LOCKFILE):
        os.remove(LOCKFILE)