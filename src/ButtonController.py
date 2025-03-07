from datetime import datetime
import subprocess

import win32api

import ButtonData
import Utils


NUM_BUTTONS = 4
NUM_PRESETS = 5


class ButtonController:
    def __init__(self, arduino_controller, audio_controller):
        self._arduino_controller = arduino_controller
        self._audio_controller = audio_controller
        self._current_preset = 0

        self.buttons = [
            [[-1, ButtonData.Mode.PUSH_SINGLE, ""] for _ in range(NUM_BUTTONS)]
            for _ in range(NUM_PRESETS)
        ]

        self.programs = Utils.get_full_list_installed_apps()

        self._lastButtonsState = [0, 0, 0, 0]
        self._lastPressTime = [0, 0, 0, 0]
        self._pressCount = [0, 0, 0, 0]
        self._timeThreshold = 500

        # TODO: Init lastButtonState

    def update(self):
        if not self._arduino_controller.is_opened():
            return

        for i in range(NUM_BUTTONS):
            button_value = self._arduino_controller.get_button_value(i)

            if not self._lastButtonsState[i] and button_value:
                currentTime = int(datetime.now().timestamp() * 1000)

                if currentTime - self._lastPressTime[i] <= self._timeThreshold:
                    self._pressCount[i] = self._pressCount[i] + 1
                else:
                    self._pressCount[i] = 1

                self._lastPressTime[i] = currentTime

            if (
                int(datetime.now().timestamp() * 1000) - self._lastPressTime[i]
                > self._timeThreshold
                and self._pressCount[i] > 0
            ):
                if self._pressCount[i] == 1:
                    self._apply_button(i)

                elif self._pressCount[i] == 2:
                    self._update_preset(i)

                self._pressCount[i] = 0

            self._lastButtonsState[i] = button_value

    def update_button_values(self, button_apps):
        for preset in range(NUM_PRESETS):
            for button in range(NUM_BUTTONS):
                button_name = button_apps[preset][button][
                    ButtonData.ButtonIndex.NAME.value
                ]

                self.buttons[preset][button][ButtonData.ButtonIndex.NAME.value] = (
                    ButtonData.get_button_id_from_name(button_name)
                )

                self.buttons[preset][button][ButtonData.ButtonIndex.MODE.value] = (
                    ButtonData.get_mode_from_name(
                        button_apps[preset][button][ButtonData.ButtonIndex.MODE.value]
                    )
                )

                program_name = ""
                if (
                    button_name
                    == ButtonData.program_mode_names[
                        ButtonData.ProgramModes.PROGRAM.value
                    ]
                ):
                    program_name = self.programs[
                        button_apps[preset][button][
                            ButtonData.ButtonIndex.PROGRAM.value
                        ]
                    ]

                elif (
                    button_name
                    == ButtonData.program_mode_names[
                        ButtonData.ProgramModes.PROGRAM_PATH.value
                    ]
                ):
                    program_name = button_apps[preset][button][
                        ButtonData.ButtonIndex.PROGRAM_PATH.value
                    ]

                self.buttons[preset][button][ButtonData.ButtonIndex.PROGRAM.value] = (
                    program_name
                )

    def get_program_names(self):
        return list(self.programs.keys())

    def _apply_button(self, i):
        button_id = self.buttons[self._current_preset][i][0]

        match ButtonData.get_button_type_from_id(button_id):
            case ButtonData.Type.SOUND:
                self._apply_sound_button(
                    ButtonData.get_button_action_from_id(button_id)
                )

            case ButtonData.Type.VK:
                self._apply_vk_button(ButtonData.get_button_action_from_id(button_id))

            case ButtonData.Type.PROGRAM:
                self._apply_open_program(i)

            case _:
                return

    def _apply_sound_button(self, action):
        if action == "mic":
            self._audio_controller.update_mic_mute_status()
        elif action == "speakers":
            self._audio_controller.update_speaker_mute_status()

    def _apply_vk_button(self, action):
        try:
            hwcode = win32api.MapVirtualKey(action, 0)
            win32api.keybd_event(action, hwcode)
        except Exception:
            print("Key not mapped to any know key")

    def _apply_open_program(self, id):
        program_name = self.buttons[self._current_preset][id][2]

        try:
            result = subprocess.run(
                ["where", program_name], capture_output=True, text=True, check=True
            )
        except Exception as e:
            print(f"Error finding path for program {program_name}: {e}")
            return

        path = result.stdout.strip().split("\n")[0]  # Get the first found path
        if not path:
            print("Path for {program_name} not found")

        try:
            subprocess.Popen(path, shell=True)
        except Exception as e:
            print(f"Error opening {program_name}: {e}")

    def _update_preset(self, i):
        if i == 3:
            self._increase_preset()
        elif i == 0:
            self._decrease_preset()
        else:
            return False

        self._reset_press_counts()
        # self._arduino_controller.send_board_button_mode(
        #    self._lastButtonsState[self._current_preset]
        # )
        return True

    def _increase_preset(self):
        self._current_preset = (self._current_preset + 1) % NUM_PRESETS
        print(f"Current Preset: {self._current_preset}")

    def _decrease_preset(self):
        self._current_preset = (self._current_preset - 1) % (NUM_PRESETS + 1)
        print(f"Current Preset: {self._current_preset}")

    def _reset_press_counts(self):
        self._lastButtonsState = [0, 0, 0, 0]
        self._lastPressTime = [0, 0, 0, 0]
        self._pressCount = [0, 0, 0, 0]
