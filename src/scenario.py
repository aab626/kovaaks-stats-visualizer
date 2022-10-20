import os
import datetime
import statistics

import ksv_exceptions
import ksv_utilities

# holds the data for a single kovaaks stat file
class Scenario:
	def __init__(self, scenario_path = None):
		if scenario_path is None:
			return None

		self._scenario_path = scenario_path
		self._name = ''
		self._timestamp = datetime.datetime.fromtimestamp(os.path.getctime(self._scenario_path))
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
		sce_timestamp = datetime.datetime.combine(date, time)

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



stats_folder = os.path.join('C:\\Program Files (x86)\\Steam\\steamapps\\common\\FPSAimTrainer\\FPSAimTrainer\\stats')
scenarios = Scenario.list_scenarios(stats_folder)

s1_path = os.path.join(stats_folder, 'VoxTargetSwitch Click Small - Challenge - 2022.10.19-13.51.05 Stats.csv')
s2_path = os.path.join(stats_folder, 'VoxTargetSwitch Click Small - Challenge - 2022.10.19-13.52.18 Stats.csv')
s3_path = os.path.join(stats_folder, 'VoxTargetSwitch Click Small - Challenge - 2022.10.19-13.53.23 Stats.csv')
s4_path = os.path.join(stats_folder, 'VoxTargetSwitch Click Small - Challenge - 2022.10.19-13.54.28 Stats.csv')
s5_path = os.path.join(stats_folder, 'VoxTargetSwitch Click Small - Challenge - 2022.10.19-13.55.33 Stats.csv')

scen = Scenario(s1_path)


sc_list = [Scenario(s_path) for s_path in [s1_path, s2_path, s3_path, s4_path, s5_path]]
scm = Scenario.merge_scenarios(sc_list, date_mode=2, time_mode=2, data_mode=2)

print(scm)
print(scm.get_name())
print(scm.get_timestamp())
print(scm.get_data())