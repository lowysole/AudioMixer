from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume

MAX_LEVEL = 1024

class AudioController:
    def __init__(self, arduino_controller):
        self.devices = None
        self.interface = None
        self.sessions = [None, None, None, None]

        self.arduino_controller = arduino_controller

        self.volume_threshold = 4.0

        self.volume_main = 0.0
        self.volumes = [None, None, None, None]

    def start(self):
        self.devices = AudioUtilities.GetSpeakers()
        self.interface = self.devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)

        # Volumes
        self.volume_main = self.interface.QueryInterface(IAudioEndpointVolume)
        for i in range(0,4):
            if self.sessions[i]:
                self.volumes[i] = self.sessions[i].SimpleAudioVolume


    def update(self):
        if not self.arduino_controller:
            return

        slicer_main_gain = self.arduino_controller.get_slicer_main_gain()
        if abs(self.volume_main.GetMasterVolumeLevel() - slicer_main_gain) > self.volume_threshold:
            self.volume_main.SetMasterVolumeLevel(slicer_main_gain / MAX_LEVEL * 100, None)

        for i in range(0,4):
            if self.sessions[i]:
                slicer_gain = self.arduino_controller.get_slicer_gain(i)
                if abs(self.volumes[i].GetMasterVolume() - slicer_gain) > self.volume_threshold:
                    self.volumes[i].SetMasterVolume(slicer_gain / MAX_LEVEL * 100, None)


    def update_audio_sessions(self, values):

        sessions = AudioUtilities.GetAllSessions()
        for session in sessions:
            if session.Process and session.Process.name() == values[0]:
                self.sessions[0] = session
            elif session.Process and session.Process.name() == values[1]:
                self.sessions[1] = session
            elif session.Process and session.Process.name() == values[2]:
                self.sessions[2] = session
            elif session.Process and session.Process.name() == values[3]:
                self.sessions[3] = session
