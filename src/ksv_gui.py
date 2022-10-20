import tkinter as tk
from tkinter import ttk

class AppGUI:
	def __init__(self):
		root = tk.Tk()
		root.title('KovaaK\'s Stat Visualizer')
		root.columnconfigure(0, weight=1)
		root.rowconfigure(0, weight=1, minsize=600)

		# frames
		content = ttk.Frame(root)
		content.grid(row=0, column=0, sticky='news', pady=(5,5))
		content.columnconfigure((0,1), weight=1)
		content.rowconfigure(0, weight=1)

		scenarios_frame = ttk.LabelFrame(content, text='Scenarios')
		scenarios_frame.grid(row=0, column=0, rowspan=3, sticky='news', padx=(5,5))
		scenarios_frame.columnconfigure(0, weight=1, minsize=250)
		scenarios_frame.rowconfigure(0, weight=1)

		right_frame = ttk.Frame(content)
		right_frame.grid(row=0, column=1, columnspan=2, sticky='news', padx=(5,5))
		right_frame.columnconfigure(0, weight=1)
		right_frame.rowconfigure(0, weight=1)

		playlist_frame = ttk.LabelFrame(right_frame, text='Playlists')
		playlist_frame.grid(row=0, column=0, sticky='news')
		playlist_frame.columnconfigure((0,1), weight=1)
		playlist_frame.rowconfigure(0, weight=1)

		options_frame = ttk.LabelFrame(right_frame, text='Options')
		options_frame.grid(row=1, column=0, columnspan=2, sticky='news', pady=(5, 5))
		options_frame.columnconfigure(0, weight=1)

		# scenarios frame
		scenarios_list = [f'scenario_{str(x).zfill(3)}' for x in range(100)]
		scenarios_var = tk.StringVar(value=scenarios_list)
		scenarios_listbox = tk.Listbox(scenarios_frame, listvariable=scenarios_var)
		scenarios_scroll = ttk.Scrollbar(scenarios_frame, orient=tk.VERTICAL, command=scenarios_listbox.yview)
		scenarios_listbox['yscrollcommand'] = scenarios_scroll.set

		scenarios_listbox.grid(row=0, column=0, sticky='news')
		scenarios_scroll.grid(row=0, column=0, sticky='nes')

		# right frame: playlist
		playlist_list = [f'playlist_{str(x).zfill(2)}' for x in range(30)]
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
		option1_checkbox = ttk.Checkbutton(options_frame, text='Option 1')
		option2_checkbox = ttk.Checkbutton(options_frame, text='Option 2')
		option3_checkbox = ttk.Checkbutton(options_frame, text='Option 3')

		option1_checkbox.grid(row=0, column=0, sticky='w')
		option2_checkbox.grid(row=1, column=0, sticky='w')
		option3_checkbox.grid(row=2, column=0, sticky='w')

		# right frame: generate button
		generate_button = ttk.Button(right_frame, text='Generate')
		generate_button.grid(row=2, column=0, columnspan=2, pady=(0, 5))

		# right frame: banner
		banner_label = ttk.Label(right_frame)
		banner_img = tk.PhotoImage(file='./resources/banner.png')
		banner_label['image'] = banner_img
		banner_label.grid(row=3, column=0, sticky='s', pady=(0, 5))

		# make space for banner
		right_frame.columnconfigure(0, weight=1, minsize=max(250, banner_img.width()+5*2))

		root.mainloop()

AppGUI()