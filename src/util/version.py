from __future__ import annotations
import os
import requests

from models.config import Config

VERSION_FILENAME = 'VERSION'
VERSION_REMOTE_URL = 'https://raw.githubusercontent.com/drizak/kovaaks-stats-visualizer/main/src/VERSION'

class VersionChecker:
    def __init__(self):
        self.version = None

    def get(self):
        return self.version

    def set(self, version):
        self.version = version

    def load_local_version(self):
        version_file_path = os.path.join(os.getcwd(), VERSION_FILENAME)
        with open(version_file_path, 'r') as fp:
            version = self.parse_version_text(fp.read())
            self.set(version)

    def load_remote_version(self):
        r = requests.get(url=VERSION_REMOTE_URL, timeout=5)
        version = self.parse_version_text(r.text)
        self.set(version)

    def parse_version_text(self, version_text):
        version = [int(n) for n in version_text.strip('\n').split('.')]
        return version

    # checks whether a version is higher/lower or equal than other
    # returns:  1:  self is higher than the other version
    #           -1: self is lower than the other
    #           0:  self is equal to the other
    def compare_versions(self, other_version: VersionChecker) -> int:
        v1 = self.get().copy()
        v2 = other_version.get().copy()

        max_len = max(len(v1), len(v2))

        for v in [v1, v2]:
            if len(v) < max_len:
                for i in range(max_len-len(v)):
                    v.append(0)

        i = 0
        while i < max_len:
            if v1[i] > v2[i]:
                return 1
            elif v1[i] < v2[i]:
                return -1

            i += 1
        
        return 0

    def __str__(self):
        return '.'.join([str(n) for n in self.version])