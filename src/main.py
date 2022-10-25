# import configparser

# CONFIG_FILENAME = 'config.cfg'

# class Main:
# 	def __init__(self):
# 		pass

# 	def load_config(self):
# 		cfg = configparser.ConfigParser()
# 		cfg.read(CONFIG_FILENAME) # might raise NameError if non existant
# 		return cfg

# 	def create_folders(self):
# 		# todo create local playlists folder
# 		# todo create local reports folder
# 		pass

import gui.mainwindow as mainwindow

import os
os.chdir('C:\\Users\\a626\\Desktop\\kovaaks-stats-visualizer\\src')

app = mainwindow.AppGUI('dummy config')
# app.window_select_folder()
# app.window_main()
app.mainloop()