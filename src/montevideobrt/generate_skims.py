"""Generate Core-zone to Core-zone public-transit travel-time skims."""

from __future__ import annotations

import argparse
import datetime
from pathlib import Path

import geopandas as gpd
import r5py

from montevideobrt.generate_population_job_matrices import SCENARIO_DEPARTURES


def generate_skims(
    *,
    population_path: Path,
    osm_path: Path,
    feeds: list[Path],
    output_dir: Path,
    scenarios: tuple[str, ...] = tuple(SCENARIO_DEPARTURES),
    overwrite: bool = False,
) -> None:
    """Write one Core-zone skim per departure scenario."""
    missing = [
        path for path in [population_path, osm_path, *feeds] if not path.exists()
    ]
    if missing:
        raise FileNotFoundError("Missing skim inputs: " + ", ".join(map(str, missing)))

    zones = gpd.read_file(population_path)
    points = zones.loc[zones["tipo_zona"].eq("Core"), ["id_poligono", "geometry"]]
    points = points.rename(columns={"id_poligono": "id"}).to_crs("EPSG:32721")
    points.geometry = points.geometry.centroid
    points = points.to_crs("EPSG:4326")

    output_dir.mkdir(parents=True, exist_ok=True)
    pending = [
        scenario
        for scenario in scenarios
        if overwrite or not (output_dir / f"{scenario}.parquet").exists()
    ]
    if not pending:
        print(f"All skim files already exist in {output_dir}")
        return

    network = r5py.TransportNetwork(osm_path, feeds)
    for scenario in pending:
        output_path = output_dir / f"{scenario}.parquet"
        travel_times = r5py.TravelTimeMatrix(
            network,
            origins=points,
            destinations=points,
            departure=SCENARIO_DEPARTURES[scenario],
            departure_time_window=datetime.timedelta(minutes=60),
            percentiles=[25, 50, 75],
            transport_modes=[r5py.TransportMode.TRANSIT, r5py.TransportMode.WALK],
            snap_to_network=True,
        )
        skim = travel_times.rename(
            columns={
                "travel_time_p25": "p25",
                "travel_time_p50": "p50",
                "travel_time_p75": "p75",
            }
        )[["from_id", "to_id", "p25", "p50", "p75"]]
        temporary_path = output_path.with_name(output_path.name + ".tmp")
        skim.to_parquet(temporary_path, index=False)
        temporary_path.replace(output_path)
        print(f"Wrote {output_path} ({len(skim)} pairs)")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--population-path",
        type=Path,
        default=Path("data/population/poblacion-zonificacion.gpkg"),
    )
    parser.add_argument(
        "--osm-path", type=Path, default=Path("data/uruguay-260624.osm.pbf")
    )
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
    parser.add_argument("--output-dir", type=Path, default=Path("data/skims"))
    parser.add_argument(
        "--scenario", choices=tuple(SCENARIO_DEPARTURES), action="append"
    )
    parser.add_argument("--overwrite", action="store_true")
    args = parser.parse_args()
    generate_skims(
        population_path=args.population_path,
        osm_path=args.osm_path,
        feeds=args.feeds,
        output_dir=args.output_dir,
        scenarios=tuple(args.scenario or SCENARIO_DEPARTURES),
        overwrite=args.overwrite,
    )


if __name__ == "__main__":
    main()
