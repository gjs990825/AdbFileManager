import logging
import subprocess
from dataclasses import dataclass, field

from file import File


def wrap_with_single_quotes(path):
    return f'\'{path}\''


def wrap_with_double_quotes(path):
    return f'"{path}"'


def command_run(command_list):
    logging.info(f'Command to run: {" ".join(command_list)}')
    return subprocess.run(command_list, capture_output=True)


def convert_command_output(out, trim_start=0, trim_end=0):
    lines_bytes = out.split(bytes('\r\n', encoding='utf-8'))
    if trim_end > 0:
        lines_bytes = lines_bytes[trim_start:-trim_end]
    else:
        lines_bytes = lines_bytes[trim_start:]

    return [x.decode('utf-8') for x in lines_bytes]


# TODO Go back to last directory(history)
class AdbDevice:
    @dataclass(frozen=True)
    class Device:
        name: str
        type: str
        is_adb_device: bool = field(init=False, repr=False)

        def __post_init__(self):
            object.__setattr__(self, 'is_adb_device', self.type == 'device')

        def __str__(self):
            return f'({self.name}, {self.type}, {self.is_adb_device})'

    def __init__(self, device, root_dir='/sdcard/'):
        self.name = device.name
        self.root_dir = root_dir
        self.current_dir = root_dir
        self.children: list[File] = []
        self.enter_folder(root_dir)

    def compose_cmd(self, *args):
        return ['adb', '-s', self.name, *args]

    def enter_folder(self, path):
        path = path.replace('\\', '/')
        cmd = self.compose_cmd('shell', 'ls', '-al', wrap_with_single_quotes(path))

        result = command_run(cmd)
        if result.returncode != 0:
            raise FileNotFoundError

        lines = convert_command_output(result.stdout, trim_start=1, trim_end=1)

        self.current_dir = path
        self.children = [File.from_info(path, line) for line in lines]

        return self.children

    def enter_sub_folder(self, name):
        for child in self.children:
            if not child.is_file and child.name == name:
                return self.enter_folder(child.get_full_path())
        raise FileNotFoundError(f'no folder named "{name}"')

    @staticmethod
    def get_adb_devices():
        cmd = ['adb', 'devices']
        result = command_run(cmd)
        if result.returncode != 0:
            raise Exception('adb command execution error')
        devices_str = convert_command_output(result.stdout, trim_start=1, trim_end=2)
        return (AdbDevice.Device(*d.split(sep='\t')) for d in devices_str)

    @staticmethod
    def connect_via_network(address):
        cmd = ['adb', 'connect', address]
        result = command_run(cmd)
        if result.returncode != 0:
            raise Exception('adb connection via network failed')

    @staticmethod
    def disconnect():
        cmd = ['adb', 'disconnect']
        result = command_run(cmd)
        if result.returncode != 0:
            raise Exception('adb disconnect operation failed')

    def get_directory_count_inside_children(self):
        return sum(0 if child.is_file else 1 for child in self.children)

    def get_children_count(self):
        return len(self.children)

    def get_children_size_sum(self):
        return sum(child.size if child.is_file else 0 for child in self.children)

    def get_item_count_inside(self, file: File):
        if not file.is_file:
            return len(AdbDevice(self.name, file.get_full_path()).children)
        return -1

    def pull_file(self, from_dir, to_dir):
        cmd = self.compose_cmd('pull', from_dir, to_dir)
        if command_run(cmd).returncode != 0:
            raise RuntimeError("pull file(s) failed")
        logging.info('file pulling succeed')

    def push_file(self, from_dir, to_dir=None):
        if to_dir is None:
            to_dir = self.current_dir
        cmd = self.compose_cmd('push', from_dir, to_dir)
        if command_run(cmd).returncode != 0:
            raise RuntimeError("push file(s) failed")
        logging.info('file pushing succeed')

    def delete_file(self, obj):
        cmd = self.compose_cmd('shell', 'rm', '-f', '-rR', '-v', wrap_with_single_quotes(obj.get_full_path()))
        if command_run(cmd).returncode != 0:
            raise RuntimeError("delete file(s) failed")
        logging.info('file deleting succeed')
