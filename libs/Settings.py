import json

class Settings:
    '''json getter and setter for settings.json'''
    def __init__(self, path: str = 'settings.json'):
        self.path = path
        self._load()

    def _load(self):
        '''Load settings from JSON file'''
        try:
            with open(self.path, 'r', encoding='utf-8') as f:
                self.settings = json.load(f)
        except FileNotFoundError:
            self.settings = {}
        except json.JSONDecodeError:
            print(f"Error decoding JSON from {self.path}. Using empty settings.")
            self.settings = {}
    def _save(self):
        '''Save settings to JSON file'''
        with open(self.path, 'w', encoding='utf-8') as f:
            json.dump(self.settings, f, indent=4)
    def get(self, key: str, default=None):
        '''Get a setting by key, return default if not found'''
        return self.settings.get(key, default)
    def set(self, key: str, value):
        '''Set a setting by key and value, save to file'''
        self.settings[key] = value
        self._save()
    def remove(self, key: str):
        '''Remove a setting by key, save to file'''
        if key in self.settings:
            del self.settings[key]
            self._save()
    def clear(self):
        '''Clear all settings, save to file'''
        self.settings.clear()
        self._save()
    def reset(self):
        '''Reset settings to default values, save to file'''
        self.settings = {
            'base_directory': '',
            'search_string': '',
            'last_scan_date': '',
            'scan_results': []
        }
        self._save()
    def __getitem__(self, key: str):
        '''Get a setting using dictionary-like access'''
        return self.get(key)
    def __setitem__(self, key: str, value):
        '''Set a setting using dictionary-like access'''
        self.set(key, value)
    def __delitem__(self, key: str):
        '''Remove a setting using dictionary-like access'''
        self.remove(key)
    def __contains__(self, key: str):
        '''Check if a setting exists using dictionary-like access'''
        return key in self.settings
