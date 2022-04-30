import itertools
import os.path
from math import floor
from tkinter import *
from tkinter import filedialog

from adb_device import AdbDevice
from config import *
from file import File


def explorer(device_name, root: Tk):
    device = AdbDevice(device_name, APP_CONFIG['default_root'])
    root.title(APP_CONFIG['app_name'])
    root.iconbitmap(APP_CONFIG['icon'])
    root.minsize(*APP_CONFIG['min_size'])
    root.maxsize(*APP_CONFIG['max_size'])
    root.title(f'{device.name} - {APP_CONFIG["app_name"]}')

    head_frame = LabelFrame(root, text='Header', padx=10, pady=10)
    head_frame.pack(fill=X, anchor=N)
    foot_frame = LabelFrame(root, text='Footer', padx=10, pady=10)
    foot_frame.pack(fill=X, anchor=S, side=BOTTOM)

    address_bar_text = StringVar(head_frame, device.current_dir)
    bottom_bar_text = StringVar(head_frame)
    address_bar = Entry(head_frame, textvariable=address_bar_text, borderwidth=3)
    address_bar.pack(fill=X, expand=1, side=LEFT)
    bottom_bar = Label(foot_frame, textvariable=bottom_bar_text, borderwidth=10)
    bottom_bar.grid(row=1, column=0, columnspan=4, sticky=W)

    view_frame = LabelFrame(root, text='Files', padx=10, pady=10)
    view_frame.pack_propagate(False)
    view_frame.pack(fill=BOTH, expand=1)
    view_items = []

    def file_ui_position_generator():
        column_max = floor(root.winfo_width() / (FILE_ITEM_CONFIG['width'] + 10))
        for r in itertools.count(0):
            for c in range(column_max):
                yield r, c

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

        button_enter = Button(inner_frame, text='↗', command=lambda: enter_path_with_obj(file),
                              state=button_enter_state)

        button_download.pack(side=RIGHT)
        button_delete.pack(side=RIGHT)
        button_enter.pack(side=RIGHT)

        return file_frame

    def enter_path():
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

    def upload_folder():
        folder_to_upload = filedialog.askdirectory(initialdir='./', title='Select a folder to upload')
        if not os.path.exists(folder_to_upload):
            raise FileNotFoundError()
        else:
            device.push_file(folder_to_upload)
            print(f'Folder push succeed:{folder_to_upload}')
        enter_path()

    button_enter_path = Button(head_frame, text='→/⚪', command=enter_path)
    button_upload_file = Button(head_frame, text='↑ File(s)', command=upload_files)
    button_upload_folder = Button(head_frame, text='↑ Folder', command=upload_folder)
    button_upload_folder.pack(side=RIGHT)
    button_upload_file.pack(side=RIGHT)
    button_enter_path.pack(side=RIGHT)

    mainloop()
