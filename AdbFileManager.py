import logging
import customtkinter

from config import APP_CONFIG
from device_selection import device_selection

logging.getLogger().setLevel(logging.INFO)

customtkinter.set_appearance_mode("System")
customtkinter.set_default_color_theme("blue")

if __name__ == '__main__':
    root = customtkinter.CTk()
    root.title(APP_CONFIG["app_name"])
    root.iconbitmap(APP_CONFIG['icon'])

    device_selection(root)

    root.mainloop()
