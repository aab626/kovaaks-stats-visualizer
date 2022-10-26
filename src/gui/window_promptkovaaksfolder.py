import os

import tkinter as tk
from tkinter import ttk
from tkinter import filedialog

from models.config import Config, PATHKEY_KOVAAKS_FOLDER
from gui.messagebox import KSVMessageBox

KOVAAKS_EXECUTABLE_FNAME = 'FPSAimTrainer.exe'

# small window, functions as a prompt for the kovaaks folder
class BrowseKovaaksFolder(tk.Tk):
    def __init__(self, cfg: Config, icon_error_path):
        super().__init__()

        self.cfg = cfg
        self.icon_error_path = icon_error_path
        
        self.title('Browse Kovaak\'s Folder')
        self.grab_set()
        
        self.var_kovaaks_path = None
        self.create_widgets()

    def create_widgets(self):
        content = ttk.Frame(self)
        content.grid(row=0, column=0, sticky='news', pady=(5, 5), padx=(5, 5))
        content.columnconfigure((0,2), weight=0)
        content.columnconfigure(1, weight=1, minsize=500)
        content.rowconfigure((0, 1), weight=0)

        text_content = 'Enter your KovaaK\'s folder.\nCommonly found in the Steam\\steamapps\\common\\FPSAimTrainer directory.'
        text_label = ttk.Label(content, text=text_content)
        text_label.grid(row=0, column=0, columnspan=3, sticky='nw', padx=(5, 5), pady=(0, 10))

        browse_button = ttk.Button(content, text='Browse Folder', command=self.command_select_kovaaks_folder)
        browse_button.grid(row=1, column=0, sticky='w')

        self.var_kovaaks_path = tk.StringVar(master=content, value=self.cfg.get_path(PATHKEY_KOVAAKS_FOLDER))
        folder_entry = ttk.Entry(content, textvariable=self.var_kovaaks_path)
        folder_entry.grid(row=1, column=1, sticky='nswe', padx=(5, 5))

        continue_button = ttk.Button(content, text='Continue', command=self.command_continue)
        continue_button.grid(row=1, column=2, sticky='e')

    # methods
    def confirm_kovaaks_path(self):
        executable_path = os.path.join(self.var_kovaaks_path.get(), KOVAAKS_EXECUTABLE_FNAME)
        return os.path.isfile(executable_path)

    # commands
    def command_select_kovaaks_folder(self, *args):
        directory = filedialog.askdirectory()
        kovaaks_path = os.path.normpath(directory)
        self.var_kovaaks_path.set(kovaaks_path)
        
    def command_continue(self, *args):
        if self.confirm_kovaaks_path():
            self.cfg.set_path(PATHKEY_KOVAAKS_FOLDER, self.var_kovaaks_path.get())
            self.destroy()
        else:
            KSVMessageBox(
                parent    = self,
                title     = 'Error!',
                message   = 'Error!\nSelect the correct KovaaK\'s folder, it has the FPSAimTrainer executable in it.',
                icon_path = self.icon_error_path
                )
