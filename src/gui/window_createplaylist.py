import tkinter as tk
from tkinter import ttk

from models.scenario import Scenario
from models.playlist import Playlist
from models.playlist import PLAYLIST_SOURCE_LOCAL, PLAYLIST_SOURCE_KOVAAKS
from models.config import Config
from models.config import PATHKEY_KOVAAKS_STATS, PATHKEY_LOCAL_PLAYLISTS

# window that handles playlist creation
class CreatePlaylistWindow(tk.Toplevel):
	def __init__(self, parent, playlists, cfg: Config):
		tk.Toplevel.__init__(self)
		self.title('Playlist Creator')
		self.grab_set()

		self.parent = parent
		self.playlists = playlists
		self.cfg = cfg

		self.all_scenarios = Scenario.list_scenarios(self.cfg.get_path(PATHKEY_KOVAAKS_STATS))
		self.avaliable_scenarios = self.all_scenarios.copy()
		self.selected_scenarios = []
		
		self.var_avaliable_scenarios = tk.StringVar(value=self.avaliable_scenarios)
		self.var_search = tk.StringVar(value='')
		self.var_playlist_name = tk.StringVar(value='')
		self.var_selected_scenarios = tk.StringVar(value=self.selected_scenarios)

		# declaration for dummy widgets
		self.listbox_avaliable_scenarios = None
		self.listbox_selected_scenarios = None
		
		# Binds
		self.var_search.trace_add('write', self.f_search)
		self.bind('<Destroy>', self.parent.command_reload_playlists)

		self.create_widgets()

	def create_widgets(self):
		self.rowconfigure(0, weight=1)
		self.columnconfigure(0, weight=1)

		content = ttk.Frame(self)
		content.grid(row=0, column=0, sticky='news', pady=(5,5))
		content.rowconfigure(0, weight=1, minsize=500)
		content.columnconfigure(0, weight=1, minsize=350)
		content.columnconfigure(1, weight=1, minsize=350)

		frame_left = ttk.LabelFrame(content, text='Avaliable scenarios')
		frame_left.grid(row=0, column=0, sticky='news', padx=(5,5))
		frame_left.rowconfigure(1, weight=1)
		frame_left.columnconfigure(0, weight=1)

		search_box = ttk.Entry(frame_left, textvariable=self.var_search)
		search_box.grid(row=0, column=0, sticky='news', padx=(2,2), pady=(2, 5))

		self.listbox_avaliable_scenarios = tk.Listbox(frame_left, listvariable=self.var_avaliable_scenarios)
		scrollbar_avaliable_scenarios = ttk.Scrollbar(frame_left, orient=tk.VERTICAL, command=self.listbox_avaliable_scenarios.yview)
		self.listbox_avaliable_scenarios['yscrollcommand'] = scrollbar_avaliable_scenarios.set
		self.listbox_avaliable_scenarios.grid(row=1, column=0, columnspan=2, sticky='news', padx=(2, 2))
		scrollbar_avaliable_scenarios.grid(row=1, column=1, sticky='nes')

		button_add = ttk.Button(frame_left, text='Add', command=self.f_command_add)
		button_add.grid(row=2, column=0, sticky='ns', padx=(10, 10), pady=(5, 2))

		frame_right = ttk.Frame(content)
		frame_right.grid(row=0, column=1, sticky='news', padx=(5,5))
		frame_right.rowconfigure(1, weight=1)
		frame_right.columnconfigure(0, weight=1)

		frame_playlist_info = ttk.LabelFrame(frame_right, text='Playlist info')
		frame_playlist_info.grid(row=0, column=0, sticky='news')
		frame_playlist_info.columnconfigure(0, weight=0)
		frame_playlist_info.columnconfigure(1, weight=1)

		label_name = ttk.Label(frame_playlist_info, text='Name')
		label_name.grid(row=0, column=0, sticky='news', padx=(2, 5), pady=(2, 2))

		entry_name = ttk.Entry(frame_playlist_info, textvariable=self.var_playlist_name)
		entry_name.grid(row=0, column=1, sticky='news', padx=(0, 2), pady=(2, 2))

		frame_selected_scenarios = ttk.LabelFrame(frame_right, text='Selected scenarios')
		frame_selected_scenarios.grid(row=1, column=0, sticky='news')
		frame_selected_scenarios.rowconfigure(0, weight=1)
		frame_selected_scenarios.columnconfigure(0, weight=1)
		
		self.listbox_selected_scenarios = tk.Listbox(frame_selected_scenarios, listvariable=self.var_selected_scenarios)
		scrollbar_selected_scenarios = ttk.Scrollbar(frame_selected_scenarios, orient=tk.VERTICAL, command=self.listbox_selected_scenarios.yview)
		self.listbox_selected_scenarios['yscrollcommand'] = scrollbar_selected_scenarios.set
		self.listbox_selected_scenarios.grid(row=0, column=0, columnspan=2, sticky='news', padx=(2, 2))
		scrollbar_selected_scenarios.grid(row=0, column=1, sticky='nes')

		button_remove = ttk.Button(frame_selected_scenarios, text='Remove', command=self.f_command_remove)
		button_remove.grid(row=1, column=0, sticky='news', padx=(10, 10), pady=(5, 2))

		frame_controls = ttk.Frame(frame_right)
		frame_controls.grid(row=2, column=0, sticky='news')
		frame_controls.columnconfigure((0, 1), weight=1)

		button_create = ttk.Button(frame_controls, text='Create', command=self.f_command_create)
		self.bind('<Return>', self.f_command_create)
		button_create.grid(row=0, column=0, sticky='news', padx=(10, 10), pady=(5, 2))

		button_cancel = ttk.Button(frame_controls, text='Cancel', command=lambda: self.destroy())
		button_cancel.grid(row=0, column=1, sticky='news', padx=(10, 10), pady=(5, 2))

	def f_search(self, *args):
		if self.var_search.get() == '':
			self.avaliable_scenarios = self.all_scenarios.copy()
		else:
			self.avaliable_scenarios = [s for s in self.all_scenarios if self.var_search.get().lower() in s]

		self.var_avaliable_scenarios.set(self.avaliable_scenarios)

	def f_command_add(self, *args):
		i = self.listbox_avaliable_scenarios.curselection()[0]
		self.selected_scenarios.append(self.avaliable_scenarios[i])
		self.var_selected_scenarios.set(self.selected_scenarios)

	def f_command_remove(self, *args):
		i = self.listbox_selected_scenarios.curselection()[0]
		self.selected_scenarios.pop(i)
		self.var_selected_scenarios.set(self.selected_scenarios)

	def f_command_create(self, *args):
		c1 = self.var_playlist_name.get() != ''
		c2 = len(self.selected_scenarios) > 0
		c3 = self.var_playlist_name.get() not in [p.name for p in self.playlists]
		if c1 and c2 and c3:
			playlist = Playlist(self.var_playlist_name.get(), self.selected_scenarios, PLAYLIST_SOURCE_LOCAL, None)
			playlist.save_to_local(self.cfg.get_path(PATHKEY_LOCAL_PLAYLISTS)) 
			self.destroy()
		else:
			self.bell()
