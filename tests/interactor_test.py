import pytest
from datetime import datetime
import json
import os
from pathlib import Path

from interactor.person import Person
from interactor.rfi import Rfi
from interactor.submittal import Submittal


objects_path = os.path.join(Path(os.path.realpath(__file__)).parent, 'objects')


def test_create_rfi():
    with open(os.path.join(objects_path, 'rfi.json')) as f:
        contents_dict = json.load(f)
    rfi = Rfi()
    rfi.update_from_dict(contents_dict)

    assert rfi.number == "C-1477"
    assert rfi.title == "Specifications [99 14.44B]"
    assert rfi.location == "1 space"
    assert rfi.description == ''
    assert rfi.due_date == datetime(2017, 1, 18).date()
    assert len(rfi.assignees) == 1
    assert rfi.assignees[0].email == "exampleuser@website.com"
    assert rfi.assignees[0].full_name =='Carl the Contractor'
    assert rfi.rfi_manager.email == "exampleuser@website.com"
    assert rfi.rfi_manager.full_name =='Carl the Contractor'
    assert rfi.cost_impact == 12039.55
    assert rfi.cost_code == "Earthwork"
    assert rfi.questions == "Are the items listed on Schedule C acceptable?"
    assert rfi.drawing_number == "107.3D"
    assert rfi.subject == "Specifications [99 14.44B]"


def test_create_submittal():
    with open(os.path.join(objects_path, 'submittal.json')) as f:
        contents_dict = json.load(f)
    submittal = Submittal()
    submittal.update_from_dict(contents_dict)

    assert submittal.number == "118"
    assert submittal.title == "Smiths - Teardown & Assembly Bldg"
    assert submittal.location == "1 space"
    assert submittal.description == "Thermal Insulation submittal"
    assert submittal.due_date == datetime(2014, 7, 22).date()
    assert submittal.ball_in_court.full_name == 'Carl Contractor' 
    assert submittal.ball_in_court.email == 'exampleuser@website.com' 
    assert submittal.approver.full_name == "Other Contractor"
    assert submittal.approver.email == "otherexampleuser@website.com"
    assert submittal.attachments[0].url == "http://www.example.com/"
    assert submittal.attachments[0].filename == "january_receipt_copy.jpg"
    assert submittal.required_on_site_date == datetime(2016, 11, 28).date()