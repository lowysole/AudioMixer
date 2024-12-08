import threading

from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume

mutex = threading.Lock()

MAX_LEVEL = 1024


class AudioController:
    def __init__(self, arduino_controller):
        self.devices = None
        self.interface = None
        self.sessions = [None, None, None, None]
        self.sessions_name = ["", "", "", ""]

        self.arduino_controller = arduino_controller

        self.volume_threshold = 4.0

        self.volume_main = 0.0
        self.volumes = [None, None, None, None]

    def start(self):
        self.devices = AudioUtilities.GetSpeakers()
        self.interface = self.devices.Activate(
            IAudioEndpointVolume._iid_, CLSCTX_ALL, None
        )

        self._update_audio_sessions()
        self._update_audio_volumes()

        self.volume_main = self.interface.QueryInterface(IAudioEndpointVolume)

    def update(self):
        if not self.arduino_controller.is_opened():
            return

        mutex.acquire()

        slicer_main_gain = self.arduino_controller.get_slicer_main_gain()
        if (
            abs(self.volume_main.GetMasterVolumeLevel() - slicer_main_gain)
            > self.volume_threshold
        ):
            self.volume_main.SetMasterVolumeLevel(
                slicer_main_gain / MAX_LEVEL * 100, None
            )

        self._update_audio_sessions()
        self._update_audio_volumes()

        for i in range(0, 4):
            if self.sessions[i]:
                slicer_gain = self.arduino_controller.get_slicer_gain(i)
                if (
                    abs(self.volumes[i].GetMasterVolume() - slicer_gain)
                    > self.volume_threshold
                ):
                    self.volumes[i].SetMasterVolume(slicer_gain / MAX_LEVEL * 100, None)

        mutex.release()

    def _update_audio_sessions(self):
        sessions = AudioUtilities.GetAllSessions()
        for session in sessions:
            for i in range(0, 4):
                if not session.Process:
                    break

                if (
                    self.sessions_name[i] == "Active"
                    and session.Process.name() not in self.sessions_name
                ):
                    if session.State:
                        self.sessions_name[i] = session.Process.name()

                if session.Process.name() == self.sessions_name[i]:
                    self.sessions[i] = session
                    break

    def _update_audio_volumes(self):
        for i in range(0, 4):
            if self.sessions[i]:
                self.volumes[i] = self.sessions[i].SimpleAudioVolume

    def set_audio_sessions_name(self, values):
        mutex.acquire()

        for i in range(0, 4):
            if values[i].get() == "Active":
                self.sessions_name[i] = f"{values[i].get()}"
            elif values[i].get() != "":
                self.sessions_name[i] = f"{values[i].get()}.exe"

        mutex.release()
