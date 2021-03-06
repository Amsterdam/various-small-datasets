import logging
from datetime import datetime
import requests
import json
import os
import pylru

from geomet import wkt
from django.contrib.gis.geos import GEOSGeometry

api_config = {
    'bag_api_root': os.getenv('BAG_API_ROOT', 'https://api.data.amsterdam.nl/bag/v1.1'),
    'monumenten_api_root': os.getenv('MONUMENTEN_API_ROOT', 'https://api.data.amsterdam.nl/monumenten')
}
log = logging.getLogger(__name__)

# Use cache to prevent calls to the same URL to get data for different targets
_api_cache = None


def _init_api_cache():
    global _api_cache
    _api_cache = pylru.lrucache(512)


def clear_cache():
    if not _api_cache:
        _init_api_cache()
    _api_cache.clear()


def _get_cached_api(url):
    if not _api_cache:
        _init_api_cache()

    content = _api_cache.get(url)
    from_cache = " (from cache)"
    if not content:
        with requests.get(url) as response:
            if response.status_code == 200:
                content = _api_cache[url] = json.loads(response.content)
                from_cache = ""
    log.warning(f"getting {url}{from_cache}:\n{content}")
    return content


def _get_nested(data, args):
    if data and args:
        if not isinstance(args, (tuple, list)):
            args = [args]
        element = args[0]
        if isinstance(element, int):
            if isinstance(data, (list, tuple)) and element < len(data):
                value = data[element]
            else:
                return None
        elif element:
            value = data.get(element)
        else:
            return None
        return value if len(args) == 1 else _get_nested(value, args[1:])
    return None


def _geometry_from_string(geos_input, source_srid, target_srid):
    geometry = GEOSGeometry(geos_input, srid=source_srid)
    geometry.transform(target_srid)
    return geometry


def geometry_from_geojson(_, source, field_repr):
    if source is None:
        return None

    geos_input = str(source)
    source_srid = 4326  # as per GeoJSON standard
    target_srid = field_repr.srid

    return _geometry_from_string(geos_input, source_srid, target_srid)


def geometry_from_rd_geojson(_, source, field_repr):
    if source is None:
        return None

    geos_input = wkt.dumps(source, decimals=4)
    source_srid = 28992
    target_srid = field_repr.srid

    return _geometry_from_string(geos_input, source_srid, target_srid)


def geometry_from_api(transform_def, source, _):
    if source is None:
        return None
    url = transform_def['url_pattern'].format(id=source, **api_config)

    content = _get_cached_api(url)
    if content:
        return content[transform_def['field']]
    return None


def string_from_api(transform_def, source, _):
    if source is None:
        return None
    url = transform_def['url_pattern'].format(id=source, **api_config)
    content = _get_cached_api(url)
    if content:
        return _get_nested(content, transform_def['field'])
    return None


def integer_from_api(transform_def, source, _):
    if source is None:
        return None
    url = transform_def['url_pattern'].format(id=source, **api_config)
    content = _get_cached_api(url)
    if content:
        value = _get_nested(content, transform_def['field'])
        return value if isinstance(value, int) else int(value) if isinstance(value, str) and value.isdigits() else None
    return None


def array_from_api(transform_def, source, _):
    if source is None:
        return None
    url = transform_def['url_pattern'].format(id=source, **api_config)
    content = _get_cached_api(url)
    if content:
        value = _get_nested(content, transform_def['field'])
        return value if isinstance(value, list) else list(value) if value else []
    return None


def pluck_attr_from_api(transform_def, source, _):
    if source is None:
        return None
    url = transform_def['url_pattern'].format(id=source, **api_config)
    content = _get_cached_api(url)
    if content:
        value = _get_nested(content, transform_def['field'])
        return map(lambda x: x[transform_def['attr']], value)
    return None


def concat_string(transform_def, source, _):
    if source is None:
        return None
    return transform_def['separator'].join(source)


def datetime_from_string(transform_def, source, _):
    if source is None:
        return None
    date = datetime.strptime(source, transform_def['properties']['pattern'])
    if transform_def['type'] == "time_from_string":
        return str(date.time())
    return date


def check_integer_or_null(transform_def, source, _):
    if source is None or not source.isdigit():
        return None
    return source
