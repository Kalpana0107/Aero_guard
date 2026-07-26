# modules/spatial.py

import requests
import numpy as np
import folium
from folium.plugins import HeatMap


def fetch_multi_station_aqi(
    lat: float,
    lon: float,
    token: str,
    radius_deg: float = 0.15,
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

    # Logging/Debugging WAQI token and request info
    masked_token = "empty"
    if token:
        masked_token = f"{token[:4]}...{token[-4:]}" if len(token) > 8 else "***"
    print(f"[AeroGuard Debug] fetch_multi_station_aqi called. Token len={len(token)}, Masked='{masked_token}'")
    print(f"[AeroGuard Debug] Request URL: {url}")

    try:
        resp = requests.get(url, timeout=10)
        print(f"[AeroGuard Debug] Response Status: {resp.status_code}")
        print(f"[AeroGuard Debug] Response Text (first 1000 chars): {resp.text[:1000]}")
        resp.raise_for_status()
        payload = resp.json()
    except Exception as e:
        print(f"[AeroGuard Debug] Network request or JSON parse failed: {e}")
        return []

    data = payload.get("data", [])

    if not isinstance(data, list):
        print(f"[AeroGuard Debug] Expected a list for 'data', got: {type(data)} ({repr(data)})")
        data = []

    stations = []

    for s in data:
        if not isinstance(s, dict):
            continue
        
        aqi_val = s.get("aqi")
        if aqi_val is None:
            continue

        try:
            # Parse AQI robustly
            aqi_str = str(aqi_val).strip()
            if aqi_str in ["", "-", "n/a", "null", "none"]:
                continue
            aqi = int(round(float(aqi_str)))
            
            # Parse lat/lon robustly
            lat_val = float(s["lat"])
            lon_val = float(s["lon"])
            
            # Extract station name robustly
            station_info = s.get("station", {})
            name = "Unknown"
            if isinstance(station_info, dict):
                name = station_info.get("name", "Unknown")
            elif isinstance(station_info, str):
                name = station_info

            stations.append(
                {
                    "lat": lat_val,
                    "lon": lon_val,
                    "aqi": aqi,
                    "name": name,
                }
            )
        except (ValueError, TypeError, KeyError):
            continue

    print(f"[AeroGuard Debug] Parsed {len(stations)} valid stations.")
    return stations



def idw_interpolate(
    stations: list,
    grid_size: int = 15,
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

        print(f"[DEBUG] heat_points count: {len(heat_points)}")
        
        # Color mapping: green (0-50), yellow (51-100), orange (101-150), red/darkred (150+)
        gradient_map = {
            0.0: '#00e400',   # Green (AQI 0)
            0.1: '#00e400',   # Green (AQI 50)
            0.2: '#ffff00',   # Yellow (AQI 100)
            0.3: '#ff7e00',   # Orange (AQI 150)
            0.4: '#ff0000',   # Red (AQI 200)
            1.0: '#7e0023'    # Dark Red (AQI 500)
        }

        HeatMap(
            heat_points,
            radius=25,
            blur=15,
            max_zoom=13,
            max=1.0,          # Set max intensity to 1.0 to map weights absolutely (0-500 scale normalized by 500)
            gradient=gradient_map,
            min_opacity=0.3,
        ).add_to(m)

        for s in stations:
            folium.CircleMarker(
                location=[s["lat"], s["lon"]],
                radius=5,
                popup=f"{s['name']}: AQI {s['aqi']}",
                color="#004d4d",
                fill=True,
                fill_color="#004d4d",
                fill_opacity=0.9,
            ).add_to(m)

    else:
        folium.Marker(
            [lat, lon],
            popup="No nearby stations found",
        ).add_to(m)

    return m