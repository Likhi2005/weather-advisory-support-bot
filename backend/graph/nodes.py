from services.sop_service import SOPService

sop_service = SOPService(policy_path="data/sop.yaml")

def evaluate_sops(state):
    weather = state["weather"]
    intent = state.get("intent", {})
    
    matched_sops = sop_service.evaluate_rule(
        weather=weather,
        intent=intent
        )
    
    return {
        "sop_results": matched_sops
    }
    
    