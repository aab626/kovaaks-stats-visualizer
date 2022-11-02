import os
import io
from datetime import datetime, date, timedelta

import numpy as np
from matplotlib import pyplot as plt
import matplotlib.patheffects as pe
from scipy.interpolate import PchipInterpolator

import yattag
import cssmin

from models.scenario import Scenario
from models.scenario import TARGET_SCORE
import models.config as ckeys
from models.config import Config

CHAR_DELTA = '\u0394'
CHAR_TRIANGLE = '\u2BC8'
CHAR_TRIANGLE_SMALL_UP = '\u25B4'
CHAR_TRIANGLE_SMALL_DOWN = '\u25BE'

REPORT_RESOURCES_FOLDERNAME = 'report_resources'
REPORT_FILENAME = 'KSV_report.html'
CSS_FILENAME = 'style.css'

CSS_REPLACER_MARK = '$REPLACEME$'
CSS_REPLACER_COLOR_BG = 'COLOR-BG'
CSS_REPLACER_COLOR_TEXT = 'COLOR-TEXT'
CSS_REPLACER_COLOR_TITLES = 'COLOR-TITLES'
CSS_REPLACER_COLOR_MAIN = 'COLOR-MAIN'
CSS_REPLACER_COLOR_SECONDARY = 'COLOR-SECONDARY'

class Report:
	def __init__(self, playlist, cfg: Config):
		self.playlist = playlist
		self.cfg = cfg

		self.report_folder_path = None
		self.resources_folder_path = None

	# Loads the stats for a given scenario, up to days_n number of days
	# if days_n is None, then loads all stats
	def load_scenario_stats(self, scenario_name, days_n = None):
		scenarios = []
		for fname in os.listdir(self.cfg.get_path(ckeys.PATHKEY_KOVAAKS_STATS)):
			scen_path = os.path.join(self.cfg.get_path(ckeys.PATHKEY_KOVAAKS_STATS), fname)
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

	# plots a graph of one scenario
	# data_x: datetimes
	# data_y: scores or target value
	# data_y_avg: averages over time of data_y
	# data_y_values: statistical values of data_y (min, max, etc)
	def plot(self, data_x, data_y, data_y_avg = None, data_y_values = None, scenario_name = None, folder_path = None):
		if data_y_values is None or scenario_name is None or folder_path is None:
			raise ValueError('data_y_values, scenario_name, folder_path cannot be None!')

		if len(data_x) >= 2:
			# smooth x data
			x_floats = [date.timestamp() for date in data_x]
			x_smooth_floats = np.linspace(x_floats[0], x_floats[-1], 500)
			x_smooth = [datetime.fromtimestamp(t) for t in x_smooth_floats]
			
			# score curve
			interpolated_score = PchipInterpolator(x_floats, data_y)
			y_smooth = interpolated_score(x_smooth_floats)

			# average curve
			if data_y_avg is not None:
				interpolated_avg = PchipInterpolator(x_floats, data_y_avg)
				y_smooth_avg = interpolated_avg(x_smooth_floats)

		fig, ax = plt.subplots(figsize=(10, 5))

		# plot week lines
		min_x = min(data_x)
		x = max(data_x) - timedelta(days=7)
		while x > min_x:
			ax.axvline(x=x, linestyle=(0, (5, 5)), color=self.cfg.get_graph(ckeys.GRAPHKEY_COLOR_WEEKLINE), alpha=0.3, linewidth=0.75)
			x = x - timedelta(days=7)

		# plot max and min
		min_y = data_y_values['min']
		max_y = data_y_values['max']
		ax.axhline(y=min_y, linestyle=(0, (5, 5)), color=self.cfg.get_graph(ckeys.GRAPHKEY_COLOR_MIN), alpha=0.5, linewidth=0.75, xmin=min(data_x))
		ax.axhline(y=max_y, linestyle=(0, (5, 5)), color=self.cfg.get_graph(ckeys.GRAPHKEY_COLOR_MAX), alpha=0.5, linewidth=0.75, xmin=min(data_x))

		# plot curves
		if len(data_x) >= 2:
			ax.plot(x_smooth, y_smooth, '-', color=self.cfg.get_graph(ckeys.GRAPHKEY_COLOR_SCORECURVE))

			if data_y_avg is not None:
				ax.plot(x_smooth, y_smooth_avg, '--', color=self.cfg.get_graph(ckeys.GRAPHKEY_COLOR_AVERAGECURVE))
		else:
			ax.plot(data_x, data_y, '-', color=self.cfg.get_graph(ckeys.GRAPHKEY_COLOR_SCORECURVE))

			if data_y_avg is not None:
				ax.plot(data_x, data_y_avg, '--', color=self.cfg.get_graph(ckeys.GRAPHKEY_COLOR_AVERAGECURVE))

		# plot points
		ax.plot(data_x, data_y, 'o', color=self.cfg.get_graph(ckeys.GRAPHKEY_COLOR_SCOREDATA), label='score')

		if data_y_avg is not None:
			ax.plot(data_x, data_y_avg, 'o', color=self.cfg.get_graph(ckeys.GRAPHKEY_COLOR_AVERAGEDATA), label='avg')

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
		yticks = list(set([round(y) for y in yticks]))

		if round(min_y) not in yticks:
			yticks.append(min_y)

		if round(max_y) not in yticks:
			yticks.append(max_y)

		yticks.sort()
		yticks_str = [round(y) for y in yticks]

		ax.set_xticks(xticks)
		ax.set_xticklabels(xticks_str)
		ax.tick_params(axis='x', labelsize=7, color=self.cfg.get_graph(ckeys.GRAPHKEY_COLOR_XTICKS), labelcolor=self.cfg.get_graph(ckeys.GRAPHKEY_COLOR_XTICKSLABELS))

		ax.set_yticks(yticks)
		ax.set_yticklabels(yticks_str)
		ax.tick_params(axis='y', labelsize=7, color=self.cfg.get_graph(ckeys.GRAPHKEY_COLOR_YTICKS), labelcolor=self.cfg.get_graph(ckeys.GRAPHKEY_COLOR_YTICKSLABELS))

		# borders
		ax.spines['top'].set_visible(False)
		ax.spines['right'].set_visible(False)

		ax.spines['left'].set_color(self.cfg.get_graph(ckeys.GRAPHKEY_COLOR_BORDERLEFT))
		ax.spines['bottom'].set_color(self.cfg.get_graph(ckeys.GRAPHKEY_COLOR_BORDERBOTTOM))

		# annotations
		if self.cfg.get_option(ckeys.OPTIONKEY_PERCENTAGES_CHECK) and self.cfg.get_option(ckeys.OPTIONKEY_AVERAGE_CHECK):
			for i in range(len(data_y)):
				percentage = data_y[i]/data_y_avg[i]*100

				if percentage != 100:
					percentage_txt = round(percentage - 100 if percentage > 100 else 100 - percentage, 1)
					color = self.cfg.get_graph(ckeys.GRAPHKEY_COLOR_PERCENTAGE_POSITIVE) if percentage > 100 else self.cfg.get_graph(ckeys.GRAPHKEY_COLOR_PERCENTAGE_NEGATIVE)
					symbol = CHAR_TRIANGLE_SMALL_UP if percentage > 100 else CHAR_TRIANGLE_SMALL_DOWN
					text = f'{symbol} {percentage_txt}%'
					y_offset = 50 if percentage > 100 else -50

					ax.annotate(text, (data_x[i], data_y[i]), ha='center', textcoords='offset pixels', xytext=(0, y_offset), 
                                            color=color, fontsize=9, path_effects=[pe.withStroke(linewidth=1.5, foreground=self.cfg.get_graph(ckeys.GRAPHKEY_COLOR_PERCENTAGE_OUTLINE))])

		# layout
		fig.tight_layout()

		fname = f'{scenario_name}.png'
		fpath = os.path.join(folder_path, fname)
		fig.savefig(fpath, dpi=300, transparent=True)

		return fpath

	# returns the body of the report html file
	def generate_report(self):
		folders = self.create_folders()
		
		# document creation
		doc, tag, text = yattag.Doc().tagtext()

		doc.asis('<!DOCTYPE html>')
		with tag('html'):
			with tag('head'):
				with tag('title'):
					text('KovaaK\'s Stat Report')

				css_path = os.path.join(self.resources_folder_path, CSS_FILENAME)
				css_path_href = os.path.join('.', os.path.relpath(css_path, self.report_folder_path))
				doc.stag('link', rel='stylesheet', href=css_path_href)

			with tag('body'):
				with tag('div', klass='header'):
					with tag('div', klass='top'):
						with tag('h1', klass='title'):
							text('KOVAAK\'S STAT REPORT')

						with tag('p', klass='author'):
							text(f'Made by st{CHAR_DELTA}r')

					with tag('div', klass='bottom'):
						with tag('a', klass='link-homepage', href='https://github.com/drizak/kovaaks-stats-visualizer', target='_blank'):
							text('GitHub Repository')

						with tag('p', klass='timestamp'):
							text(f'Generated at {datetime.now().strftime("%d-%m-%y @ %H:%M:%S")}')

				doc.stag('hr', klass='main-sep')
				
				with tag('div', klass='content'):
					with tag('h2', klass='playlist-name'):
						text(f'Playlist: {self.playlist.name}')

					i = 0
					for scenario_name in self.playlist.scenarios_names:
						with tag('div', klass='scenario'):
							with tag('div', klass='title'):
								with tag('p', klass='icon'):
									text(f'{str(i+1).zfill(2)} {CHAR_TRIANGLE}')
								with tag('h3', klass='name'):
									text(scenario_name)
							
							days = self.cfg.get_option(ckeys.OPTIONKEY_DAYS_NUMBER) if self.cfg.get_option(ckeys.OPTIONKEY_DAYS_CHECK) else None
							scenarios = self.load_scenario_stats(scenario_name, days_n=days)

							# if there are played scenarios, plot graph
							if len(scenarios) > 0:
								if self.cfg.get_option(ckeys.OPTIONKEY_GROUP_SESSIONS_CHECK):
									hours_threshold = self.cfg.get_option(ckeys.OPTIONKEY_GROUP_SESSIONS_NUMBER)
									scenarios_grouped = self.group_sessions(scenarios, hours_n=hours_threshold)
									data = self.make_plottable_data(scenarios_grouped, target=TARGET_SCORE)
								else:
									data = self.make_plottable_data(scenarios, target=TARGET_SCORE)

								x_ungrouped, y_ungrouped = self.make_plottable_data(scenarios, target=TARGET_SCORE)
								y_values = self.get_data_values(y_ungrouped)

								# plot averages
								if self.cfg.get_option(ckeys.OPTIONKEY_AVERAGE_CHECK):
									y_avg = self.make_averaged_data(data[1], average_sessions=5)
									y_avg_ungrouped = self.make_averaged_data(y_avg, average_sessions=5)
									y_avg_values = self.get_data_values(y_avg_ungrouped)
								else:
									y_avg = None

								with tag('div', klass='content'):
									img_path = self.plot(data[0], data[1], y_avg, y_values, scenario_name, self.resources_folder_path)
									img_path_href = os.path.join('.', os.path.relpath(img_path, self.report_folder_path))
									doc.stag('img', src=img_path_href, klass='graph')

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
														text(y_values['max'])
													with tag('td', klass='value'):
														text(y_avg_values['max'] if self.cfg.get_option(ckeys.OPTIONKEY_AVERAGE_CHECK) else '-')

												with tag('tr', klass='row3'):
													with tag('td', klass='category rightborder'):
														text('Min')
													with tag('td', klass='value'):
														text(y_values['min'])
													with tag('td', klass='value'):
														text(y_avg_values['min'] if self.cfg.get_option(ckeys.OPTIONKEY_AVERAGE_CHECK) else '-')

												with tag('tr', klass='row4'):
													with tag('td', klass='category rightborder'):
														text('Avg')
													with tag('td', klass='value'):
														text(y_values['avg'])
													with tag('td', klass='value'):
														text(y_avg_values['avg'] if self.cfg.get_option(ckeys.OPTIONKEY_AVERAGE_CHECK) else '-')

												with tag('tr', klass='row5'):
													with tag('td', klass='category rightborder'):
														text('StDev')
													with tag('td', klass='value'):
														text(y_values['std'])
													with tag('td', klass='value'):
														text(y_avg_values['std'] if self.cfg.get_option(ckeys.OPTIONKEY_AVERAGE_CHECK) else '-')

							# otherwise, display an alert in the report
							else:
								with tag('div', klass='no-scenarios'):
									with tag('p'):
										text('No stat files found!')



						if i != len(self.playlist.scenarios_names) - 1:
							doc.stag('hr', klass='scenario-sep')

						i += 1

		return doc.getvalue()

	def create_folders(self):
		report_folder_name = f'KSV_report_{datetime.now().isoformat().replace(":","_").replace("T","_")}'
		self.report_folder_path = os.path.join(self.cfg.get_path(ckeys.PATHKEY_LOCAL_REPORTS), report_folder_name)
		self.resources_folder_path = os.path.join(self.cfg.get_path(ckeys.PATHKEY_LOCAL_REPORTS), report_folder_name, REPORT_RESOURCES_FOLDERNAME)

		os.mkdir(self.report_folder_path)
		os.mkdir(self.resources_folder_path)

	def write_report(self, report_content):
		fpath = os.path.join(self.report_folder_path, REPORT_FILENAME)
		with io.open(fpath, 'w', encoding='utf-8') as fp:
			fp.write(report_content)

		return fpath

	def generate_css(self):
		template_css_path = self.cfg.get_path(ckeys.PATHKEY_CSS)
		with io.open(template_css_path, 'r') as fp:
			css_content = fp.read()

		replacer_color_bg = CSS_REPLACER_MARK + CSS_REPLACER_COLOR_BG + CSS_REPLACER_MARK
		replacer_color_text = CSS_REPLACER_MARK + CSS_REPLACER_COLOR_TEXT + CSS_REPLACER_MARK
		replacer_color_titles = CSS_REPLACER_MARK + CSS_REPLACER_COLOR_TITLES + CSS_REPLACER_MARK
		replacer_color_main = CSS_REPLACER_MARK + CSS_REPLACER_COLOR_MAIN + CSS_REPLACER_MARK
		replacer_color_secondary = CSS_REPLACER_MARK + CSS_REPLACER_COLOR_SECONDARY + CSS_REPLACER_MARK
		
		css_content = css_content.replace(replacer_color_bg, self.cfg.get_css(ckeys.CSSKEY_COLOR_BACKGROUND))
		css_content = css_content.replace(replacer_color_text, self.cfg.get_css(ckeys.CSSKEY_COLOR_TEXT))
		css_content = css_content.replace(replacer_color_titles, self.cfg.get_css(ckeys.CSSKEY_COLOR_TITLES))
		css_content = css_content.replace(replacer_color_main, self.cfg.get_css(ckeys.CSSKEY_COLOR_MAIN))
		css_content = css_content.replace(replacer_color_secondary, self.cfg.get_css(ckeys.CSSKEY_COLOR_SECONDARY))

		css_content_minified = cssmin.cssmin(css_content)
		return css_content_minified

	def write_css(self, css_content):
		fpath = os.path.join(self.resources_folder_path, CSS_FILENAME)
		with io.open(fpath, 'w', encoding='utf-8') as fp:
			fp.write(css_content)
