import os

from models.config import Config
import models.config as ckeys
from models.config import CONFIG_FILENAME
from gui.window_main import MainWindow
from gui.messagebox import KSVMessageBox
from gui.window_promptkovaaksfolder import BrowseKovaaksFolder
from util.version import VersionChecker

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

        version_local = VersionChecker()
        version_local.load_local_version()
        self.cfg.set_app(ckeys.APPKEY_VERSION, str(version_local))
        self.cfg.set_app(ckeys.APPKEY_VERSION_OUTDATED, False)
        self.cfg.set_app(ckeys.APPKEY_VERSION_MISSCHECK, False)

        try:
            version_remote = VersionChecker()
            version_remote.load_remote_version()

            if version_local.compare_versions(version_remote) < 0:
                self.cfg.set_app(ckeys.APPKEY_VERSION_OUTDATED, True)
        except Exception as e:
            self.cfg.set_app(ckeys.APPKEY_VERSION_MISSCHECK, True)

        # check folders, then run koovaks folder prompt if no config was found earlier
        folders = self.create_folders()
        if not cfg_exists_at_run or self.cfg.get_path(ckeys.PATHKEY_KOVAAKS_FOLDER) is None:
            self.cfg.set_path(ckeys.PATHKEY_LOCAL_RESOURCES, os.path.join(os.getcwd(), LOCAL_RESOURCES_FOLDERNAME))
            self.cfg.set_path(ckeys.PATHKEY_LOCAL_PLAYLISTS, folders[ckeys.PATHKEY_LOCAL_PLAYLISTS])
            self.cfg.set_path(ckeys.PATHKEY_LOCAL_REPORTS, folders[ckeys.PATHKEY_LOCAL_REPORTS])
            
            icon_error_path = os.path.join(self.cfg.get_path(ckeys.PATHKEY_LOCAL_RESOURCES), ICON_ERROR_FILENAME)
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

        return {ckeys.PATHKEY_LOCAL_PLAYLISTS: local_playlists_path, ckeys.PATHKEY_LOCAL_REPORTS: local_reports_path}
        
# execution
if __name__ == '__main__':
    os.chdir(os.path.dirname(__file__))
    Main()