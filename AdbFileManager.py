import logging
from tkinter import *
from tkinter import messagebox

from adb_device import AdbDevice
from config import APP_CONFIG
from ui.explorer import explorer

logging.getLogger().setLevel(logging.INFO)

if __name__ == '__main__':
    root = Tk()
    root.minsize(*APP_CONFIG['device_selection_min_size'])
    root.title(f'Select a device - {APP_CONFIG["app_name"]}')
    root.iconbitmap(APP_CONFIG['icon'])

    device_buttons = {}

    devices_frame = LabelFrame(root, text='Attached adb devices:', padx=3, pady=3)
    devices_frame.pack(side=BOTTOM, fill=BOTH, expand=1, padx=3, pady=3)


    def launch(device_name):
        for k, v in root.children.items():
            v.pack_forget()
            v.grid_forget()
            v.place_forget()
        print(device_name)
        explorer(device_name, root)


    def refresh_devices():
        devices = AdbDevice.get_adb_devices()
        for device in devices:
            if device not in device_buttons.keys():
                print(device)
                button = Button(devices_frame, text=device, command=lambda: launch(device))
                button.pack(fill=X)
                device_buttons[device] = button


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

    mainloop()
