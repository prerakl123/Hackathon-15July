from tkinter import *
import tkinter
# from tkinter import messagebox as tk_mb
# import os
# import importlib
# import sys
import webbrowser
import json
import time
from PIL import Image, ImageTk

LIGHT = 'Light'
DARK = 'Dark'
PLACEHOLDER = 'Search by Name, Ticker or RIC'

with open('themes.json', 'r') as theme_file:
    themes = json.loads(theme_file.read())

font = themes['font']
# label_frame_config = themes[themes['current_theme']]['label_frame']
frame_config = themes[themes['current_theme']]['frame']
canvas_config = themes[themes['current_theme']]['canvas']
# text_config = themes[themes['current_theme']]['text']
# button_config = themes[themes['current_theme']]['button']
# label_config = themes[themes['current_theme']]['label']
# checkbtn_config = themes[themes['current_theme']]['checkbutton']
# combo_config = themes[themes['current_theme']]['combobox']
# entry_config = themes[themes['current_theme']]['entry']

webbrowser.register('chrome', None, webbrowser.BackgroundBrowser("C:/Program Files (x86)/Google//Chrome/Application/chrome.exe"))


def center_window(win: Tk or Toplevel):
    """
    centers a tkinter window
    :param win: the main window or Toplevel window to center
    """
    win.update_idletasks()
    width = win.winfo_width()
    frm_width = win.winfo_rootx() - win.winfo_x()
    win_width = width + 2 * frm_width
    height = win.winfo_height()
    titlebar_height = win.winfo_rooty() - win.winfo_y()
    win_height = height + titlebar_height + frm_width
    x = win.winfo_screenwidth() // 2 - win_width // 2
    y = win.winfo_screenheight() // 2 - win_height // 2
    win.geometry('+{}+{}'.format(x, y))
    win.deiconify()


def load_image(path: str, dimensions: tuple) -> ImageTk.PhotoImage:
    img = Image.open(path)
    img_dimen = img.resize(dimensions, Image.ANTIALIAS)
    return ImageTk.PhotoImage(img_dimen)


def update_themes(event=None, _app=None):
    """
    Updates current "theme widget configuration" variables and,
    refreshes and applies the theme if `app` is not None
    :param event: argument for binders
    :param _app: for refreshing app contents according to theme
    """
    global font, frame_config, canvas_config

    font = themes['font']
    frame_config = themes[themes['current_theme']]['frame']

    if _app is not None:
        _app.refresh()


class PlaceHolderEntry(Entry):
    def __init__(self, master=None, placeholder="PLACEHOLDER", placeholdercolor='grey', **kw):
        Entry.__init__(self, master, **kw)

        self.placeholder = placeholder
        self.placeholder_color = placeholdercolor
        self.default_fg_color = self['fg']

        self.bind("<FocusIn>", self.foc_in)
        self.bind("<FocusOut>", self.foc_out)

        self.put_placeholder()

    def configure(self, cnf=None, **kw):
        if 'placeholdercolor' in list(kw.keys()):
            self.placeholder_color = kw['placeholdercolor']
            self.put_placeholder()
            kw.pop('placeholdercolor')
        tkinter.Entry.configure(self=self, cnf=cnf, **kw)

    config = configure

    def put_placeholder(self):
        self.delete(0, END)
        self.insert(0, self.placeholder)
        self['fg'] = self.placeholder_color

    def foc_in(self, *args):
        if self['fg'] == self.placeholder_color:
            self.delete('0', 'end')
            self['fg'] = self.default_fg_color

    def foc_out(self, *args):
        if not self.get():
            self.put_placeholder()


class SmoothScrollFrame(LabelFrame):
    def __init__(self, master, **kw):
        LabelFrame.__init__(self, master, **kw)
        self.canvas = Canvas(self, **canvas_config)
        v_scroll = Scrollbar(self, orient=VERTICAL)
        h_scroll = Scrollbar(self, orient=HORIZONTAL)

        v_scroll.config(command=self.canvas.yview)
        h_scroll.config(command=self.canvas.xview)
        self.canvas.config(yscrollcommand=v_scroll.set, xscrollcommand=h_scroll.set, yscrollincrement=1)

        v_scroll.pack(side=RIGHT, fill=Y)
        h_scroll.pack(side=BOTTOM, fill=X)
        self.canvas.pack(side=LEFT, expand=YES, fill=BOTH)

        self.widget_frame = Frame(self.canvas, **frame_config)
        self.canvas.create_window(0, 0, window=self.widget_frame, anchor=NW)

        self.bind('<Configure>', self.on_interior_config)
        self.master.master.bind_all('<MouseWheel>', self.on_mouse_wheel)

    @staticmethod
    def pack_multiple_widgets(*widgets, **kwargs):
        if len(kwargs.items()) < 1:
            for i in widgets:
                i.pack()
        else:
            for i in widgets:
                i.pack(**kwargs)

    def on_interior_config(self, event=None):
        self.update_idletasks()
        width, height = self.widget_frame.winfo_reqwidth(), self.widget_frame.winfo_reqheight()
        self.canvas.config(scrollregion=(0, 0, width, height+50))

    refresh = on_interior_config

    def on_mouse_wheel(self, event=None):
        def _scroll(e=None):
            """For smooth scrolling"""
            nonlocal shift_scroll, scroll, scrolled
            if shift_scroll:
                if scrolled == 15:
                    return
                self.canvas.xview_scroll(scroll, 'units')
                scrolled += 1
                self.after(30, _scroll)
            else:
                if scrolled == 105:
                    return
                self.canvas.yview_scroll(scroll, 'units')
                scrolled += 1
                self.after(5, _scroll)

        scrolled = 0
        shift_scroll = (event.state & 0x1) != 0
        scroll = -1 if event.delta > 0 else 1
        _scroll()


class SearchResultDropDownFrame(Frame):
    def __init__(self, master, root, parent_frame_list: list, bank_name: str, ownership: str, perm_id: int or str,
                 industry: str, country: str, key: int or str, perm_id_url='Link not available', **kw):
        Frame.__init__(self, master, **kw)
        self.master = master
        self.root = root
        self.parent_frame_list = parent_frame_list
        self.bank_name, self.ownership, self.perm_id, self.industry, self.country, self.key, \
            self.perm_id_url = bank_name, ownership, perm_id, industry, country, key, perm_id_url

        self.perm_id_img, self.industry_img, self.country_img, self.key_img = [None] * 4
        self.dropped_down = False
        self.set_images()

        # ------------ UPPER FRAME ------------ #
        self.upper_frame = Frame(self)
        self.name_and_id_frame = Frame(self.upper_frame)
        self.bank_name_lbl = Label(self.name_and_id_frame, text=self.bank_name, anchor=W)
        self.ownership_lbl = Label(self.name_and_id_frame, text=self.ownership, anchor=W)

        self.drop_down_frame = Frame(self.upper_frame)
        self.drop_down_lbl = Label(self.drop_down_frame, text='⤵', anchor=S, width=7)
        self.drop_down_lbl.bind('<ButtonRelease-1>', self.drop_config)

        self.perm_id_url_frame = Frame(self.upper_frame)
        self.permidurl_lbl = Label(self.perm_id_url_frame, text='🔗 PermID URL', anchor=SE)
        self.perm_id_url_lbl = Label(self.perm_id_url_frame, text=self.perm_id_url, anchor=SE)
        self.perm_id_url_lbl.bind('<Enter>', lambda _=None: self.perm_id_url_lbl.config(cursor='hand2', font="Calibri 12 underline"))
        self.perm_id_url_lbl.bind('<Leave>', lambda _=None: self.perm_id_url_lbl.config(cursor='', font="Calibri 12"))
        self.perm_id_url_lbl.bind('<ButtonRelease-1>', self.open_url)

        # ------------ MIDDLE FRAME ------------ #
        self.middle_frame = Frame(self)

        self.perm_id_frame = Frame(self.middle_frame)
        self.perm_id_lbl = Label(self.perm_id_frame, text='Perm ID', width=30, height=125, anchor=S, image=self.perm_id_img)
        self.perm_id_name_lbl = Label(self.perm_id_frame, text=str(self.perm_id), width=30)

        self.industry_frame = Frame(self.middle_frame)
        self.industry_lbl = Label(self.industry_frame, text='Industry', width=30, height=125, anchor=S, image=self.industry_img)
        self.industry_name_lbl = Label(self.industry_frame, text=self.industry, width=30)

        self.country_frame = Frame(self.middle_frame)
        self.country_lbl = Label(self.country_frame, text='Country', width=30, height=125, anchor=S, image=self.country_img)
        self.country_name_lbl = Label(self.country_frame, text=self.country, width=30)

        self.key_frame = Frame(self.middle_frame)
        self.key_lbl = Label(self.key_frame, text='Lei', width=30, height=125, anchor=S, image=self.key_img)
        self.key_name_lbl = Label(self.key_frame, text=str(self.key), width=30)

        # ------------ LOWER FRAME ------------ #
        self.lower_frame = Frame(self)

        self.edit_frame = Frame(self.lower_frame)
        self.edit_lbl = Label(self.edit_frame, text='🖉 Edit')
        self.edit_lbl.bind('<Enter>', lambda _=None: self.edit_lbl.config(cursor='hand2', font=('Century Gothic', 15, 'underline')))
        self.edit_lbl.bind('<Leave>', lambda _=None: self.edit_lbl.config(cursor='', font=('Century Gothic', 15)))
        self.edit_lbl.bind('<ButtonRelease-1>', self.edit_info)

        self.confirm_frame = Frame(self.lower_frame)
        self.confirm_lbl = Label(self.confirm_frame, text=f'{chr(10004)}Confirm')
        self.confirm_lbl.bind('<Enter>', lambda _=None: self.confirm_lbl.config(cursor='hand2', font=('Century Gothic', 15, 'underline')))
        self.confirm_lbl.bind('<Leave>', lambda _=None: self.confirm_lbl.config(cursor='', font=('Century Gothic', 15)))
        self.confirm_lbl.bind('<ButtonRelease-1>', lambda _=None: self.root.confirm(frame=self))

        self.refresh()

    def back_up(self):
        self.drop_down_lbl.config(text='⤵')
        self.dropped_down = False
        self.unpack_dropdown_frames()
        self.configure(height=50)

    def drop(self):
        self.drop_down_lbl.config(text='⤶')
        self.dropped_down = True
        self.pack_dropdown_frames()
        self.configure(height=280)

    def drop_config(self, event=None):
        if self.dropped_down:
            self.back_up()
        else:
            for _frame in self.parent_frame_list:
                if _frame.dropped_down:
                    _frame.drop_config()
            self.drop()
        self.master.master.master.refresh()

    def edit_info(self, event=None):
        self.root.clear_search_results()
        self.root.root.remove_frame(SearchResultsFrame)
        self.root.root.show_frame(TitlePageFrame)

    def open_url(self, event=None):
        url = self.perm_id_url_lbl.cget('text')
        webbrowser.get('chrome').open(url)

    def pack_all(self):
        self.upper_frame.pack(side=TOP, fill=X, expand=TRUE)
        self.name_and_id_frame.pack(side=LEFT, fill=BOTH, expand=TRUE)
        self.drop_down_frame.pack(side=RIGHT, fill=BOTH)
        self.perm_id_url_frame.pack(side=RIGHT, fill=BOTH, expand=TRUE)
        self.bank_name_lbl.pack(side=TOP, anchor=NW, ipady=5)
        self.ownership_lbl.pack(side=TOP, anchor=SW, ipady=5)
        self.drop_down_lbl.pack(anchor=CENTER)
        self.permidurl_lbl.pack(side=TOP, anchor=NE, ipady=5)
        self.perm_id_url_lbl.pack(side=TOP, anchor=SE, ipady=5)
        if self.dropped_down:
            self.pack_dropdown_frames()

    def pack_dropdown_frames(self):
        self.middle_frame.pack(side=TOP, fill=X, expand=TRUE, ipady=15)
        self.perm_id_frame.pack(side=LEFT)
        self.industry_frame.pack(side=LEFT)
        self.key_frame.pack(side=RIGHT)
        self.country_frame.pack(side=RIGHT)
        self.perm_id_lbl.pack(side=TOP, anchor=CENTER, fill=BOTH, expand=TRUE, padx=3)
        self.perm_id_name_lbl.pack(side=BOTTOM, anchor=CENTER, padx=3)
        self.industry_lbl.pack(side=TOP, anchor=CENTER, fill=BOTH, expand=TRUE, padx=3)
        self.industry_name_lbl.pack(side=BOTTOM, anchor=CENTER, padx=3)
        self.key_lbl.pack(side=TOP, anchor=CENTER, fill=BOTH, expand=TRUE, padx=3)
        self.key_name_lbl.pack(side=BOTTOM, anchor=CENTER, padx=3)
        self.country_lbl.pack(side=TOP, anchor=CENTER, fill=BOTH, expand=TRUE, padx=3)
        self.country_name_lbl.pack(side=BOTTOM, anchor=CENTER, padx=3)
        self.lower_frame.pack(side=TOP, fill=X, expand=TRUE, ipady=5)
        self.edit_frame.pack(side=LEFT, expand=TRUE, fill=BOTH, ipady=5)
        self.confirm_frame.pack(side=RIGHT, expand=TRUE, fill=BOTH, ipady=5)
        self.edit_lbl.pack(side=RIGHT, fill=BOTH, ipadx=8)
        self.confirm_lbl.pack(side=LEFT, fill=BOTH, ipadx=8)

    def unpack_all(self):
        if self.dropped_down:
            self.unpack_dropdown_frames()
        self.upper_frame.pack_forget()
        self.name_and_id_frame.pack_forget()
        self.drop_down_frame.pack_forget()
        self.perm_id_url_frame.pack_forget()
        self.bank_name_lbl.pack_forget()
        self.ownership_lbl.pack_forget()
        self.drop_down_lbl.pack_forget()
        self.permidurl_lbl.pack_forget()
        self.perm_id_url_lbl.pack_forget()

    def unpack_dropdown_frames(self):
        self.middle_frame.pack_forget()
        self.perm_id_frame.pack_forget()
        self.industry_frame.pack_forget()
        self.key_frame.pack_forget()
        self.country_frame.pack_forget()
        self.perm_id_lbl.pack_forget()
        self.perm_id_name_lbl.pack_forget()
        self.industry_lbl.pack_forget()
        self.industry_name_lbl.pack_forget()
        self.key_lbl.pack_forget()
        self.key_name_lbl.pack_forget()
        self.country_lbl.pack_forget()
        self.country_name_lbl.pack_forget()
        self.lower_frame.pack_forget()
        self.edit_frame.pack_forget()
        self.confirm_frame.pack_forget()
        self.edit_lbl.pack_forget()
        self.confirm_lbl.pack_forget()

    def refresh(self):
        if themes['current_theme'] == DARK:
            self.drop_down_lbl.bind('<Enter>', lambda _=None: [self.drop_down_lbl.config(fg='#55dd5d'), self.drop_down_lbl.config(cursor='hand2')])
            self.drop_down_lbl.bind('<Leave>', lambda _=None: [self.drop_down_lbl.config(fg='#00a30b'), self.drop_down_lbl.config(cursor='')])
        else:
            self.drop_down_lbl.bind('<Enter>', lambda _=None: [self.drop_down_lbl.config(fg='#069943'), self.drop_down_lbl.config(cursor='hand2')])
            self.drop_down_lbl.bind('<Leave>', lambda _=None: [self.drop_down_lbl.config(fg='#000000'), self.drop_down_lbl.config(cursor='')])

        self.config(**frame_config)
        self.upper_frame.config(**themes[themes['current_theme']]['searchresultdropdownframe_upperframe'])
        self.name_and_id_frame.config(**themes[themes['current_theme']]['searchresultdropdownframe_nameandidframe'])
        self.bank_name_lbl.config(**themes[themes['current_theme']]['searchresultdropdownframe_banknamelbl'])
        self.ownership_lbl.config(**themes[themes['current_theme']]['searchresultdropdownframe_ownershiplbl'])
        self.drop_down_frame.config(**themes[themes['current_theme']]['searchresultdropdownframe_dropdownframe'])
        self.drop_down_lbl.config(**themes[themes['current_theme']]['searchresultdropdownframe_dropdownlbl'])
        self.perm_id_url_frame.config(**themes[themes['current_theme']]['searchresultdropdownframe_permidurlframe'])
        self.permidurl_lbl.config(**themes[themes['current_theme']]['searchresultdropdownframe_permidurl_lbl'])
        self.perm_id_url_lbl.config(**themes[themes['current_theme']]['searchresultdropdownframe_permidurllbl'])
        self.middle_frame.config(**themes[themes['current_theme']]['searchresultdropdownframe_middleframe'])
        self.perm_id_frame.config(**themes[themes['current_theme']]['searchresultdropdownframe_permidframe'])
        self.perm_id_lbl.config(**themes[themes['current_theme']]['searchresultdropdownframe_permidlbl'])
        self.perm_id_name_lbl.config(**themes[themes['current_theme']]['searchresultdropdownframe_permidnamelbl'])
        self.industry_frame.config(**themes[themes['current_theme']]['searchresultdropdownframe_industryframe'])
        self.industry_lbl.config(**themes[themes['current_theme']]['searchresultdropdownframe_industrylbl'])
        self.industry_name_lbl.config(**themes[themes['current_theme']]['searchresultdropdownframe_industrynamelbl'])
        self.country_frame.config(**themes[themes['current_theme']]['searchresultdropdownframe_countryframe'])
        self.country_lbl.config(**themes[themes['current_theme']]['searchresultdropdownframe_countrylbl'])
        self.country_name_lbl.config(**themes[themes['current_theme']]['searchresultdropdownframe_countrynamelbl'])
        self.key_frame.config(**themes[themes['current_theme']]['searchresultdropdownframe_keyframe'])
        self.key_lbl.config(**themes[themes['current_theme']]['searchresultdropdownframe_keylbl'])
        self.key_name_lbl.config(**themes[themes['current_theme']]['searchresultdropdownframe_keynamelbl'])
        self.lower_frame.config(**themes[themes['current_theme']]['searchresultdropdownframe_lowerframe'])
        self.edit_frame.config(**themes[themes['current_theme']]['searchresultdropdownframe_editframe'])
        self.edit_lbl.config(**themes[themes['current_theme']]['searchresultdropdownframe_editlbl'])
        self.confirm_frame.config(**themes[themes['current_theme']]['searchresultdropdownframe_confirmframe'])
        self.confirm_lbl.config(**themes[themes['current_theme']]['searchresultdropdownframe_confirmlbl'])

    def set_images(self):
        dimensions = (75, 81)
        self.perm_id_img = load_image('./images/permID.png', dimensions)
        self.industry_img = load_image('./images/industry.png', dimensions)
        self.country_img = load_image('./images/country.png', dimensions)
        self.key_img = load_image('./images/key.png', dimensions)


class TitlePageFrame(Frame):
    def __init__(self, master, root, **kw):
        Frame.__init__(self, master, **kw)
        self.master = master
        self.root = root

        self.title_frame = Frame(self, **frame_config)
        self.go_title_lbl = Label(self.title_frame, text='GO', font='Calibri 51 bold')
        self.green_title_lbl = Label(self.title_frame, text='GREEN', font='Calibri 51 bold')
        self.other_title_lbl = Label(self.title_frame, text='Connecting Data to the world', font='Cambria 21')

        self.search_frame = Frame(self, **frame_config)
        self.search_entry = PlaceHolderEntry(self.search_frame, placeholder=PLACEHOLDER, width=40,
                                             placeholdercolor='#b0b0b0' if themes['current_theme'] is DARK else '#7a7a7a',
                                             font=('Century Gothic', 13), relief=FLAT)
        self.search_btn = Button(self.search_frame, text='🔍', width=4, font=('Century Gothic', 10), relief=GROOVE, bd=0,
                                 bg='' if themes['current_theme'] is DARK else '#d1bb60',
                                 fg='' if themes['current_theme'] is DARK else 'white', command=self.search)
        self.search_btn.bind('<Return>', self.search)

    def refresh(self):
        self.config(**frame_config)
        self.title_frame.config(**themes[themes['current_theme']]['titlepageframe_titleframe'])
        self.go_title_lbl.config(**themes[themes['current_theme']]['titlepageframe_gotitlelbl'])
        self.green_title_lbl.config(**themes[themes['current_theme']]['titlepageframe_greentitlelbl'])
        self.other_title_lbl.config(**themes[themes['current_theme']]['titlepageframe_othertitlelbl'])
        self.search_frame.config(**themes[themes['current_theme']]['titlepageframe_searchframe'])
        self.search_entry.config(**themes[themes['current_theme']]['titlepageframe_searchentry'])
        self.search_btn.config(**themes[themes['current_theme']]['titlepageframe_searchbtn'])

    def search(self, event=None):
        """
        Method for searching inside database
        """
        example_data = [
            ['Qatar National Bank QPSC', 'QNBK | Company Publicly Held', 15486, 'Banking Services', 'Qatar', '879879',
             'https://permid.org/1-423255436'],
            ['London National Bank LPSC', 'LNBK | Company Publicly Held', 64189, 'Banking Services', 'Britain', 812383,
             'https://permid.org/6-377451629'],
            ['Paris National Bank PPSC', 'PNBK | Company Privately Held', 48237, 'Banking and Finance Services',
             'France', 442783, 'https://permid.org/7-352759846'],
            ['German National Bank GPSC', 'GNBK | Company Publicly Held', 78991, 'Catering and Restaurant Services',
             'Germany', 889921, 'https://permid.org/7-7481983123']]

        search_keyword = self.search_entry.get()
        if search_keyword in PLACEHOLDER:
            search_keyword = ''


        # # # # #    TO BE FILLED !!!    # # # # #


        search_results = example_data                     # list of lists containing all the stuff
        self.visible(False)
        self.root.search_results = search_results
        self.root.search_keyword = search_keyword
        self.root.show_frame(SearchResultsFrame)

    def visible(self, _bool: bool):
        if _bool:
            self.pack_all()
        else:
            self.unpack_all()

    def pack_all(self):
        self.root.remove_frame(self.root.current_visible_frame)
        self.title_frame.pack(side=TOP, anchor=CENTER, expand=TRUE, fill=Y, pady=130)
        self.go_title_lbl.grid(row=0, column=0)
        self.green_title_lbl.grid(row=0, column=1)
        self.other_title_lbl.grid(row=1, columnspan=2)
        self.search_frame.pack(side=TOP, anchor=CENTER, expand=TRUE)
        self.search_entry.pack(side=LEFT, fill=X, ipady=2)
        self.search_btn.pack(side=RIGHT, ipady=2)

    def unpack_all(self):
        self.title_frame.pack_forget()
        self.go_title_lbl.grid_forget()
        self.green_title_lbl.grid_forget()
        self.other_title_lbl.grid_forget()
        self.search_frame.pack_forget()
        self.search_entry.pack_forget()
        self.search_btn.pack_forget()


class SearchResultsFrame(Frame):
    def __init__(self, master, root, **kw):
        Frame.__init__(self, master, **kw)
        self.master = master
        self.root = root
        self.search_results = root.search_results
        self.search_keyword = root.search_keyword
        self._screen_height = _screen_height = self.winfo_screenheight()
        self._screen_width = _screen_width = self.winfo_screenwidth()
        self.search_result_frame_list = []
        self.pack_propagate(False)
        self.config(width=_screen_width, height=_screen_height-25)

        self.main_frame = Frame(self, width=_screen_width, height=25)
        self.main_frame.pack_propagate(False)
        self.search_results_title_frame = Frame(self.main_frame, width=_screen_width, height=25)
        self.search_results_title_frame.pack_propagate(False)
        self.search_results_title_lbl = Label(self.search_results_title_frame, anchor=W,
                                              text=f'Search Results for: {self.search_keyword}')

        self.search_results_frame = SmoothScrollFrame(self, width=_screen_width, height=_screen_height-100)
        self.search_results_widget_frame = self.search_results_frame.widget_frame

    def confirm(self, frame):
        bank_name, ownership, perm_id, industry, country, key, perm_id_url\
            = frame.bank_name, frame.ownership, frame.perm_id, frame.industry, frame.country, frame.key, frame.perm_id_url

        # # # # #       S E T    S C O R E S    H E R E     # # # # #
        self.root.selfscore = 0
        self.root.localpeerscore = 0
        self.root.globalpeerscore = 0

    def clear_search_results(self):
        for _frame in self.search_result_frame_list:
            _frame.pack_forget()
            del _frame

    def insert_search_results(self, results):
        self.search_keyword = self.root.search_keyword
        self.search_results_title_lbl.config(text=f'Search Results for: {self.search_keyword}')
        for bank_name, ownership, perm_id, industry, country, key, perm_id_url in self.search_results:
            # print(bank_name, ownership, perm_id, industry, country, key, perm_id_url)
            result_frame = SearchResultDropDownFrame(self.search_results_widget_frame, root=self,
                                                     parent_frame_list=self.search_result_frame_list,
                                                     bank_name=bank_name, ownership=ownership, perm_id=perm_id,
                                                     industry=industry, country=country, key=key, perm_id_url=perm_id_url,
                                                     width=self._screen_width-40, height=50)
            self.search_result_frame_list.append(result_frame)
            result_frame.pack(side=TOP, fill=BOTH, expand=TRUE, padx=5, pady=5, ipady=10)
            result_frame.pack_propagate(False)
            result_frame.pack_all()
            result_frame.refresh()

    def refresh(self):
        self.config(**frame_config)
        self.main_frame.config(**themes[themes['current_theme']]['searchresultsframe_mainframe'])
        self.search_results_title_frame.config(**themes[themes['current_theme']]['searchresultsframe_searchresultstitleframe'])
        self.search_results_title_lbl.config(**themes[themes['current_theme']]['searchresultsframe_searchresultstitlelbl'])
        self.search_results_frame.config(**themes[themes['current_theme']]['searchresultsframe_searchresultsframe'])
        self.search_results_widget_frame.config(**themes[themes['current_theme']]['searchresultsframe_searchresultswidgetframe'])
        self.search_results_frame.canvas.config(**themes[themes['current_theme']]['canvas'])
        for _frame in self.search_result_frame_list:
            _frame.config(**themes[themes['current_theme']]['searchresultdropdownframe'])
            _frame.refresh()
        self.search_results_frame.refresh()

    def pack_all(self):
        self.root.remove_frame(self.root.current_visible_frame)
        self.main_frame.pack(side=TOP, fill=BOTH, ipady=10)
        self.search_results_title_frame.pack(side=TOP, fill=BOTH, ipady=5)
        self.search_results_title_lbl.pack(side=LEFT, fill=BOTH, ipady=5)
        self.search_results_frame.pack(side=TOP, fill=BOTH, expand=TRUE)
        self.search_results = self.root.search_results
        self.clear_search_results()
        self.insert_search_results(self.search_results)

    def unpack_all(self):
        self.main_frame.pack_forget()
        self.search_results_frame.pack_forget()

    def visible(self, _bool: bool):
        if _bool:
            self.pack_all()
        else:
            self.unpack_all()


class BankESGLevelFrame(Frame):
    def __init__(self, master, root, **kw):
        Frame.__init__(self, master, **kw)
        self.master = master
        self.root = root
        self.slider_img, self.esgscoreslider_img, self.selfscore_img, self.localpeerscore_img, \
            self.globalpeerscore_img = [None] * 5
        self.slider_range = [151, 1098]
        self.enter_period = 1000   # time period for
        self.slider_height = 64
        self.set_images()

        self.aspirational_score_frame = Frame(self)
        self.aspirational_score_lbl = Label(self.aspirational_score_frame, text='Your Aspirational ESG Score', anchor=W)
        self.score_lbl = Label(self.aspirational_score_frame, text='0')

        self.slider_canvas = Canvas(self, width=root.screen_width, height=200)
        self.slider_canvas.update_idletasks()
        self.slider_canvas.create_image((self.root.screen_width-1004)//2, self.slider_height, anchor=NW, image=self.slider_img)
        self.canvas_slider_img = self.slider_canvas.create_image(
            ((self.root.screen_width-1004)//2)-30, self.slider_height + 17, image=self.esgscoreslider_img, anchor=NW
        )
        self.slider_canvas.bind('<B1-Motion>', self.move_slider)
        # self.slider_canvas.bind('<Enter>', )

    def calculate_esgscore(self, x_coord):
        upper = self.slider_range[1]
        lower = self.slider_range[0]
        cent = upper - lower
        current_score = 100 - ((upper - x_coord) / cent) * 100
        self.score_lbl.config(text=f"{current_score}")

    def move_slider(self, event):
        if event.x_root < ((self.root.screen_width-1004)//2) + 62:
            x_coord = ((self.root.screen_width-1004)//2) + 62 - 92
        elif event.x_root > (((self.root.screen_width-1004)//2) + 1004) + 5:
            x_coord = (((self.root.screen_width-1004)//2) + 1004) + 5 - 92
        else:
            x_coord = event.x_root - 92
        self.calculate_esgscore(x_coord)
        self.esgscoreslider_img = load_image('./images/ESGscoreslider.png', dimensions=(120, 85))
        self.canvas_slider_img = self.slider_canvas.create_image(x_coord, self.slider_height + 17, anchor=NW,
                                                                 image=self.esgscoreslider_img)

    def refresh(self):
        self.config(**themes[themes['current_theme']]['bankesglevelframe'])
        self.aspirational_score_frame.config(**themes[themes['current_theme']]['bankesglevelframe_aspirationalscoreframe'])
        self.aspirational_score_lbl.config(**themes[themes['current_theme']]['bankesglevelframe_aspirationallbl'])
        self.score_lbl.config(**themes[themes['current_theme']]['bankesglevelframe_scorelbl'])
        self.slider_canvas.config(**themes[themes['current_theme']]['bankesglevelframe_slidercanvas'])

    def pack_all(self):
        self.root.remove_frame(self.root.current_visible_frame)
        self.aspirational_score_frame.pack(side=TOP, fill=BOTH, expand=TRUE)
        self.aspirational_score_lbl.pack(side=TOP, fill=BOTH, expand=TRUE, anchor=W)
        self.score_lbl.pack(side=TOP, fill=BOTH, expand=TRUE)
        self.slider_canvas.pack(side=TOP, expand=TRUE, fill=BOTH)
        self.set_globalpeerscore()
        self.set_localpeerscore()
        self.set_selfscore()

    def unpack_all(self):
        self.aspirational_score_frame.pack_forget()
        self.slider_canvas.pack_forget()
        self.aspirational_score_lbl.pack_forget()
        self.score_lbl.pack_forget()
        self.slider_canvas.pack_forget()

    def set_selfscore(self):
        upper = self.slider_range[1]
        lower = self.slider_range[0]
        cent = upper - lower
        x_coord = int(((cent * (self.root.selfscore - 100)) / 100) + upper)
        self.selfscore_img = load_image('images/SelfScore.png', dimensions=(130, 85))
        self.slider_canvas.create_image(x_coord, self.slider_height - 68, anchor=NW, image=self.selfscore_img)
        self.slider_canvas.create_text(x_coord + 20, self.slider_height - 40, font=('Century Gothic', 18, 'bold'),
                                       text=str(int(self.root.selfscore)), fill='white')

    def set_localpeerscore(self):
        upper = self.slider_range[1]
        lower = self.slider_range[0]
        cent = upper - lower
        x_coord = int(((cent*(self.root.localpeerscore - 100)) / 100) + upper)
        self.localpeerscore_img = load_image('./images/LocalPeerScore.png', dimensions=(130, 85))
        self.slider_canvas.create_image(x_coord, self.slider_height - 68, anchor=NW, image=self.localpeerscore_img)
        self.slider_canvas.create_text(x_coord + 20, self.slider_height - 40, font=('Century Gothic', 18, 'bold'),
                                       text=str(int(self.root.localpeerscore)), fill='white')

    def set_globalpeerscore(self):
        upper = self.slider_range[1]
        lower = self.slider_range[0]
        cent = upper - lower
        x_coord = int(((cent * (self.root.globalpeerscore - 100)) / 100) + upper)
        self.globalpeerscore_img = load_image('./images/GlobalPeerScore.png', dimensions=(130, 85))
        self.slider_canvas.create_image(x_coord, self.slider_height - 68, anchor=NW, image=self.globalpeerscore_img)
        self.slider_canvas.create_text(x_coord + 20, self.slider_height - 40, font=('Century Gothic', 18, 'bold'),
                                       text=str(int(self.root.globalpeerscore)), fill='white')

    def set_images(self):
        dimensions = (120, 85)
        self.esgscoreslider_img = load_image('./images/ESGscoreslider.png', dimensions=dimensions)
        self.selfscore_img = load_image('images/SelfScore.png', dimensions=dimensions)
        self.localpeerscore_img = load_image('./images/LocalPeerScore.png', dimensions=dimensions)
        self.globalpeerscore_img = load_image('./images/GlobalPeerScore.png', dimensions=dimensions)
        self.slider_img = load_image('./images/Slider.png', (1004, 59))

    def visible(self, _bool: bool):
        if _bool:
            self.pack_all()
        else:
            self.unpack_all()


class LastPageFrame(Frame):
    def __init__(self, master, root, **kw):
        Frame.__init__(self, master, **kw)

    def refresh(self):
        self.config(**frame_config)

    def pack_all(self):
        pass

    def unpack_all(self):
        pass

    def visible(self, _bool: bool):
        if _bool:
            self.pack_all()
        else:
            self.unpack_all()


class App(Tk):
    def __init__(self):
        Tk.__init__(self)
        self.screen_width = _screen_width = self.winfo_screenwidth()
        self.screen_height = _screen_height = self.winfo_screenheight()
        self.available_frames = [TitlePageFrame, SearchResultsFrame, BankESGLevelFrame, LastPageFrame]
        self.frame_list = []
        self.light_mode_img = None
        self.dark_mode_img = None
        # self.title_page_img = None
        # self.search_results_img = None
        # self.bank_esg_level_img = None
        self.frames = {}
        self.current_visible_frame = None
        self.search_results = []
        self.search_keyword = ''
        self.selfscore = 22
        self.localpeerscore = 35
        self.globalpeerscore = 75

        self.set_images()

        # ------------- LEFT FRAME ------------- #
        self.left_frame = Frame(self, width=25, bg=str('#454545' if themes['current_theme'] is DARK else '#bababa'))
        self.left_frame.pack_propagate(False)
        if themes['current_theme'] == DARK:
            self.theme_btn = Button(self.left_frame, image=self.light_mode_img, compound=LEFT, bd=0, command=self.config_theme)
            self.cur_frame = Frame(self.left_frame, bg='#454545')
            self.active_frame_lbl1 = Label(self.cur_frame, text='○', bg='#454545', fg='#b56a45', font=font)
            self.active_frame_lbl2 = Label(self.cur_frame, text='○', bg='#454545', fg='#b56a45', font=font)
            self.active_frame_lbl3 = Label(self.cur_frame, text='○', bg='#454545', fg='#b56a45', font=font)
            self.active_frame_lbl4 = Label(self.cur_frame, text='○', bg='#454545', fg='#b56a45', font=font)
        else:
            self.theme_btn = Button(self.left_frame, image=self.dark_mode_img, compound=LEFT, bd=0, command=self.config_theme)
            self.cur_frame = Frame(self.left_frame, bg='#bababa')
            self.active_frame_lbl1 = Label(self.cur_frame, text='○', bg='#bababa', fg='#ff9e6e', font=font)
            self.active_frame_lbl2 = Label(self.cur_frame, text='○', bg='#bababa', fg='#ff9e6e', font=font)
            self.active_frame_lbl3 = Label(self.cur_frame, text='○', bg='#bababa', fg='#ff9e6e', font=font)
            self.active_frame_lbl4 = Label(self.cur_frame, text='○', bg='#bababa', fg='#ff9e6e', font=font)
        self.active_frame_lbl1.bind('<Enter>', lambda _=None: self.active_frame_lbl1.config(cursor='hand2'))
        self.active_frame_lbl2.bind('<Enter>', lambda _=None: self.active_frame_lbl2.config(cursor='hand2'))
        self.active_frame_lbl3.bind('<Enter>', lambda _=None: self.active_frame_lbl3.config(cursor='hand2'))
        self.active_frame_lbl4.bind('<Enter>', lambda _=None: self.active_frame_lbl4.config(cursor='hand2'))
        self.active_frame_lbl1.bind('<Leave>', lambda _=None: self.active_frame_lbl1.config(cursor=''))
        self.active_frame_lbl2.bind('<Leave>', lambda _=None: self.active_frame_lbl2.config(cursor=''))
        self.active_frame_lbl3.bind('<Leave>', lambda _=None: self.active_frame_lbl3.config(cursor=''))
        self.active_frame_lbl4.bind('<Leave>', lambda _=None: self.active_frame_lbl4.config(cursor=''))
        self.active_frame_lbl1.bind('<ButtonRelease-1>', lambda _=None: [self.show_frame(TitlePageFrame), self.change_active_frame(1)])
        self.active_frame_lbl2.bind('<ButtonRelease-1>', lambda _=None: [self.show_frame(SearchResultsFrame), self.change_active_frame(2)])
        self.active_frame_lbl3.bind('<ButtonRelease-1>', lambda _=None: [self.show_frame(BankESGLevelFrame), self.change_active_frame(3)])
        self.active_frame_lbl4.bind('<ButtonRelease-1>', lambda _=None: [self.show_frame(LastPageFrame), self.change_active_frame(4)])

        # ------------- RIGHT FRAME ------------- #
        self.right_frame = Frame(self, **frame_config)
        self.container_frame = Frame(self.right_frame, width=_screen_width-100, **frame_config)
        # self.container_frame.pack_propagate(False)

        for f in self.available_frames:
            frame = f(self.container_frame, self, **frame_config, width=self.container_frame['width'],
                      height=self.container_frame['height'])
            self.frames[f] = frame
            frame.grid(row=1, column=0, sticky=N)
            # frame.pack_propagate(False)
            self.frame_list.append(frame)

        # ------------- PACKING WIDGETS ------------- #
        self.left_frame.pack(side=LEFT, fill=BOTH)
        self.right_frame.pack(side=RIGHT, fill=BOTH, expand=TRUE)
        self.container_frame.pack(side=TOP, expand=TRUE, fill=BOTH)
        self.theme_btn.pack(side=BOTTOM)
        self.cur_frame.pack(side=TOP)
        self.active_frame_lbl1.pack(side=TOP, pady=4)
        self.active_frame_lbl2.pack(side=TOP, pady=4)
        self.active_frame_lbl3.pack(side=TOP, pady=4)
        self.active_frame_lbl4.pack(side=TOP, pady=4)

        self.show_frame(TitlePageFrame)
        self.current_visible_frame = TitlePageFrame
        self.change_active_frame(1)

    def change_active_frame(self, frame):
        if frame == 1:
            self.active_frame_lbl1.config(text='⬤')
            self.active_frame_lbl2.config(text='○')
            self.active_frame_lbl3.config(text='○')
            self.active_frame_lbl4.config(text='○')
        elif frame == 2:
            self.active_frame_lbl1.config(text='○')
            self.active_frame_lbl2.config(text='⬤')
            self.active_frame_lbl3.config(text='○')
            self.active_frame_lbl4.config(text='○')
        elif frame == 3:
            self.active_frame_lbl1.config(text='○')
            self.active_frame_lbl2.config(text='○')
            self.active_frame_lbl3.config(text='⬤')
            self.active_frame_lbl4.config(text='○')
        else:
            self.active_frame_lbl1.config(text='○')
            self.active_frame_lbl2.config(text='○')
            self.active_frame_lbl3.config(text='○')
            self.active_frame_lbl4.config(text='⬤')

    def config_theme(self):
        if themes['current_theme'] == LIGHT:
            self.theme_btn.config(image=self.light_mode_img)
            themes['current_theme'] = DARK
            update_themes(_app=self)
        else:
            self.theme_btn.config(image=self.dark_mode_img)
            themes['current_theme'] = LIGHT
            update_themes(_app=self)

    def refresh(self):
        self.config(**frame_config)
        self.container_frame.config(**frame_config)
        self.right_frame.config(**frame_config)
        for frame in self.frame_list:
            frame.refresh()
        if themes['current_theme'] == DARK:
            self.left_frame.config(bg='#454545')
            self.cur_frame.config(bg='#454545')
            self.active_frame_lbl1.config(bg='#454545', fg='#ff9e6e')
            self.active_frame_lbl2.config(bg='#454545', fg='#ff9e6e')
            self.active_frame_lbl3.config(bg='#454545', fg='#ff9e6e')
            self.active_frame_lbl4.config(bg='#454545', fg='#ff9e6e')
        else:
            self.left_frame.config(bg='#bababa')
            self.cur_frame.config(bg='#bababa')
            self.active_frame_lbl1.config(bg='#bababa', fg='#b56a45')
            self.active_frame_lbl2.config(bg='#bababa', fg='#b56a45')
            self.active_frame_lbl3.config(bg='#bababa', fg='#b56a45')
            self.active_frame_lbl4.config(bg='#bababa', fg='#b56a45')

    def remove_frame(self, context):
        """
        Removes unwanted frames from background
        :param context: name of frame
        """
        if context is None:
            return
        frame = self.frames[context]
        frame.forget()
        frame.visible(False)
        self.update_idletasks()

    def set_images(self):
        theme_img_dimensions = (24, 24)
        self.light_mode_img = load_image('./images/light_mode_btn_icon.png', theme_img_dimensions)
        self.dark_mode_img = load_image('./images/dark_mode_btn_icon.png', theme_img_dimensions)

        page_img_dimensions = (512, 512)

        # self.title_page_dark_img = load_image('./images/title_page.png', page_img_dimensions)
        # self.title_page_light_img = load_image('./images/title_page.png', page_img_dimensions)

        # self.search_results_dark_img = load_image('./images/search_results_page.png', page_img_dimensions)
        # self.search_results_light_img = load_image('./images/search_results_page.png', page_img_dimensions)

        # self.bank_esg_level_dark_img = load_image('./images/bank_esg_level_page.png', page_img_dimensions)
        # self.bank_esg_level_light_img = load_image('./images/bank_esg_level_page.png', page_img_dimensions)

    def show_frame(self, context):
        """
        Shows next required frame or page
        :param context: name of frame
        """
        if context is None:
            return
        frame = self.frames[context]
        frame.tkraise()
        frame.visible(True)
        self.update_idletasks()
        self.current_visible_frame = context
        if context == TitlePageFrame:
            self.change_active_frame(1)
        elif context == SearchResultsFrame:
            self.change_active_frame(2)
        elif context == BankESGLevelFrame:
            self.change_active_frame(3)
        elif context == LastPageFrame:
            self.change_active_frame(4)


if __name__ == '__main__':
    app = App()
    screen_height = app.winfo_screenheight()
    screen_width = app.winfo_screenwidth()
    # app.geometry(f"{screen_width-50}x{screen_height-100}+{screen_width//100}+{screen_height//100}")
    app.minsize(1296, 648)
    app.wm_state('zoomed')
    app.title('APP TITLE')
    update_themes(_app=app)
    app.mainloop()
