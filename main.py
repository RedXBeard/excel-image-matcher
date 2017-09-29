import os

import openpyxl
import xlrd
from kivy import Config
from kivy.app import App
from kivy.core.window import Window
from kivy.lang import Builder
from kivy.properties import StringProperty, ListProperty
from kivy.uix.screenmanager import ScreenManager, SlideTransition
from kivy.utils import get_color_from_hex

from utils import XlsRowIterator


class ExcelImageMatcher(ScreenManager):
    image_folder = StringProperty('')
    excel_file = StringProperty('')
    headers = ListProperty()

    def __init__(self):
        super(ExcelImageMatcher, self).__init__()
        self.image_folder = ''
        self.excel_file = ''

    def file_chosen(self, *args):
        try:
            path = args[0][0]
            if os.path.isfile(path):
                self.excel_file = args[0][0]
                self.switch_screen(screen='folder_chooser', direction='left')
        except IndexError:
            pass

    def folder_chosen(self, *args):
        try:
            path = args[0][0]
            if not os.path.isdir(path):
                path = os.path.dirname(path)
            if os.path.isdir(path):
                self.image_folder = path
                self.switch_screen(screen='summary_screen', direction='right')
        except IndexError:
            pass

    def parse_headers(self):
        file_name, file_ext = os.path.splitext(self.excel_file)
        rows = None
        if file_ext.lower().endswith('.xlsx'):
            wb = openpyxl.load_workbook(self.excel_file)
            sheet = wb.active
            rows = sheet.iter_rows()
        elif file_ext.lower().endswith('.xls'):
            wb = xlrd.open_workbook(filename=self.excel_file)
            sheet = wb.sheet_by_index(0)
            rows = XlsRowIterator(sheet)
        if rows:
            self.headers = map(lambda x: getattr(x, 'value', ''), rows.next())

    def switch_screen(self, screen, direction='left'):
        self.transition = SlideTransition(direction=direction)
        self.current = screen


class ExcelImageMatcherApp(App):
    def __init__(self, **kwargs):
        super(ExcelImageMatcherApp, self).__init__(**kwargs)
        Builder.load_file('assets/excelimagematcher.kv')
        self.title = 'Excel Image Matcher'
        self.icon = 'assets/images/excelimagematcher.ico'

    def build(self):
        excel_image_matcher = ExcelImageMatcher()
        return excel_image_matcher


if __name__ == '__main__':
    Config.set('kivy', 'desktop', 1)
    Config.set('input', 'mouse', 'mouse,multitouch_on_demand')
    Window.clearcolor = get_color_from_hex('E2DDD5')
    Window.size = 600, 600
    ExcelImageMatcherApp().run()
