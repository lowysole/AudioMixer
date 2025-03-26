from enum import Enum
import threading


class ErrorType(Enum):
    NONE = 0
    INFO = 1
    WARNING = 2
    ERROR = 3


def get_error_type(error_type):
    match error_type:
        case ErrorType.INFO:
            return "[Info]"
        case ErrorType.WARNING:
            return "[Warning]"
        case ErrorType.ERROR:
            return "[Error]"

    return ""


class Logger:
    def __init__(self, verbose):
        self.logs = []
        self.verbose = verbose

        self.lock = threading.Lock()

    def log(self, message, errorType=ErrorType.NONE):
        log_entry = ""
        if self.verbose:
            log_entry = f"{get_error_type(errorType)} {message}"
        else:
            log_entry = message
        print(log_entry)
        self.logs.append(log_entry)

    def info(self, message):
        self.log(message, ErrorType.INFO)

    def warning(self, message):
        self.log(message, ErrorType.WARNING)

    def error(self, message):
        self.log(message, ErrorType.ERROR)

    def get_all_logs(self):
        with self.lock:
            return "\n".join(self.logs)

    def clear_logs(self):
        with self.lock:
            self.logs = []


logger = Logger(True)
logger_arduino = Logger(False)
