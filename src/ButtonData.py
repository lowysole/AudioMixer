import win32con

from enum import Enum


class ButtonIndex(Enum):
    NAME = 0
    MODE = 1
    PROGRAM = 2
    PROGRAM_PATH = 3


class Mode(Enum):
    PUSH_SINGLE = 0
    TOGGLE = 1


mode_names = ["On Push", "Toggle"]


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
    {"type": Type.NONE, "action": ""},
    {"type": Type.PROGRAM, "action": ""},
    {"type": Type.PROGRAM, "action": ""},
    # Sound Type
    {"type": Type.SOUND, "action": "mic"},
    {"type": Type.SOUND, "action": "speakers"},
    # VK Type: Media
    {"type": Type.VK, "action": win32con.VK_MEDIA_PLAY_PAUSE},
    {"type": Type.VK, "action": win32con.VK_MEDIA_NEXT_TRACK},
    {"type": Type.VK, "action": win32con.VK_MEDIA_PREV_TRACK},
]

# TODO Merge both lists
button_list_names = [
    "",
    "Program",
    "Program (Enter Path)",
    # Sound Type
    "Mute Mic",
    "Mute Speakers",
    # VK Type: Media
    "Play/Pause",
    "Next Track",
    "Previous Track",
]


def get_button_id_from_name(name):
    for i in range(len(_button_list)):
        if name == button_list_names[i]:
            return i


def get_button_type_from_id(id):
    return _button_list[id]["type"]


def get_button_action_from_id(id):
    return _button_list[id]["action"]
