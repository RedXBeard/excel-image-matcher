import os
import re
import shutil

import openpyxl
import xlrd
from kivy import Config
from kivy.app import App
from kivy.core.window import Window
from kivy.lang import Builder
from kivy.properties import StringProperty, ListProperty, NumericProperty
from kivy.clock import Clock
from kivy.uix.button import Button
from kivy.uix.gridlayout import GridLayout
from kivy.uix.screenmanager import ScreenManager, SlideTransition
from kivy.utils import get_color_from_hex
from kivy.uix.image import Image

from utils import XlsRowIterator, find_parent, HOME_FOLDER


def excel_parser(excel_file):
    wb = sheet = rows = None
    file_name, file_ext = os.path.splitext(excel_file)
    if file_ext.lower().endswith('.xlsx'):
        wb = openpyxl.load_workbook(excel_file)
        sheet = wb.active
        rows = sheet.iter_rows()
    elif file_ext.lower().endswith('.xls'):
        wb = xlrd.open_workbook(filename=excel_file)
        sheet = wb.sheet_by_index(0)
        rows = XlsRowIterator(sheet)
    return wb, sheet, rows


class CustomButton(Button):
    def select(self, *args, **kwargs):
        pass

    def deselect(self, *args, **kwargs):
        pass


class HeaderItem(GridLayout):
    text = StringProperty('')
    index = NumericProperty(0)

    def pressed_but(self):
        root = find_parent(self, ExcelImageMatcher)
        images = self.checkbox.children
        list_name = self.parent.parent.parent.name
        if images:
            self.checkbox.remove_widget(images[0])
            try:
                if list_name == 'barcode':
                    root.selected_barcode_column = None
                elif list_name == 'versions':
                    root.selected_columns.pop(root.selected_columns.index(self.index))
                elif list_name == 'base':
                    root.selected_base_column = None
            except ValueError:
                pass
        else:
            image = Image(source="assets/images/tick.png",
                          pos=self.checkbox.pos,
                          size=self.checkbox.size)
            self.checkbox.add_widget(image)
            try:
                if list_name == 'barcode':
                    root.selected_barcode_column = self.index
                elif list_name == 'versions':
                    root.selected_columns.append(self.index)
                elif list_name == 'base':
                    root.selected_base_column = self.index
            except ValueError:
                pass


class ExcelImageMatcher(ScreenManager):
    image_folder = StringProperty('')
    excel_file = StringProperty('')
    headers = ListProperty()
    selected_columns = []
    selected_base_column = None
    selected_barcode_column = None

    def __init__(self):
        super(ExcelImageMatcher, self).__init__()
        self.dest_folder = os.path.join(HOME_FOLDER, 'processed')
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

    def headers_to_items(self, row_index, item):
        return {'text': item['text'], 'index': item['index']}

    def parse_headers(self):
        wb, sheet, rows = excel_parser(self.excel_file)
        if rows:
            self.headers = map(
                lambda x: {'text': getattr(x, 'value', ''), 'index': getattr(x, 'row_idx', '')}, rows.next()
            )
            self.switch_screen('column_matcher')
        wb.close()

    def start_matching(self, *args, **kwargs):
        self.selected_columns
        self.switch_screen('processing')
        if not os.path.exists(self.dest_folder):
            os.makedirs(self.dest_folder)
        wb, sheet, rows = excel_parser(self.excel_file)
        _ = rows.next()

        Clock.schedule_once(lambda dt: self.parse_rows(rows), .1)

    def parse_rows(self, rows):
        try:
            cols = rows.next()
            base_column = cols[self.selected_base_column].value
            barcode_column = cols[self.selected_barcode_column].value
            files = os.listdir(self.image_folder)
            matched = filter(
                lambda x: re.match(r'{}.*\.(?P<ext>(JPG|jpg|JPEG|jpeg|PNG|png))'.format(base_column), x), files
            )
            for file_name in matched:
                src = os.path.join(self.image_folder, file_name)
                dst = os.path.join(self.dest_folder, str(barcode_column), file_name)
                if not os.path.exists(os.path.join(self.dest_folder, str(barcode_column))):
                    os.makedirs(os.path.join(self.dest_folder, str(barcode_column)))
                shutil.copyfile(src, dst)
            self.history.text += '{} processed\n'.format(base_column)
            Clock.schedule_once(lambda dt: self.parse_rows(rows), .1)
        except StopIteration:
            self.switch_screen('congrats')

    def congrats(self, *args, **kwargs):
        self.switch_screen('congrats')

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
