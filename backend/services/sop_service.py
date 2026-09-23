import yaml
from datetime import datetime


class SOPService:

    def __init__(self, policy_path: str = "data/sop.yaml"):
        self.policy_path = policy_path
        self.rules = self._load_rules()

    def _load_rules(self):
        with open(self.policy_path, "r", encoding="utf-8") as file:
            data = yaml.safe_load(file) or {}

        return data.get("rules", [])

    def get_rules(self):
        return self.rules

    def evaluate_rule(self, weather: dict, intent: dict):
        matched_rules = []

        current = weather.get("current", {})
        hourly = weather.get("hourly", {})

        # -----------------------------
        # Normalize current weather
        # -----------------------------
        normalized_weather = {
            "wind_speed_kmh": current.get("wind_speed_10m"),
            "temperature_c": current.get("temperature_2m"),
            "precipitation_probability": current.get(
                "precipitation_probability"
            ),
            "weather_code": current.get("weather_code"),
        }

        # -----------------------------
        # Get UV data
        # -----------------------------
        times = hourly.get("time", [])
        uv_values = hourly.get("uv_index", [])

        if uv_values and times:
            current_time = current.get("time")
            requested_time = intent.get("time")

            # User asked about TODAY
            if requested_time == "today" and current_time:
                current_date = current_time[:10]

                today_uv = [
                    uv
                    for time, uv in zip(times, uv_values)
                    if time.startswith(current_date)
                ]

                if today_uv:
                    # For "today", use the maximum UV
                    normalized_weather["uv_index"] = max(today_uv)

            # For requests without "today",
            # use the UV closest to current time
            elif current_time:
                try:
                    current_dt = datetime.fromisoformat(current_time)

                    closest_index = min(
                        range(len(times)),
                        key=lambda i: abs(
                            datetime.fromisoformat(times[i])
                            - current_dt
                        ),
                    )

                    normalized_weather["uv_index"] = uv_values[
                        closest_index
                    ]

                except (ValueError, TypeError):
                    pass

        # -----------------------------
        # Thunderstorm detection
        # -----------------------------
        normalized_weather["thunderstorm"] = self._is_thunderstorm(
            normalized_weather.get("weather_code")
        )

        # -----------------------------
        # Combine weather + user intent
        # -----------------------------
        context = {
            **normalized_weather,
            **intent,
        }

        print("SOP CONTEXT:", context)

        # -----------------------------
        # Evaluate rules
        # -----------------------------
        for rule in self.rules:
            if self._matches(rule, context):
                matched_rules.append({
                    "id": rule["id"],
                    "name": rule["name"],
                    "severity": rule["severity"],
                    "guidance": rule["guidance"],
                })

        return matched_rules

    def _is_thunderstorm(self, weather_code):

        if weather_code is None:
            return False

        return weather_code in [95, 96, 99]

    def _matches(self, rule, context):

        conditions = rule.get("conditions", {})

        for key, condition in conditions.items():

            value = context.get(key)

            # Required value does not exist
            if value is None:
                return False

            # greater_than
            if "greater_than" in condition:
                try:
                    if float(value) <= float(
                        condition["greater_than"]
                    ):
                        return False
                except (TypeError, ValueError):
                    return False

            # greater_than_or_equal
            if "greater_than_or_equal" in condition:
                try:
                    if float(value) < float(
                        condition["greater_than_or_equal"]
                    ):
                        return False
                except (TypeError, ValueError):
                    return False

            # equals
            if "equals" in condition:

                expected = condition["equals"]

                if value != expected:
                    return False

            # in
            if "in" in condition:

                allowed = condition["in"]

                if value not in allowed:
                    return False

            # between
            if "between" in condition:

                start, end = condition["between"]

                try:
                    if isinstance(value, str):

                        value_time = datetime.strptime(
                            value,
                            "%H:%M"
                        ).time()

                        start_time = datetime.strptime(
                            str(start),
                            "%H:%M"
                        ).time()

                        end_time = datetime.strptime(
                            str(end),
                            "%H:%M"
                        ).time()

                        if not (
                            start_time
                            <= value_time
                            <= end_time
                        ):
                            return False

                    else:

                        if not (
                            float(start)
                            <= float(value)
                            <= float(end)
                        ):
                            return False

                except (TypeError, ValueError):
                    return False

        return True