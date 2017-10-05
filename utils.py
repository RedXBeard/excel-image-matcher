import os

from subprocess import Popen, PIPE


class XlsRowIterator:
    def __init__(self, sheet):
        self.sheet = sheet
        self.row_index = 0
        self.max_index = sheet.nrows

    def __iter__(self):
        return self

    def next(self):
        if self.row_index < self.max_index:
            row = self.sheet.row(self.row_index)
            self.row_index += 1
            return row
        else:
            raise StopIteration


def run_syscall(command):
    """
    run_syscall; handle sys calls this function used as shortcut.
    ::cmd: String, shell command is expected.
    """
    p = Popen(command, shell=True, stdout=PIPE, stderr=PIPE)
    out, err = p.communicate()
    return out.rstrip()


def get_color(obj):
    u"""Color of widget returns."""
    try:
        obj_color = filter(lambda x: str(x).find('Color') != -1, obj.canvas.before.children)[0]
    except IndexError:
        obj_color = None
    return obj_color


def set_color(obj, color):
    obj_color = get_color(obj)
    try:
        obj_color.rgba = color
    except AttributeError:
        pass


def find_parent(cur_class, target_class):
    """find wanted widget from selected or current one"""
    req_class = cur_class
    if type(target_class) in [unicode, str]:
        target_class_name = target_class
    else:
        target_class_name = str(target_class().__class__).split('.')[1].replace("'>", "")
    while True:
        cls = str(req_class.__class__).split('.')[1].replace("'>", "")
        if cls == target_class_name:
            break
        elif cls == 'core':
            req_class = None
            break

        req_class = req_class.parent
    return req_class


PATH_SEPERATOR = '\\' if os.path.realpath(__file__).find('\\') != -1 else '/'

if PATH_SEPERATOR == '/':
    cmd = "echo $HOME"
else:
    cmd = "echo %USERPROFILE%"

HOME_FOLDER = run_syscall(cmd)
