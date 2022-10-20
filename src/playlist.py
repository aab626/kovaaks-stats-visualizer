import json

# holds the data in a playlist 
class Playlist:
	def __init__(self, name, scenarios_names):
		self.name = name
		self.scenarios_names = scenarios_names

	@staticmethod
	def from_kovaaks_json(playlist_path):
		with open(playlist_path, 'r') as fp:
			data = json.load(fp)

		name = data['playlistName']
		scenarios_names = [sce_dict['scenario_Name'] for sce_dict in data['scenarioList']]

		return Playlist(name, scenarios_names)


ppath = 'C:\\Program Files (x86)\\Steam\\steamapps\\common\\FPSAimTrainer\\FPSAimTrainer\\Saved\\SaveGames\\Playlists\\Void\'s.json'
pl = Playlist.from_kovaaks_json(ppath)
