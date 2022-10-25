import os
import webbrowser

import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
from tkinter import messagebox

from PIL import Image, ImageTk

from models.scenario import Scenario
from models.playlist import Playlist
from models.playlist import PLAYLIST_SOURCE_LOCAL, PLAYLIST_SOURCE_KOVAAKS
from gui.messagebox import KSVMessageBox
from gui.confirmbox import KSVConfirmBox
from models.report import Report

KOVAAKS_EXECUTABLE_FNAME = 'FPSAimTrainer.exe'
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
		
		# config loading
		if config is None:
			self.window_select_folder()
		else:
			self.load_gui_config(config)

		# initialization methods
		if config is not None:
			self.window_main()


	# main application window
	def window_main(self):
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
		self.playlist_listbox.bind('<<ListboxSelect>>', self.command_listbox_playlist_selection)

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

		button_browse_folder = ttk.Button(frame_options, text='Change KovaaK\'s folder', command=lambda: [self.command_clear_gui(content), self.window_select_folder()])
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

	# prompt to select the kovaaks folder
	def window_select_folder(self):
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

		folder_entry = ttk.Entry(content, textvariable=self.kovaaks_path)
		folder_entry.grid(row=1, column=1, sticky='nswe', padx=(5, 5))

		continue_button = ttk.Button(content, text='Continue', command=lambda: [self.command_clear_gui(content), self.window_main()] \
																				if self.command_confirm_kovaaks_path() \
																				else self.command_alert_bad_kovaaks_path())
		continue_button.grid(row=1, column=2, sticky='e')

	# prompt to create a new playlist
	def window_create_new_playlist(self):
		root = tk.Toplevel()
		root.grab_set()
		root.rowconfigure(0, weight=1)
		root.columnconfigure(0, weight=1)

		content = ttk.Frame(root)
		content.grid(row=0, column=0, sticky='news', pady=(5,5))
		content.rowconfigure(0, weight=1, minsize=500)
		content.columnconfigure(0, weight=1, minsize=350)
		content.columnconfigure(1, weight=1, minsize=350)

		frame_left = ttk.LabelFrame(content, text='Avaliable scenarios')
		frame_left.grid(row=0, column=0, sticky='news', padx=(5,5))
		frame_left.rowconfigure(1, weight=1)
		frame_left.columnconfigure(0, weight=1)

		var_search = tk.StringVar(value='')
		search_box = ttk.Entry(frame_left, textvariable=var_search)
		search_box.grid(row=0, column=0, sticky='news', padx=(2,2), pady=(2, 5))

		all_scenarios = Scenario.list_scenarios(self.kovaaks_stats_path)
		avaliable_scenarios = all_scenarios.copy()
		var_avaliable_scenarios = tk.StringVar(value=avaliable_scenarios)

		f_search_results = lambda: [s for s in all_scenarios if var_search.get().lower() in s.lower()] if var_search.get() != '' else all_scenarios
		f_search = lambda x,y,z: var_avaliable_scenarios.set(f_search_results())
		var_search.trace_add('write', f_search)

		listbox_avaliable_scenarios = tk.Listbox(frame_left, listvariable=var_avaliable_scenarios)
		scrollbar_avaliable_scenarios = ttk.Scrollbar(frame_left, orient=tk.VERTICAL, command=listbox_avaliable_scenarios.yview)
		listbox_avaliable_scenarios['yscrollcommand'] = scrollbar_avaliable_scenarios.set
		listbox_avaliable_scenarios.grid(row=1, column=0, columnspan=2, sticky='news', padx=(2,2))
		scrollbar_avaliable_scenarios.grid(row=1, column=1, sticky='nes')

		f_command_add = lambda: [f_add_to_selected(), f_update_selected_scenarios()]
		f_add_to_selected = lambda: list_selected_scenarios.append(f_search_results()[listbox_avaliable_scenarios.curselection()[0]])
		f_update_selected_scenarios = lambda: var_selected_scenarios.set(list_selected_scenarios)
		button_add = ttk.Button(frame_left, text='Add', command=f_command_add)
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

		var_name = tk.StringVar(value='')
		entry_name = ttk.Entry(frame_playlist_info, textvariable=var_name)
		entry_name.grid(row=0, column=1, sticky='news', padx=(0, 2), pady=(2, 2))

		frame_selected_scenarios = ttk.LabelFrame(frame_right, text='Selected scenarios')
		frame_selected_scenarios.grid(row=1, column=0, sticky='news')
		frame_selected_scenarios.rowconfigure(0, weight=1)
		frame_selected_scenarios.columnconfigure(0, weight=1)

		list_selected_scenarios = []
		var_selected_scenarios = tk.StringVar(value=list_selected_scenarios)
		listbox_selected_scenarios = tk.Listbox(frame_selected_scenarios, listvariable=var_selected_scenarios)
		scrollbar_selected_scenarios = ttk.Scrollbar(frame_selected_scenarios, orient=tk.VERTICAL, command=listbox_selected_scenarios.yview)
		listbox_selected_scenarios['yscrollcommand'] = scrollbar_selected_scenarios.set
		listbox_selected_scenarios.grid(row=0, column=0, columnspan=2, sticky='news', padx=(2, 2))
		scrollbar_selected_scenarios.grid(row=0, column=1, sticky='nes')

		f_command_remove = lambda: [f_remove_from_selected(), f_update_selected_scenarios()]
		f_remove_from_selected = lambda: list_selected_scenarios.pop(listbox_selected_scenarios.curselection()[0])
		f_update_selected_scenarios = lambda: var_selected_scenarios.set(list_selected_scenarios)

		button_remove = ttk.Button(frame_selected_scenarios, text='Remove', command=f_command_remove)
		button_remove.grid(row=1, column=0, sticky='news', padx=(10, 10), pady=(5, 2))

		frame_controls = ttk.Frame(frame_right)
		frame_controls.grid(row=2, column=0, sticky='news')
		frame_controls.columnconfigure((0, 1), weight=1)

		f_command_create = lambda: f_create_actions() if (var_name.get()!='' and len(list_selected_scenarios)>0 and var_name.get() not in self.playlists_dict.keys()) else root.bell()
		f_create_actions = lambda: [f_save_playlist(), self.command_reload_playlists(), root.destroy()]
		f_save_playlist = lambda: Playlist(var_name.get(), list_selected_scenarios, PLAYLIST_SOURCE_LOCAL, None).save_to_local(LOCAL_PLAYLIST_FOLDER_PATH)
		button_create = ttk.Button(frame_controls, text='Create', command=f_command_create)
		button_create.grid(row=0, column=0, sticky='news', padx=(10, 10), pady=(5, 2))

		button_cancel = ttk.Button(frame_controls, text='Cancel', command=lambda: root.destroy())
		button_cancel.grid(row=0, column=1, sticky='news', padx=(10, 10), pady=(5, 2))

		root.mainloop()

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

	# main window commands
	def command_create_playlist(self):
		self.window_create_new_playlist()

	def command_reload_playlists(self):
		kovaaks_playlists = Playlist.get_kovaaks_playlists(self.kovaaks_playlist_path)
		local_playlists = Playlist.get_local_playlists(LOCAL_PLAYLIST_FOLDER_PATH)
		playlists = kovaaks_playlists + local_playlists
		playlists.sort(key=lambda p: p.name)

		self.playlists_dict = {pl.name: pl for pl in playlists}
		self.var_playlists_list.set([pl.get_listname() for pl in playlists])

	def command_confirm_playlist_deletion(self):
		if self.selected_playlist.source == PLAYLIST_SOURCE_KOVAAKS:
			self.bell()
		else:
			KSVConfirmBox(	self,
							'Confirm playlist deletion', 
							f'About to delete: {self.selected_playlist.name}\nThis operation cannot be undone.',
							ICON_QUESTION_PATH,
							'Delete', self.command_delete_playlist,
							'Cancel')

	def command_delete_playlist(self):
		i = self.playlist_listbox.curselection()[0]
		playlist_name = list(self.playlists_dict.keys())[i]
		self.selected_playlist = self.playlists_dict[playlist_name]

		if self.selected_playlist.source == PLAYLIST_SOURCE_LOCAL:
			self.selected_playlist.delete()
			self.command_reload_playlists()
			self.update_scenarios()


	# main window events
	def command_listbox_playlist_selection(self, e):
		i = self.playlist_listbox.curselection()[0]
		playlist_name = list(self.playlists_dict.keys())[i]
		self.selected_playlist = self.playlists_dict[playlist_name]
		self.update_scenarios()

	def event_banner_enter(self, e):
		self.banner_label.image = self.banner_hover_img
		self.banner_label.configure(image=self.banner_hover_img)

	def event_banner_leave(self, e):
		self.banner_label.image = self.banner_regular_img
		self.banner_label.configure(image=self.banner_regular_img)

	def event_banner_click(self, e):
		webbrowser.open('https://github.com/drizak/kovaaks-stats-visualizer', new=2)

	# select kovaaks folder window commands
	def command_select_kovaaks_folder(self):
		directory = filedialog.askdirectory()
		kovaaks_path = os.path.normpath(directory)
		self.kovaaks_path.set(kovaaks_path)
		self.kovaaks_stats_path = os.path.join(self.kovaaks_path.get(), KOVAAKS_STATS_FOLDER_SUBPATH)
		self.kovaaks_playlist_path = os.path.join(self.kovaaks_path.get(), KOVAAKS_PLAYLIST_FOLDER_SUBPATH)

	def command_clear_gui(self, content_frame):
		content_frame.destroy()
		self.columnconfigure(0, weight=1, minsize=0)
		self.rowconfigure(0, weight=1, minsize=0)

	def command_confirm_kovaaks_path(self):
		executable_path = os.path.join(self.kovaaks_path.get(), KOVAAKS_EXECUTABLE_FNAME)
		if os.path.exists(executable_path):
			self.stats_path = os.path.join(self.kovaaks_path.get(), KOVAAKS_STATS_FOLDER_SUBPATH)
			self.playlist_path = os.path.join(self.kovaaks_path.get(), KOVAAKS_PLAYLIST_FOLDER_SUBPATH)
			return True
		else:
			return False

	def command_alert_bad_kovaaks_path(self):
		KSVMessageBox(	self,
						'Error!', 
						'Error!\nSelect the correct KovaaK\'s folder, it has the FPSAimTrainer executable in it.',
						ICON_ERROR_PATH)

	def command_generate_report(self):
		if self.selected_playlist is not None:
			css_path = os.path.join(RESOURCES_FOLDER, 'report_style.css')
			report = Report(self.selected_playlist, self.kovaaks_stats_path, REPORTS_FOLDER, css_path)
			report_path = report.generate_report()
			webbrowser.open(report_path, new=2)
		else:
			self.bell()



# os.chdir('C:\\Users\\a626\\Desktop\\kovaaks-stats-visualizer\\src')

# app = AppGUI('dummy config')
# # app.window_select_folder()
# # app.window_main()
# app.mainloop()

