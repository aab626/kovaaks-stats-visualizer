import os

from models.config import Config
from models.config import CONFIG_FILENAME
from models.config import PATHKEY_KOVAAKS_FOLDER, PATHKEY_LOCAL_RESOURCES, PATHKEY_LOCAL_PLAYLISTS, PATHKEY_LOCAL_REPORTS
from gui.window_main import MainWindow
from gui.window_promptkovaaksfolder import BrowseKovaaksFolder

LOCAL_RESOURCES_FOLDERNAME = 'resources'
LOCAL_PLAYLIST_FOLDERNAME = 'playlists'
LOCAL_REPORTS_FOLDERNAME = 'reports'

ICON_ERROR_FILENAME = 'icon_error.png'

class Main():
    def __init__(self):
        # check config existance at run
        cfg_path = os.path.join(os.getcwd(), CONFIG_FILENAME)
        cfg_exists_at_run = os.path.exists(cfg_path)
        self.cfg = Config(cfg_path)

        # check folders, then run koovaks folder prompt if no config was found earlier
        folders = self.create_folders()
        if not cfg_exists_at_run or self.cfg.get_path(PATHKEY_KOVAAKS_FOLDER) is None:
            self.cfg.set_path(PATHKEY_LOCAL_RESOURCES, os.path.join(os.getcwd(), LOCAL_RESOURCES_FOLDERNAME))
            self.cfg.set_path(PATHKEY_LOCAL_PLAYLISTS, folders[PATHKEY_LOCAL_PLAYLISTS])
            self.cfg.set_path(PATHKEY_LOCAL_REPORTS, folders[PATHKEY_LOCAL_REPORTS])
            
            icon_error_path = os.path.join(self.cfg.get_path(PATHKEY_LOCAL_RESOURCES), ICON_ERROR_FILENAME)
            window = BrowseKovaaksFolder(self.cfg, icon_error_path)
            window.mainloop()

        # run the main gui
        app = MainWindow(self.cfg)
        app.mainloop()

    def create_folders(self):
        local_playlists_path = os.path.join(os.getcwd(), LOCAL_PLAYLIST_FOLDERNAME)
        if not os.path.isdir(local_playlists_path):
            os.mkdir(local_playlists_path)

        local_reports_path = os.path.join(os.getcwd(), LOCAL_REPORTS_FOLDERNAME)
        if not os.path.isdir(local_reports_path):
            os.mkdir(local_reports_path)

        return {PATHKEY_LOCAL_PLAYLISTS: local_playlists_path, PATHKEY_LOCAL_REPORTS: local_reports_path}

        


        

if __name__ == '__main__':
    # todo update notification
    Main()