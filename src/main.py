from threading import Thread

import App
from AudioController import AudioController
from BoardController import ArduinoController

def controllers_thread( application, arduino_controller, audio_controller ):
    while application.update():
        arduino_controller.update()
        audio_controller.update()


def main():
    arduino_controller = ArduinoController(9600, "COM3")
    audio_controller = AudioController(arduino_controller)
    application = App.Application(audio_controller)

    arduino_controller.start()
    audio_controller.start()
    application.start()

    # Controllers threads
    thread = Thread(target=controllers_thread,
                    args=(application, arduino_controller, audio_controller))
    thread.daemon = True
    thread.start()


    application.start_main_loop()

    thread.join()

    arduino_controller.close()

    print("Finished!")


if __name__ == "__main__":
    main()
