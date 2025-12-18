import os
import datetime
import pandas as pd
from decimal import Decimal


def _is_date_as_str(s):
    if not isinstance(s, str):
        return False
    # len('2021-12-31_07:00:00') == 19
    if len(s) != 19:
        return False
    # Check for this format: 2021-12-31_07:00:00 (regex is too costly)
    return s[4] == s[7] == '-' and s[10] == '_' and s[13] == s[16] == ':'


def _to_datetime(s):
    try:
        return datetime.datetime.strptime(s, '%Y-%m-%d_%H:%M:%S')
    except ValueError:
        return s


def _to_obj(obj):
    if isinstance(obj, dict):
        rv = {}
        for k, v in obj.items():
            assert isinstance(k, str), 'key is not a string'
            if _is_date_as_str(k):
                k = _to_datetime(k)
            elif k == 'null':
                k = None
            elif k.isnumeric():
                k = int(k)
            v = _to_obj(v)
            rv[k] = v
        return rv
    elif isinstance(obj, list):
        return list(map(_to_obj, obj))
    elif isinstance(obj, tuple):
        return tuple(map(_to_obj, obj))
    elif _is_date_as_str(obj):
        return _to_datetime(obj)
    return obj


def _to_tuple(cfg):
    # convert period into a tuple of (start, end)
    periods = cfg.get('timeline', {}).get('periods', [])
    for idx, p in enumerate(periods):
        cfg['timeline']['periods'][idx] = tuple(p)

    # convert the value of quality ranges into tuple
    products = cfg.get('products', [])
    for prod in products:
        quality_ranges = prod.get('quality_ranges', {})
        for k, v in quality_ranges.items():
            prod['quality_ranges'][k] = tuple(v)
        production_targets = prod.get('production_targets', {})
        for k, v in production_targets.items():
            prod['production_targets'][k] = tuple(v)

    # convert values in capacity dict into a tuple
    stockpiles = cfg.get('stockpiles', [])
    for sp in stockpiles:
        capacity = sp.get('capacity', {})
        for k, v in capacity.items():
            sp['capacity'][k] = tuple(v)

    generic_tonnage_constraints = cfg.get('generic_tonnage_constraints', [])
    for c in generic_tonnage_constraints:
        ranges = c.get('ranges', {})
        for k, v in ranges.items():
            lb = Decimal(v[1][0]) if v[1][0] is not None else None
            ub = Decimal(v[1][1]) if v[1][1] is not None else None
            c['ranges'][k] = (v[0], [lb, ub])

    return cfg


class ImportProcessorColumnError(Exception):
    autofix_id = 'file_import_processor_error'
    err_type = 'error'

    def __init__(self, message, column_name, **params):
        self.message = message
        self.column = column_name
        self.params = params or {}

    def __str__(self):
        return f'{self.autofix_id} {self.message}'

    def to_params(self):
        return {
            'message': self.message,
            **self.params
        }


class ImportProcessorGlobalError(Exception):
    autofix_id = 'file_import_processor_error'
    err_type = 'error'

    def __init__(self, message, **params):
        self.message = message
        self.params = params or {}

    def __str__(self):
        return f'{self.autofix_id} {self.message}'

    def to_params(self):
        return {
            'message': self.message,
            **self.params
        }


class MockAPI(object):
    """ A mock API that is meant to provide a mocked interface to the
        application (and serve data without actually requiring the application).
    """
    def __init__(self, mock_files):
        self._input_data = mock_files
        self.result_table = None
        self.warning_counter = 0

    def read_table(self, datakey):
        return self._input_data.get(datakey)

    def write_table(self, tbl):
        self.result_table = tbl

    def show_error(self, message, column_name=None):
        if column_name is None:
            raise ImportProcessorGlobalError(message)
        raise ImportProcessorColumnError(message, column_name)

    def show_warning(self, decision_id, message, column_name=None, options=None):
        pass

    def set_change_comment(self, message):
        self.change_comment = message

    def get_output(self):
        return self.result_table


def create_mock_api_from_data(dataset_key):
    import glob
    import pandas as pd

    data_dir = os.path.abspath(
        os.path.join(os.path.dirname(__file__), 'data', dataset_key)
    )

    file_filter = os.path.join(data_dir, '*')
    mock_files = {}
    for f in glob.glob(file_filter):
        name = os.path.basename(f)
        # expected file in ./data/testcase folder => not an input, skip
        if name.startswith('__expected'):
            continue

        data = pd.read_pickle(f)
        mock_files[name] = data

    api = MockAPI(mock_files)
    return api

class MockTimer():
    def __init__(self):
        self.past_due = True

class MockOut():
    def __init__(self):
        self.val = None
    def set(self, val):
        self.val = val

class MockIn():
    def __init__(self, body:str):
        self.body = body.encode('utf-8')
    def get_body(self):
        return self.body

class MockBlobClient():
    def __init__(self, body:str):
        self.body = body.encode('utf-8')
    def read(self):
        return self.body

def _save_json_result_to_local_csv_file(result, filename:str, sample_rows:int=3):
    # now use json.loads to load blobstr.val and save it as a table to output.csv
    import json
    import csv
    # if result is string then load it as json
    if isinstance(result, str):
        data = json.loads(result)
    else:
        data = result
    with open(f"{filename}.csv", 'w', newline='', encoding="utf-8") as f:
        csvwriter = csv.writer(f)
        count = 0
        for emp in data:
            if count == 0:
                header = emp.keys()
                csvwriter.writerow(header)
            csvwriter.writerow(emp.values())
            count += 1
            if count > sample_rows:
                break
