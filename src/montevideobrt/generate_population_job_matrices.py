"""Generate direct population-zone to employment-grid travel-time matrices."""

from __future__ import annotations

import argparse
import datetime
from pathlib import Path

import geopandas as gpd
import r5py


LOCAL_CRS = "EPSG:32721"
WGS84_CRS = "EPSG:4326"
SCENARIO_DEPARTURES = {
    # "wed_07": datetime.datetime(2026, 3, 25, 7),
    "wed_08": datetime.datetime(2026, 3, 25, 8),
    # "wed_09": datetime.datetime(2026, 3, 25, 9),
    # "wed_10": datetime.datetime(2026, 3, 25, 10),
    # "sat_07": datetime.datetime(2026, 3, 28, 7),
    # "sat_08": datetime.datetime(2026, 3, 28, 8),
    # "sat_09": datetime.datetime(2026, 3, 28, 9),
    # "sat_10": datetime.datetime(2026, 3, 28, 10),
}


def _routing_points(
    zonas_path: Path,
    employment_path: Path,
) -> tuple[gpd.GeoDataFrame, gpd.GeoDataFrame]:
    """Read the two layers and represent each polygon by its centroid."""

    zonas = gpd.read_file(zonas_path)
    zonas_origins = zonas.rename(columns={"poligono_id": "id"})[
        ["id", "geometry"]
    ].assign(
        geometry=lambda frame: frame.geometry.to_crs(LOCAL_CRS)
        .centroid.to_crs(WGS84_CRS)
    )

    employment = gpd.read_file(employment_path)
    employment_destinations = employment.rename(columns={"grid_id": "id"})[
        ["id", "geometry"]
    ].assign(
        geometry=lambda frame: frame.geometry.to_crs(LOCAL_CRS)
        .centroid.to_crs(WGS84_CRS)
    )
    return zonas_origins, employment_destinations


def generate_matrices(
    *,
    zonas_path: Path,
    employment_path: Path,
    osm_path: Path,
    feeds: list[Path],
    output_dir: Path,
    scenarios: tuple[str, ...] = tuple(SCENARIO_DEPARTURES),
    overwrite: bool = False,
) -> None:
    """Generate one direct matrix for each requested departure scenario."""

    unknown = sorted(set(scenarios).difference(SCENARIO_DEPARTURES))
    if unknown:
        raise ValueError(f"Unknown scenarios: {unknown}")
    missing_inputs = [path for path in [zonas_path, employment_path, osm_path, *feeds] if not path.exists()]
    if missing_inputs:
        raise FileNotFoundError(
            "Missing routing inputs: " + ", ".join(str(path) for path in missing_inputs)
        )

    origins, destinations = _routing_points(zonas_path, employment_path)
    output_dir.mkdir(parents=True, exist_ok=True)
    network = r5py.TransportNetwork(osm_path, feeds)

    for scenario in scenarios:
        output_path = output_dir / f"accessibility_{scenario}.parquet"
        if output_path.exists() and not overwrite:
            print(f"Skipping {scenario}: {output_path} already exists")
            continue

        departure = SCENARIO_DEPARTURES[scenario]
        print(
            f"Routing {scenario} ({departure:%Y-%m-%d %H:%M}) from "
            f"{len(origins)} origins to {len(destinations)} employment cells",
            flush=True,
        )
        travel_times = r5py.TravelTimeMatrix(
            network,
            origins=origins,
            destinations=destinations,
            departure=departure,
            departure_time_window=datetime.timedelta(minutes=60),
            percentiles=[50],
            transport_modes=[r5py.TransportMode.TRANSIT, r5py.TransportMode.WALK],
            snap_to_network=1600,
            max_time=datetime.timedelta(hours=2),
            max_time_walking=datetime.timedelta(hours=2),
        )
        matrix = travel_times.rename(columns={"travel_time": "p50"})[
            ["from_id", "to_id", "p50"]
        ]
        temporary_path = output_path.with_name(output_path.name + ".tmp")
        matrix.to_parquet(temporary_path, index=False)
        temporary_path.replace(output_path)
        print(
            f"Wrote {output_path} ({len(matrix)} pairs; "
            f"{matrix['p50'].notna().sum()} non-null p50)",
            flush=True,
        )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--zonas-path",
        type=Path,
        default=Path("data/geography-levels/zonas-montevideo-actualizadas-steer.gpkg"),
    )
    parser.add_argument(
        "--employment-path",
        type=Path,
        default=Path("data/URY_montevideo_employment_predictions_relative.gpkg"),
    )
    parser.add_argument("--osm-path", type=Path, default=Path("data/uruguay-260624.osm.pbf"))
    parser.add_argument(
        "--feed",
        dest="feeds",
        action="append",
        type=Path,
        default=[
            Path("data/GTFS/google_transit.zip"),
            Path("data/GTFS/gtfs_20260326.zip"),
        ],
    )
    parser.add_argument("--output-dir", type=Path, default=Path("data/opportunities"))
    parser.add_argument("--scenario", choices=tuple(SCENARIO_DEPARTURES), action="append")
    parser.add_argument("--overwrite", action="store_true")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    generate_matrices(
        zonas_path=args.zonas_path,
        employment_path=args.employment_path,
        osm_path=args.osm_path,
        feeds=args.feeds,
        output_dir=args.output_dir,
        scenarios=tuple(args.scenario or SCENARIO_DEPARTURES),
        overwrite=args.overwrite,
    )


if __name__ == "__main__":
    main()
