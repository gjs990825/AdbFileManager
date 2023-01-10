import itertools
import os.path
import tkinter
from math import floor
import customtkinter
from tkinter import filedialog, messagebox, ttk

from adb_device import AdbDevice
from config import *
from file import File


# not works when window size fixed(full screen, max/min size)
# fix scrollbar issue
def scrollbar_util(root: customtkinter.CTk):
    # width x height + x + y
    w, h = [int(i) for i in root.geometry().split('+')[0].split('x')]
    root.geometry(f'{w}x{h - 5}')
    root.update()
    root.geometry(f'{w}x{h}')


def file_explorer(device, root: customtkinter.CTk):
    adb_device = AdbDevice(device, APP_CONFIG['default_root'])
    root.title(APP_CONFIG['app_name'])
    root.iconbitmap(APP_CONFIG['icon'])
    root.minsize(*APP_CONFIG['min_size'])
    root.maxsize(*APP_CONFIG['max_size'])
    root.title(f'{device.get_user_friendly_name()} - {APP_CONFIG["app_name"]}')
    root.geometry(APP_CONFIG["default_size"])

    header_frame = customtkinter.CTkFrame(root)
    header_frame.pack(fill=customtkinter.X, anchor=customtkinter.N, padx=5, pady=5)
    footer_frame = customtkinter.CTkFrame(root)
    footer_frame.pack(fill=customtkinter.X, anchor=customtkinter.S, side=customtkinter.BOTTOM)

    address_bar_text = tkinter.StringVar(header_frame, adb_device.current_dir)
    footer_text = tkinter.StringVar(header_frame)
    address_bar = customtkinter.CTkEntry(header_frame, textvariable=address_bar_text)
    footer = customtkinter.CTkLabel(footer_frame, textvariable=footer_text)
    footer.grid(row=1, column=0, columnspan=4, sticky=customtkinter.W)

    base_view_frame = customtkinter.CTkFrame(root)
    base_view_frame.pack(fill=customtkinter.BOTH, expand=1)
    view_items = []

    # view_frame = LabelFrame(base_view_frame, text='View Frame')
    view_frame = customtkinter.CTkFrame(base_view_frame)
    view_frame.pack(fill=customtkinter.BOTH, expand=1)

    view_canvas = customtkinter.CTkCanvas(view_frame)
    view_canvas.pack(side=customtkinter.LEFT, fill=customtkinter.BOTH, expand=1)

    view_scrollbar = ttk.Scrollbar(view_frame, orient=customtkinter.VERTICAL, command=view_canvas.yview)
    view_scrollbar.pack(side=customtkinter.RIGHT, fill=customtkinter.BOTH)

    view_canvas.configure(yscrollcommand=view_scrollbar.set)
    view_canvas.bind('<Configure>', lambda e: view_canvas.configure(scrollregion=view_canvas.bbox("all")))

    def on_mouse_wheel(event):
        view_canvas.yview_scroll(-1 * int((event.delta / 120)), "units")

    view_canvas.bind_all("<MouseWheel>", on_mouse_wheel)

    # view_scrollable_frame = LabelFrame(view_canvas, text='Scrollable Frame', padx=10, pady=10)
    view_scrollable_frame = customtkinter.CTkFrame(view_canvas, fg_color='transparent')
    view_scrollable_frame.pack(fill=customtkinter.BOTH, expand=1)

    view_canvas.create_window((0, 0), window=view_scrollable_frame, anchor="nw")

    def file_ui_position_generator():
        view_canvas.update()  # Fix initial size problem
        column_max = floor(view_canvas.winfo_width() / (FILE_ITEM_CONFIG['width']))
        if column_max < 1:  # Safety concern
            column_max = 1
        for r in itertools.count(0):
            for c in range(column_max):
                yield r, c

    def download_file(file: File):
        target = filedialog.askdirectory()
        if os.path.exists(target):
            adb_device.pull_file(file.get_full_path(), target)

    def delete_file(obj: File):
        result = messagebox.askokcancel('Confirm Deleting', f'{obj.name} will be deleted')
        if result:
            adb_device.delete_file(obj)
            enter_with_address_bar_path()

    def get_file_ui_element(file: File):
        file_item_frame = customtkinter.CTkFrame(view_scrollable_frame, width=FILE_ITEM_CONFIG['width'],
                                                 height=FILE_ITEM_CONFIG['height'])
        file_item_frame.pack_propagate(False)

        if len(file.name) > FILE_ITEM_CONFIG['max_display_name_length']:
            f_name = file.name[0:FILE_ITEM_CONFIG['max_display_name_length'] + 1] + '...'
        else:
            f_name = file.name

        file_name = customtkinter.CTkLabel(file_item_frame, text=f_name, wraplength=FILE_ITEM_CONFIG['width'] - 10,
                                           anchor=customtkinter.NW)
        file_name.pack(fill=customtkinter.X, padx=10, pady=10)

        if file.is_file:
            info = file.get_readable_size()
        elif FILE_ITEM_CONFIG['show_directory_item_count']:
            info = f'({adb_device.get_item_count_inside(file)})'
        else:
            info = ''

        file_info = customtkinter.CTkLabel(file_item_frame, text=info)
        file_info.pack(side=customtkinter.LEFT, padx=3)

        button_download = customtkinter.CTkButton(file_item_frame, text='↓', command=lambda: download_file(file), width=60)
        button_delete = customtkinter.CTkButton(file_item_frame, text='X', command=lambda: delete_file(file), width=60)

        button_download.pack(side=customtkinter.RIGHT, padx=3)
        button_delete.pack(side=customtkinter.RIGHT, padx=3)
        if not file.is_file:
            button_enter = customtkinter.CTkButton(file_item_frame, text='↗', command=lambda: enter_path_with_obj(file), width=60)
            button_enter.pack(side=customtkinter.RIGHT, padx=3)

        return file_item_frame

    def refresh_view():
        file_position_generator = file_ui_position_generator()
        for item in view_items:
            item.grid_forget()
        view_items.clear()

        items = sorted(adb_device.children, key=lambda obj: (obj.is_file, obj.name))

        for item in items:
            label = get_file_ui_element(item)
            r_w = next(file_position_generator)
            label.grid(row=r_w[0], column=r_w[1], sticky=customtkinter.W, padx=3, pady=3)
            view_items.append(label)

        total = adb_device.get_children_count()
        dir_count = adb_device.get_directory_count_inside_children()
        file_count = total - dir_count
        size = File.parse_readable_size(adb_device.get_children_size_sum())

        footer_text.set(f'Total {total} item(s), {dir_count} folder(s), {file_count} file(s), {size}')

        back_state = customtkinter.NORMAL if adb_device.history.able_to_go_back() else customtkinter.DISABLED
        forward_state = customtkinter.NORMAL if adb_device.history.able_to_go_forward() else customtkinter.DISABLED

        button_back.configure(state=back_state)
        button_forward.configure(state=forward_state)

        if total == 0:
            label = customtkinter.CTkLabel(view_scrollable_frame, text='Empty Directory')
            label.grid()
            view_items.append(label)

        scrollbar_util(root)

    def enter_with_address_bar_path():
        adb_device.enter_folder(address_bar_text.get())
        refresh_view()

    def enter_path_with_obj(obj: File):
        if not obj.is_file:
            print(obj)
            address_bar_text.set(obj.get_full_path())
            enter_with_address_bar_path()

    def upload_files():
        files_to_upload = filedialog.askopenfilenames(initialdir='./', title='Select file(s) to Upload')
        for file in files_to_upload:
            if not os.path.exists(file):
                raise FileNotFoundError()
            else:
                adb_device.push_file(file)
                print(f'File push succeed:{file}')
        enter_with_address_bar_path()

    def upload_folder():
        folder_to_upload = filedialog.askdirectory(initialdir='./', title='Select a folder to upload')
        if not os.path.exists(folder_to_upload):
            if folder_to_upload != '':
                raise FileNotFoundError()
        else:
            adb_device.push_file(folder_to_upload)
            print(f'Folder push succeed:{folder_to_upload}')
        enter_with_address_bar_path()

    def go_back():
        adb_device.go_back()
        address_bar_text.set(adb_device.current_dir)
        refresh_view()

    def go_forward():
        adb_device.go_forward()
        address_bar_text.set(adb_device.current_dir)
        refresh_view()

    button_enter_path = customtkinter.CTkButton(header_frame, text='GO', command=enter_with_address_bar_path, width=60)
    button_upload_file = customtkinter.CTkButton(header_frame, text='↑ File(s)', command=upload_files, width=60)
    button_upload_folder = customtkinter.CTkButton(header_frame, text='↑ Folder', command=upload_folder, width=60)
    button_upload_folder.pack(side=customtkinter.RIGHT)
    button_upload_file.pack(side=customtkinter.RIGHT)
    button_enter_path.pack(side=customtkinter.RIGHT)

    button_back = customtkinter.CTkButton(header_frame, text='←', command=go_back, state=customtkinter.DISABLED, width=60)
    button_forward = customtkinter.CTkButton(header_frame, text='→', command=go_forward, state=customtkinter.DISABLED, width=60)
    button_back.pack(side=customtkinter.LEFT)
    button_forward.pack(side=customtkinter.LEFT)
    address_bar.pack(fill=customtkinter.X, expand=1, side=customtkinter.LEFT)

    enter_with_address_bar_path()

    tkinter.mainloop()
