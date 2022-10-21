import os
import webbrowser

import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
from tkinter import messagebox

from PIL import Image, ImageTk

from scenario import Scenario
from playlist import Playlist
from ksv_messagebox import KSVMessageBox

KOVAAKS_EXECUTABLE_FNAME = 'FPSAimTrainer.exe'
KOVAAKS_STATS_FOLDER_PATH = os.path.join('FPSAimTrainer','stats')
KOVAAKS_PLAYLIST_FOLDER_PATH = os.path.join('FPSAimTrainer','Saved','SaveGames','Playlists')

RESOURCES_FOLDER = os.path.join('.', 'resources')
BANNER_REGULAR_PATH = os.path.join(RESOURCES_FOLDER, 'banner_regular.png')
BANNER_HOVER_PATH = os.path.join(RESOURCES_FOLDER, 'banner_hover.png')
ICON_ERROR_PATH = os.path.join(RESOURCES_FOLDER, 'icon_error.png')

class AppGUI(tk.Tk):
	def __init__(self):
		super().__init__()
		self.title('KovaaK\'s Stat Visualizer')
		self.columnconfigure(0, weight=1, minsize=0)
		self.rowconfigure(0, weight=1, minsize=0)

		self.kovaaks_path = tk.StringVar()
		self.stats_path = os.path.join('')
		self.playlist_path = os.path.join('')

		self.var_playlists_list = tk.StringVar(value=[])
		self.scenarios_list = []

		self.banner_regular_img = ImageTk.PhotoImage(Image.open(BANNER_REGULAR_PATH))
		self.banner_hover_img = ImageTk.PhotoImage(Image.open(BANNER_HOVER_PATH))

	def window_main(self):
		# main frame
		content = ttk.Frame(self)
		content.grid(row=0, column=0, sticky='news', pady=(5,5))
		content.columnconfigure((0,1), weight=1)
		content.rowconfigure(0, weight=1)

		# left frame
		frame_left = ttk.LabelFrame(content, text='Routines')
		frame_left.grid(row=0, column=0, sticky='news', padx=(5,5))
		frame_left.columnconfigure((0,1,2), weight=1)
		frame_left.rowconfigure(0, weight=1, minsize=300)
		frame_left.rowconfigure(1, weight=0)

		# left frame: playlist listbox
		playlists_list = ['playlist_'+str(i).zfill(2) for i in range(50)]
		self.var_playlists_list.set(playlists_list)

		playlist_listbox = tk.Listbox(frame_left, listvariable=self.var_playlists_list)
		playlist_scroll = ttk.Scrollbar(frame_left, orient=tk.VERTICAL, command=playlist_listbox.yview)
		playlist_listbox['yscrollcommand'] = playlist_scroll.set

		playlist_listbox.grid(row=0, column=0, columnspan=3, sticky='news')
		playlist_scroll.grid(row=0, column=2, sticky='nes')

		# left frame: playlist buttons
		button_create = ttk.Button(frame_left, text='Create')
		button_reload = ttk.Button(frame_left, text='Reload')
		button_delete = ttk.Button(frame_left, text='Delete')

		button_create.grid(row=1, column=0, sticky='news', pady=(5, 0))
		button_reload.grid(row=1, column=1, sticky='news', pady=(5, 0))
		button_delete.grid(row=1, column=2, sticky='news', pady=(5, 0))

		# left frame: playlist legend 
		frame_playlist_legend = ttk.LabelFrame(frame_left, text='Routine legend')
		frame_playlist_legend.grid(row=2, column=0, columnspan=3)

		text1 = '[K]: Imported from KovaaK\'s downloaded routines.\n'
		text2 = '[S]: Saved by the application.'
		text_legend = text1 + text2
		label_legend = ttk.Label(frame_playlist_legend, text=text_legend)
		label_legend.grid(row=0, column=0)

		# right frame
		frame_right = ttk.Frame(content)
		frame_right.grid(row=0, column=1, sticky='news', padx=(5,5))
		frame_right.columnconfigure(0, weight=1, minsize=400)
		frame_right.rowconfigure(0, weight=1, minsize=300)
		frame_right.rowconfigure(1, weight=1)


		# right frame: routine info
		frame_playlist_info = ttk.LabelFrame(frame_right, text='Routine Info')
		frame_playlist_info.grid(row=0, column=0, sticky='news', pady=(0, 10))

		self.scenarios_list = ['scenario_'+str(i).zfill(2) for i in range(12)]

		i = 0
		for scenario_name in self.scenarios_list:
			# label_text = f'{str(i)}: {scenario_name}'
			ttk.Label(frame_playlist_info, text=f'{str(i)}:').grid(row=i, column=0, sticky='e')
			ttk.Label(frame_playlist_info, text=scenario_name).grid(row=i, column=1, sticky='w')
			i += 1

		# right frame: options
		frame_options = ttk.LabelFrame(frame_right, text='Options')
		frame_options.grid(row=1, column=0, sticky='news', pady=(0, 10))
		frame_options.columnconfigure(0, weight=1)
		# frame_options.rowconfigure((0,1,2,3), weight=0)

		option1_checkbox = ttk.Checkbutton(frame_options, text='Option 1')
		option2_checkbox = ttk.Checkbutton(frame_options, text='Option 2')
		option3_checkbox = ttk.Checkbutton(frame_options, text='Option 3')

		option1_checkbox.grid(row=0, column=0, sticky='w')
		option2_checkbox.grid(row=1, column=0, sticky='w')
		option3_checkbox.grid(row=2, column=0, sticky='w')

		button_browse_folder = ttk.Button(frame_options, text='Change KovaaK\'s folder')
		button_browse_folder.grid(row=3, column=0, sticky='ns', pady=(5, 5))

		# right frame: generate button
		button_generate = ttk.Button(frame_right, text='Generate report')
		button_generate.grid(row=2, column=0, sticky='news', padx=(50, 50))

		# right frame: banner
		self.banner_label = ttk.Label(frame_right)
		self.banner_label.image = self.banner_regular_img
		self.banner_label.configure(image=self.banner_regular_img)
		self.banner_label.grid(row=3, column=0, sticky='s', pady=(0, 5))

		self.banner_label.bind('<Enter>', self.event_banner_enter)
		self.banner_label.bind('<Leave>', self.event_banner_leave)
		self.banner_label.bind('<Button-1>', self.event_banner_click)

		# make space for banner
		frame_right.columnconfigure(0, weight=1, minsize=max(250, self.banner_regular_img.width()+5*2))

	def event_banner_enter(self, e):
		self.banner_label.image = self.banner_hover_img
		self.banner_label.configure(image=self.banner_hover_img)

	def event_banner_leave(self, e):
		self.banner_label.image = self.banner_regular_img
		self.banner_label.configure(image=self.banner_regular_img)

	def event_banner_click(self, e):
		webbrowser.open('https://github.com/drizak/kovaaks-stats-visualizer', new=2)



	def old_window_main(self):
		self.rowconfigure(0, weight=1, minsize=600)

		# main content frame
		content = ttk.Frame(self)
		content.grid(row=0, column=0, sticky='news', pady=(5,5))
		content.columnconfigure((0,1), weight=1)
		content.rowconfigure(0, weight=1)

		# left frame: scenarios
		scenarios_frame = ttk.LabelFrame(content, text='Scenarios')
		scenarios_frame.grid(row=0, column=0, sticky='news', padx=(5,5))
		scenarios_frame.columnconfigure(0, weight=1, minsize=350)
		scenarios_frame.rowconfigure(0, weight=1)

		scenarios_list = Scenario.list_scenarios(self.stats_path)
		scenarios_var = tk.StringVar(value=scenarios_list)
		scenarios_listbox = tk.Listbox(scenarios_frame, listvariable=scenarios_var)
		scenarios_scroll = ttk.Scrollbar(scenarios_frame, orient=tk.VERTICAL, command=scenarios_listbox.yview)
		scenarios_listbox['yscrollcommand'] = scenarios_scroll.set

		scenarios_listbox.grid(row=0, column=0, sticky='news')
		scenarios_scroll.grid(row=0, column=0, sticky='nes')

		# right frame
		right_frame = ttk.Frame(content)
		right_frame.grid(row=0, column=1, sticky='news', padx=(5,5))
		right_frame.columnconfigure(0, weight=1)
		right_frame.rowconfigure(0, weight=1)

		# right frame: playlist
		playlist_frame = ttk.LabelFrame(right_frame, text='Playlists')
		playlist_frame.grid(row=0, column=0, sticky='news')
		playlist_frame.columnconfigure((0,1), weight=1)
		playlist_frame.rowconfigure(0, weight=1)
		playlist_frame.rowconfigure((1,2,3), weight=0)

		playlist_list = Playlist.list_kovaaks_playlists(self.playlist_path)
		playlist_var = tk.StringVar(value=playlist_list)
		playlist_listbox = tk.Listbox(playlist_frame, listvariable=playlist_var)
		playlist_scroll = ttk.Scrollbar(playlist_frame, orient=tk.VERTICAL, command=playlist_listbox.yview)
		playlist_listbox['yscrollcommand'] = playlist_scroll.set

		playlist_listbox.grid(row=0, column=0, columnspan=2, sticky='news', pady=(0, 5))
		playlist_scroll.grid(row=0, column=1, sticky='nes')

		save_button = ttk.Button(playlist_frame, text='Save')
		delete_button = ttk.Button(playlist_frame, text='Delete')
		
		save_button.grid(row=1, column=0, pady=(0, 5))
		delete_button.grid(row=1, column=1, pady=(0, 5))

		# right frame: options
		options_frame = ttk.LabelFrame(right_frame, text='Options')
		options_frame.grid(row=1, column=0, sticky='news', pady=(5, 5))
		options_frame.columnconfigure(0, weight=1)

		option1_checkbox = ttk.Checkbutton(options_frame, text='Option 1')
		option2_checkbox = ttk.Checkbutton(options_frame, text='Option 2')
		option3_checkbox = ttk.Checkbutton(options_frame, text='Option 3')

		option1_checkbox.grid(row=0, column=0, sticky='w')
		option2_checkbox.grid(row=1, column=0, sticky='w')
		option3_checkbox.grid(row=2, column=0, sticky='w')

		select_kovaaks_folder_button = ttk.Button(options_frame, text='Change KovaaK\'s folder', command=lambda:[self.command_clear_gui(content), self.window_noconfig()])
		select_kovaaks_folder_button.grid(row=3, column=0, pady=(10, 5))

		# right frame: generate button
		generate_button = ttk.Button(right_frame, text='Generate')
		generate_button.grid(row=2, column=0, pady=(0, 5))

		# right frame: banner
		banner_img = ImageTk.PhotoImage(Image.open(BANNER_PATH))
		banner_label = ttk.Label(right_frame)
		banner_label.image = banner_img
		banner_label.configure(image=banner_img)
		banner_label.grid(row=3, column=0, sticky='s', pady=(0, 5))

		# make space for banner
		right_frame.columnconfigure(0, weight=1, minsize=max(250, banner_img.width()+5*2))

	def window_noconfig(self):
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

	def command_select_kovaaks_folder(self):
		directory = filedialog.askdirectory()
		kovaaks_path = os.path.normpath(directory)
		self.kovaaks_path.set(kovaaks_path)

	def command_clear_gui(self, content_frame):
		content_frame.destroy()
		self.columnconfigure(0, weight=1, minsize=0)
		self.rowconfigure(0, weight=1, minsize=0)

	def command_confirm_kovaaks_path(self):
		executable_path = os.path.join(self.kovaaks_path.get(), KOVAAKS_EXECUTABLE_FNAME)
		if os.path.exists(executable_path):
			self.stats_path = os.path.join(self.kovaaks_path.get(), KOVAAKS_STATS_FOLDER_PATH)
			self.playlist_path = os.path.join(self.kovaaks_path.get(), KOVAAKS_PLAYLIST_FOLDER_PATH)
			return True
		else:
			return False

	def command_alert_bad_kovaaks_path(self):
		KSVMessageBox(	self,
						'Error!', 
						'Error!\nSelect the correct KovaaK\'s folder, it has the FPSAimTrainer executable in it.',
						ICON_ERROR_PATH)



os.chdir('C:\\Users\\a626\\Desktop\\kovaaks-stats-visualizer\\src')

app = AppGUI()
# app.window_noconfig()
app.window_main()
app.mainloop()
