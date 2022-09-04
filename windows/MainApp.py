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

import webbrowser

from Manager import *
from windows.AboutWindow import *
from windows.HelpWindow import *
from windows.SettingsWindow import *
from windows.Alerts import *

import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from tkinter import filedialog


class MainApp(tk.Tk):
    def __init__(self):
        super().__init__()

        self.download_alert = None
        self.selected_row_id = None
        self.current_query = None
        self.current_query_type = None
        self.search_results = {}
        self.search_IDs = {}

        self.title(Manager.get_title())
        self.geometry(f'1024x768+433+150')

        self.queryType = tk.IntVar()

        self.__add_components()
        self.__configure_components()

    def __add_components(self):
        # Menu
        self.mMenu = tk.Menu(self)
        self.mMenu.add_cascade(label=Manager.get_name('settings'), command=self.settings_window)
        self.mMenu.add_cascade(label=Manager.get_name('help'), command=self.help_window)
        self.mMenu.add_cascade(label=Manager.get_name('about'), command=self.about_window)

        # Frame 1
        self.frame1 = tk.Frame(self)

        self.lQuery = tk.Label(self.frame1, text=Manager.get_name('query'))
        self.eQuery = tk.Entry(self.frame1)
        self.bSearch = tk.Button(self.frame1, text=Manager.get_name('search'), command=self.on_button_search)
        self.lType = tk.Label(self.frame1, text=Manager.get_name('type'))

        # Frame 2
        self.frame2 = tk.Frame(self.frame1)
        self.rAuthor = tk.Radiobutton(self.frame2, text=Manager.get_name('author'), variable=self.queryType,
                                      value=QueryType.AUTHOR.value)
        self.rBook = tk.Radiobutton(self.frame2, text=Manager.get_name('book'), variable=self.queryType,
                                    value=QueryType.BOOK.value)

        # Frame 3
        self.frame3 = tk.Frame(self)
        self.lResults = tk.Label(self.frame3, text=Manager.get_name('results'))
        self.tResults = tk.ttk.Treeview(self.frame3, show='headings',
                                        columns=('1', Manager.get_name('author'), Manager.get_name('book')))
        self.scrollResults = tk.Scrollbar(self.tResults, orient=tk.VERTICAL, command=self.tResults.yview)

        # Frame 4
        self.frame4 = tk.Frame(self)
        self.lStatus = tk.Label(self.frame4, text=Manager.get_name('ready'))
        self.bDownloadSelected = tk.Button(self.frame4, text=Manager.get_name('downloadSelected'),
                                           command=self.on_download_selected)

    def __configure_components(self):
        self.config(menu=self.mMenu)

        # Frame 1
        self.lQuery.grid(row=0, column=0, sticky='w')
        self.eQuery.grid(row=0, column=1, sticky='nsew', padx=3, pady=3)
        self.eQuery.bind('<Return>', self.on_button_search)
        self.bSearch.grid(row=0, column=2, sticky='nsew', padx=3)
        self.lType.grid(row=1, column=0, sticky='w')

        self.frame1.grid_rowconfigure(0, weight=1)
        self.frame1.grid_rowconfigure(1, weight=1)
        self.frame1.grid_columnconfigure(0, weight=3)
        self.frame1.grid_columnconfigure(1, weight=100)
        self.frame1.grid_columnconfigure(2, weight=7)

        # Frame 2
        self.rAuthor.pack(side=tk.LEFT)
        self.rBook.pack(side=tk.LEFT)
        self.frame2.grid(row=1, column=1, sticky='w')

        # Frame 3
        self.lResults.grid(row=0, column=0, sticky='w')
        self.tResults.grid(row=1, column=0, sticky='nsew', columnspan=2)

        self.tResults.heading('1', text='*')
        self.tResults.column('1', width=15, minwidth=30, stretch=tk.NO)
        self.tResults.heading(Manager.get_name('author'), text=Manager.get_name('author'))
        self.tResults.column(Manager.get_name('author'), width=200)
        self.tResults.heading(Manager.get_name('book'), text=Manager.get_name('book'))
        self.tResults.column(Manager.get_name('book'), width=551)
        self.tResults.bind('<Double-1>', self.on_search_result_dclick)
        self.tResults.bind('<Button-3>', self.on_search_result_rclick)

        self.frame3.grid_rowconfigure(0, weight=1)
        self.frame3.grid_rowconfigure(1, weight=50, pad=7)
        self.frame3.grid_columnconfigure(0, weight=6)
        self.frame3.grid_columnconfigure(1, weight=1)

        self.scrollResults.pack(side=tk.RIGHT, fill='y')
        self.tResults.configure(yscrollcommand=self.scrollResults.set)

        # Frame 4
        self.lStatus.pack(side=tk.LEFT)
        self.bDownloadSelected.pack(side=tk.RIGHT)

        # Result
        self.frame1.pack(side=tk.TOP, fill='x', padx=(7, 7), pady=(7, 0))
        self.frame3.pack(side=tk.TOP, fill='both', expand=True, padx=(7, 7), pady=(0, 7))
        self.frame4.pack(side=tk.TOP, fill='both', expand=False, padx=(10, 7), pady=(0, 7))

    def on_button_search(self, event=None):
        if self.eQuery.get() and self.queryType.get() != 0:
            self.current_query = self.eQuery.get()
            self.current_query_type = self.queryType.get()
            temp1 = SearchAlert(self)
            self.update()
            self.search_results = Manager.do_search(self.current_query, self.current_query_type)
            self.__update_results()
            temp1.destroy()
            self.lStatus.config(text=Manager.get_name('searchCompleted') + str(len(self.search_results)))
            if self.current_query_type == QueryType.AUTHOR.value:
                self.bDownloadSelected['state'] = tk.DISABLED
            else:
                self.bDownloadSelected['state'] = tk.NORMAL
        else:
            messagebox.showwarning(Manager.get_title(), Manager.get_name('emptyQuery'))

    def on_book_download(self, event=None):
        self.__create_download_alert()

        Manager.do_book_download(self.search_IDs[self.selected_row_id],
                                 Manager.get_config('bookFormat'),
                                 Manager.get_config('saveDir') if Manager.get_config('isSaveToDir')
                                 else filedialog.askdirectory(),
                                 self.__download_callback)
        self.download_alert.destroy()

    def on_book_download_in(self, event=None):
        self.__create_download_alert()
        Manager.do_book_download(self.search_IDs[self.selected_row_id],
                                 Manager.get_config('bookFormat'),
                                 filedialog.askdirectory(),
                                 self.__download_callback)
        self.download_alert.destroy()

    # Download selected books
    def on_download_selected(self, event=None, down_in=False):
        download_list = []
        if len(self.search_IDs) == 0:
            return
        for (item_id, link) in self.search_IDs.items():
            if self.tResults.item(item_id)['values'][0] == '*':
                download_list.append(link)
        if len(download_list) != 0:
            self.__create_download_alert()
            Manager.do_books_download(download_list,
                                      Manager.get_config('bookFormat'),
                                      Manager.get_config('saveDir') if Manager.get_config('isSaveToDir') and not down_in
                                      else filedialog.askdirectory(),
                                      self.__download_callback)
            self.download_alert.destroy()

    # Downloads all authors books
    def on_author_download(self, event=None):
        self.__author_transition()
        self.on_download_selected(down_in=False)

    def on_author_download_in(self, event=None):
        self.__author_transition()
        self.on_download_selected(down_in=True)

    # Marks book as to be downloaded
    def on_search_result_dclick(self, event):
        row_to_check = self.tResults.identify_row(event.y)
        if row_to_check:
            temp1 = self.tResults.item(row_to_check)['values']
            if not (temp1[1].startswith('-') or self.queryType.get() == QueryType.AUTHOR.value):
                if temp1[0] == '*':
                    temp1[0] = ' '
                else:
                    temp1[0] = '*'
            self.tResults.item(row_to_check, values=temp1)
        self.tResults.update()

    def on_search_result_rclick(self, event):
        self.selected_row_id = self.tResults.identify_row(event.y)
        if self.selected_row_id:
            if self.current_query_type == QueryType.BOOK.value:
                context_menu = self.create_book_context_menu()
            elif self.current_query_type == QueryType.AUTHOR.value:
                context_menu = self.create_author_context_menu()
            else:
                print('UNIMPLEMENTED')
                exit(1)
            context_menu.tk_popup(event.x_root, event.y_root)
            context_menu.grab_release()

    def create_book_context_menu(self):
        result = tk.Menu(self, tearoff=0)
        result.add_command(label=Manager.get_name('downloadBook'), command=self.on_book_download)
        result.add_separator()
        # result.add_command(label=Manager.get_name('viewAuthor'), command=self.on_view_author) TODO: Implement
        result.add_command(label=Manager.get_name('sDownloadBook'), command=self.on_book_download_in)
        result.add_command(label=Manager.get_name('openInBrowser'), command=self.on_open_browser)
        return result

    def create_author_context_menu(self):
        result = tk.Menu(self, tearoff=0)
        result.add_command(label=Manager.get_name('viewAuthor'), command=self.on_view_author)
        result.add_separator()
        result.add_command(label=Manager.get_name('downloadAllBooks'), command=self.on_author_download)
        result.add_command(label=Manager.get_name('sDownloadAllBooks'), command=self.on_author_download_in)
        result.add_command(label=Manager.get_name('openInBrowser'), command=self.on_open_browser)
        return result

    # Shows all authors books
    def on_view_author(self, event=None):
        self.eQuery.delete(0, tk.END)
        for e in self.search_results:
            if e[2] == self.search_IDs[self.selected_row_id]:
                self.eQuery.insert(0, e[1] if self.queryType == QueryType.BOOK.value else e[0])
        self.current_query_type = QueryType.BOOK.value
        self.queryType.set(QueryType.BOOK.value)
        self.search_results = Manager.do_get_authors_books(self.search_IDs[self.selected_row_id])
        self.bDownloadSelected['state'] = tk.NORMAL
        self.__update_results()

    def on_open_browser(self, event=None):
        webbrowser.open(Manager.get_url() + self.search_IDs[self.selected_row_id], new=0, autoraise=True)

    def __update_results(self):
        self.__clear_tree()

        for element in self.search_results:
            list_id = self.tResults.insert('', tk.END, values=('', element[0], element[1]))
            self.search_IDs[list_id] = element[2]

    def __clear_tree(self):
        for element in self.tResults.get_children():
            self.tResults.delete(element)
        self.search_IDs.clear()

    def __create_download_alert(self):
        self.download_alert = DownloadAlert(self)
        self.download_alert.attributes('-topmost', 'true')
        self.update()
        self.download_alert.grab_set()

    def __download_callback(self, value):
        assert self.download_alert is not None
        self.download_alert.progress_set(value)
        self.update()

    # Selects all author's books
    def __author_transition(self):
        self.on_view_author()
        for e in self.search_IDs.keys():
            temp1 = self.tResults.item(e)['values']
            if not temp1[1].startswith('-') or not self.queryType.get() == QueryType.AUTHOR.value:
                temp1[0] = '*'
            self.tResults.item(e, values=temp1)
        self.tResults.update()

    def about_window(self):
        new_window = AboutWindow(self)
        new_window.attributes('-topmost', 'true')
        new_window.grab_set()

    def help_window(self):
        new_window = HelpWindow(self)
        new_window.attributes('-topmost', 'true')
        new_window.grab_set()

    def settings_window(self):
        new_window = SettingsWindow(self)
        new_window.attributes('-topmost', 'true')
        new_window.grab_set()
