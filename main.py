# main.py
import pygame
from src.ui.UserInterface import UserInterface

def main():
    ui = UserInterface()
    ui.run()
    pygame.quit()

if __name__ == "__main__":
    main()