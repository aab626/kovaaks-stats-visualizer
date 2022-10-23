import os
import io
from datetime import datetime
from datetime import date

import numpy as np
from matplotlib import pyplot as plt
from scipy.interpolate import make_interp_spline

import yattag

from playlist import Playlist
from scenario import Scenario
from scenario import TARGET_SCORE

CHAR_DELTA = '\u0394'
CHAR_TRIANGLE = '\u2BC8'

class Report:
	def __init__(self, playlist, kovaaks_stats_folder, reports_folder):
		self.playlist = playlist
		self.kovaaks_stats_folder = kovaaks_stats_folder
		self.reports_folder = reports_folder

	# Loads the stats for a given scenario, up to days_n number of days
	# if days_n is None, then loads all stats
	def load_scenario_stats(self, scenario_name, days_n = None):
		scenarios = []
		for fname in os.listdir(self.kovaaks_stats_folder):
			scen_path = os.path.join(self.kovaaks_stats_folder, fname)
			scen = Scenario(scen_path)

			if scen.get_name() == scenario_name:
				if days_n is None:
					scenarios.append(scen)
				else:
					days_delta = abs((scen.get_timestamp().date() - date.today()).days)
					if days_delta <= days_n:
						scenarios.append(scen)

		return scenarios

	# returns the x,y data for a given target
	# where:	x are datetime
	#			y are int/float
	def make_plottable_data(self, scenario_list, target):
		x = [sce.get_timestamp() for sce in scenario_list]
		y = [sce.get_data_target(target) for sce in scenario_list]
		return x,y

	def get_data_values(self, data_y):
		data = dict()
		data['max'] = round(max(data_y))
		data['min'] = round(min(data_y))

		data['avg'] = round(np.mean(data_y))
		data['std'] = round(np.std(data_y), 3)

		return data

	def make_averaged_data(self, data_y, average_sessions = 1):
		data_y_average = []

		i = 0
		while i < len(data_y):
			j = max(i - (average_sessions - 1), 0)
			data_slice = data_y[j: i+1]
			y_avg = np.mean(data_slice)
			data_y_average.append(y_avg)
			i += 1

		return data_y_average

	# returns a list of scenarios merged by a hourly threshold
	# hours_n recommended to be set as: 24/times_trained_a_day
	#         ex: if you train 3 times a day: 24/3 = 8
	#         floats quotients are accepted (ex: 24/5)
	def group_sessions(self, scenario_list, hours_n):
		threshold = hours_n*60*60
		i, j = 0, 0
		scenarios_merged = []
		while i < len(scenario_list):
			j = i
			scen0 = scenario_list[i]
			scen1 = scen0
			while j< len(scenario_list) and abs((scenario_list[j].get_timestamp() - scen0.get_timestamp()).total_seconds()) <= threshold:
				j += 1

			scen_merged = Scenario.merge_scenarios(scenario_list[i:j], 0, 0, 2)
			scenarios_merged.append(scen_merged)

			i = j

		return scenarios_merged

	def plot(self, data_x, data_y, data_y_avg, data_y_values, scenario_name, folder_path):
		if len(data_x) >= 3:
			# score curve
			spline_k = 3 if len(data_x) > 3 else 2
			x_floats = [date.timestamp() for date in data_x]
			spline_score = make_interp_spline(x_floats, data_y, k=spline_k)
			x_smooth_floats = np.linspace(x_floats[0], x_floats[-1], 500)
			x_smooth = [datetime.fromtimestamp(t) for t in x_smooth_floats]
			y_smooth = spline_score(x_smooth_floats)

			# average curve
			spline_avg = make_interp_spline(x_floats, data_y_avg, k=spline_k)
			y_smooth_avg = spline_avg(x_smooth_floats)

		fig, ax = plt.subplots(figsize=(10, 5))

		# plot max and min
		min_y = data_y_values['min']
		max_y = data_y_values['max']
		ax.axhline(y=min_y, linestyle=(0, (5,5)), color='#47DDFF', linewidth=0.75, xmin=min(data_x))
		ax.axhline(y=max_y, linestyle=(0, (5,5)), color='#47DDFF', linewidth=0.75, xmin=min(data_x))

		# plot curves
		if len(data_x) >= 3:
			ax.plot(x_smooth, y_smooth, '-', color='#47DDFF', label='score spline')
			ax.plot(x_smooth, y_smooth_avg, '--', color='#EC368D', label='avg spline')
		else:
			ax.plot(data_x, data_y, '-', color='#47DDFF', label='score line') 
			ax.plot(data_x, data_y_avg, '--', color='#EC368D', label='avg line') 

		# plot points
		ax.plot(data_x, data_y, 'o', color='#4781ff', label='score')
		ax.plot(data_x, data_y_avg, 'o', color='#F2FF49', label='avg')

		# ticks
		xticks = []
		xticks.append(data_x[0])
		xticks.append(np.quantile(data_x, 0.25))
		xticks.append(np.quantile(data_x, 0.5))
		xticks.append(np.quantile(data_x, 0.75))
		xticks.append(data_x[-1])
		xticks_str = [d.strftime('%d-%m') for d in xticks]

		yticks = []
		yticks.append(min(data_y))
		yticks.append(np.quantile(data_y, 0.25))
		yticks.append(np.quantile(data_y, 0.5))
		yticks.append(np.quantile(data_y, 0.75))
		yticks.append(max(data_y))

		if round(min_y) not in [round(y) for y in yticks]:
			yticks.append(min_y)

		if round(max_y) not in [round(y) for y in yticks]:
			yticks.append(max_y)

		yticks.sort()
		yticks_str = [round(y) for y in yticks]

		ax.set_xticks(xticks)
		ax.set_xticklabels(xticks_str)
		ax.tick_params(axis='x', labelsize=7, color='#47DDFF', labelcolor='#F1F1F9')

		ax.set_yticks(yticks)
		ax.set_yticklabels(yticks_str)
		ax.tick_params(axis='y', labelsize=7, color='#47DDFF', labelcolor='#F1F1F9')

		# borders
		ax.spines['top'].set_visible(False)
		ax.spines['right'].set_visible(False)

		ax.spines['left'].set_color('#47DDFF')
		ax.spines['bottom'].set_color('#47DDFF')

		# layout
		fig.tight_layout()

		fname = f'{scenario_name}.png'
		fpath = os.path.join(folder_path, fname)
		fig.savefig(fpath, dpi=300, transparent=True)

		return fpath

	def generate_report(self):
		# report folder creation
		# report_folder_name = f'KSV_report_{datetime.now().isoformat().replace(":","_")}'
		report_folder_name = 'KSV_report_DEBUGFOLDER'
		resources_folder_name = 'resources'

		report_folder_path = os.path.join(self.reports_folder, report_folder_name)
		resources_folder_path = os.path.join(self.reports_folder, report_folder_name, resources_folder_name)
		# os.mkdir(report_folder_path)
		# os.mkdir(resources_folder_path)

		# document creation
		doc, tag, text = yattag.Doc().tagtext()

		doc.asis('<!DOCTYPE html>')
		with tag('html'):
			with tag('head'):
				with tag('title'):
					text('KovaaK\'s Stat Report')

				doc.stag('link', rel='stylesheet', href='style.css')

			with tag('body'):
				with tag('div', klass='header'):
					with tag('div', klass='top'):
						with tag('h1', klass='title'):
							text('KOVAAK\'S STAT REPORT')

						with tag('p', klass='author'):
							text(f'Made by st{CHAR_DELTA}r')

					with tag('div', klass='bottom'):
						with tag('a', klass='link-homepage', href='https://github.com/drizak/kovaaks-stats-visualizer'):
							text('GitHub Repository')

						with tag('p', klass='timestamp'):
							text(f'Generated at {datetime.now().strftime("%d-%m-%y @ %H:%M:%S")}')

				doc.stag('hr', klass='main-sep')
				
				with tag('div', klass='content'):
					with tag('h2', klass='playlist-name'):
						text(f'Playlist: {self.playlist.name}')

					i = 0
					for scenario_name in playlist.scenarios_names:
						with tag('div', klass='scenario'):
							with tag('div', klass='title'):
								with tag('p', klass='icon'):
									text(CHAR_TRIANGLE)
								with tag('h3', klass='name'):
									text(scenario_name)

							scenarios = self.load_scenario_stats(scenario_name, days_n=30)
							scenarios_grouped = self.group_sessions(scenarios, hours_n=8)
							x, data_y_ungrouped = self.make_plottable_data(scenarios, target=TARGET_SCORE)
							data_y_values = self.get_data_values(data_y_ungrouped)

							data = self.make_plottable_data(scenarios_grouped, target=TARGET_SCORE)
							data_y_avg = self.make_averaged_data(data[1], average_sessions=5)
							data_y_avg_ungrouped = self.make_averaged_data(data_y_ungrouped, average_sessions=5)
							data_y_avg_values = self.get_data_values(data_y_avg_ungrouped)

							with tag('div', klass='content'):
								img_path = self.plot(data[0], data[1], data_y_avg, data_y_values, scenario_name, resources_folder_path)
								doc.stag('img', src=img_path, klass='graph')

								with tag('div', klass='data'):
									with tag('h4', klass='title'):
										text('Ungrouped Stats')

									doc.stag('hr', klass='data-sep')

									with tag('table', klass='datatable'):
										with tag('tbody'):
											with tag('tr', klass='row1'):
												with tag('td'):
													text('')
												with tag('td', klass='bottomborder'):
													text('Original')
												with tag('td', klass='bottomborder'):
													text('Average')

											with tag('tr', klass='row2'):
												with tag('td', klass='category rightborder'):
													text('Max')
												with tag('td', klass='value'):
													text(data_y_values['max'])
												with tag('td', klass='value'):
													text(data_y_avg_values['max'])

											with tag('tr', klass='row3'):
												with tag('td', klass='category rightborder'):
													text('Min')
												with tag('td', klass='value'):
													text(data_y_values['min'])
												with tag('td', klass='value'):
													text(data_y_avg_values['min'])

											with tag('tr', klass='row4'):
												with tag('td', klass='category rightborder'):
													text('Avg')
												with tag('td', klass='value'):
													text(data_y_values['avg'])
												with tag('td', klass='value'):
													text(data_y_avg_values['avg'])

											with tag('tr', klass='row5'):
												with tag('td', klass='category rightborder'):
													text('StDev')
												with tag('td', klass='value'):
													text(data_y_values['std'])
												with tag('td', klass='value'):
													text(data_y_avg_values['std'])

						if i != len(playlist.scenarios_names) - 1:
							doc.stag('hr', klass='scenario-sep')

						i += 1

		# writing file
		fname = f'KSV_report.html'
		fpath = os.path.join(report_folder_path, fname)

		with io.open(fpath, 'w', encoding='utf-8') as fp:
			out = yattag.indent(doc.getvalue())
			fp.write(out)
		
		# # todo
		# # fname = f'KSV_report_{datetime.now().isoformat().replace(":","_")}.html'
		# fname = 'report_test.html'

		# fpath = os.path.join(self.reports_folder, fname)
		# with open(fpath, 'w') as fp:
		# 	out = yattag.indent(doc.getvalue())
		# 	fp.write(out)

		# return fpath





stat_path = 'C:\\Program Files (x86)\\Steam\\steamapps\\common\\FPSAimTrainer\\FPSAimTrainer\\stats'
pl_path = 'C:\\Program Files (x86)\\Steam\\steamapps\\common\\FPSAimTrainer\\FPSAimTrainer\\Saved\\SaveGames\\Playlists\\Zeeq - Pyth.json'
rep_folder = 'C:\\Users\\a626\\Desktop\\kovaaks-stats-visualizer\\src\\reports'
playlist = Playlist.from_kovaaks_json(pl_path)
rep = Report(playlist, stat_path, rep_folder)
rep.generate_report()

# for scen_name in playlist.scenarios_names:
# 	print(scen_name, flush=True)
# 	scen = rep.load_scenario_stats(scen_name)
# 	grp = rep.group_sessions(scen, 8)

# 	data = rep.make_plotabble_data(grp, TARGET_SCORE)
# 	data_avg = rep.make_averaged_data(data[1], 5)

# 	rep.plot(data[0], data[1], data_avg)