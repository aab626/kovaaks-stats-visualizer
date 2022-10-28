from importlib.resources import path
import json
import os
import io

CONFIG_FILENAME = 'config.json'

SECTION_PATH = 'PATHS'
SECTION_OPTIONS = 'OPTIONS'
SECTION_CSS = 'CSS'
SECTION_GRAPHS = 'GRAPHS'

PATHKEY_KOVAAKS_FOLDER = 'kovaaks_folder'
PATHKEY_KOVAAKS_STATS = 'kovaaks_stats'
PATHKEY_KOVAAKS_PLAYLISTS = 'kovaaks_playlists'
PATHKEY_LOCAL_RESOURCES = 'local_resources'
PATHKEY_LOCAL_PLAYLISTS = 'local_playlists'
PATHKEY_LOCAL_REPORTS = 'local_reports'
PATHKEY_CSS = 'local_css'

GRAPHKEY_COLOR_WEEKLINE = 'color:weekline'
GRAPHKEY_COLOR_MIN = 'color:min'
GRAPHKEY_COLOR_MAX = 'color:max'
GRAPHKEY_COLOR_SCORECURVE = 'color:score_curve'
GRAPHKEY_COLOR_SCOREDATA = 'color:score_data'
GRAPHKEY_COLOR_AVERAGECURVE = 'color:average_curve'
GRAPHKEY_COLOR_AVERAGEDATA = 'color:average_data'
GRAPHKEY_COLOR_XTICKS = 'color:xticks'
GRAPHKEY_COLOR_XTICKSLABELS = 'color:xtickslabels'
GRAPHKEY_COLOR_YTICKS = 'color:yticks'
GRAPHKEY_COLOR_YTICKSLABELS = 'color:ytickslabels'
GRAPHKEY_COLOR_BORDERLEFT = 'color:border_left'
GRAPHKEY_COLOR_BORDERBOTTOM = 'color:border_bottom'

CSSKEY_COLOR_BACKGROUND = 'color:background'
CSSKEY_COLOR_TEXT = 'color:text'
CSSKEY_COLOR_TITLES = 'color:titles'
CSSKEY_COLOR_MAIN = 'color:main'
CSSKEY_COLOR_SECONDARY = 'color:secondary'

OPTIONKEY_AUTO_OPEN_CHECK = 'option:auto_open_check'
OPTIONKEY_GROUP_SESSIONS_CHECK = 'option:group_sessions_check'
OPTIONKEY_GROUP_SESSIONS_NUMBER = 'option:group_sessions_number'
OPTIONKEY_DAYS_CHECK = 'option:days_check'
OPTIONKEY_DAYS_NUMBER = 'option:days_number'

KOVAAKS_STATS_SUBPATH = os.path.join('FPSAimTrainer', 'stats')
KOVAAKS_PLAYLISTS_SUBPATH = os.path.join('FPSAimTrainer', 'Saved', 'SaveGames', 'Playlists')
LOCAL_STYLE_SUBPATH = os.path.join('style_template.css')

class Config:
    def __init__(self, cfg_path):
        self.cfg_path = cfg_path

        self.data_ = dict()
        if os.path.isfile(self.cfg_path):
            self.load_config()
        else:
            self.create_default_config()
            self.save_config()

    # returns the config instance
    def get_data(self):
        return self.data_

    def set_data(self, data):
        self.data_ = data

    def load_config(self):
        with io.open(self.cfg_path, 'r') as fp:
            self.set_data(json.load(fp))

    def save_config(self):
        with io.open(self.cfg_path, 'w') as fp:
            json.dump(self.get_data(), fp, indent=4)

    def create_default_config(self):
        # paths
        self.get_data()[SECTION_PATH] = dict()
        paths = self.get_data()[SECTION_PATH]

        paths[PATHKEY_KOVAAKS_FOLDER] = None
        paths[PATHKEY_KOVAAKS_STATS] = None
        paths[PATHKEY_KOVAAKS_PLAYLISTS] = None

        paths[PATHKEY_LOCAL_RESOURCES] = None
        paths[PATHKEY_LOCAL_PLAYLISTS] = None
        paths[PATHKEY_LOCAL_REPORTS] = None

        paths[PATHKEY_CSS] = None

        # options
        self.get_data()[SECTION_OPTIONS] = dict()
        options = self.get_data()[SECTION_OPTIONS]

        options[OPTIONKEY_AUTO_OPEN_CHECK] = True
        options[OPTIONKEY_GROUP_SESSIONS_CHECK] = True
        options[OPTIONKEY_GROUP_SESSIONS_NUMBER] = 6
        options[OPTIONKEY_DAYS_CHECK] = True
        options[OPTIONKEY_DAYS_NUMBER] = 30

        # css
        self.get_data()[SECTION_CSS] = dict()
        css = self.get_data()[SECTION_CSS]

        css[CSSKEY_COLOR_BACKGROUND] = '#342E5C'
        css[CSSKEY_COLOR_TEXT] = '#F1F1F9'
        css[CSSKEY_COLOR_TITLES] = '#F2FF49'
        css[CSSKEY_COLOR_MAIN] = '#47DDFF'
        css[CSSKEY_COLOR_SECONDARY] = '#EC368D'

        # graphs
        self.get_data()[SECTION_GRAPHS] = dict()
        graphs = self.get_data()[SECTION_GRAPHS]

        graphs[GRAPHKEY_COLOR_WEEKLINE] = '#7f7f7f'
        graphs[GRAPHKEY_COLOR_MIN] = '#47DDFF'
        graphs[GRAPHKEY_COLOR_MAX] = '#47DDFF'
        graphs[GRAPHKEY_COLOR_SCORECURVE] = '#47DDFF'
        graphs[GRAPHKEY_COLOR_SCOREDATA] = '#4781ff'
        graphs[GRAPHKEY_COLOR_AVERAGECURVE] = '#EC368D'
        graphs[GRAPHKEY_COLOR_AVERAGEDATA] = '#F2FF49'
        graphs[GRAPHKEY_COLOR_XTICKS] = '#47DDFF'
        graphs[GRAPHKEY_COLOR_XTICKSLABELS] = '#F1F1F9'
        graphs[GRAPHKEY_COLOR_YTICKS] = '#47DDFF'
        graphs[GRAPHKEY_COLOR_YTICKSLABELS] = '#F1F1F9'
        graphs[GRAPHKEY_COLOR_BORDERLEFT] = '#47DDFF'
        graphs[GRAPHKEY_COLOR_BORDERBOTTOM] = '#47DDFF'

    def get_path(self, path_key):
        paths = self.get_data()[SECTION_PATH]
        if path_key not in paths:
            raise KeyError(f'Invalid config path key: {path_key}')

        return paths[path_key]

    def set_path(self, path_key, path):
        paths = self.get_data()[SECTION_PATH]
        if path_key not in paths:
            raise KeyError(f'Invalid config path key: {path_key}')

        paths[path_key] = path

        if path_key == PATHKEY_KOVAAKS_FOLDER:
            self.update_kovaaks_paths()
        elif path_key == PATHKEY_LOCAL_RESOURCES:
            self.update_local_paths()

        self.save_config()

    def update_kovaaks_paths(self):
        kovaaks_folder = self.get_path(PATHKEY_KOVAAKS_FOLDER)
        if kovaaks_folder is None:
            raise ValueError('KovaaK\'s folder not set!')

        self.set_path(PATHKEY_KOVAAKS_STATS, os.path.join(kovaaks_folder, KOVAAKS_STATS_SUBPATH))
        self.set_path(PATHKEY_KOVAAKS_PLAYLISTS, os.path.join(kovaaks_folder, KOVAAKS_PLAYLISTS_SUBPATH))

    def update_local_paths(self):
        resources_folder = self.get_path(PATHKEY_LOCAL_RESOURCES)
        if resources_folder is None:
            raise ValueError('Resources folder not set!')

        self.set_path(PATHKEY_CSS, os.path.join(resources_folder, LOCAL_STYLE_SUBPATH))

    def get_graph(self, graph_key):
        graphs = self.get_data()[SECTION_GRAPHS]
        if graph_key not in graphs:
            raise KeyError(f'Invalid config graph key: {graph_key}')

        return graphs[graph_key]

    def get_css(self, css_key):
        css = self.get_data()[SECTION_CSS]
        if css_key not in css:
            raise KeyError(f'Invalid config css key: {css_key}')

        return css[css_key]

    def get_option(self, option_key):
        options = self.get_data()[SECTION_OPTIONS]
        if option_key not in options:
            raise KeyError(f'Invalid config option key: {option_key}')

        return options[option_key]

    def set_option(self, option_key, value):
        options = self.get_data()[SECTION_OPTIONS]
        if option_key not in options:
            raise KeyError(f'Invalid config option key: {option_key}')
        
        value_casted = type(options[option_key])(value)
        options[option_key] = value_casted

        self.save_config()


# todo keep track of version in order to upgrade config file