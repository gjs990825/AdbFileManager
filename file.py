import os
from datetime import datetime


def check_is_file(s):
    return s[0] == '-'


class File:
    def __init__(self, path, name, is_file, size, date_time, children=None):
        self.path = path
        self.name = name
        self.is_file = is_file
        self.children = children
        self.size = size
        self.date_time = date_time

    @classmethod
    def from_info(cls, path, info):
        # 1.permission 2.links 3.owner 4.group 5.size ... name
        # -rwxrwx--- 1 u0_a185 media_rw 3426365 2022-04-09 13:52 zhca574.pdf
        info = info.split()
        name = ' '.join(info[7:])
        is_file = check_is_file(info[0])
        size = int(info[4])
        date_time = datetime.strptime(' '.join(info[5:7]), '%Y-%m-%d %H:%M')
        return cls(path, name, is_file, size, date_time)

    def __str__(self):
        return f'[{self.get_type_mark()}] {self.get_full_path()} {self.get_readable_size()}B {self.date_time}'

    @staticmethod
    def parse_readable_size(size_in_byte):
        units = ('B', 'KB', 'MB', 'GB')  # , 'TB', 'PB', 'EB', 'ZB', 'YB')
        for unit in units:
            if size_in_byte < 1024:
                return '%.1f %s' % (size_in_byte, unit)
            else:
                size_in_byte /= 1024
        return 'unknown size'

    def get_readable_size(self):
        if not self.is_file:
            return ''
        return self.parse_readable_size(self.size)

    def get_type_mark(self):
        if self.is_file:
            identifier = 'F'
        else:
            identifier = 'D'
        return identifier

    def get_type(self):
        if self.is_file:
            identifier = 'File'
        else:
            identifier = 'Directory'
        return identifier

    def get_simple_name(self):
        return f'[{self.get_type_mark()}] {self.name}'

    def get_full_path(self):
        return os.path.join(self.path, self.name).replace('\\', '/')

    def update_children(self, children):
        self.children = children

    def get_children(self):
        return self.children
