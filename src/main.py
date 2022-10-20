import configparser

CONFIG_FILENAME = 'config.cfg'

class Main:
	def __init__(self):
		pass

	def load_config(self):
		cfg = configparser.ConfigParser()
		cfg.read(CONFIG_FILENAME) # might raise NameError if non existant
		return cfg