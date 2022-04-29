import logging
import os.path
from math import floor
from tkinter import *
from tkinter import filedialog

from adb_device import AdbDevice
from file import File

logging.getLogger().setLevel(logging.INFO)

APP_CONFIG = {
    'app_name': 'Adb File Manager',
    'icon': 'resources/images/icon.ico',
    'default_root': '/sdcard/DCIM',
    'max_size': (1920, 900),
    'min_size': (400, 200),
}

FILE_ITEM_CONFIG = {
    'width': 250,
    'height': 70
}

if __name__ == '__main__':

    device = AdbDevice('4TLZXWNBR8Q8CUE6', APP_CONFIG['default_root'])

    root = Tk()
    root.title(APP_CONFIG['app_name'])
    root.iconbitmap(APP_CONFIG['icon'])
    root.minsize(*APP_CONFIG['min_size'])
    root.maxsize(*APP_CONFIG['max_size'])

    address_bar_text = StringVar(root, device.current_dir)
    bottom_bar_text = StringVar(root)
    address_bar = Entry(root, textvariable=address_bar_text, borderwidth=3, width=100)
    address_bar.grid(row=0, column=0, sticky=EW, padx=10, pady=10)
    bottom_bar = Label(root, textvariable=bottom_bar_text, borderwidth=10)
    bottom_bar.grid(row=2, column=0, columnspan=4, sticky=W)

    view_frame = LabelFrame(root, text='Files', padx=10, pady=10, width=700, height=400)
    view_frame.pack_propagate(False)
    view_frame.grid(row=1, column=0, columnspan=4, padx=10, pady=10, sticky=EW)
    view_items = []


    def file_ui_position_generator():
        row_max = floor(root.winfo_height() / (FILE_ITEM_CONFIG['height'] + 10))
        column_max = floor(root.winfo_width() / (FILE_ITEM_CONFIG['width'] + 10))
        for r in range(row_max):
            for c in range(column_max):
                yield r, c


    file_position_generator = file_ui_position_generator()


    def download_file(file: File):
        target = filedialog.askdirectory()
        if os.path.exists(target):
            device.pull_file(file.get_full_path(), target)


    def delete_file(obj: File):
        device.delete_file(obj)
        enter_path()


    def get_file_ui_element(file: File):
        file_frame = LabelFrame(view_frame, text=file.get_type_mark(), padx=3, pady=3, width=FILE_ITEM_CONFIG['width'],
                                height=FILE_ITEM_CONFIG['height'])
        file_frame.pack_propagate(False)

        file_name = Label(file_frame, text=file.name, wraplength=FILE_ITEM_CONFIG['width'] - 100)
        file_size = Label(file_frame, text=str(file.size))
        file_name.pack(side=LEFT)
        file_size.pack(side=LEFT)

        inner_frame = LabelFrame(file_frame, padx=3, pady=3)
        inner_frame.pack(side=RIGHT)

        button_download = Button(inner_frame, text='↓', command=lambda: download_file(file))
        button_delete = Button(inner_frame, text='X', command=lambda: delete_file(file))

        if file.is_file:
            button_enter_state = DISABLED
        else:
            button_enter_state = NORMAL

        button_enter = Button(inner_frame, text='↗', command=lambda: enter_path_with_obj(file), state=button_enter_state)

        button_download.pack(side=RIGHT)
        button_delete.pack(side=RIGHT)
        button_enter.pack(side=RIGHT)

        return file_frame


    def enter_path():
        global file_position_generator

        file_position_generator = file_ui_position_generator()
        for item in view_items:
            item.grid_forget()
        view_items.clear()

        items = device.enter_folder(address_bar_text.get())

        for item in items:
            label = get_file_ui_element(item)
            r_w = next(file_position_generator)
            label.grid(row=r_w[0], column=r_w[1], sticky=W)
            view_items.append(label)

        bottom_bar_text.set(f'Total {len(device.children)} item(s), {device.get_children_size()}B')


    def enter_path_with_obj(obj: File):
        if not obj.is_file:
            print(obj)
            address_bar_text.set(obj.get_full_path())
            enter_path()


    def upload_files():
        files_to_upload = filedialog.askopenfilenames(initialdir='./', title='Select file(s) to Upload')
        for file in files_to_upload:
            if not os.path.exists(file):
                raise FileNotFoundError()
            else:
                device.push_file(file)
                print(f'File push succeed:{file}')
        enter_path()


    button_enter_path = Button(root, text='→/⚪', command=enter_path)
    button_upload_file = Button(root, text='↑ File(s)', command=upload_files)
    button_upload_folder = Button(root, text='↑ Folder')
    button_enter_path.grid(row=0, column=1)
    button_upload_file.grid(row=0, column=2)
    button_upload_folder.grid(row=0, column=3)

    mainloop()
