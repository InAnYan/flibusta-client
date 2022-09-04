"""
MIT License

Copyright (c) 2022 Ruslan Popov <ruslanpopov1512@gmail.com>

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

from Manager import *
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from tkinter import filedialog


class SettingsWindow(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)

        self.geometry(f'533x143+600+300')
        self.title(Manager.get_name('settings'))

        self.gbChecked = tk.BooleanVar()
        self.sLangSelected = tk.StringVar()
        self.sDir = tk.StringVar()
        self.iBookFormat = tk.IntVar()

        self.__add_components()
        self.__configure_components()

    def __add_components(self):
        self.lLanguage = tk.Label(self, text=Manager.get_name('language'))
        self.cLangCombo = ttk.Combobox(self, values=list(Manager.get_languages().keys()),
                                       textvariable=self.sLangSelected)

        self.lSaveDir = tk.Label(self, text=Manager.get_name('saveDir'))
        self.eDir = tk.Entry(self, textvariable=self.sDir)
        self.bSelectDir = tk.Button(self, text=Manager.get_name('selectDir'), command=self.on_button_dir)

        self.gIsSaveToDir = tk.Checkbutton(self, text=Manager.get_name('isSaveToDir'), command=self.on_check_box,
                                           variable=self.gbChecked)
        self.bSaveSettings = tk.Button(self, text=Manager.get_name('saveSettings'), command=self.on_button_save)
        self.lReminder = tk.Label(self, text=Manager.get_name('changesDetected'))

        # Frame
        self.lBookFormat = tk.Label(self, text=Manager.get_name('bookFormat'))
        self.frame1 = tk.Frame(self)
        self.rFb2 = tk.Radiobutton(self.frame1, text='fb2', variable=self.iBookFormat, value=BookFormat.FB2.value,
                                   command=self.on_radio_changed)
        self.rEpub = tk.Radiobutton(self.frame1, text='epub', variable=self.iBookFormat, value=BookFormat.EPUB.value,
                                    command=self.on_radio_changed)
        self.rPdf = tk.Radiobutton(self.frame1, text='mobi', variable=self.iBookFormat, value=BookFormat.MOBI.value,
                                   command=self.on_radio_changed)

    def __configure_components(self):
        self.lLanguage.grid(row=0, column=0, sticky=tk.W, padx=(7, 0), pady=(7, 0))
        self.cLangCombo.grid(row=0, column=1, sticky='we', padx=(0, 7), pady=(7, 0))
        self.cLangCombo.current(list(Manager.get_languages().values()).index(Manager.get_current_language()))
        self.cLangCombo.bind('<<ComboboxSelected>>', self.on_combo_box_changed)

        self.lSaveDir.grid(row=1, column=0, sticky=tk.W, padx=(7, 0))
        self.eDir.grid(row=1, column=1, columnspan=2, sticky='we', padx=(0, 7))
        self.sDir.set(Manager.get_config('saveDir'))
        self.bSelectDir.grid(row=1, column=3, sticky='we', padx=(0, 7))

        self.gIsSaveToDir.grid(row=2, column=0, columnspan=2, sticky=tk.W, padx=(7, 0))

        self.lBookFormat.grid(row=3, column=0, padx=(7, 0), sticky='w')
        self.rFb2.pack(side=tk.LEFT)
        self.rEpub.pack(side=tk.LEFT)
        self.rPdf.pack(side=tk.LEFT)
        self.frame1.grid(row=3, column=1, columnspan=2, sticky='w')

        self.iBookFormat.set(Manager.get_config('bookFormat'))

        self.bSaveSettings.grid(row=4, column=3, sticky='we', padx=(0, 7), pady=(0, 7))

        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        self.grid_rowconfigure(2, weight=1)
        self.grid_rowconfigure(3, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=10)
        self.grid_columnconfigure(2, weight=10)
        self.grid_columnconfigure(3, weight=1)

        if not Manager.get_config('isSaveToDir'):
            self.eDir.configure(state='readonly')
            self.gIsSaveToDir.select()

    def on_radio_changed(self, event=None):
        self.lReminder.grid(row=4, column=0, columnspan=2)

    def on_combo_box_changed(self, event=None):
        self.lReminder.grid(row=4, column=0, columnspan=2)

    def on_button_dir(self):
        dir_name = filedialog.askdirectory()
        if dir_name:
            self.sDir.set(dir_name)
            self.lReminder.grid(row=4, column=0, columnspan=2)

    def on_check_box(self):
        if self.gbChecked.get():
            self.eDir.config(state='readonly')
        else:
            self.eDir.config(state='normal')
        self.lReminder.grid(row=4, column=0, columnspan=2)

    def on_button_save(self):
        language_selected = Manager.get_languages()[self.sLangSelected.get()]

        with open(Manager.get_config_file(), 'r') as file:
            new_dict = json.load(file)

        if language_selected != Manager.get_current_language():
            messagebox.showwarning(Manager.get_title(), Manager.get_name('languageWarning'))

        new_dict['currentLanguage'] = language_selected
        if self.gbChecked.get():
            new_dict['isSaveToDir'] = False
        else:
            new_dict['isSaveToDir'] = True

        new_dict['saveDir'] = self.eDir.get()
        new_dict['bookFormat'] = self.iBookFormat.get()

        with open(Manager.get_config_file(), 'w') as file:
            json.dump(new_dict, file)

        Manager.init(Manager.get_config_file(), Manager.get_lang_file())
        self.destroy()
