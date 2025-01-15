import threading
import win32api, win32con

from comtypes import CLSCTX_ALL
from datetime import datetime
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume

mutex = threading.Lock()


class AudioController:
    def __init__(self, arduino_controller):
        self.speaker = None
        self.mic = None

        self._sessions = [None, None, None, None]
        self._sessions_name = ["", "", "", ""]
        self._sessions_size = len(self._sessions)

        self._arduino_controller = arduino_controller

        self._volume_threshold = 0.01
        self._volume_main = None
        self._volumes = [None, None, None, None]

        self._mic_main = None

        self._lastButtonsState = [False, False]
        self._lastPressTime = [0, 0]
        self._pressCount = [0, 0]
        self._timeThreshold = 500

        assert len(self._sessions) == len(self._volumes)

    def start(self):
        self.speaker = AudioUtilities.GetSpeakers()
        speaker_interface = self.speaker.Activate(
            IAudioEndpointVolume._iid_, CLSCTX_ALL, None
        )

        self._update_audio_sessions()
        self._update_audio_volumes()

        self._volume_main = speaker_interface.QueryInterface(IAudioEndpointVolume)

        self.mic = AudioUtilities.GetMicrophone()
        mic_interface = self.mic.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
        self._mic_main = mic_interface.QueryInterface(IAudioEndpointVolume)

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

        self._update_buttons()

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

    def _update_buttons(self):
        if self._volume_main:
            muted = self._arduino_controller.get_button_speaker_mute()
            self._volume_main.SetMute(muted, None)
        if self._mic_main:
            muted = self._arduino_controller.get_button_mic_mute()
            self._mic_main.SetMute(muted, None)

        button_first = self._arduino_controller.get_button_player_control_first()

        if not self._lastButtonsState[0] and button_first:
            currentTime = int(datetime.now().timestamp() * 1000)

            if currentTime - self._lastPressTime[0] <= self._timeThreshold:
                self._pressCount[0] = self._pressCount[0] + 1
            else:
                self._pressCount[0] = 1

            self._lastPressTime[0] = currentTime

        if (
            int(datetime.now().timestamp() * 1000) - self._lastPressTime[0]
            > self._timeThreshold
            and self._pressCount[0] > 0
        ):
            if self._pressCount[0] == 1:
                try:
                    hwcode = win32api.MapVirtualKey(win32con.VK_MEDIA_PLAY_PAUSE, 0)
                    win32api.keybd_event(win32con.VK_MEDIA_PLAY_PAUSE, hwcode)
                except Exception:
                    print("Key not mapped to any know key")

            elif self._pressCount[0] == 2:
                try:
                    hwcode = win32api.MapVirtualKey(win32con.VK_MEDIA_PREV_TRACK, 0)
                    win32api.keybd_event(win32con.VK_MEDIA_PREV_TRACK, hwcode)
                except Exception:
                    print("Key not mapped to any know key")
            self._pressCount[0] = 0

        self._lastButtonsState[0] = button_first

        button_second = self._arduino_controller.get_button_player_control_second()

        if not self._lastButtonsState[1] and button_second:
            currentTime = int(datetime.now().timestamp() * 1000)

            if currentTime - self._lastPressTime[1] <= self._timeThreshold:
                self._pressCount[1] = self._pressCount[1] + 1
            else:
                self._pressCount[1] = 1

            self._lastPressTime[1] = currentTime

        if (
            int(datetime.now().timestamp() * 1000) - self._lastPressTime[1]
            > self._timeThreshold
            and self._pressCount[1] > 0
        ):
            if self._pressCount[1] == 1:
                try:
                    hwcode = win32api.MapVirtualKey(win32con.VK_MEDIA_NEXT_TRACK, 0)
                    win32api.keybd_event(win32con.VK_MEDIA_NEXT_TRACK, hwcode)
                except Exception:
                    print("Key not mapped to any know key")

            elif self._pressCount[1] == 2:
                print("Key not mapped to any know key")
            self._pressCount[1] = 0

        self._lastButtonsState[1] = button_second

    def set_audio_sessions_name(self, values):
        mutex.acquire()

        for i in range(0, self._sessions_size):
            if values[i].get() == "Active":
                self._sessions_name[i] = f"{values[i].get()}"
            elif values[i].get() != "":
                self._sessions_name[i] = f"{values[i].get()}.exe"

        mutex.release()
