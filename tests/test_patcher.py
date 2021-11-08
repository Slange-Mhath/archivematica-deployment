import json
import os
from unittest import mock

import pytest


from patcher import main


THIS_DIR = os.path.dirname(os.path.realpath(__file__))
DATA_DIR = os.path.join(THIS_DIR, "data")


def test_patcher_writes_to_stdout(capsys):
    workflow_file = os.path.join(DATA_DIR, "workflow.json")
    main.CREATE_METS_V2_LINKS = (
        {
            "id": "3b5dd6a5-b951-4e44-b00d-1180e5557beb",
            "next_id": "47bf2a2c-8d72-4f36-96d0-53b53a2bbc3f"
        },
    )

    main.main(workflow_file)

    captured = capsys.readouterr()
    workflow = json.loads(captured.out)

    assert captured.err == ""
    assert len(workflow["links"]) == 10

    old_link_ids = ["3b5dd6a5-b951-4e44-b00d-1180e5557beb", "47bf2a2c-8d72-4f36-96d0-53b53a2bbc3f",
                                        "5678bbab-c0ea-4b3c-9de9-addc92d0de50", "c38f7b32-6f0c-48a5-a5f6-6dbe97ca75ba", "d875dcf3-5e0e-4546-a66d-b2580c7a1a75",
                                        "de6eb412-0029-4dbd-9bfa-7311697d6012", "ea5f2361-d210-43f9-955b-2cc3cbeb348d", "f44a33b2-ba1a-43d9-807f-3b3cdab680e3",
                                        "f8e4c1ee-3e43-4caa-a664-f6b6bd8f156e"]
    new_link_id = list((set(workflow["links"].keys()) - set(old_link_ids)))[0]

    assert workflow["links"].keys() != old_link_ids
    assert workflow['links'][new_link_id]['exit_codes']['0']['link_id'] == "47bf2a2c-8d72-4f36-96d0-53b53a2bbc3f"
    assert workflow['links']["3b5dd6a5-b951-4e44-b00d-1180e5557beb"]['exit_codes']['0']['link_id'] == new_link_id

    # TODO: more assertions needed in workflow


def test_patcher_writes_to_file(tmp_path):
    workflow_file = os.path.join(DATA_DIR, "workflow.json")
    output_file = tmp_path / "output.json"

    main.CREATE_METS_V2_LINKS = (
        {
            "id": "3b5dd6a5-b951-4e44-b00d-1180e5557beb",
            "next_id": "47bf2a2c-8d72-4f36-96d0-53b53a2bbc3f"
        },
    )

    main.main(workflow_file, str(output_file))
    workflow = json.loads(output_file.read_text())

    assert len(workflow["links"]) == 10

    # TODO: more assertions needed in workflow
