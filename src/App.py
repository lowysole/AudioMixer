import customtkinter as ctk
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
                buttons[preset][button][ButtonData.ButtonIndex.PROGRAM_PATH.value] = (
                    json_buttons[str(button_id)][
                        ButtonData.ButtonIndex.PROGRAM_PATH.value
                    ]
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
                    buttons[preset][button][ButtonData.ButtonIndex.PROGRAM_PATH.value],
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
                ["", ButtonData.mode_names[0], "", ""]
                for _ in range(ButtonController.NUM_BUTTONS)
            ]
            for _ in range(ButtonController.NUM_PRESETS)
        ]

        self.current_preset = 0

        read_settings_file(self.slider_apps, self.button_apps)
        self._update_values()

    def start(self):
        # TODO Uncomment self._check_lock()
        self.app.title("Audio Mixer")
        self.app.geometry("1000x1000")
        self.app.protocol("WM_DELETE_WINDOW", self._on_close)
        self.app.resizable(width=True, height=True)  # Allow resizing

        self.column_widths = {"combobox1": 150, "combobox2": 100, "dynamic": 200}

        # Set theme
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        # Main container
        container = ctk.CTkFrame(self.app)
        container.pack(expand=True, fill="both", padx=15, pady=15)

        ctk.CTkLabel(container, text="Sliders").pack(pady=5)
        self.slider_apps = [ctk.StringVar() for _ in range(4)]
        for i in range(4):
            ctk.CTkEntry(
                container,
                textvariable=self.slider_apps[i],
                font=("Arial", 10),
                width=250,
            ).pack(pady=3)

        ctk.CTkLabel(container, text="Buttons").pack(pady=10)
        self._create_buttons_view(container)
        self._load_preset()

        ctk.CTkButton(container, text="Save", command=self._save_settings).pack(pady=10)

    def update(self):
        if self.finished:
            return False

        self._update_preset()

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

    def _create_buttons_view(self, parent):
        self.frame = ctk.CTkFrame(parent)
        self.frame.pack(pady=5, fill="x")

        self.comboboxes = []
        self.dynamic_widgets = {}

        grid_config = {
            "combobox1": self.column_widths["combobox1"],
            "combobox2": self.column_widths["combobox2"],
            "dynamic": self.column_widths["dynamic"],
        }

        for i in range(4):  # Example with 4 buttons
            row = ctk.CTkFrame(self.frame)
            row.pack(pady=3, fill="x")

            # First combobox
            cb = ctk.CTkComboBox(
                row,
                values=[
                    "Option 1",
                    "Option 2",
                    "Option 3",
                    "Option 4",
                ],  # Replace with actual values
                state="normal",
                font=("Arial", 10),
                width=int(grid_config["combobox1"]),
            )
            cb.pack(side="left", padx=5)
            cb.set("")

            # Second combobox
            cb2 = ctk.CTkComboBox(
                row,
                values=["Mode 1", "Mode 2", "Mode 3"],  # Replace with actual values
                state="normal",
                font=("Arial", 10),
                width=int(grid_config["combobox2"]),
            )
            cb2.set("Mode 1")
            cb2.pack(side="left", padx=5)

            # Dynamic frame
            frame_dynamic = ctk.CTkFrame(row, width=grid_config["dynamic"])
            frame_dynamic.pack(side="left", padx=5, fill="x", expand=True)
            self.dynamic_widgets[i] = frame_dynamic

            self.comboboxes.append((cb, cb2))

        # Preset Navigation Controls
        control_frame = ctk.CTkFrame(parent)
        control_frame.pack(pady=10)

        btn_prev = ctk.CTkButton(control_frame, text="<<", command=self._prev_preset)
        btn_prev.pack(side="left", padx=10)

        self.label_preset = ctk.CTkLabel(
            control_frame, text=f"Preset {self.current_preset + 1}"
        )
        self.label_preset.pack(side="left", padx=10)

        btn_next = ctk.CTkButton(control_frame, text=">>", command=self._next_preset)
        btn_next.pack(side="right", padx=10)

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
            self._update_third_column(i)
        self.label_preset.configure(text=f"Preset {self.current_preset + 1}")

    def _save_preset(self):
        for i in range(ButtonController.NUM_BUTTONS):
            self.button_apps[self.current_preset][i][
                ButtonData.ButtonIndex.NAME.value
            ] = self.comboboxes[i][ButtonData.ButtonIndex.NAME.value].get()
            self.button_apps[self.current_preset][i][
                ButtonData.ButtonIndex.MODE.value
            ] = self.comboboxes[i][ButtonData.ButtonIndex.MODE.value].get()

            self.button_apps[self.current_preset][i][
                ButtonData.ButtonIndex.PROGRAM.value
            ] = ""

            self.button_apps[self.current_preset][i][
                ButtonData.ButtonIndex.PROGRAM.value
            ] = ""

            widget = self.dynamic_widgets[i].winfo_children()
            if widget:
                if isinstance(widget[0], ttk.Combobox):
                    self.button_apps[self.current_preset][i][
                        ButtonData.ButtonIndex.PROGRAM.value
                    ] = widget[0].get()
                elif isinstance(widget[0], ttk.Entry):
                    self.button_apps[self.current_preset][i][
                        ButtonData.ButtonIndex.PROGRAM_PATH.value
                    ] = widget[0].get()

    def _update_third_column(self, index):
        selected_option = self.comboboxes[index][0].get()
        frame_dynamic = self.dynamic_widgets[index]

        for widget in frame_dynamic.winfo_children():
            widget.destroy()

        if (
            selected_option
            == ButtonData.program_mode_names[ButtonData.ProgramModes.PROGRAM.value]
        ):
            combo3 = ttk.Combobox(
                frame_dynamic, values=self.button_controler.get_program_names()
            )
            combo3.pack()
        elif (
            selected_option
            == ButtonData.program_mode_names[ButtonData.ProgramModes.PROGRAM_PATH.value]
        ):
            entry = ttk.Entry(frame_dynamic)
            entry.pack()

        widget = self.dynamic_widgets[index].winfo_children()
        if widget:
            if isinstance(widget[0], ttk.Combobox):
                widget[0].set(
                    self.button_apps[self.current_preset][index][
                        ButtonData.ButtonIndex.PROGRAM.value
                    ]
                )
            elif isinstance(widget[0], ttk.Entry):
                widget[0].delete(0, tk.END)
                widget[0].insert(
                    0,
                    self.button_apps[self.current_preset][index][
                        ButtonData.ButtonIndex.PROGRAM_PATH.value
                    ],
                )

    def _next_preset(self):
        self._save_preset()
        self.current_preset = self.button_controler.increase_preset()
        self._load_preset()

    def _prev_preset(self):
        self._save_preset()
        self.current_preset = self.button_controler.decrease_preset()
        self._load_preset()

    def _update_preset(self):
        new_preset = self.button_controler.get_preset()
        if new_preset != self.current_preset:
            self.current_preset = new_preset
            self._load_preset()

    def _update_values(self):
        self.audio_controller.set_audio_sessions_name(self.slider_apps)
        self.button_controler.update_button_values(self.button_apps)
