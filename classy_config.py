import os
import canvasapi
import click
import yaml

class ClassyConfig:
    def __init__(self):
        self.config_path = os.path.join(os.path.expanduser('~'), '.config', 'classy', 'config.yaml')
        try:
            with open(self.config_path, 'r') as f:
                self.config = yaml.safe_load(f)
        except FileNotFoundError:
            # Create config file at config_path
            self.config = self.get_default_config()
            self.save()
    
    def get_default_config(self):
        return {
            'school_workspace': os.path.join(os.path.expanduser('~'), 'test_school'),
            'canvas_api_key': None,
            'canvas_api_url': None,
        }

    def get_canvas_api(self):
        return canvasapi.Canvas(self['canvas_api_url'], self['canvas_api_key'])

    def save(self):
        os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
        with open(self.config_path, 'w') as f:
            yaml.dump(self.config, f)
    
    def __getitem__(self, arg):
        try:
            return self.config[arg]
        except KeyError:
            return None

    def __setitem__(self, arg, value):
        self.config[arg] = value
        self.save()

    def ask_or_get(self, arg, prompt):
        if self[arg] is None:
            result = click.prompt(prompt)
            self.config[arg] = result
            self.save()
            return result
        else:
            return self[arg]