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
        "Good": "Air quality is ideal for all outdoor activities and exercise. There are no health risks associated with the current atmosphere, so feel free to open windows and ventilate your home. Enjoy the clean air and outdoor environment.",
        "Moderate": "Air quality is acceptable, but there may be a moderate concern for a small number of unusually sensitive individuals. If you are sensitive, monitor your breathing, consider reducing heavy exertion, and keep track of changes in air quality. Outdoor plans do not need to be cancelled, but mindfulness is advised.",
        "Unhealthy (Sensitive)": "Members of sensitive groups may experience health effects, while the general public is less likely to be affected. If you are sensitive, reduce prolonged or heavy outdoor exertion and plan more indoor activities. Keep windows closed to prevent outdoor pollutants from entering.",
        "Unhealthy": "Everyone may begin to experience health effects, and members of sensitive groups may experience more serious health effects. Please avoid prolonged or strenuous outdoor activities and limit your time spent outside. If you must go outdoors, wear a well-fitted protective mask like an N95.",
        "Very Unhealthy": "Health warnings of emergency conditions are active, meaning the entire population is likely to be affected. Avoid all outdoor physical activity and keep windows and doors tightly shut to protect your indoor air quality. Run an indoor air purifier with a HEPA filter if available.",
        "Hazardous": "This is a serious health alert where everyone may experience emergency health effects. Remain entirely indoors in a clean room, minimize physical exertion, and keep all doors and windows sealed shut. Ensure your air filtration systems are running on high to maintain safe breathing conditions.",
    },
    "children_elderly": {
        "Good": "The air quality is excellent and completely safe for children's play and seniors' recreational activities. Take advantage of these clean conditions to encourage active outdoor exercise. No special precautions or monitoring are required.",
        "Moderate": "Conditions are mostly safe, but children and elderly individuals should avoid excessive, prolonged outdoor exertion. Watch for symptoms such as coughing or shortness of breath, which may indicate sensitivity. Consider moving high-energy activities indoors if symptoms arise.",
        "Unhealthy (Sensitive)": "Children and the elderly are at higher risk and should move high-effort physical activities indoors to protect their sensitive respiratory systems. Limit outdoor playtime and park visits to short durations. Keep indoor spaces clean and free from outdoor air intrusion.",
        "Unhealthy": "Children and elderly individuals should avoid all outdoor activity and remain indoors. Keep all windows closed and operate indoor air purifiers to clean the air. Ensure sensitive individuals have access to quick-relief medications if needed.",
        "Very Unhealthy": "Seniors and children must stay indoors and keep physical activity levels to a minimum to avoid respiratory strain. Keep all entryways sealed to prevent toxic outdoor air from leaking inside. If you must travel, use a vehicle with recirculating air conditioning.",
        "Hazardous": "This is an emergency-level health risk for vulnerable populations. Children and the elderly must remain in a sealed indoor environment with running air purifiers. Avoid all outdoor exposure, monitor breathing closely, and seek medical attention if distress occurs.",
    },
    "outdoor_workers": {
        "Good": "Conditions are safe and clear for all outdoor tasks and full shifts. Workers can carry out their duties without any breathing restrictions or special health-related pauses. No protective equipment or changes in scheduling are required.",
        "Moderate": "Air quality is acceptable for standard shifts, but workers should stay hydrated and monitor for early signs of respiratory discomfort. Those with pre-existing conditions like asthma should take light-duty options if they feel any chest tightness. Keep an eye on air quality updates during the workday.",
        "Unhealthy (Sensitive)": "Sensitive workers should limit heavy physical exertion and take more frequent breaks in clean, air-conditioned indoor spaces. Employers should consider adjusting shift schedules to avoid peak pollution times. Ensure drinking water and rest stations are easily accessible.",
        "Unhealthy": "All outdoor workers should reduce heavy manual labor and wear a certified respirator like an N95 mask while working outside. Take regular breaks indoors in a filtered environment to reduce cumulative exposure. Rotate workers to limit individual time on high-exertion tasks.",
        "Very Unhealthy": "Reschedule non-essential outdoor work to a day with better air quality, or move operations indoors. If work is mandatory, ensure all personnel wear properly fitted respirators and take frequent mandatory rests in sealed, clean-air environments. Monitor all team members closely.",
        "Hazardous": "Postpone all non-emergency outdoor work immediately. For emergency operations, workers must wear full respirators and limit exposure to short, strictly timed intervals. Establish a completely sealed clean-air shelter on-site for rest periods.",
    },
    "athletes": {
        "Good": "Atmospheric conditions are ideal for high-intensity training, long-run endurance work, and outdoor competitions. Take full advantage of the clean air to maximize your training volume. No respiratory constraints are expected.",
        "Moderate": "Outdoor training is generally fine, but sensitive athletes should monitor their breathing and reduce intensity if needed. Consider planning workouts away from high-traffic areas where localized pollution is higher. Ease off or move indoors if you feel chest tightness.",
        "Unhealthy (Sensitive)": "Athletes with respiratory sensitivities should move high-intensity or prolonged training indoors. Healthy athletes should consider reducing the duration or intensity of outdoor workouts. Stay well hydrated to support your body's natural defense mechanisms.",
        "Unhealthy": "Avoid outdoor aerobic workouts entirely and shift your training sessions to an indoor gym or filtered environment. High-intensity cardio outdoors under these conditions will lead to significant inhalation of harmful pollutants. Switch to strength training or low-impact exercises.",
        "Very Unhealthy": "Cancel all outdoor training, runs, and competitive athletic events. Exposure during intense training can cause long-term respiratory damage and acute performance drops. Keep all physical activity indoors in a well-ventilated, filtered room.",
        "Hazardous": "Athletic training of any kind must not take place outdoors. Rest completely or perform only light, indoor recovery exercises in a room with active HEPA air filtration. Do not jeopardize your health or respiratory system under these severe conditions.",
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