import pytest
from datetime import datetime
import json
import os
from pathlib import Path

from interactor.person import Person
from interactor.rfi import Rfi


objects_path = os.path.join(Path(os.path.realpath(__file__)).parent, 'objects')


def test_create_rfi():
    with open(os.path.join(objects_path, 'rfi.json')) as f:
        contents_dict = json.load(f)
    rfi = Rfi()
    rfi.update_from_dict(contents_dict)

    assignee = Person()
    assignee.full_name = 'Carl the Contractor'
    assignee.email = "exampleuser@website.com"

    assert rfi.number == "C-1477"
    assert rfi.title == "Specifications [99 14.44B]"
    assert rfi.location == "1 space"
    assert rfi.description == ''
    assert rfi.due_date == datetime(2017, 1, 18)
    assert len(rfi.asignees) == 1
    assert rfi.asignees[0].email == "exampleuser@website.com"
    assert rfi.asignees[0].full_name =='Carl the Contractor'
    assert rfi.rfi_manager.email == "exampleuser@website.com"
    assert rfi.rfi_manager.full_name =='Carl the Contractor'
    assert rfi.cost_impact == 12039.55
    assert rfi.cost_code == 12345
    assert rfi.questions == "Are the items listed on Schedule C acceptable?"
    assert rfi.drawing_number == "107.3D"
    assert rfi.subject == "Specifications [99 14.44B]"
