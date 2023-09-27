# -*- coding: utf-8 -*-

import json

from ..paths import path_data_json


def reformat_path_data_json():
    """
    Sort service_id and resource_type in alphabetical order.
    """
    data = json.loads(path_data_json.read_text())
    new_data = {}
    for k in data:
        if k.startswith("_"):
            new_data[k] = data[k]
    service_id_list = [k for k in data if not k.startswith("_")]
    service_id_list.sort()
    for service_id in service_id_list:
        new_sub_data = {}
        sub_data = data[service_id]
        for k in sub_data:
            if k.startswith("_"):
                new_sub_data[k] = sub_data[k]
        resource_type_list = [k for k in sub_data if not k.startswith("_")]
        resource_type_list.sort()
        for resource_type in resource_type_list:
            new_sub_data[resource_type] = sub_data[resource_type]
        new_data[service_id] = sub_data
    path_data_json.write_text(json.dumps(new_data, indent=4))
