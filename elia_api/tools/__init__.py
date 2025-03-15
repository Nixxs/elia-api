from elia_api.tools.update_map_data import update_map_data
from elia_api.tools.get_weather import get_weather
from elia_api.tools.find_place import find_place
from elia_api.tools.geoprocessing import lat_long_to_geojson, buffer_features, union_features, wkt_to_geojson
from elia_api.tools.data_access import list_available_tables, query_table

tools = [
	update_map_data,
	get_weather,
    find_place,
    lat_long_to_geojson,
    buffer_features,
    union_features,
    list_available_tables,
    query_table,
    wkt_to_geojson
]