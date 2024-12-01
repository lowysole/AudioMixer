import App
from BoardController import ArduinoController
from threading import Thread

def controllers_thread( application, arduino_controller ):
    while application.update():
        arduino_controller.update()


def main():
    arduino_controller = ArduinoController(9600, "COM3")
    arduino_controller.start()

    application = App.Application()
    application.start()

    # Controllers threads 
    thread = Thread(target=controllers_thread, args=(application, arduino_controller))
    thread.daemon = True
    thread.start()


    application.start_main_loop()

    thread.join()

    arduino_controller.close()

    print("Finished!")


if __name__ == "__main__":
    main()