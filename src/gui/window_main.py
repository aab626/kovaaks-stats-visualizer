import os
import webbrowser

import tkinter as tk
from tkinter import ttk

from PIL import ImageTk

from models.playlist import Playlist
from models.playlist import PLAYLIST_SOURCE_LOCAL, PLAYLIST_SOURCE_KOVAAKS
from models.config import Config
from models.config import PATHKEY_CSS, PATHKEY_KOVAAKS_PLAYLISTS, PATHKEY_LOCAL_PLAYLISTS, PATHKEY_LOCAL_REPORTS, PATHKEY_LOCAL_RESOURCES

from gui.confirmbox import KSVConfirmBox
from gui.window_createplaylist import CreatePlaylistWindow
from gui.window_promptkovaaksfolder import BrowseKovaaksFolder
from models.report import Report

BANNER_REGULAR_FILENAME = 'banner_regular.png'
BANNER_HOVER_FILENAME = 'banner_hover.png'
ICON_ERROR_FILENAME = 'icon_error.png'
ICON_QUESTION_FILENAME = 'icon_question.png'

# main window
class MainWindow(tk.Tk):
    def __init__(self, cfg: Config):
        super().__init__()

        self.cfg = cfg

        self.deiconify()
        self.title('KovaaK\'s Stat Visualizer')
        self.columnconfigure(0, weight=1, minsize=0)
        self.rowconfigure(0, weight=1, minsize=0)

        self.playlists = []
        self.var_playlists = tk.StringVar(value=[])
        self.selected_playlist = None

        self.playlist_listbox = None
        self.banner_regular = None
        self.banner_hover = None
        
        # widget init
        self.create_widgets()

    # main application window
    def create_widgets(self):
        # main frame
        content = ttk.Frame(self)
        content.grid(row=0, column=0, sticky='news', pady=(5,5))
        content.columnconfigure((0,1), weight=1)
        content.rowconfigure(0, weight=1)

        # left frame
        frame_left = ttk.LabelFrame(content, text='Playlists')
        frame_left.grid(row=0, column=0, sticky='news', padx=(5,5))
        frame_left.columnconfigure((0,1,2), weight=1)
        frame_left.rowconfigure(0, weight=1, minsize=300)
        frame_left.rowconfigure(1, weight=0)

        # left frame: playlist listbox
        self.command_reload_playlists()
        self.playlist_listbox = tk.Listbox(frame_left, listvariable=self.var_playlists)
        playlist_scroll = ttk.Scrollbar(frame_left, orient=tk.VERTICAL, command=self.playlist_listbox.yview)
        self.playlist_listbox['yscrollcommand'] = playlist_scroll.set
        self.playlist_listbox.bind('<<ListboxSelect>>', self.event_listbox_playlist_selection)

        self.playlist_listbox.grid(row=0, column=0, columnspan=3, sticky='news')
        playlist_scroll.grid(row=0, column=2, sticky='nes')

        # left frame: playlist buttons
        button_create = ttk.Button(frame_left, text='Create', command=self.command_create_playlist)
        button_reload = ttk.Button(frame_left, text='Reload', command=self.command_reload_playlists)
        button_delete = ttk.Button(frame_left, text='Delete', command=self.command_confirm_playlist_deletion)

        button_create.grid(row=1, column=0, sticky='news', pady=(5, 0))
        button_reload.grid(row=1, column=1, sticky='news', pady=(5, 0))
        button_delete.grid(row=1, column=2, sticky='news', pady=(5, 0))

        # left frame: playlist legend 
        frame_playlist_legend = ttk.LabelFrame(frame_left, text='Playlist legend')
        frame_playlist_legend.grid(row=2, column=0, columnspan=3, sticky='ew')

        text1 = '[K]: Imported from KovaaK\'s downloaded playlists.\n'
        text2 = '[S]: Saved by the application.'
        text_legend = text1 + text2
        label_legend = ttk.Label(frame_playlist_legend, text=text_legend)
        label_legend.grid(row=0, column=0, sticky='w')

        text_note = 'Note: You can only delete playlists made with\n           this application, KovaaK\'s playlists must\n           this be deleted ingame'
        label_note = ttk.Label(frame_playlist_legend, text=text_note)
        label_note.grid(row=1, column=0, sticky='w')

        # right frame
        frame_right = ttk.Frame(content)
        frame_right.grid(row=0, column=1, sticky='news', padx=(5,5))
        frame_right.columnconfigure(0, weight=1, minsize=400)
        frame_right.rowconfigure(0, weight=1, minsize=420)
        frame_right.rowconfigure(1, weight=1)

        # right frame: playlist info
        self.frame_playlist_info = ttk.LabelFrame(frame_right, text='Playlist Info')
        self.frame_playlist_info.grid(row=0, column=0, sticky='news', pady=(0, 10))
        # self.update_scenarios()

        # right frame: options
        frame_options = ttk.LabelFrame(frame_right, text='Options')
        frame_options.grid(row=1, column=0, sticky='news', pady=(0, 10))
        frame_options.columnconfigure(0, weight=1)

        option1_checkbox = ttk.Checkbutton(frame_options, text='Open report after generating')
        option2_checkbox = ttk.Checkbutton(frame_options, text='Group sessions')
        option3_checkbox = ttk.Checkbutton(frame_options, text='Include only last X days')

        option1_checkbox.grid(row=0, column=0, sticky='w')
        option2_checkbox.grid(row=1, column=0, sticky='w')
        option3_checkbox.grid(row=2, column=0, sticky='w')

        button_browse_folder = ttk.Button(frame_options, text='Change KovaaK\'s folder', command=self.command_browse_kovaaks_folder)
        button_browse_folder.grid(row=3, column=0, sticky='ns', pady=(5, 5))

        # right frame: generate button
        button_generate = ttk.Button(frame_right, text='Generate report', command=self.command_generate_report)
        button_generate.grid(row=2, column=0, sticky='news', padx=(50, 50))

        # right frame: banner
        self.banner_label = ttk.Label(frame_right, cursor='hand2')
        self.banner_regular = ImageTk.PhotoImage(master=self.banner_label, file=os.path.join(self.cfg.get_path(PATHKEY_LOCAL_RESOURCES), BANNER_REGULAR_FILENAME))
        self.banner_hover = ImageTk.PhotoImage(master=self.banner_label, file=os.path.join(self.cfg.get_path(PATHKEY_LOCAL_RESOURCES), BANNER_HOVER_FILENAME))
        self.banner_label.configure(image=self.banner_regular)
        self.banner_label.grid(row=3, column=0, sticky='s', pady=(0, 5))

        self.banner_label.bind('<Enter>', self.event_banner_enter)
        self.banner_label.bind('<Leave>', self.event_banner_leave)
        self.banner_label.bind('<Button-1>', self.event_banner_click)

        # make space for banner
        frame_right.columnconfigure(0, weight=1, minsize=max(250, self.banner_regular.width()+5*2))	
                                                                     
    def update_scenarios(self):
        for wchild in self.frame_playlist_info.winfo_children():
            wchild.destroy()

        i = 0
        for scenario_name in self.selected_playlist.scenarios_names:
            ttk.Label(self.frame_playlist_info, text=f'{str(i)}:').grid(row=i, column=0, sticky='e')
            ttk.Label(self.frame_playlist_info, text=scenario_name).grid(row=i, column=1, sticky='w')
            i += 1

    # commands
    def command_create_playlist(self, *args):
        window = CreatePlaylistWindow(self, self.playlists, self.cfg)
        window.mainloop()

    def command_reload_playlists(self, *args):
        kovaaks_playlists = Playlist.get_kovaaks_playlists(self.cfg.get_path(PATHKEY_KOVAAKS_PLAYLISTS))
        local_playlists = Playlist.get_local_playlists(self.cfg.get_path(PATHKEY_LOCAL_PLAYLISTS))
        self.playlists = kovaaks_playlists + local_playlists
        self.playlists.sort(key=lambda p: p.name)

        playlists_names = [p.get_listname() for p in self.playlists]
        self.var_playlists.set(playlists_names)

    def command_confirm_playlist_deletion(self, *args):
        if self.selected_playlist.source == PLAYLIST_SOURCE_KOVAAKS:
            self.bell()
        else:
            # todo fix icon path to icon
            KSVConfirmBox(
                parent      =   self,
                title       =   'Confirm playlist deletion',
                message     =   f'About to delete: {self.selected_playlist.name}\nThis operation cannot be undone.',
                icon_path   =   os.path.join(self.cfg.get_path(PATHKEY_LOCAL_RESOURCES), ICON_QUESTION_FILENAME),
                text_option1=   'Delete',
                f_option1   =   self.command_delete_playlist,
                text_option2=   'Cancel',
                f_option2   =   None
            )

    def command_delete_playlist(self, *args):
        i = self.playlist_listbox.curselection()[0]
        self.selected_playlist = self.playlists[i]

        if self.selected_playlist.source == PLAYLIST_SOURCE_LOCAL:
            self.selected_playlist.delete()
            self.command_reload_playlists()
            self.update_scenarios()
        else:
            self.bell()

    def command_browse_kovaaks_folder(self, *args):
        icon_error_path = os.path.join(self.cfg.get_path(PATHKEY_LOCAL_RESOURCES), ICON_ERROR_FILENAME)
        window = BrowseKovaaksFolder(self.cfg, icon_error_path)
        window.mainloop()

    def command_generate_report(self, *args):
        if self.selected_playlist is not None:
            # todo fix using cfg
            report = Report(self.selected_playlist, self.cfg)
            report_content = report.generate_report()
            report_path = report.write_report(report_content)
            webbrowser.open(report_path, new=2)
        else:
            self.bell()

    # events
    def event_listbox_playlist_selection(self, *args):
        i = self.playlist_listbox.curselection()[0]
        self.selected_playlist = self.playlists[i]
        self.update_scenarios()

    def event_banner_enter(self, *args):
        self.banner_label.image = self.banner_hover
        self.banner_label.configure(image=self.banner_hover)

    def event_banner_leave(self, *args):
        self.banner_label.image = self.banner_regular
        self.banner_label.configure(image=self.banner_regular)

    def event_banner_click(self, *args):
        webbrowser.open('https://github.com/drizak/kovaaks-stats-visualizer', new=2)


# os.chdir('C:\\Users\\a626\\Desktop\\kovaaks-stats-visualizer\\src')

# app = AppGUI('dummy config')
# # app.window_select_folder()
# # app.window_main()
# app.mainloop()