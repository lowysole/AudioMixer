import tkinter as tk
from tkinter import ttk

import json
import os

LOCKFILE = "app.lock"
SETTINGS = "settings.json"

def read_settings_file(sliders, buttons):
    if not os.path.exists(SETTINGS):
        return

    with open(SETTINGS, 'r', encoding='utf-8') as settings_file:
        json_file = json.load(settings_file)

        sliders[0].set(json_file['sliders']['slider_1'])
        sliders[1].set(json_file['sliders']['slider_2'])
        sliders[2].set(json_file['sliders']['slider_3'])
        sliders[3].set(json_file['sliders']['slider_4'])

        buttons[0].set(json_file['buttons']['button_1'])
        buttons[1].set(json_file['buttons']['button_2'])
        buttons[2].set(json_file['buttons']['button_3'])
        buttons[3].set(json_file['buttons']['button_4'])


def save_settings_file(sliders, buttons):
    with open(SETTINGS, 'w', encoding='utf-8') as settings_file:

        data = { 'sliders' : {'slider_1': sliders[0].get(),
                              'slider_2': sliders[1].get(),
                              'slider_3': sliders[2].get(),
                              'slider_4': sliders[3].get() },
                'buttons' : {'button_1': buttons[0].get(),
                             'button_2': buttons[1].get(),
                             'button_3': buttons[2].get(),
                             'button_4': buttons[3].get() }
        }

        json.dump(data, settings_file )

def check_lock():
    if os.path.exists(LOCKFILE):
        print("The app is already running!")
        return False
    # Create lock file
    with open(LOCKFILE, "w", encoding='utf-8') as f:
        f.write("locked")
    return True

def release_lock():
    if os.path.exists(LOCKFILE):
        os.remove(LOCKFILE)


class Application:
    def __init__(self, audio_controller):
        self.finished = False
        self.app = tk.Tk()

        self.audio_controller = audio_controller

        # App parameters
        self.slider_apps = [tk.StringVar(), tk.StringVar(), tk.StringVar(), tk.StringVar()]
        self.button_apps = [tk.StringVar(), tk.StringVar(), tk.StringVar(), tk.StringVar()]

        read_settings_file(self.slider_apps, self.button_apps)

        self.audio_controller.update_audio_sessions(self.slider_apps)

        # release_lock()

    def start(self):
        if not check_lock():
            return

        self.app.title("Audio Mixer")
        self.app.geometry("380x480")
        self.app.protocol("WM_DELETE_WINDOW", self._on_close)
        self.app.resizable(width=False, height=False)

        ttk.Label(text="Sliders", master=self.app).pack()
        tk.Entry(textvariable=self.slider_apps[0], master=self.app).pack()
        tk.Entry(textvariable=self.slider_apps[1], master=self.app).pack()
        tk.Entry(textvariable=self.slider_apps[2], master=self.app).pack()
        tk.Entry(textvariable=self.slider_apps[3], master=self.app).pack()

        tk.Label(text="Buttons", master=self.app).pack()
        tk.Entry(textvariable=self.button_apps[0], master=self.app).pack()
        tk.Entry(textvariable=self.button_apps[1], master=self.app).pack()
        tk.Entry(textvariable=self.button_apps[2], master=self.app).pack()
        tk.Entry(textvariable=self.button_apps[3], master=self.app).pack()

        ttk.Label(text="", master=self.app).pack()
        ttk.Button(text="Save", command=self._save_settings).pack()


    def update(self):
        if self.finished:
            return False

        return True


    def start_main_loop(self):
        self.app.mainloop()


    def _on_close(self):
        self.finished = True
        release_lock()
        self.app.destroy()


    def _save_settings(self):
        self.audio_controller.update_audio_sessions(self.slider_apps)
        save_settings_file(self.slider_apps, self.button_apps)
