import win32con

from enum import Enum


class ButtonIndex(Enum):
    NAME = 0
    MODE = 1
    PROGRAM = 2
    PROGRAM_PATH = 3


class Mode(Enum):
    PUSH_SINGLE = 0
    # TOGGLE = 1


mode_names = ["On Push"]


class ProgramModes(Enum):
    PROGRAM = 0
    PROGRAM_PATH = 1


program_mode_names = ["Program", "Program (Enter Path)"]


def get_mode_from_name(name):
    if name == mode_names[0]:
        return Mode.PUSH_SINGLE
    elif name == mode_names[1]:
        return Mode.TOGGLE


class Type(Enum):
    NONE = 0
    SOUND = 1
    VK = 2
    PROGRAM = 3


_button_list = [
    {"name": "", "type": Type.NONE, "action": ""},
    {"name": "Program", "type": Type.PROGRAM, "action": ""},
    {"name": "Program (Enter Path)", "type": Type.PROGRAM, "action": ""},
    # Sound Type
    {"name": "Mute Mic", "type": Type.SOUND, "action": "mic"},
    {"name": "Mute Speakers", "type": Type.SOUND, "action": "speakers"},
    # VK Type: Media
    {"name": "Play/Pause", "type": Type.VK, "action": win32con.VK_MEDIA_PLAY_PAUSE},
    {"name": "Next Track", "type": Type.VK, "action": win32con.VK_MEDIA_NEXT_TRACK},
    {"name": "Previous Track", "type": Type.VK, "action": win32con.VK_MEDIA_PREV_TRACK},
]


def get_names_from_button_list():
    return [d.get("name") for d in _button_list]


def get_button_id_from_name(name):
    names = [d.get("name") for d in _button_list]
    for i in range(len(_button_list)):
        if name == names[i]:
            return i


def get_button_type_from_id(id):
    return _button_list[id]["type"]


def get_button_action_from_id(id):
    return _button_list[id]["action"]
