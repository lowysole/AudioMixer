import Controller
import sys


def main():
    controller = Controller.Controller(9600, "COM3")
    controller.start()


    while True:
        controller.update()
        # controller.printPinInfo()
    
    controller.close()

    print("Finished!")


if __name__ == "__main__":
    main()