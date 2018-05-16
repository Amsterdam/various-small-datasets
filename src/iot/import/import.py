import pandas as pd
import csv
import math
import re
import argparse
import json

import pprint
pp = pprint.PrettyPrinter()

# Configuration
CONFIG = {
    # 111    ' Omschrijving\n ', ' Primaire functie(s)\n ', ' Type code\n (V&OR)',
    #        ' Object nr.\n (leverancier)', ' Locatie nr.\n (leverancier)',
    #        ' Standplaatsomschrijving\n', ' Rijksdriehoek\n X-coördinaat (m)',
    #        ' Rijksdriehoek\n Y-coördinaat (m)', ' WGS84 DD\n Latitude (gr)',
    #        ' WGS84 DD\n Longitude (gr)', ' Google Maps\n link coördinaten',
    #        ' Richting\n van het verkeer'
    # 124    ' Omschrijving\n ', ' Primaire functie(s)\n ', ' Type code\n (V&OR)',
    #        ' Object nr.\n (leverancier)', ' Locatie nr.\n (leverancier)',
    #        ' Standplaatsomschrijving\n', ' Rijksdriehoek\n X-coördinaat (m)',
    #        ' Rijksdriehoek\n Y-coördinaat (m)', ' WGS84 DD\n Latitude (gr)',
    #        ' WGS84 DD\n Longitude (gr)', ' Google Maps\n link coördinaten',
    #        ' Richting\n van het verkeer'
    # 127    ' Omschrijving\n ', ' Primaire functie(s)\n ', ' Type code\n (V&OR)',
    #        ' Object nr.\n (leverancier)', ' Locatie nr.\n (leverancier)',
    #        ' Standplaatsomschrijving\n', ' Rijksdriehoek\n X-coördinaat (m)',
    #        ' Rijksdriehoek\n Y-coördinaat (m)', ' WGS84 DD\n Latitude (gr)',
    #        ' WGS84 DD\n Longitude (gr)', ' Google Maps\n link coördinaten',
    #        ' Richting\n van het verkeer'
    "cameras": {
        "sheet_names": ["111", "124", "127"],
        "header": 1,
        "default": {
            "thing": {
                "ref": "Objectnummer Amsterdam",
                "name": " Omschrijving\n ",
                "description": " Omschrijving\n ",
                "purpose": " Primaire functie(s)\n "
            },
            "location": {
                "ref": " Standplaatsomschrijving\n",
                "name": " Standplaatsomschrijving\n",
                "rd_x": " Rijksdriehoek\n X-coördinaat (m)",
                "rd_y": " Rijksdriehoek\n Y-coördinaat (m)",
                "wgs84_lat": " WGS84 DD\n Latitude (gr)",
                "wgs84_lon": " WGS84 DD\n Longitude (gr)"
            }
        },
        "124": {
            "thing": {
                "ref": " Object nr.\n (leverancier)"
            },
            "location": {
                "ref": " Locatie nr.\n (leverancier)"
            }
        }
    },
    # Name, Description, Status, Level, Latitude, Longitude, PlaceID, ExpectedStability
    "beacons": {
        "thing": {
            "ref": "Name",
            "name": "Description",
            "description": "Description",
            "purpose": None
        },
        "location": {
            "ref": "PlaceID",
            "name": "PlaceID",
            "rd_x": None,
            "rd_y": None,
            "wgs84_lat": "Latitude",
            "wgs84_lon": "Longitude"
        }
    }
}

# Table names to write new IoT data to
THINGS_TABLE = "iot_things_new"
LOCATIONS_TABLE = "iot_locations_new"
# OWNERS_TABLE = "iot_owners_new"


def thing(id, ref, name, description, device_type, purpose):
    return {"id": id, "ref": ref, "name": name, "description": description, "device_type": device_type, "purpose": purpose}


def geometry(x, y, code):
    if x == None or y == None:
        return None
    else:
        return f"ST_GeomFromText('POINT({x} {y})', {code})"


def location(thing_id, ref, name, rd_x, rd_y, wgs84_lat, wgs84_lon):
    rd_geometry = geometry(rd_x, rd_y, 28992)
    wgs84_geometry = geometry(wgs84_lat, wgs84_lon, 4326)
    return {"thing_id": thing_id, "ref": ref, "name": name, "rd_geometry": rd_geometry, "wgs84_geometry": wgs84_geometry}


def print_summary(id, things, locations):
    print(f'''{id}
  Total things {len(things)}
  Total locations {len(locations)}''')


def import_sensors(filename):
    things = []
    locations = []
    with open(filename, newline='') as jsonfile:
        reader = json.load(jsonfile)
        for id, items in enumerate(reader):
            for row in items:
                id = f'{row["SELECTIE"]}.{row["VOLGNR"]}'
                things.append(thing(
                    id=id,
                    ref=row['VOLGNR'],
                    name=row['LABEL'],
                    description=row['SELECTIE'],
                    device_type=row['SELECTIE'],
                    purpose=row['SELECTIE'],
                ))
                locations.append(location(
                    thing_id=id,
                    ref=row['LABEL'],
                    name=row['LABEL'],
                    rd_x=None,
                    rd_y=None,
                    wgs84_lat=row['LATMAX'],
                    wgs84_lon=row['LNGMAX'],
                ))
    print_summary(id='Sensors', things=things, locations=locations)
    return (things, locations)

def beacon_value(row, entity, key):
    try:
        return row[CONFIG["beacons"][entity][key]]
    except:
        return None


def import_beacons(filename):
    things = []
    locations = []
    with open(filename, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for id, row in enumerate(reader):
            if row['Status'] == 'ACTIVE' and row["ExpectedStability"] == "STABLE":
                id = f"beacons.{id}"
                # Active and stationary beacons
                things.append(thing(
                    id=id,
                    ref=beacon_value(row, "thing", "ref"),
                    name=beacon_value(row, "thing", "name"),
                    description=beacon_value(row, "thing", "description"),
                    device_type="Beacon",
                    purpose=beacon_value(row, "thing", "purpose"),
                ))
                locations.append(location(
                    thing_id=id,
                    ref=beacon_value(row, "location", "ref"),
                    name=beacon_value(row, "location", "name"),
                    rd_x=beacon_value(row, "location", "rd_x"),
                    rd_y=beacon_value(row, "location", "rd_y"),
                    wgs84_lat=beacon_value(row, "location", "wgs84_lat"),
                    wgs84_lon=beacon_value(row, "location", "wgs84_lon"),
                ))
    print_summary(id='Beacons', things=things, locations=locations)
    return (things, locations)


def camera_value(sheet, series, entity, key):
    try:
        value = CONFIG["cameras"][sheet][entity][key]
    except:
        value = CONFIG["cameras"]["default"][entity][key]
    value = series[value]
    try:
        if math.isnan(value):
            return None
    except:
        return value
    return value


def import_cameras(filename):
    sheet_names = CONFIG["cameras"]["sheet_names"]
    df = pd.read_excel(filename, sheet_name=sheet_names, header=1)

    things = []
    locations = []
    for sheet in sheet_names:
        for row in df[sheet].iterrows():
            id, series = row
            try:
                id = f"cameras.{sheet}.{int(id)}"
            except:
                # End of input
                break

            things.append(thing(
                id=id,
                ref=camera_value(sheet, series, "thing", "ref"),
                name=camera_value(sheet, series, "thing", "name"),
                description=camera_value(sheet, series, "thing", "description"),
                device_type="Camera",
                purpose=camera_value(sheet, series, "thing", "purpose"),
            ))
            locations.append(location(
                thing_id=id,
                ref=camera_value(sheet, series, "location", "ref"),
                name=camera_value(sheet, series, "location", "name"),
                rd_x=camera_value(sheet, series, "location", "rd_x"),
                rd_y=camera_value(sheet, series, "location", "rd_y"),
                wgs84_lat=camera_value(sheet, series, "location", "wgs84_lat"),
                wgs84_lon=camera_value(sheet, series, "location", "wgs84_lon"),
            ))
    print_summary(id='Cameras', things=things, locations=locations)
    return (things, locations)


def get_value(item, field):
    # Values are stored as strings, '...'. Convert any containg quotes to double quotes
    value = item[field]
    if value == None:
        return 'NULL'
    elif isinstance(value, str):
        if not re.match(r'ST_GeomFromText', value):
            value = value.replace("'", "\"")
            value = f"'{value}'"
    return str(value)


def write_inserts(out_dir, things, locations):
    # Write import statements
    # INSERT INTO table
    #     (fieldA, fieldB, ...)
    # VALUES
    #     (valueA, valueB, ...)
    #     (valueA, valueB, ...);
    for (collection, table_name) in [(things, THINGS_TABLE), (locations, LOCATIONS_TABLE)]:
        with open(f"{out_dir}/{table_name}.sql", "a+") as f:
            fields = collection[0].keys()
            f.write(f"""
INSERT INTO {table_name}
    ({', '.join(fields)})
VALUES""")
            for i, item in enumerate(collection):
                values = [get_value(item, field) for field in fields]
                f.write(f"""{"," if i > 0 else ""}
    ({', '.join(values)})""")
            f.write(";")


def import_things(item, arg):
    if item == "cameras":
        return import_cameras(arg)
    elif item == "beacons":
        return import_beacons(arg)
    else:
        return import_sensors(arg)



def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("cameras", type=str, help="Cameras input xlsx")
    parser.add_argument("beacons", type=str, help="Beacons input csv")
    parser.add_argument("sensors", type=str, help="Sensors input json")
    parser.add_argument("out_dir", type=str, help="Output directory for resulting SQL import files")
    args = parser.parse_args()

    for item in ["cameras", "beacons", "sensors"]:
        things, locations = import_things(item, getattr(args, item))
        write_inserts(args.out_dir, things, locations)


if __name__ == '__main__':
    main()
