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

import enum
import json
import os
import zipfile

import requests
import re

from bs4 import BeautifulSoup
from tkinter import messagebox


# TODO: Add more query types
class QueryType(enum.Enum):
    AUTHOR = enum.auto()
    BOOK = enum.auto()


# TODO: Add more formats
# TODO: Allow to specify format for specific book
class BookFormat(enum.Enum):
    FB2 = enum.auto()
    EPUB = enum.auto()
    MOBI = enum.auto()


# Static class
# Used for downloading and multilanguage support
class Manager(object):
    __hasInited = False
    __currentLanguage = None
    __version = None
    __langDictionary = None
    __names = None
    __titleStr = None
    __languages = None
    __aboutTitleStr = None
    __configDictionary = None
    __currentURL = "http://flibusta.is"  # TODO: Add connection settings support

    __config_file = None
    __lang_file = None

    @staticmethod
    def init(config_file_path, lang_file_path):
        Manager.__config_file = config_file_path
        Manager.__lang_file = lang_file_path

        with open(config_file_path, "r", encoding="utf-8") as configJson:
            Manager.__configDictionary = json.load(configJson)

        Manager.__currentLanguage = Manager.__configDictionary["currentLanguage"]
        Manager.__version = Manager.__configDictionary["version"]

        with open(lang_file_path, "r", encoding="utf-8") as langJson:
            Manager.__langDictionary = json.load(langJson)

        Manager.__names = Manager.__langDictionary[Manager.__currentLanguage]
        Manager.__titleStr = Manager.__names["title"] + " v" + str(Manager.__version)
        Manager.__aboutTitleStr = Manager.__names["aboutTitle"] + " \"" + Manager.__titleStr + "\""
        Manager.__languages = Manager.__langDictionary["languages"]

        Manager.__hasInited = True

    @staticmethod
    def get_config_file():
        assert Manager.__hasInited
        return Manager.__config_file

    @staticmethod
    def get_lang_file():
        assert Manager.__hasInited
        return Manager.__lang_file

    @staticmethod
    def get_name(name):
        assert Manager.__hasInited
        return Manager.__names[name]

    @staticmethod
    def get_title():
        assert Manager.__hasInited
        return Manager.__titleStr

    @staticmethod
    def get_about_title():
        assert Manager.__hasInited
        return Manager.__aboutTitleStr

    @staticmethod
    def get_current_language():
        assert Manager.__hasInited
        return Manager.__currentLanguage

    @staticmethod
    def get_languages():
        assert Manager.__hasInited
        return Manager.__languages

    @staticmethod
    def get_config(name):
        assert Manager.__hasInited
        assert name in Manager.__configDictionary
        return Manager.__configDictionary[name]

    @staticmethod
    def get_url():
        assert Manager.__hasInited
        return Manager.__currentURL

    # Doesn't work as named
    @staticmethod
    def change_language(lang):
        assert Manager.__hasInited
        assert lang in Manager.__langDictionary
        Manager.__currentLanguage = lang
        Manager.__names = Manager.__langDictionary[lang]

    # Returns list of lists
    # In case of QueryType.AUTHOR
    # [0] - Author name
    # [1] - Other information (e.g. books count)
    # [2] - Link
    # In case of QueryType.BOOK
    # [0] - Book name
    # [1] - Author
    # [2] - Link
    @staticmethod
    def do_search(query, query_type):
        url = Manager.__currentURL + "/bookSearch?ask=" + query
        if query_type == QueryType.AUTHOR.value:
            url += "&cha=on"
        elif query_type == QueryType.BOOK.value:
            url += "&chb=on"
        else:  # TODO: Series support
            print("do_search: UNIMPLEMENTED")
            exit(0)
        page = requests.get(url)
        document = BeautifulSoup(page.text, "html.parser")

        # TODO: Different mirrors of "Flibusta" has different html content organisation
        search_results = []
        for li_tag in document.find_all("ul", {"class": ""})[0]:
            if li_tag.text == "\n":
                continue
            else:
                parsed_text = None
                if query_type == QueryType.AUTHOR.value:
                    parsed_text = Manager.__parse_author_line(li_tag.text)
                elif query_type == QueryType.BOOK.value:
                    parsed_text = Manager.__parse_book_line(li_tag.text)
                else:
                    print("do_search: UNIMPLEMENTED")
                    exit(0)
                search_results.append([parsed_text[0], parsed_text[1], li_tag.find_all("a", href=True)[0]["href"]])
        return search_results

    # Returns list
    # [0] - Author name
    # [1] - Other information (e.g. books count)
    @staticmethod
    def __parse_author_line(line):  # TODO: Better parsing
        return [line[:line.find("(")], line[line.find("("):]]

    # Returns list
    # [0] - Book name
    # [1] - Author
    @staticmethod
    def __parse_book_line(line):  # TODO: Better parsing
        return [line[:line.find("-")], line[line.find("-") + 1:]]

    @staticmethod
    def do_book_download(url, file_format, path, progress_callback=None, file_index=1, file_count=1):
        if path is None:
            messagebox.showerror(Manager.get_title(), Manager.get_name("emptyQuery"))

        # Full URL is created automatically
        # Maybe, would be useful for variable connections modes (Tor, VPN or different mirrors)
        full_url = Manager.__currentURL + url + "/"
        if file_format == BookFormat.FB2.value:
            full_url += "fb2"
        elif file_format == BookFormat.EPUB.value:
            full_url += "epub"
        elif file_format == BookFormat.MOBI.value:
            full_url += "mobi"
        else:
            print("do_book_download: UNIMPLEMENTED")
            exit(0)

        response = requests.get(full_url, stream=True)
        total_length = int(response.headers.get('content-length'))
        if total_length is None:
            messagebox.showerror(Manager.get_name("error"), Manager.get_name("errorOccurred"))  # TODO: Error handling
        else:
            file_name = response.headers.get("Content-Disposition")
            if file_name is None:
                return  # TODO: Error handling
            file_name = file_name[file_name.find("=") + 1:]
            file_name = file_name.replace("\"", "")
            file_name = path + "/" + file_name
            with open(file_name, "wb") as write_file:
                downloaded = 0
                for data in response.iter_content(chunk_size=4096):
                    downloaded += len(data)
                    write_file.write(data)
                    try:
                        # TODO: Create better architecture for progress indication
                        progress_callback(int(100*(downloaded/(total_length*file_count))+(file_index/file_count)*100))
                    except:  # Download canceled
                        break
            # Auto unpacking
            if file_name.endswith("zip"):
                zip_file = zipfile.ZipFile(file_name)
                zip_file.extractall(path)
                zip_file.close()
                os.remove(file_name)

    @staticmethod
    def do_books_download(links, file_format, path, progress_callback=None):
        if path is None:
            messagebox.showerror(Manager.get_title(), Manager.get_name("emptyQuery"))  # TODO: Better handling

        i_counter = 1
        for e in links:
            Manager.do_book_download(e, file_format, path, progress_callback, i_counter, len(links))
            i_counter += 1

    # Returns list of lists
    # [0] - Book name
    # [1] - Author
    # [2] - Link
    @staticmethod
    def do_get_authors_books(url):
        full_url = Manager.__currentURL + url
        page = requests.get(full_url)
        document = BeautifulSoup(page.text, "html.parser")  # It's hard to parse author's page on "Flibusta"

        search_results = []
        author = document.find_all("h1")[1].text
        for e in document.find_all(['a', "br"]):
            if e.name == 'a':
                if re.match("/b/[0-9]+$", e["href"]):  # Is it a book URL
                    search_results.append([e.text, author, e["href"]])
            else:
                if e.next.next.name == 'a':  # TODO: Series support
                    search_results.append(['-'*36, e.next.next.text, ""])
        return search_results
