import tkinter as tk
from tkinter import ttk
import ButtonData
import ButtonController

import json
import os

LOCKFILE = "app.lock"
SETTINGS = "settings.json"


def read_settings_file(sliders, buttons):
    if not os.path.exists(SETTINGS):
        return

    with open(SETTINGS, "r", encoding="utf-8") as settings_file:
        json_file = json.load(settings_file)

        sliders[0].set(json_file["sliders"]["slider_1"])
        sliders[1].set(json_file["sliders"]["slider_2"])
        sliders[2].set(json_file["sliders"]["slider_3"])
        sliders[3].set(json_file["sliders"]["slider_4"])

        json_buttons = json_file["buttons"]

        for preset in range(ButtonController.NUM_PRESETS):
            for button in range(ButtonController.NUM_BUTTONS):
                button_id = preset * (ButtonController.NUM_PRESETS - 1) + button
                buttons[preset][button][ButtonData.ButtonIndex.NAME.value] = (
                    json_buttons[str(button_id)][ButtonData.ButtonIndex.NAME.value]
                )
                buttons[preset][button][ButtonData.ButtonIndex.MODE.value] = (
                    json_buttons[str(button_id)][ButtonData.ButtonIndex.MODE.value]
                )
                buttons[preset][button][ButtonData.ButtonIndex.PROGRAM.value] = (
                    json_buttons[str(button_id)][ButtonData.ButtonIndex.PROGRAM.value]
                )


def save_settings_file(sliders, buttons):
    with open(SETTINGS, "w", encoding="utf-8") as settings_file:
        data = {
            "sliders": {
                "slider_1": sliders[0].get(),
                "slider_2": sliders[1].get(),
                "slider_3": sliders[2].get(),
                "slider_4": sliders[3].get(),
            },
            "buttons": {},
        }

        for preset in range(ButtonController.NUM_PRESETS):
            for button in range(ButtonController.NUM_BUTTONS):
                button_id = preset * (ButtonController.NUM_PRESETS - 1) + button
                data["buttons"][button_id] = [
                    buttons[preset][button][ButtonData.ButtonIndex.NAME.value],
                    buttons[preset][button][ButtonData.ButtonIndex.MODE.value],
                    buttons[preset][button][ButtonData.ButtonIndex.PROGRAM.value],
                ]

        json.dump(data, settings_file)


def check_lock():
    if os.path.exists(LOCKFILE):
        print("The app is already running!")
        return False
    # Create lock file
    with open(LOCKFILE, "w", encoding="utf-8") as f:
        f.write("locked")
    return True


def release_lock():
    if os.path.exists(LOCKFILE):
        os.remove(LOCKFILE)


class Application:
    def __init__(self, audio_controller, button_controller):
        self.finished = False
        self.app = tk.Tk()

        self.audio_controller = audio_controller
        self.button_controler = button_controller

        # App parameters
        self.slider_apps = [
            tk.StringVar(),
            tk.StringVar(),
            tk.StringVar(),
            tk.StringVar(),
        ]

        self.button_apps = [
            [
                [ButtonData.button_list_names[0], ButtonData.mode_names[0], ""]
                for _ in range(ButtonController.NUM_BUTTONS)
            ]
            for _ in range(ButtonController.NUM_PRESETS)
        ]

        self.current_preset = 0

        read_settings_file(self.slider_apps, self.button_apps)
        self._update_values()

    def start(self):
        self.app.title("Audio Mixer")
        self.app.geometry("480x480")
        self.app.protocol("WM_DELETE_WINDOW", self._on_close)
        self.app.resizable(width=False, height=False)

        ttk.Label(text="Sliders", master=self.app).pack()
        tk.Entry(textvariable=self.slider_apps[0], master=self.app).pack()
        tk.Entry(textvariable=self.slider_apps[1], master=self.app).pack()
        tk.Entry(textvariable=self.slider_apps[2], master=self.app).pack()
        tk.Entry(textvariable=self.slider_apps[3], master=self.app).pack()

        tk.Label(text="Buttons", master=self.app).pack()

        self._create_buttons_view()
        self._load_preset()

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
        self._save_preset()
        self._update_values()
        save_settings_file(self.slider_apps, self.button_apps)

    def _create_buttons_view(self):
        self.frame = tk.Frame(self.app)
        self.frame.pack(pady=20)

        self.comboboxes = []
        self.entries = []

        for i in range(ButtonController.NUM_BUTTONS):
            row = []
            cb = ttk.Combobox(
                self.frame, values=ButtonData.button_list_names, state="readonly"
            )
            cb.grid(row=i, column=0, padx=5, pady=5)
            cb.bind(
                "<<ComboboxSelected>>",
                lambda event, index=i: self._check_entries(index),
            )
            row.append(cb)

            cb2 = ttk.Combobox(
                self.frame, values=ButtonData.mode_names, state="readonly"
            )
            cb2.set(ButtonData.mode_names[0])  # Default value
            cb2.grid(row=i, column=1, padx=5, pady=5)
            row.append(cb2)

            entry_var = tk.StringVar()
            entry = tk.Entry(self.frame, textvariable=entry_var, state=tk.DISABLED)
            entry.grid(row=i, column=2, padx=5, pady=5)
            row.append(entry)

            self.comboboxes.append(row)
            self.entries.append(entry_var)

        self.prev_button = tk.Button(self.app, text="<<", command=self._prev_preset)
        self.prev_button.pack(side=tk.LEFT, padx=10)

        self.label_preset = tk.Label(self.app, text=f"Preset {self.current_preset + 1}")
        self.label_preset.pack(side=tk.LEFT)

        self.next_button = tk.Button(self.app, text=">>", command=self._next_preset)
        self.next_button.pack(side=tk.RIGHT, padx=10)

    def _load_preset(self):
        for i in range(ButtonController.NUM_BUTTONS):
            self.comboboxes[i][ButtonData.ButtonIndex.NAME.value].set(
                self.button_apps[self.current_preset][i][
                    ButtonData.ButtonIndex.NAME.value
                ]
            )
            self.comboboxes[i][ButtonData.ButtonIndex.MODE.value].set(
                self.button_apps[self.current_preset][i][
                    ButtonData.ButtonIndex.MODE.value
                ]
            )
            self._check_entries(i)
        self.label_preset.config(text=f"Preset {self.current_preset + 1}")

    def _save_preset(self):
        for i in range(ButtonController.NUM_BUTTONS):
            selected_value = self.comboboxes[i][ButtonData.ButtonIndex.NAME.value].get()
            program_name = ""
            if selected_value == "Program":
                program_name = self.entries[i].get()

            self.button_apps[self.current_preset][i][
                ButtonData.ButtonIndex.NAME.value
            ] = self.comboboxes[i][ButtonData.ButtonIndex.NAME.value].get()
            self.button_apps[self.current_preset][i][
                ButtonData.ButtonIndex.MODE.value
            ] = self.comboboxes[i][ButtonData.ButtonIndex.MODE.value].get()
            self.button_apps[self.current_preset][i][
                ButtonData.ButtonIndex.PROGRAM.value
            ] = program_name

    def _check_entries(self, index):
        if self.comboboxes[index][ButtonData.ButtonIndex.NAME.value].get() == "Program":
            self.comboboxes[index][ButtonData.ButtonIndex.PROGRAM.value].config(
                state=tk.NORMAL
            )
        else:
            self.comboboxes[index][ButtonData.ButtonIndex.PROGRAM.value].config(
                state=tk.DISABLED
            )

        self.entries[index].set(
            self.button_apps[self.current_preset][index][
                ButtonData.ButtonIndex.PROGRAM.value
            ]
        )

    def _next_preset(self):
        self._save_preset()
        self.current_preset = (self.current_preset + 1) % len(self.button_apps)
        self._load_preset()

    def _prev_preset(self):
        self._save_preset()
        self.current_preset = (self.current_preset - 1) % len(self.button_apps)
        self._load_preset()

    def _update_values(self):
        self.audio_controller.set_audio_sessions_name(self.slider_apps)
        self.button_controler.update_button_values(self.button_apps)
