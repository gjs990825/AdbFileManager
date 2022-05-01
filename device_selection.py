from tkinter import *
from tkinter import messagebox

from adb_device import AdbDevice
from config import APP_CONFIG
from file_explorer import file_explorer


def device_selection(root: Tk):
    root.minsize(*APP_CONFIG['device_selection_min_size'])
    root.title(f'Select a device - {APP_CONFIG["app_name"]}')

    device_view_items: list[Widget] = []

    devices_frame = LabelFrame(root, text='Attached adb devices:', padx=3, pady=3)
    devices_frame.pack(side=BOTTOM, fill=BOTH, expand=1, padx=3, pady=3)

    def launch(device):
        for k, v in root.children.items():
            v.pack_forget()
            v.grid_forget()
            v.place_forget()
        print(device)
        file_explorer(device, root)

    def refresh_devices():
        devices = AdbDevice.get_adb_devices()

        for item in device_view_items:
            item.pack_forget()
        device_view_items.clear()

        for device in devices:
            state = NORMAL if device.is_adb_device else DISABLED
            button = Button(devices_frame, text=f'{device.name} ({device.type})', command=lambda: launch(device),
                            state=state)
            button.pack(fill=X)
            device_view_items.append(button)

        if len(devices) == 0:
            info_label = Label(devices_frame, text='No Device Attached')
            info_label.pack(fill=BOTH, expand=1)
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

    address_text = StringVar(root)
    address_input = Entry(root, textvariable=address_text, borderwidth=3, width=30)
    button_connect_via_address = Button(root, text='>-<',
                                        command=connect_via_network)
    button_disconnect = Button(root, text='>/<', command=disconnect_devices)
    button_refresh_device = Button(root, text='Refresh', command=refresh_devices)

    address_input.pack(side=LEFT, fill=X, expand=1)
    button_refresh_device.pack(side=RIGHT)
    button_disconnect.pack(side=RIGHT)
    button_connect_via_address.pack(side=RIGHT)

    refresh_devices()