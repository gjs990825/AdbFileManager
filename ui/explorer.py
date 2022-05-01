import itertools
import os.path
from math import floor
from tkinter import *
from tkinter import filedialog, messagebox, ttk

from adb_device import AdbDevice
from config import *
from file import File


# not works when window size fixed(full screen, max/min size)
# fix scrollbar issue
def scrollbar_util(root: Tk):
    # width x height + x + y
    w, h = [int(i) for i in root.geometry().split('+')[0].split('x')]
    root.geometry(f'{w}x{h - 5}')
    root.update()
    root.geometry(f'{w}x{h}')


def explorer(device, root: Tk):
    adb_device = AdbDevice(device, APP_CONFIG['default_root'])
    root.title(APP_CONFIG['app_name'])
    root.iconbitmap(APP_CONFIG['icon'])
    root.minsize(*APP_CONFIG['min_size'])
    root.maxsize(*APP_CONFIG['max_size'])
    root.title(f'{adb_device.name} - {APP_CONFIG["app_name"]}')
    root.geometry(APP_CONFIG["default_size"])

    header_frame = Frame(root, padx=3, pady=3)
    header_frame.pack(fill=X, anchor=N)
    footer_frame = Frame(root)
    footer_frame.pack(fill=X, anchor=S, side=BOTTOM)

    address_bar_text = StringVar(header_frame, adb_device.current_dir)
    footer_text = StringVar(header_frame)
    address_bar = Entry(header_frame, textvariable=address_bar_text, borderwidth=3)
    address_bar.pack(fill=X, expand=1, side=LEFT)
    footer = Label(footer_frame, textvariable=footer_text, borderwidth=10)
    footer.grid(row=1, column=0, columnspan=4, sticky=W)

    base_view_frame = LabelFrame(root, text='Files', padx=10, pady=10)
    base_view_frame.pack(fill=BOTH, expand=1)
    view_items = []

    # view_frame = LabelFrame(base_view_frame, text='View Frame')
    view_frame = Frame(base_view_frame)
    view_frame.pack(fill=BOTH, expand=1)

    view_canvas = Canvas(view_frame)
    view_canvas.pack(side=LEFT, fill=BOTH, expand=1)

    view_scrollbar = ttk.Scrollbar(view_frame, orient=VERTICAL, command=view_canvas.yview)
    view_scrollbar.pack(side=RIGHT, fill=BOTH)

    view_canvas.configure(yscrollcommand=view_scrollbar.set)
    view_canvas.bind('<Configure>', lambda e: view_canvas.configure(scrollregion=view_canvas.bbox("all")))

    def on_mouse_wheel(event):
        view_canvas.yview_scroll(-1 * int((event.delta / 120)), "units")

    view_canvas.bind_all("<MouseWheel>", on_mouse_wheel)

    # view_scrollable_frame = LabelFrame(view_canvas, text='Scrollable Frame', padx=10, pady=10)
    view_scrollable_frame = Frame(view_canvas)
    view_scrollable_frame.pack(fill=BOTH, expand=1)

    view_canvas.create_window((0, 0), window=view_scrollable_frame, anchor="nw")

    def file_ui_position_generator():
        column_max = floor(view_canvas.winfo_width() / (FILE_ITEM_CONFIG['width']))
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
            enter_path()

    def get_file_ui_element(file: File):
        file_item_frame = LabelFrame(view_scrollable_frame, text=file.get_type(), padx=3, pady=3,
                                     width=FILE_ITEM_CONFIG['width'],
                                     height=FILE_ITEM_CONFIG['height'])
        file_item_frame.pack_propagate(False)

        if len(file.name) > FILE_ITEM_CONFIG['max_display_name_length']:
            f_name = file.name[0:FILE_ITEM_CONFIG['max_display_name_length'] + 1] + '...'
        else:
            f_name = file.name

        file_name = Label(file_item_frame, text=f_name, wraplength=FILE_ITEM_CONFIG['width'] - 10, anchor=NW)
        file_name.pack(fill=X)

        if file.is_file:
            info = file.get_readable_size()
        elif FILE_ITEM_CONFIG['show_directory_item_count']:
            info = f'({adb_device.get_item_count_inside(file)})'
        else:
            info = ''

        file_info = Label(file_item_frame, text=info)
        file_info.pack(side=LEFT)

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

        items = adb_device.enter_folder(address_bar_text.get())

        for item in items:
            label = get_file_ui_element(item)
            r_w = next(file_position_generator)
            label.grid(row=r_w[0], column=r_w[1], sticky=W)
            view_items.append(label)

        total = adb_device.get_children_count()
        dir_count = adb_device.get_directory_count_inside_children()
        file_count = total - dir_count
        size = File.parse_readable_size(adb_device.get_children_size_sum())

        footer_text.set(f'Total {total} item(s), {dir_count} folder(s), {file_count} file(s), {size}')
        scrollbar_util(root)

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
                adb_device.push_file(file)
                print(f'File push succeed:{file}')
        enter_path()

    def upload_folder():
        folder_to_upload = filedialog.askdirectory(initialdir='./', title='Select a folder to upload')
        if not os.path.exists(folder_to_upload):
            raise FileNotFoundError()
        else:
            adb_device.push_file(folder_to_upload)
            print(f'Folder push succeed:{folder_to_upload}')
        enter_path()

    button_enter_path = Button(header_frame, text='→/⚪', command=enter_path)
    button_upload_file = Button(header_frame, text='↑ File(s)', command=upload_files)
    button_upload_folder = Button(header_frame, text='↑ Folder', command=upload_folder)
    button_upload_folder.pack(side=RIGHT)
    button_upload_file.pack(side=RIGHT)
    button_enter_path.pack(side=RIGHT)

    mainloop()
