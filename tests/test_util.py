import json
import os
import pytest
from pathlib import Path

objects_path = os.path.join(Path(os.path.realpath(__file__)).parent, 'objects')


def load_json(filename):
    path = os.path.join(objects_path, filename)
    with open(path, 'r') as f:
        return json.load(f)

