import tkinter, tkinter.filedialog
from tkinter import *
from tkinter import PhotoImage

import threading
import os
import sys

from Sankaku import Sankaku
import Settings

def resource_path(relative_path):    
    if(hasattr(sys, "_MEIPASS")):
        base_path = getattr(sys, "_MEIPASS")
    else:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

class MainWindow(Tk):
    #string vars
    downloadFolderString = None

    #region Controls
    queryEntry = None
    browseButton = None
    downloadButton = None
    logTextArea = None
    #endregion

    def __init__(self):
        super(MainWindow,self).__init__()
        self.title("Sankaku Downloader")
        self.geometry('350x200')
        self.update()
        self.minsize(self.winfo_width(), self.winfo_height())

        #region icon
        datafile = os.path.join("resources", "icon." + ("ico" if os.name == "Windows" else "png"))
        if not hasattr(sys, "frozen"):
            datafile = os.path.join(os.path.dirname(__file__), datafile)
        else:
            datafile = os.path.join(sys.prefix, datafile)
        #endregion

        img = PhotoImage(file=resource_path(datafile))
        self.tk.call('wm', 'iconphoto', self._w, img)

        #region Panel Input
        gridpadding = 2
        parent = Frame(self,padx=10,pady=6)
        parent.pack(fill="x")
        parent.grid_columnconfigure(1, weight=1)
        
        #region Query
        temp = Label(parent,text="Query:")
        temp.grid(row=0,column=0,sticky="w",padx=gridpadding)

        self.queryEntry = Entry(parent)
        self.queryEntry.grid(row=0,column=1,sticky='we',padx=gridpadding, columnspan=2)
        #endregion
        
        #region Download Folder
        temp = Label(parent,text="Download Folder:")
        temp.grid(row=1,column=0,sticky="w",padx=gridpadding)

        self.downloadFolderString = StringVar(self);
        self.downloadFolderEntry = Entry(parent, textvariable=self.downloadFolderString)
        self.downloadFolderEntry.grid(row=1,column=1,sticky='we',padx=gridpadding)

        self.browseButton = Button(parent, text="Select",command = self.browseButton_Click)
        self.browseButton.grid(row=1,column=2,sticky='e',padx=gridpadding)
        #endregion

        #region Download Button
        self.downloadButton = Button(parent)
        self.downloadButton.configure(text="Download",command = self.downloadButton_Click)
        self.downloadButton.grid(row=2, column = 0,sticky="w",padx=gridpadding)
        #endregion
        #endregion
        
        self.logTextArea = Text(self)
        self.logTextArea.pack(expand=YES, fill=BOTH)

        #start window
        self.mainloop()
    
    def downloadButton_Click(self):
        task = Sankaku(self.queryEntry.get(), self.downloadFolderEntry.get(), self.output)
        threading.Thread(target = task.download).start()

    def browseButton_Click(self):
        directory = tkinter.filedialog.askdirectory(parent=self,title="Choose Download Folder")
        if directory != "":
            self.downloadFolderString.set(directory)      

    def output(self, string):
        self.logTextArea.insert(END, string+"\r\n")
        self.logTextArea.see(END)

if __name__ == '__main__':
    MainWindow()
