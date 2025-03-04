from threading import Thread

import App
from AudioController import AudioController
from BoardController import ArduinoController
from ButtonController import ButtonController


def controllers_thread(
    application, arduino_controller, audio_controller, button_controller
):
    while application.update():
        arduino_controller.update()
        audio_controller.update()
        button_controller.update()


def main():
    App.release_lock()  ## Uncomment

    if not App.check_lock():
        return

    arduino_controller = ArduinoController(115200)
    audio_controller = AudioController(arduino_controller)
    button_controller = ButtonController(arduino_controller, audio_controller)
    application = App.Application(audio_controller, button_controller)

    application.start()
    arduino_controller.start()
    audio_controller.start()

    # Controllers threads
    thread = Thread(
        target=controllers_thread,
        args=(application, arduino_controller, audio_controller, button_controller),
    )
    thread.daemon = True
    thread.start()

    application.start_main_loop()

    thread.join()

    arduino_controller.close()

    print("Finished!")


if __name__ == "__main__":
    main()
