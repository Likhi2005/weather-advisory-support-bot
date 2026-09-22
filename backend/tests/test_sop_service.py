from services.sop_service import SOPService

service = SOPService(policy_path="data/sop.yaml")
weather = {
    "wind_speed_kmh": 45
}

intent = {
    "activity": "cycling"
}
results = service.evaluate_rule(weather, intent)

print(results)