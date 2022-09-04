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
import tkinter.scrolledtext as tk_scrolled_text


class AboutWindow(tk.Toplevel):
	def __init__(self, parent):
		super().__init__(parent)
		self.geometry(f'570x450+700+300')
		self.title(Manager.get_name('about'))

		self.__add_components()
		self.__configure_components()

	def __add_components(self):
		self.lTitle = tk.Label(self, text=Manager.get_about_title())
		self.tText = tk_scrolled_text.ScrolledText(self, height=7, width=3)

	def __configure_components(self):
		self.tText.insert(tk.END, Manager.get_name('copyright') + '\n\n' + Manager.get_name('aboutText'))
		self.tText.config(state='disabled')

		self.lTitle.grid(row=0, column=0, sticky='nsew')
		self.tText.grid(row=1, column=0, sticky='nsew')

		self.grid_rowconfigure(0, weight=1)
		self.grid_rowconfigure(1, weight=10)
		self.grid_columnconfigure(0, weight=1)
