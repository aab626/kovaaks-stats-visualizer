import os
import webbrowser

import tkinter as tk
from tkinter import ttk

from PIL import Image, ImageTk

from models.scenario import Scenario
from models.playlist import Playlist
from models.playlist import PLAYLIST_SOURCE_LOCAL, PLAYLIST_SOURCE_KOVAAKS

from gui.confirmbox import KSVConfirmBox
from gui.window_createplaylist import CreatePlaylistWindow
from gui.window_promptkovaaksfolder import BrowseKovaaksFolder
from models.report import Report

KOVAAKS_STATS_FOLDER_SUBPATH = os.path.join('FPSAimTrainer','stats')
KOVAAKS_PLAYLIST_FOLDER_SUBPATH = os.path.join('FPSAimTrainer','Saved','SaveGames','Playlists')
LOCAL_PLAYLIST_FOLDER_PATH = os.path.join(os.getcwd(), 'playlists')

RESOURCES_FOLDER = os.path.join(os.getcwd(), 'resources')
REPORTS_FOLDER = os.path.join(os.getcwd(), 'reports')
BANNER_REGULAR_PATH = os.path.join(RESOURCES_FOLDER, 'banner_regular.png')
BANNER_HOVER_PATH = os.path.join(RESOURCES_FOLDER, 'banner_hover.png')
ICON_ERROR_PATH = os.path.join(RESOURCES_FOLDER, 'icon_error.png')
ICON_QUESTION_PATH = os.path.join(RESOURCES_FOLDER, 'icon_question.png')

class AppGUI(tk.Tk):
    def __init__(self, config):
        super().__init__()
        self.title('KovaaK\'s Stat Visualizer')
        self.columnconfigure(0, weight=1, minsize=0)
        self.rowconfigure(0, weight=1, minsize=0)

        # instance variables
        self.kovaaks_path = tk.StringVar()
        self.kovaaks_stats_path = os.path.join('')
        self.kovaaks_playlist_path = os.path.join('')

        self.playlists_dict = dict()
        self.var_playlists_list = tk.StringVar(value=[])
        self.selected_playlist = None

        self.playlist_listbox = None
        self.banner_regular_img = ImageTk.PhotoImage(Image.open(BANNER_REGULAR_PATH))
        self.banner_hover_img = ImageTk.PhotoImage(Image.open(BANNER_HOVER_PATH))

        self.created_playlist = None
        
        # todo fix logic: usage with main.py
        # config loading
        if config is None:
            self.window_select_folder()
        else:
            self.load_gui_config(config)

        # initialization methods
        if config is not None:
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
        self.playlist_listbox = tk.Listbox(frame_left, listvariable=self.var_playlists_list)
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
        self.banner_label.image = self.banner_regular_img
        self.banner_label.configure(image=self.banner_regular_img)
        self.banner_label.grid(row=3, column=0, sticky='s', pady=(0, 5))

        self.banner_label.bind('<Enter>', self.event_banner_enter)
        self.banner_label.bind('<Leave>', self.event_banner_leave)
        self.banner_label.bind('<Button-1>', self.event_banner_click)

        # make space for banner
        frame_right.columnconfigure(0, weight=1, minsize=max(250, self.banner_regular_img.width()+5*2))	

    # methods
    def load_gui_config(self, config):
        # todo fix, temporary
        self.kovaaks_path.set('C:\\Program Files (x86)\\Steam\\steamapps\\common\\FPSAimTrainer')
        self.kovaaks_stats_path = os.path.join(self.kovaaks_path.get(), KOVAAKS_STATS_FOLDER_SUBPATH)
        self.kovaaks_playlist_path = os.path.join(self.kovaaks_path.get(), KOVAAKS_PLAYLIST_FOLDER_SUBPATH)

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
        window = CreatePlaylistWindow(self, self.playlists_dict, LOCAL_PLAYLIST_FOLDER_PATH, self.kovaaks_stats_path)
        window.mainloop()

    def command_reload_playlists(self, *args):
        kovaaks_playlists = Playlist.get_kovaaks_playlists(self.kovaaks_playlist_path)
        local_playlists = Playlist.get_local_playlists(LOCAL_PLAYLIST_FOLDER_PATH)
        playlists = kovaaks_playlists + local_playlists
        playlists.sort(key=lambda p: p.name)

        self.playlists_dict = {pl.name: pl for pl in playlists}
        self.var_playlists_list.set([pl.get_listname() for pl in playlists])

    def command_confirm_playlist_deletion(self, *args):
        if self.selected_playlist.source == PLAYLIST_SOURCE_KOVAAKS:
            self.bell()
        else:
            KSVConfirmBox(	self,
                            'Confirm playlist deletion', 
                            f'About to delete: {self.selected_playlist.name}\nThis operation cannot be undone.',
                            ICON_QUESTION_PATH,
                            'Delete', self.command_delete_playlist,
                            'Cancel')

    def command_delete_playlist(self, *args):
        i = self.playlist_listbox.curselection()[0]
        playlist_name = list(self.playlists_dict.keys())[i]
        self.selected_playlist = self.playlists_dict[playlist_name]

        if self.selected_playlist.source == PLAYLIST_SOURCE_LOCAL:
            self.selected_playlist.delete()
            self.command_reload_playlists()
            self.update_scenarios()

    def command_browse_kovaaks_folder(self, *args):
        window = BrowseKovaaksFolder(self.kovaaks_path, ICON_ERROR_PATH)
        window.mainloop()

    def command_generate_report(self, *args):
        if self.selected_playlist is not None:
            css_path = os.path.join(RESOURCES_FOLDER, 'report_style.css')
            report = Report(self.selected_playlist, self.kovaaks_stats_path, REPORTS_FOLDER, css_path)
            report_path = report.generate_report()
            webbrowser.open(report_path, new=2)
        else:
            self.bell()

    # events
    def event_listbox_playlist_selection(self, *args):
        i = self.playlist_listbox.curselection()[0]
        playlist_name = list(self.playlists_dict.keys())[i]
        self.selected_playlist = self.playlists_dict[playlist_name]
        self.update_scenarios()

    def event_banner_enter(self, *args):
        self.banner_label.image = self.banner_hover_img
        self.banner_label.configure(image=self.banner_hover_img)

    def event_banner_leave(self, *args):
        self.banner_label.image = self.banner_regular_img
        self.banner_label.configure(image=self.banner_regular_img)

    def event_banner_click(self, *args):
        webbrowser.open('https://github.com/drizak/kovaaks-stats-visualizer', new=2)


# os.chdir('C:\\Users\\a626\\Desktop\\kovaaks-stats-visualizer\\src')

# app = AppGUI('dummy config')
# # app.window_select_folder()
# # app.window_main()
# app.mainloop()

# TODO fix playlist listbox issues when selecting after creating a playlist