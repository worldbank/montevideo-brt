import pandas as pd
import ast
import io
import os
import requests
from datetime import datetime, timezone
import yaml
import argparse

ODS_CSV = """od_id,od_name,origin,destination,points
0,Troncal Cno. Maldonado - 8 de octubre,Ciudad Vieja,Zonamerica - Facultad de Veterinaria,"[0, 2]"
1,Troncal Av. Italia,Ciudad Vieja,El Pinar,"[1, 3]"
2,Av. 18 de Julio - Ciudad del Plata,Av. 18 de Julio (Barrio Sur),Ruta 1 Vieja (Ciudad del Plata),"[4, 5]"
"""

POINTS_CSV = """id,name,latitude,longitude
0,Av. 18 Convencion Andes,-34.90637,-56.19754
1,Tres Cruces,-34.89499,-56.16483
2,Veterinaria,-34.79094,-56.0676
3,Guenoas,-34.78994,-55.89604
4,Av. 18 de Julio (Barrio Sur),-34.906246,-56.196546
5,Ruta 1 Vieja (Ciudad del Plata),-34.760895,-56.401903
"""


class Mapbox:
    """
    Wrapper class for handling authentication and requests (GET) to Mapbox API

    Notes
    -----
    For more information, please see at https://docs.mapbox.com/api/overview/
    """

    BASE_URL = "https://api.mapbox.com"

    def __init__(self, token=None):
        self.TOKEN = token if token else os.getenv("")

    def get(self, method, profile, coordinates, params):
        """
        Return HTTP response from GET request with access token to Mapbox API

        Parameters
        ----------
        method (str): Mapbox API method. See https://docs.mapbox.scom/api/overview/

        coordinates (list): Mapbox API coordinates. See https://docs.mapbox.com/api/overview/

        profile (str): Mapbox API profile. See https://docs.mapbox.com/api/overview/

        params (dict): Parameters for Mapbox API method. See See https://docs.mapbox.com/api/overview/
        """

        coordinates = ";".join([",".join(str(x) for x in y) for y in coordinates])
        params["access_token"] = self.TOKEN

        url = f"{self.BASE_URL}{method}/{profile}/{coordinates}"

        response = requests.get(url, params=params, verify=False)
        response.raise_for_status()

        return response


def retrieve_date_time():
    """
    Return current date and time in UTC timezone as strings (year, month, day, hour, minute)
    """
    now = datetime.now(timezone.utc)
    year = str(now.year)
    month = str(now.month).zfill(2)
    day = str(now.day).zfill(2)
    hour = str(now.hour).zfill(2)
    minute = str(now.minute).zfill(2)
    return year, month, day, hour, minute


def query_ods(city):
    """Query Mapbox API for each OD pair in the ODs file and save results in a new CSV file"""

    with open("config.yaml", "r") as file:
        config = yaml.safe_load(file)

    token = os.getenv(config["Montevideo"]["mapbox_token_env_var"])
    method = config["Montevideo"]["method"]
    profile = config["Montevideo"]["profile"]
    params = {
        "sources": "all",
        "destinations": "all",
        "annotations": "distance,duration",
    }

    year, month, day, hour, minute = retrieve_date_time()

    ods = pd.read_csv(io.StringIO(ODS_CSV)).set_index("od_id")
    points = pd.read_csv(io.StringIO(POINTS_CSV)).set_index("id")
    ods["points"] = ods["points"].apply(lambda x: ast.literal_eval(x))

    mapbox = Mapbox(token=token)

    for od_id, row in ods.iterrows():
        points_od = row["points"]
        duration_od = []
        duration_do = []
        distance_od = []
        distance_do = []
        for i, point in enumerate(points_od):
            if i < len(points_od) - 1:
                o_id = point
                d_id = points_od[i + 1]
                coordinates = (
                    [points.loc[o_id]["longitude"], points.loc[o_id]["latitude"]],
                    [points.loc[d_id]["longitude"], points.loc[d_id]["latitude"]],
                )
                response = mapbox.get(method, profile, coordinates, params)
                data = response.json()
                # import pdb; pdb.set_trace()
                duration_od.append(data["durations"][0][1])
                duration_do.append(data["durations"][1][0])
                distance_od.append(data["distances"][0][1])
                distance_do.append(data["distances"][1][0])

        ods.loc[od_id, f"tt_{year}{month}{day}{hour}{minute}"] = sum(duration_od)
        ods.loc[od_id, f"dist_{year}{month}{day}{hour}{minute}"] = sum(distance_od)
        ods.loc[od_id, f"flipped_tt_{year}{month}{day}{hour}{minute}"] = sum(
            duration_do
        )
        ods.loc[od_id, f"flipped_dist_{year}{month}{day}{hour}{minute}"] = sum(
            distance_do
        )
    os.makedirs("../../results", exist_ok=True)
    ods.to_csv(f"../../results/mapbox_matrixapi_{year}{month}{day}{hour}{minute}.csv")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-c",
        "--city",
        type=str,
        help="City name for which to query Mapbox API, saved in the config file",
    )

    args = parser.parse_args()
    city = args.city

    query_ods(city)
