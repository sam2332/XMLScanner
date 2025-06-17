"""
Whitelist SHA1 management logic for XMLScanner
"""
import json
import os
from libs.Settings import Settings

class WhitelistManager:
    SETTINGS_KEY = 'dll_sha1_whitelist'
    NAME_KEY = 'dll_sha1_whitelist_name'

    def __init__(self):
        self.settings = Settings()
        self.whitelist = set(self.settings.get(self.SETTINGS_KEY, []))
        self.name = self.settings.get(self.NAME_KEY, 'Default Whitelist')

    def add(self, sha1):
        self.whitelist.add(sha1)
        self.save()

    def remove(self, sha1):
        self.whitelist.discard(sha1)
        self.save()

    def get_all(self):
        return sorted(self.whitelist)

    def set_name(self, name):
        self.name = name
        self.settings.set(self.NAME_KEY, name)

    def get_name(self):
        return self.name

    def save(self):
        self.settings.set(self.SETTINGS_KEY, sorted(self.whitelist))
        self.settings.set(self.NAME_KEY, self.name)

    def is_whitelisted(self, sha1):
        return sha1 in self.whitelist
