from tkinter import *
from tkinter import messagebox as tk_mb
import os
import importlib
import sys
import webbrowser
import json
from PIL import Image, ImageTk

LIGHT = 'Light'
DARK = 'Dark'

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


def install_necessary_modules(*modnames) -> None:
    """
    Function to install and import modules
    """
    for modname in modnames:
        try:
            # If module is already installed, try to import it
            importlib.import_module(modname)
            print(f"Importing {modname}")
        except ImportError:

            # Error if module is not installed
            if os.system('PIP --version') == 0:
                # No error from running PIP in the Command Window, therefore PIP.exe is in the %PATH%
                os.system(f'PIP install {modname}')

            else:
                # Error, PIP.exe is NOT in the Path!!
                pip_location_attempt_1 = sys.executable.replace("python.exe", "") + "pip.exe"
                pip_location_attempt_2 = sys.executable.replace("python.exe", "") + "scripts/pip.exe"

                if os.path.exists(pip_location_attempt_1):
                    # The Attempt #1 File exists!!!
                    os.system(pip_location_attempt_1 + " install " + modname)

                elif os.path.exists(pip_location_attempt_2):
                    # The Attempt #2 File exists!!!
                    os.system(pip_location_attempt_2 + " install " + modname)

                else:
                    # Neither Attempts found the PIP.exe file, So Fail...
                    print('Fatal error: Can\'t find PIP.exe')
        else:
            tk_mb.showerror('Installation Error!', f"Can't install {modname}")
            continue


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

    def put_placeholder(self):
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
    def __init__(self, master: str, bank_name: str, ownership: str, perm_id: int or str,
                 industry: str, country: str, key: int or str, perm_id_url='Link not available',
                 **kw):
        Frame.__init__(self, master, **kw)
        self.bank_name, self.ownership, self.perm_id, self.industry, self.country, self.key, \
            self.perm_id_url = bank_name, ownership, perm_id, industry, country, key, perm_id_url
        self.perm_id_img, self.industry_img, self.country_img, self.key_img = [None] * 4
        self.dropped_down = False
        # self.set_images()

        # ------------ UPPER FRAME ------------ #
        self.upper_frame = Frame(self)
        self.name_and_id_frame = Frame(self.upper_frame)
        self.bank_name_lbl = Label(self.name_and_id_frame, text=self.bank_name, anchor=W)
        self.ownership_lbl = Label(self.name_and_id_frame, text=self.ownership, anchor=W)

        self.drop_down_frame = Frame(self.upper_frame)
        self.drop_down_lbl = Label(self.drop_down_frame, text='⤵', anchor=CENTER, width=7)
        self.drop_down_lbl.bind('<ButtonRelease-1>', self.drop_down)

        self.perm_id_url_frame = Frame(self.upper_frame)
        self.permidurl_lbl = Label(self.perm_id_url_frame, text='🔗 PermID URL', anchor=SE)
        self.perm_id_url_lbl = Label(self.perm_id_url_frame, text=self.perm_id_url, anchor=SE)
        self.perm_id_url_lbl.bind('<Enter>', lambda _=None: self.perm_id_url_lbl.config(cursor='hand2', font="Calibri 12 underline"))
        self.perm_id_url_lbl.bind('<Leave>', lambda _=None: self.perm_id_url_lbl.config(cursor='', font="Calibri 12"))
        self.perm_id_url_lbl.bind('<ButtonRelease-1>', self.open_url)

        # ------------ MIDDLE FRAME ------------ #
        self.middle_frame = Frame(self)

        self.perm_id_frame = Frame(self.middle_frame)
        self.perm_id_lbl = Label(self.perm_id_frame, text='PERM ID', width=30, height=5, anchor=S)  # image=self.perm_id_img)
        self.perm_id_name_lbl = Label(self.perm_id_frame, text=str(self.perm_id), width=30)

        self.industry_frame = Frame(self.middle_frame)
        self.industry_lbl = Label(self.industry_frame, text='Industry', width=30, height=5, anchor=S)  # image=self.industry_img)
        self.industry_name_lbl = Label(self.industry_frame, text=self.industry, width=30)

        self.country_frame = Frame(self.middle_frame)
        self.country_lbl = Label(self.country_frame, text='Country', width=30, height=5, anchor=S)  # image=self.country_img)
        self.country_name_lbl = Label(self.country_frame, text=self.country, width=30)

        self.key_frame = Frame(self.middle_frame)
        self.key_lbl = Label(self.key_frame, text='Key', width=30, height=5, anchor=S)  # image=self.key_img)
        self.key_name_lbl = Label(self.key_frame, text=str(self.key), width=30)

        # ------------ LOWER FRAME ------------ #
        self.lower_frame = Frame(self)

        self.edit_frame = Frame(self.lower_frame)
        self.edit_lbl = Label(self.edit_frame, text='✎ Edit')
        self.edit_lbl.bind('<Enter>', lambda _=None: self.edit_lbl.config(cursor='hand2', font='Cambria 13 underline'))
        self.edit_lbl.bind('<Leave>', lambda _=None: self.edit_lbl.config(cursor='', font='Cambria 13'))

        self.confirm_frame = Frame(self.lower_frame)
        self.confirm_lbl = Label(self.confirm_frame, text=f'{chr(10004)}Confirm')
        self.confirm_lbl.bind('<Enter>', lambda _=None: self.confirm_lbl.config(cursor='hand2', font='Cambria 13 underline'))
        self.confirm_lbl.bind('<Leave>', lambda _=None: self.confirm_lbl.config(cursor='', font='Cambria 13'))

        self.refresh()

    def drop_down(self, event=None):
        if self.dropped_down:
            self.drop_down_lbl.config(text='⤵')
            self.dropped_down = False
            self.unpack_dropdown_frames()
            self.configure(height=50)
        else:
            self.drop_down_lbl.config(text='⤶')
            self.dropped_down = True
            self.pack_dropdown_frames()
            self.configure(height=250)
        self.master.master.master.refresh()

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
        self.permidurl_lbl.pack(side=TOP, anchor=NE)
        self.perm_id_url_lbl.pack(side=TOP, anchor=SE)
        if self.dropped_down:
            self.pack_dropdown_frames()

    def pack_dropdown_frames(self):
        self.middle_frame.pack(side=TOP, fill=X, expand=TRUE)
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
            self.config(**frame_config)
            self.upper_frame.config(**themes[themes['current_theme']]['searchresultdropdownframe_upperframe'])
            self.name_and_id_frame.config(**themes[themes['current_theme']]['searchresultdropdownframe_nameandidframe'])
            self.bank_name_lbl.config(**themes[themes['current_theme']]['searchresultdropdownframe_banknamelbl'])
            self.ownership_lbl.config(**themes[themes['current_theme']]['searchresultdropdownframe_ownershiplbl'])
            self.drop_down_frame.config(**themes[themes['current_theme']]['searchresultdropdownframe_dropdownframe'])
            self.drop_down_lbl.config(**themes[themes['current_theme']]['searchresultdropdownframe_dropdownlbl'])
            self.drop_down_lbl.bind('<Enter>', lambda _=None: [self.drop_down_lbl.config(fg='#55dd5d'), self.drop_down_lbl.config(cursor='hand2')])
            self.drop_down_lbl.bind('<Leave>', lambda _=None: [self.drop_down_lbl.config(fg='#00a30b'), self.drop_down_lbl.config(cursor='')])
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
        else:
            self.config(**frame_config)
            self.upper_frame.config(**themes[themes['current_theme']]['searchresultdropdownframe_upperframe'])
            self.name_and_id_frame.config(**themes[themes['current_theme']]['searchresultdropdownframe_nameandidframe'])
            self.bank_name_lbl.config(**themes[themes['current_theme']]['searchresultdropdownframe_banknamelbl'])
            self.ownership_lbl.config(**themes[themes['current_theme']]['searchresultdropdownframe_ownershiplbl'])
            self.drop_down_frame.config(**themes[themes['current_theme']]['searchresultdropdownframe_dropdownframe'])
            self.drop_down_lbl.config(**themes[themes['current_theme']]['searchresultdropdownframe_dropdownlbl'])
            self.drop_down_lbl.bind('<Enter>', lambda _=None: [self.drop_down_lbl.config(fg='#069943'), self.drop_down_lbl.config(cursor='hand2')])
            self.drop_down_lbl.bind('<Leave>', lambda _=None: [self.drop_down_lbl.config(fg='#058567'), self.drop_down_lbl.config(cursor='')])
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
        dimensions = (64, 64)
        try:
            self.perm_id_img = load_image('./images/perm_id.png', dimensions)
            self.industry_img = load_image('./images/industry.png', dimensions)
            self.country_img = load_image('./images/country.png', dimensions)
            self.key_img = load_image('./images/key.png', dimensions)
        except:
            self.perm_id_img, self.industry_img, self.country_img, self.key_img = [None] * 4


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
        self.search_entry = PlaceHolderEntry(self.search_frame, placeholder='Search by Name, Ticker or RIC', width=40,
                                             placeholdercolor='#b0b0b0' if themes['current_theme'] is DARK else '#7a7a7a',
                                             font=('Century Gothic', 13), relief=FLAT)
        self.search_btn = Button(self.search_frame, text='🔍', width=4, font=('Century Gothic', 10), relief=GROOVE, bd=0,
                                 bg='' if themes['current_theme'] is DARK else '#d1bb60',
                                 fg='' if themes['current_theme'] is DARK else 'white', command=self.search)
        self.search_btn.bind('<Return>', self.search)

    def refresh(self):
        if themes['current_theme'] == DARK:
            self.config(**frame_config)
            self.title_frame.config(**themes[themes['current_theme']]['titlepageframe_titleframe'])
            self.go_title_lbl.config(**themes[themes['current_theme']]['titlepageframe_gotitlelbl'])
            self.green_title_lbl.config(**themes[themes['current_theme']]['titlepageframe_greentitlelbl'])
            self.other_title_lbl.config(**themes[themes['current_theme']]['titlepageframe_othertitlelbl'])
            self.search_frame.config(**themes[themes['current_theme']]['titlepageframe_searchframe'])
            self.search_entry.config(**themes[themes['current_theme']]['titlepageframe_searchentry'])
            self.search_btn.config(**themes[themes['current_theme']]['titlepageframe_searchbtn'])
        else:
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
            ['Qatar National Bank QPSC', 'QNBK | Company Publicly Held', 15486, 'Banking Services', 'Qatar', '879879', 'https://permid.org/1-423255436'],
            ['London National Bank LPSC', 'LNBK | Company Publicly Held', 64189, 'Banking Services', 'Britain', 812383, 'https://permid.org/6-377451629'],
            ['Paris National Bank PPSC', 'PNBK | Company Privately Held', 48237, 'Banking and Finance Services', 'France', 442783, 'https://permid.org/7-352759846']
        ]
        search_keyword = self.search_entry.get()


        # # # # #    TO BE FILLED !!!    # # # # #


        search_results = example_data  # list of lists containing all the stuff
        self.visible(False)
        self.root.search_results = search_results
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
        self.searched_keyword = root.searched_keyword
        self._screen_height = _screen_height = self.winfo_screenheight()
        self._screen_width = _screen_width = self.winfo_screenwidth()
        self.search_result_frame_list = []
        self.pack_propagate(False)
        self.config(width=_screen_width-25, height=_screen_height-25)

        self.main_frame = Frame(self, width=_screen_width-25, height=25)
        self.main_frame.pack_propagate(False)
        self.search_results_title_frame = Frame(self.main_frame, width=_screen_width-25, height=25)
        self.search_results_title_frame.pack_propagate(False)
        self.search_results_title_lbl = Label(self.search_results_title_frame, anchor=W,
                                              text=f'Search Results for: {self.searched_keyword}')

        self.search_results_frame = SmoothScrollFrame(self, width=_screen_width, height=_screen_height-100)
        self.search_results_widget_frame = self.search_results_frame.widget_frame

    def clear_search_results(self):
        for _frame in self.search_result_frame_list:
            _frame.pack_forget()
            del _frame

    def insert_search_results(self, results):
        for bank_name, ownership, perm_id, industry, country, key, perm_id_url in self.search_results:
            # print(bank_name, ownership, perm_id, industry, country, key, perm_id_url)
            result_frame = SearchResultDropDownFrame(self.search_results_widget_frame, bank_name=bank_name,
                                                     ownership=ownership, perm_id=perm_id, industry=industry,
                                                     country=country, key=key, perm_id_url=perm_id_url,
                                                     width=self._screen_width-100, height=50)
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
        _screen_width = self.winfo_screenwidth()
        self.available_frames = [TitlePageFrame, SearchResultsFrame, BankESGLevelFrame, LastPageFrame]
        self.frame_list = []
        self.light_mode_img = None
        self.dark_mode_img = None
        self.title_page_img = None
        self.search_results_img = None
        self.bank_esg_level_img = None
        self.frames = {}
        self.current_visible_frame = None
        self.search_results = []
        self.searched_keyword = ''

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
    app.geometry(f"{screen_width-50}x{screen_height-100}+{screen_width//100}+{screen_height//100}")
    app.minsize(1296, 648)
    app.title('APP TITLE')
    update_themes(_app=app)
    app.mainloop()
