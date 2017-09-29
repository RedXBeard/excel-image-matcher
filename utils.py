import os

from subprocess import Popen, PIPE


def run_syscall(cmd):
    """
    run_syscall; handle sys calls this function used as shortcut.
    ::cmd: String, shell command is expected.
    """
    p = Popen(cmd, shell=True, stdout=PIPE, stderr=PIPE)
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


PATH_SEPERATOR = '\\' if os.path.realpath(__file__).find('\\') != -1 else '/'

if PATH_SEPERATOR == '/':
    cmd = "echo $HOME"
else:
    cmd = "echo %USERPROFILE%"

HOME_FOLDER = run_syscall(cmd)
