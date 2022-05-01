import logging
from tkinter import *

from config import APP_CONFIG
from device_selection import device_selection

logging.getLogger().setLevel(logging.INFO)

if __name__ == '__main__':
    root = Tk()
    root.title(APP_CONFIG["app_name"])
    root.iconbitmap(APP_CONFIG['icon'])

    device_selection(root)

    root.mainloop()
