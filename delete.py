# from tkinter import *
#
# root = Tk()
#
# lbl = Label(root, text='aloopakoda', font=('Consolas', 11, 'bold'))
# lbl.pack()
# print(type(lbl['font']))
# root.mainloop()






















# lis = [[1, 2, 3, 4, 5], [0, 9, 8, 7, 6], [2, 7, 3, 8, 1], [9, 4, 3, 7, 6]]
# for a, b, c, d, e in lis:
#     print(a, b, c, d, e)





































from tkinter import *
from PIL import Image, ImageTk


class Example(Frame):
    def __init__(self, parent):
        Frame.__init__(self, parent)
        self.parent = parent
        self.initUI()

    def initUI(self):
        self.parent.title("Layout Test")
        self.config(bg='#F0F0F0')
        self.pack(fill=BOTH, expand=1)
        # create canvas
        canvas1 = Canvas(self, relief=FLAT, background="#D2D2D2", width=1080, height=800, bd=5)
        canvas1.pack(side=TOP, anchor=NW, padx=10, pady=10)
        # add quit button
        button1 = Button(canvas1, text="Quit", command=self.quit, anchor=W)
        button1.configure(width=10, activebackground="#33B5E5", relief=FLAT)
        button1.pack(side=TOP)
        self.update_idletasks()
        img = ImageTk.PhotoImage(Image.open('./images/dark_mode_btn_icon.png'))
        canvas1.create_image(2, 2, image=img, anchor=NW)


def main():
    # root = Tk()
    # root.geometry('800x600+10+50')
    # app = Example(root)
    # app.mainloop()
    root = Tk()
    frm = Label(root, bg='grey')
    lbl = Label(frm, text='LAL MAN Y u so NOB', font='Consolas 13', padx=15, pady=10, relief=SUNKEN)
    lbl.pack(padx=(0, 1), pady=(0, 1))
    frm.pack()
    canvas = Canvas(root, width=1366, height=768)
    canvas.pack()
    img = ImageTk.PhotoImage(Image.open(r".\images\dark_mode_btn_icon.png"))
    canvas.create_image(20, 20, anchor=NW, image=img)
    canvas.create_window(25, 25, anchor=NW, window=Label(canvas, text='This is on the image', bg='black', fg='white'))
    root.mainloop()


if __name__ == '__main__':
    main()
