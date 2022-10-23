import os
import statistics
from datetime import datetime

import ksv_exceptions
import ksv_utilities

TARGET_KILLS = 'target_kills'
TARGET_DEATHS = 'target_deaths'
TARGET_TIMEPLAYED = 'target_time_played'
TARGET_TIMELEFT = 'target_time_left'
TARGET_TTK = 'target_ttk'
TARGET_DMGDONE = 'target_damage_done'
TARGET_DMGTAKEN = 'target_damage_taken'
TARGET_HITS = 'target_hits'
TARGET_MISSES = 'target_misses'
TARGET_MIDAIRS = 'target_midairs'
TARGET_DIRECTS = 'target_directs'
TARGET_DIRECTED = 'target_directed'
TARGET_RELOADS = 'target_reloads'
TARGET_DISTANCETRAVELED = 'target_distance_traveled'
TARGET_MBS_POINTS = 'target_mbs_points'
TARGET_SCORE = 'target_score'
TARGET_PAUSES = 'target_pauses'
TARGET_PAUSEDURATION = 'target_pause_duration'
TARGET_SHOTS = 'target_shots'
TARGET_ACCURACY = 'target_accuracy'

TARGETS_AVALIABLE = [
						TARGET_KILLS, TARGET_DEATHS, TARGET_TIMEPLAYED, TARGET_TIMELEFT, TARGET_TTK, 
						TARGET_DMGDONE, TARGET_DMGTAKEN, TARGET_HITS, TARGET_MISSES, TARGET_MIDAIRS, 
						TARGET_DIRECTS, TARGET_DIRECTED, TARGET_RELOADS, TARGET_DISTANCETRAVELED, 
						TARGET_MBS_POINTS, TARGET_SCORE, TARGET_PAUSES, TARGET_PAUSEDURATION, 
						TARGET_SHOTS, TARGET_ACCURACY
					]

# holds the data for a single kovaaks stat file
class Scenario:
	def __init__(self, scenario_path = None):
		if scenario_path is None:
			return None

		self._scenario_path = scenario_path
		self._name = ''
		# self._timestamp = datetime.fromtimestamp(os.path.getctime(self._scenario_path))
		self._timestamp = datetime.strptime(os.path.basename(scenario_path).split(' - Challenge - ')[1], '%Y.%m.%d-%H.%M.%S Stats.csv')
		self._data = dict()

		block = 0
		with open(self._scenario_path, 'r') as fp:
			for line in fp:
				if line == '\n':
					block += 1
					continue

				if block == 2:
					key, value = line.strip('\n').split(':,')
					key = key.lower().replace(' ', '_')

					if key == 'scenario':
						self._name = value
						continue

					if key in ['hash', 'game_version', 'challenge_start']:
						continue

					value = float(value) if '.' in value else int(value)
					self._data[key] = value

	def get_name(self):
		return self._name

	def set_name(self, new_name):
		self._name = new_name

	def get_timestamp(self):
		return self._timestamp

	def set_timestamp(self, new_timestamp):
		self._timestamp = new_timestamp

	def get_data(self):
		return self._data

	def set_data(self, new_data):
		self._data = new_data

	def get_kills(self):
		return self.get_data()['kills']

	def get_deaths(self):
		return self.get_data()['deaths']

	def get_time_played(self):
		return self.get_data()['fight_time']

	def get_time_left(self):
		return self.get_data()['time_remaining']

	def get_ttk(self):
		return self.get_data()['avg_ttk']

	def get_damage_done(self):
		return self.get_data()['damage_done']

	def get_damage_taken(self):
		return self.get_data()['damage_taken']

	def get_hits(self):
		return self.get_data()['hit_count']

	def get_misses(self):
		return self.get_data()['miss_count']

	def get_midairs(self):
		return self.get_data()['midairs']

	def get_midaired(self):
		return self.get_data()['midaired']

	def get_directs(self):
		return self.get_data()['directs']

	def get_directed(self):
		return self.get_data()['directed']

	def get_reloads(self):
		return self.get_data()['reloads']

	def get_distance_traveled(self):
		return self.get_data()['distance_traveled']

	def get_mbs_points(self):
		return self.get_data()['mbs_points']

	def get_score(self):
		return self.get_data()['score']

	def get_pauses(self):
		return self.get_data()['pause_count']

	def get_pause_duration(self):
		return self.get_data()['pause_duration']

	def get_shots(self):
		return self.get_hits() + self.get_misses()

	def get_accuracy(self):
		return self.get_hits() / self.get_shots()

	def get_data_target(self, target):
		if target not in TARGETS_AVALIABLE:
			raise ValueException(f'Invalid Target: {target} @ Scenario.get_data_target')

		if target == TARGET_KILLS:
			return self.get_kills()
		elif target == TARGET_DEATHS:
			return self.get_deaths()
		elif target == TARGET_TIMEPLAYED:
			return self.get_time_played()
		elif target == TARGET_TIMELEFT:
			return self.get_time_left()
		elif target == TARGET_TTK:
			return self.get_ttk()
		elif target == TARGET_DMGDONE:
			return self.get_damage_done()
		elif target == TARGET_DMGTAKEN:
			return self.get_damage_taken()
		elif target == TARGET_HITS:
			return self.get_hits()
		elif target == TARGET_MISSES:
			return self.get_misses()
		elif target == TARGET_MIDAIRS:
			return self.get_midairs()
		elif target == TARGET_DIRECTS:
			return self.get_directs()
		elif target == TARGET_DIRECTED:
			return self.get_directed()
		elif target == TARGET_RELOADS:
			return self.get_reloads()
		elif target == TARGET_DISTANCETRAVELED:
			return self.get_distance_traveled()
		elif target == TARGET_MBS_POINTS:
			return self.get_mbs_points()
		elif target == TARGET_SCORE:
			return self.get_score()
		elif target == TARGET_PAUSES:
			return self.get_pauses()
		elif target == TARGET_PAUSEDURATION:
			return self.get_pause_duration()
		elif target == TARGET_SHOTS:
			return self.get_shots()
		elif target == TARGET_ACCURACY:
			return self.get_accuracy()

	def __str__(self):
		return f'{self.get_name()} | {self.get_timestamp()}'


	# lists all scenario names in the stat folder
	@staticmethod
	def list_scenarios(stats_folder):
		fnames = os.listdir(stats_folder)
		scenarios = [fname.split(' - Challenge - ')[0] for fname in fnames]
		scenarios = list(set(scenarios))
		scenarios.sort()
		return scenarios

	# returns a single scenario object from a list of scenarios
	# various options for date/time and data are avaliable (min, max, average)
	@staticmethod
	def merge_scenarios(scenarios, date_mode = None, time_mode = None, data_mode = None):
		# name
		names = set([sce.get_name() for sce in scenarios])
		if len(names) != 1:
			raise ksv_exceptions.DifferentScenariosException(f'Different scenario names ({len(names)}).')

		sce_name = names.pop()

		# timestamp
		timestamps = [sce.get_timestamp() for sce in scenarios]
		
		# for both date and time modes:
		# 0: min timestamp
		# 1: max timestamp
		# 2: average timestamps
		if date_mode is None:
			raise ksv_exceptions.ModeSelectionException('No date_mode selected')
		elif date_mode == 0:
			f_date = min
		elif date_mode == 1:
			f_date = max
		elif date_mode == 2:
			f_date = ksv_utilities.avg_datetime
		else:
			raise ksv_exceptions.ModeSelectionException(f'Invalid date_mode: {date_mode}')

		if time_mode is None:
			raise ksv_exceptions.ModeSelectionException('No time_mode selected')
		elif time_mode == 0:
			f_time = min		
		elif time_mode == 1:
			f_time = max
		elif time_mode == 2:
			f_time = ksv_utilities.avg_datetime
		else:
			raise ksv_exceptions.ModeSelectionException(f'Invalid time_mode: {time_mode}')

		date = f_date(timestamps).date()
		time = f_time(timestamps).time()
		sce_timestamp = datetime.combine(date, time)

		# data
		# data modes:
		# 0: min
		# 1: max
		# 2: average (returns float)
		if data_mode is None:
			raise ksv_exceptions.ModeSelectionException('No data_mode selected')
		if data_mode == 0:
			f_data = min
		elif data_mode == 1:
			f_data = max
		elif data_mode == 2:
			f_data = statistics.fmean

		sce_data = dict()
		for key in scenarios[0].get_data():
			values = [sce.get_data()[key] for sce in scenarios]
			sce_data[key] = f_data(values)

		# assemble scenario
		merged_scenario = Scenario()
		merged_scenario.set_name(sce_name)
		merged_scenario.set_timestamp(sce_timestamp)
		merged_scenario.set_data(sce_data)

		return merged_scenario
