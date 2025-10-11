import os
import sys
import json
import pytest

# Register root path to import modules for py.test. This file is executed
# before any other test case.
root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__),  '..'))

sys.path.append(root_dir)

# def pytest_addoption(parser):
#     parser.addoption('--app', action='store', dest='app')
def load_env_from_json(root_dir, json_file='local.settings.json'):
    check_json_file = os.path.exists(os.path.join(root_dir, json_file))
    if check_json_file:
        # Load the JSON data from the file
        with open(os.path.join(root_dir, json_file), 'r') as file:
            data = json.load(file)
        
        # Add each key-value pair to the environment variables
        for key, value in data['Values'].items():
            os.environ[key] = str(value)

load_env_from_json(root_dir)

@pytest.fixture
def entry(request):
    # app_path = request.config.getoption('--app')
    # print(app_path)
    # Make sure imports work.
    # if app_path and app_path not in sys.path:
    #     sys.path.append(app_path)

    def import_file(full_name, path):
        from importlib import util
        spec = util.spec_from_file_location(full_name, path)
        mod = util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        return mod

    entry = import_file(
        'entry', os.path.join(root_dir, 'function_app.py')
    )
    return entry
