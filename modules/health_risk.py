# modules/health_risk.py

AQI_BREAKPOINTS = [
    (50, "Good", "#00e400"),
    (100, "Moderate", "#ffff00"),
    (150, "Unhealthy (Sensitive)", "#ff7e00"),
    (200, "Unhealthy", "#ff0000"),
    (300, "Very Unhealthy", "#8f3f97"),
    (500, "Hazardous", "#7e0023"),
]

ADVICE = {
    "general": {
        "Good": "Air quality is great — enjoy normal outdoor activity.",
        "Moderate": "Unusually sensitive individuals should consider reducing prolonged outdoor exertion.",
        "Unhealthy (Sensitive)": "Reduce prolonged or heavy outdoor exertion.",
        "Unhealthy": "Avoid prolonged outdoor exertion. Consider a mask outdoors.",
        "Very Unhealthy": "Avoid all outdoor exertion. Stay indoors with air filtration if possible.",
        "Hazardous": "Remain indoors and keep activity levels low.",
    },
    "children_elderly": {
        "Good": "Safe for outdoor play and activity.",
        "Moderate": "Limit prolonged outdoor exertion for children and elderly.",
        "Unhealthy (Sensitive)": "Move activities indoors where possible.",
        "Unhealthy": "Keep children and elderly indoors; use air purifiers.",
        "Very Unhealthy": "Stay indoors. Avoid any outdoor exposure.",
        "Hazardous": "Emergency-level exposure. Remain indoors in sealed rooms if available.",
    },
    "outdoor_workers": {
        "Good": "Normal outdoor work is safe.",
        "Moderate": "Stay hydrated; monitor for symptoms during long shifts.",
        "Unhealthy (Sensitive)": "Take more frequent indoor breaks.",
        "Unhealthy": "Wear an N95 mask; shorten outdoor work intervals.",
        "Very Unhealthy": "Reschedule non-essential outdoor work if possible.",
        "Hazardous": "Outdoor work should be postponed or done only with proper respirators.",
    },
    "athletes": {
        "Good": "Ideal conditions for outdoor training.",
        "Moderate": "Fine for most training; sensitive athletes should ease intensity.",
        "Unhealthy (Sensitive)": "Move high-intensity training indoors.",
        "Unhealthy": "Avoid outdoor cardio; switch to indoor training.",
        "Very Unhealthy": "Cancel outdoor training entirely.",
        "Hazardous": "No outdoor activity under any circumstance.",
    },
}


def get_aqi_category(aqi: float) -> tuple:
    """
    Returns the AQI category and its associated color.

    Returns:
        (category_name, hex_color)
    """
    for threshold, category, color in AQI_BREAKPOINTS:
        if aqi <= threshold:
            return category, color

    return "Hazardous", "#7e0023"


def get_health_advice(aqi: float, persona: str) -> str:
    """
    Returns health advice for the given AQI and user persona.
    """
    category, _ = get_aqi_category(aqi)

    if persona not in ADVICE:
        persona = "general"

    return ADVICE[persona][category]


def get_forecast_risk_timeline(
    forecast_6h: list,
    persona: str,
) -> list:
    """
    Convert a list of forecast AQI values into a timeline
    that the frontend can render directly.
    """

    timeline = []

    for i, aqi in enumerate(forecast_6h):
        category, color = get_aqi_category(aqi)

        timeline.append(
            {
                "aqi": round(aqi),
                "category": category,
                "color": color,
                "advice": get_health_advice(aqi, persona),
                "hour_offset": f"+{i + 1}h",
            }
        )

    return timeline


if __name__ == "__main__":
    demo = [78, 82, 91, 105, 98, 87]

    for row in get_forecast_risk_timeline(
        demo,
        "children_elderly",
    ):
        print(row)