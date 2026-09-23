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

        current = weather.get("current", {})
        hourly = weather.get("hourly", {})

        data = {
            "wind_speed_kmh": current.get("wind_speed_10m"),
            "temperature_c": current.get("temperature_2m"),
            "precipitation_probability": current.get(
                "precipitation_probability"
            ),
            "weather_code": current.get("weather_code"),
        }

        times = hourly.get("time", [])
        uv_values = hourly.get("uv_index", [])
        current_time = current.get("time")

        if times and uv_values and current_time:
            try:
                current_dt = datetime.fromisoformat(current_time)

                index = min(
                    range(min(len(times), len(uv_values))),
                    key=lambda i: abs(
                        datetime.fromisoformat(times[i]) - current_dt
                    )
                )

                data["uv_index"] = uv_values[index]

            except (ValueError, TypeError):
                data["uv_index"] = None

        if current_time:
            try:
                data["time"] = datetime.fromisoformat(
                    current_time
                ).strftime("%H:%M")
            except (ValueError, TypeError):
                data["time"] = None

        data["thunderstorm"] = self._is_thunderstorm(
            data.get("weather_code")
        )

        context = {
            **data,
            **intent
        }

        print("SOP CONTEXT:", context)

        matched = []

        for rule in self.rules:
            if self._matches(rule, context):
                matched.append({
                    "id": rule.get("id"),
                    "name": rule.get("name"),
                    "severity": rule.get("severity"),
                    "guidance": rule.get("guidance"),
                })

        return matched

    def _is_thunderstorm(self, weather_code):

        if weather_code is None:
            return False

        return weather_code in [95, 96, 99]

    def _matches(self, rule, context):

        conditions = rule.get("conditions", {})

        for key, condition in conditions.items():

            value = context.get(key)

            if value is None:
                return False

            if "greater_than" in condition:
                try:
                    if float(value) <= float(
                        condition["greater_than"]
                    ):
                        return False
                except (TypeError, ValueError):
                    return False

            if "greater_than_or_equal" in condition:
                try:
                    if float(value) < float(
                        condition["greater_than_or_equal"]
                    ):
                        return False
                except (TypeError, ValueError):
                    return False

            if "equals" in condition:

                expected = condition["equals"]

                if value != expected:
                    return False

            if "in" in condition:

                allowed = condition["in"]

                if value not in allowed:
                    return False

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