"""
The unit tests in here interact directly with hydra-base (rather than using the Web API).
"""
from helpers import *
from fixtures import *
from hydra_base_fixtures import *
from hydra_pywr.importer import PywrHydraImporter
from hydra_pywr.template import generate_pywr_attributes, generate_pywr_template, pywr_template_name
import hydra_base
import pytest
import json


def test_add_network(pywr_json_filename, session_with_pywr_template, projectmaker, root_user_id):
    project = projectmaker.create()

    template = JSONObject(hydra_base.get_template_by_name(pywr_template_name()))

    importer = PywrHydraImporter(pywr_json_filename, template)

    # First create the Pywr specific attribute groups.
    attribute_group_ids = {}
    for group_data in importer.add_attribute_group_request_data(project.id):
        response_group = hydra_base.add_attribute_group(JSONObject(group_data), user_id=root_user_id)
        attribute_group_ids[group_data['name']] = response_group.id

    # First the attributes must be added.
    attributes = [JSONObject(a) for a in importer.add_attributes_request_data()]

    # The response attributes have ids now.
    response_attributes = hydra_base.add_attributes(attributes)

    # Convert to a simple dict for local processing.
    # TODO change this variable name to map or lookup
    attribute_ids = {a.name: a.id for a in response_attributes}

    # Now we try to create the network
    network = importer.add_network_request_data(attribute_ids, project.id)

    # Check transformed data is about right
    with open(pywr_json_filename) as fh:
        pywr_data = json.load(fh)

    assert_hydra_pywr(network, pywr_data)

    json_network = convert_network_to_json_object(network)

    hydra_network = hydra_base.add_network(json_network, user_id=root_user_id)

    # Now we have to add the attribute group items
    attribute_group_items = importer.add_attribute_group_items_request_data(attribute_ids, attribute_group_ids,
                                                                            hydra_network.id)

    hydra_base.add_attribute_group_items([JSONObject(i) for i in attribute_group_items], user_id=root_user_id)


def test_add_template(session, root_user_id):

    attributes = [JSONObject(a) for a in generate_pywr_attributes()]

    # The response attributes have ids now.
    response_attributes = hydra_base.add_attributes(attributes)

    # Convert to a simple dict for local processing.
    attribute_ids = {a.name: a.id for a in response_attributes}

    template = generate_pywr_template(attribute_ids)

    hydra_base.add_template(JSONObject(template))
