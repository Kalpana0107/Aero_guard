# modules/spatial.py

import requests
import numpy as np
import folium
from folium.plugins import HeatMap


def fetch_multi_station_aqi(
    lat: float,
    lon: float,
    token: str,
    radius_deg: float = 0.2,
) -> list:
    """
    Query WAQI's bounds-search endpoint for all monitoring stations
    within a small bounding box around the user's coordinates.
    """

    lat1 = lat - radius_deg
    lat2 = lat + radius_deg
    lon1 = lon - radius_deg
    lon2 = lon + radius_deg

    url = (
        f"https://api.waqi.info/map/bounds/"
        f"?latlng={lat1},{lon1},{lat2},{lon2}&token={token}"
    )

    resp = requests.get(url, timeout=10)
    resp.raise_for_status()

    data = resp.json().get("data", [])

    stations = []

    for s in data:
        aqi = s.get("aqi")

        if aqi and str(aqi).isdigit():
            stations.append(
                {
                    "lat": s["lat"],
                    "lon": s["lon"],
                    "aqi": int(aqi),
                    "name": s.get("station", {}).get(
                        "name",
                        "Unknown",
                    ),
                }
            )

    return stations


def idw_interpolate(
    stations: list,
    grid_size: int = 25,
    power: int = 2,
) -> list:
    """
    Inverse Distance Weighting (IDW).

    Estimates AQI at grid points between known monitoring stations.
    Nearby stations have greater influence than distant ones.
    """

    if not stations:
        return []

    lats = [s["lat"] for s in stations]
    lons = [s["lon"] for s in stations]

    lat_grid = np.linspace(
        min(lats) - 0.05,
        max(lats) + 0.05,
        grid_size,
    )

    lon_grid = np.linspace(
        min(lons) - 0.05,
        max(lons) + 0.05,
        grid_size,
    )

    heat_points = []

    for glat in lat_grid:
        for glon in lon_grid:

            dists = np.array(
                [
                    max(
                        0.0001,
                        np.hypot(
                            glat - s["lat"],
                            glon - s["lon"],
                        ),
                    )
                    for s in stations
                ]
            )

            weights = 1 / (dists**power)

            est_aqi = (
                np.sum(
                    weights * np.array([s["aqi"] for s in stations])
                )
                / np.sum(weights)
            )

            # Normalize AQI for HeatMap (0–1)
            heat_points.append(
                [
                    glat,
                    glon,
                    est_aqi / 500,
                ]
            )

    return heat_points


def create_folium_heatmap(
    stations: list,
    lat: float,
    lon: float,
) -> folium.Map:
    """
    Build a Folium heatmap.

    The returned map can be displayed directly with st_folium().
    """

    m = folium.Map(
        location=[lat, lon],
        zoom_start=11,
        
    )

    if stations:
        heat_points = idw_interpolate(stations)

        HeatMap(
            heat_points,
            radius=18,
            blur=22,
            max_zoom=13,
        ).add_to(m)

        for s in stations:
            folium.CircleMarker(
                location=[s["lat"], s["lon"]],
                radius=6,
                popup=f"{s['name']}: AQI {s['aqi']}",
                color="#004d4d",
                fill=True,
                fill_opacity=0.9,
            ).add_to(m)

    else:
        folium.Marker(
            [lat, lon],
            popup="No nearby stations found",
        ).add_to(m)

    return m