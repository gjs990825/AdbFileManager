import itertools
import os.path
from math import floor
from tkinter import *
from tkinter import filedialog, messagebox

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
    root.geometry('800x600')

    header_frame = LabelFrame(root, text='Header', padx=10, pady=10)
    header_frame.pack(fill=X, anchor=N)
    footer_frame = LabelFrame(root, text='Footer')
    footer_frame.pack(fill=X, anchor=S, side=BOTTOM)

    address_bar_text = StringVar(header_frame, device.current_dir)
    bottom_bar_text = StringVar(header_frame)
    address_bar = Entry(header_frame, textvariable=address_bar_text, borderwidth=3)
    address_bar.pack(fill=X, expand=1, side=LEFT)
    bottom_bar = Label(footer_frame, textvariable=bottom_bar_text, borderwidth=10)
    bottom_bar.grid(row=1, column=0, columnspan=4, sticky=W)

    base_view_frame = LabelFrame(root, text='Base View Frame', padx=10, pady=10)
    base_view_frame.pack(fill=BOTH, expand=1)
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
        result = messagebox.askokcancel('Confirm Deleting', f'{obj.name} will be deleted')
        if result:
            device.delete_file(obj)
            enter_path()

    def get_file_ui_element(file: File):
        file_item_frame = LabelFrame(base_view_frame, text=file.get_type(), padx=3, pady=3,
                                     width=FILE_ITEM_CONFIG['width'],
                                     height=FILE_ITEM_CONFIG['height'])
        file_item_frame.pack_propagate(False)

        if len(file.name) > FILE_ITEM_CONFIG['max_display_name_length']:
            f_name = file.name[0:FILE_ITEM_CONFIG['max_display_name_length'] + 1] + '...'
        else:
            f_name = file.name

        file_name = Label(file_item_frame, text=f_name, wraplength=FILE_ITEM_CONFIG['width'] - 10, anchor=NW)
        file_name.pack(fill=X)
        file_size = Label(file_item_frame, text=file.get_readable_size())
        file_size.pack(side=LEFT)

        button_download = Button(file_item_frame, text='↓', command=lambda: download_file(file))
        button_delete = Button(file_item_frame, text='X', command=lambda: delete_file(file))

        button_download.pack(side=RIGHT)
        button_delete.pack(side=RIGHT)
        if not file.is_file:
            button_enter = Button(file_item_frame, text='↗', command=lambda: enter_path_with_obj(file))
            button_enter.pack(side=RIGHT)

        return file_item_frame

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

    button_enter_path = Button(header_frame, text='→/⚪', command=enter_path)
    button_upload_file = Button(header_frame, text='↑ File(s)', command=upload_files)
    button_upload_folder = Button(header_frame, text='↑ Folder', command=upload_folder)
    button_upload_folder.pack(side=RIGHT)
    button_upload_file.pack(side=RIGHT)
    button_enter_path.pack(side=RIGHT)

    mainloop()
