from pac.rrf.models import PointType, ServiceMatrix, ServiceType

child_parent_mapping = {
    "Country": None,
    "Region": None,
    "Province": None,
    "Customer Zone": None,
    "Postal Code": "Province",
    "Terminal": "Postal Code",
    "Basing Point": "Terminal",
    "Service Point": "Terminal",
    "Sub Postal Code": "Terminal",
}

unserviceable_service_types = ['NOSERVICE', 'EMBARGO']
flagged_service_types = ['QUOTERQD']

def validate_new_lane(service_level_id, orig_point_type, origin_point_value, dest_point_type, destination_point_value):

    origin_service_type = None
    while origin_service_type == None:
        origin_point_type_id = PointType.objects.filter(point_type_name=orig_point_type)[:1].get().point_type_id
        origin_filter_condition = {'sub_service_level_id: ': service_level_id, 'point_type_id': origin_point_type_id, 'point_id': origin_point_value}
        fetched_service_type = fetch_service_matrix_service_type_by_filter_condition(origin_filter_condition)
        if fetched_service_type == None:
            orig_point_type = child_parent_mapping[orig_point_type]
            if orig_point_type == None:
                break
        else:
            origin_service_type = fetched_service_type

    destination_service_type = None
    while destination_service_type == None:
        destination_point_type_id = PointType.objects.filter(point_type_name=dest_point_type)[:1].get().point_type_id
        destination_filter_condition = {'sub_service_level_id: ': service_level_id, 'point_type_id': destination_point_type_id, 'point_id': destination_point_value}
        fetched_service_type = fetch_service_matrix_service_type_by_filter_condition(destination_filter_condition)
        if fetched_service_type == None:
            dest_point_type = child_parent_mapping[dest_point_type]
            if dest_point_type == None:
                break
        else:
            destination_service_type = fetched_service_type

    if origin_service_type:
        origin_service_type_name = origin_service_type.service_type_name
    else:
        origin_service_type_name = None

    if destination_service_type:
        destination_service_type_name = destination_service_type.service_type_name
    else:
        destination_service_type_name = None

    if origin_service_type_name in unserviceable_service_types or destination_service_type_name in unserviceable_service_types:
        return {"FLAGGED": 0, "UNSERVICEABLE": 1}
    elif origin_service_type_name in flagged_service_types or destination_service_type_name in flagged_service_types:
        return {"FLAGGED": 1, "UNSERVICEABLE": 0}
    else:
        return {"FLAGGED": 0, "UNSERVICEABLE": 0}

def fetch_service_matrix_service_type_by_filter_condition(filter_condition):
    try:
        return ServiceMatrix.objects.filter(**filter_condition)[:1].get().service_type_id
    except:
        return None