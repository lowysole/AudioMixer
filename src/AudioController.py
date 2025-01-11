import threading

from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume

mutex = threading.Lock()


class AudioController:
    def __init__(self, arduino_controller):
        self.devices = None
        self.interface = None

        self._sessions = [None, None, None, None]
        self._sessions_name = ["", "", "", ""]
        self._sessions_size = len(self._sessions)

        self._arduino_controller = arduino_controller

        self._volume_threshold = 0.01
        self._volume_main = 0.0
        self._volumes = [None, None, None, None]

        assert len(self._sessions) == len(self._volumes)

    def start(self):
        self.devices = AudioUtilities.GetSpeakers()
        self.interface = self.devices.Activate(
            IAudioEndpointVolume._iid_, CLSCTX_ALL, None
        )

        self._update_audio_sessions()
        self._update_audio_volumes()

        self._volume_main = self.interface.QueryInterface(IAudioEndpointVolume)

    def update(self):
        if not self._arduino_controller.is_opened():
            return

        mutex.acquire()

        slicer_main_gain = self._arduino_controller.get_slicer_main_gain()
        if (
            abs(self._volume_main.GetMasterVolumeLevelScalar() - slicer_main_gain)
            > self._volume_threshold
        ):
            self._volume_main.SetMasterVolumeLevelScalar(slicer_main_gain, None)

        self._update_audio_sessions()
        self._update_audio_volumes()

        for i in range(0, self._sessions_size):
            if self._sessions[i]:
                slicer_gain = self._arduino_controller.get_slicer_gain(i)
                if (
                    abs(self._volumes[i].GetMasterVolume() - slicer_gain)
                    > self._volume_threshold
                ):
                    self._volumes[i].SetMasterVolume(slicer_gain, None)

        mutex.release()

    def _update_audio_sessions(self):
        sessions = AudioUtilities.GetAllSessions()
        for session in sessions:
            for i in range(0, self._sessions_size):
                if not session.Process:
                    break

                if (
                    self._sessions_name[i] == "Active"
                    and session.Process.name() not in self._sessions_name
                ):
                    if session.State:
                        self._sessions_name[i] = session.Process.name()

                if session.Process.name() == self._sessions_name[i]:
                    self._sessions[i] = session
                    break

    def _update_audio_volumes(self):
        for i in range(0, self._sessions_size):
            if self._sessions[i]:
                self._volumes[i] = self._sessions[i].SimpleAudioVolume

    def set_audio_sessions_name(self, values):
        mutex.acquire()

        for i in range(0, self._sessions_size):
            if values[i].get() == "Active":
                self._sessions_name[i] = f"{values[i].get()}"
            elif values[i].get() != "":
                self._sessions_name[i] = f"{values[i].get()}.exe"

        mutex.release()
