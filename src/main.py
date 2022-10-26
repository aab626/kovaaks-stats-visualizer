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

import gui.window_main as window_main
# TODO everything in this file lol

import os
os.chdir('C:\\Users\\a626\\Desktop\\kovaaks-stats-visualizer\\src')

playlists = os.path.join(os.getcwd(), 'playlists')
kovaaks = 'C:\\Program Files (x86)\\Steam\\steamapps\\common\\FPSAimTrainer'
stats = os.path.join(kovaaks, 'FPSAimTrainer', 'stats')

app = window_main.AppGUI('dummy config')
app.mainloop()

# a = createplaylistwindow.CreatePlaylistWindow({'name1': None, 'name2': None}, playlists, stats)
