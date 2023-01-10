from tkinter import messagebox

import customtkinter
import tkinter

from adb_device import AdbDevice
from config import APP_CONFIG
from file_explorer import file_explorer


def device_selection(root: customtkinter.CTk):
    root.minsize(*APP_CONFIG['device_selection_min_size'])
    root.title(f'Select a device - {APP_CONFIG["app_name"]}')

    device_view_items: list[tkinter.Widget] = []

    devices_frame = customtkinter.CTkFrame(root)
    devices_frame.pack(side=customtkinter.BOTTOM, fill=customtkinter.BOTH, expand=1, padx=3, pady=3)

    def launch(device):
        for k, v in root.children.items():
            v.pack_forget()
            v.grid_forget()
            v.place_forget()
        print(device)
        file_explorer(device, root)

    def refresh_devices():
        for item in device_view_items:
            item.pack_forget()
        device_view_items.clear()

        loading_indicator = customtkinter.CTkLabel(devices_frame, text='Loading devices...')
        loading_indicator.pack()
        devices_frame.update()

        devices = AdbDevice.get_adb_devices()

        loading_indicator.pack_forget()

        for device in devices:
            state = customtkinter.NORMAL if device.is_adb_device else customtkinter.DISABLED
            button = customtkinter.CTkButton(devices_frame, text=device.get_user_friendly_name(),
                                             command=lambda: launch(device),
                                             state=state)
            button.pack(fill=customtkinter.X, padx=3, pady=2)
            device_view_items.append(button)

        if len(devices) == 0:
            info_label = customtkinter.CTkLabel(devices_frame, text='No Device Attached')
            info_label.pack(fill=customtkinter.BOTH, expand=1)
            device_view_items.append(info_label)

    def connect_via_network():
        if len(address_text.get()) > 0:
            AdbDevice.connect_via_network(address_text.get())
            refresh_devices()
        else:
            messagebox.showwarning('Warning', 'Input an address first')

    def disconnect_devices():
        AdbDevice.disconnect()
        refresh_devices()

    top_bar_frame = customtkinter.CTkFrame(root, fg_color='transparent')
    top_bar_frame.pack(side=customtkinter.TOP, fill=customtkinter.X, padx=3, pady=3)

    address_text = tkinter.StringVar(top_bar_frame)
    address_input = customtkinter.CTkEntry(top_bar_frame, textvariable=address_text, width=30)
    button_connect_via_address = customtkinter.CTkButton(top_bar_frame, text='>-<', command=connect_via_network, width=60)
    button_disconnect = customtkinter.CTkButton(top_bar_frame, text='>/<', command=disconnect_devices, width=60)
    button_refresh_device = customtkinter.CTkButton(top_bar_frame, text='Refresh', command=refresh_devices, width=80)

    address_input.pack(side=customtkinter.LEFT, fill=customtkinter.X, expand=1)
    button_refresh_device.pack(side=customtkinter.RIGHT)
    button_disconnect.pack(side=customtkinter.RIGHT)
    button_connect_via_address.pack(side=customtkinter.RIGHT)

    refresh_devices()
