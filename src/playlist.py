import os
import json
import datetime

PLAYLIST_SOURCE_KOVAAKS = 'source_kovaaks'
PLAYLIST_SOURCE_LOCAL = 'source_local'

# holds the data in a playlist 
class Playlist:
	def __init__(self, name, scenarios_names, source, full_path):
		self.name = name
		self.scenarios_names = scenarios_names

		assert source in [PLAYLIST_SOURCE_KOVAAKS, PLAYLIST_SOURCE_LOCAL]
		self.source = source

		self.full_path = full_path

	def save_to_local(self, local_playlists_path):
		data = dict()
		data['name'] = self.name
		data['scenarios_names'] = self.scenarios_names

		fname = f'playlist_{datetime.datetime.now().isoformat()}.json'.replace(":","_")
		self.full_path = os.path.join(local_playlists_path, fname)

		with open(self.full_path, 'w') as fp:
			json.dump(data, fp)

	def get_listname(self):
		if self.source == PLAYLIST_SOURCE_KOVAAKS:
			source_mark = 'K'
		elif self.source == PLAYLIST_SOURCE_LOCAL:
			source_mark = 'S'
		
		return f'[{source_mark}] {self.name}'

	def delete(self):
		os.remove(self.full_path)

	@staticmethod
	def from_kovaaks_json(playlist_path):
		with open(playlist_path, 'r') as fp:
			data = json.load(fp)

		name = data['playlistName']
		scenarios_names = [sce_dict['scenario_Name'] for sce_dict in data['scenarioList']]
		return Playlist(name, scenarios_names, PLAYLIST_SOURCE_KOVAAKS, playlist_path)

	@staticmethod
	def from_local_json(playlist_path):
		with open(playlist_path, 'r') as fp:
			data = json.load(fp)

		name = data['name']
		scenarios_names = data['scenarios_names']
		return Playlist(name, scenarios_names, PLAYLIST_SOURCE_LOCAL, playlist_path)

	@staticmethod
	def get_kovaaks_playlists(kovaaks_playlists_path):
		print(kovaaks_playlists_path, flush=True)
		jsons = [f for f in os.listdir(kovaaks_playlists_path) if os.path.splitext(f)[1].lower() == '.json']
		playlists = [Playlist.from_kovaaks_json(os.path.join(kovaaks_playlists_path, f)) for f in jsons]
		return playlists

	@staticmethod
	def get_local_playlists(local_playlists_path):
		jsons = [f for f in os.listdir(local_playlists_path) if os.path.splitext(f)[1].lower() == '.json']
		playlists = [Playlist.from_local_json(os.path.join(local_playlists_path, f)) for f in jsons]
		return playlists
