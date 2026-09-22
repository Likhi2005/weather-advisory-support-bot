import yaml

class SOPService:
    def __init__(self, policy_path: str = "backend/data/sop.yaml"):
        self.policy_path = policy_path
        self.rules = self._load_rules()
        
    
    def _load_rules(self):
        try:
            with open(self.policy_path, 'r') as file:
                data = yaml.safe_load(file)
            
            return data.get('rules',[])
        
        except FileNotFoundError:
            raise FileNotFoundError(f"Policy file not found at policy_path")
    
    def get_rules(self):
        return self.rules
    
    def evaluate_rule(self, weather: dict, intent: dict):
        method_rules = []
        for rule in self.rules:
            if self._matches(rule, weather, intent):
                method_rules.append({
                    "id": rule["id"],
                    "name": rule["name"],
                    "severity": rule["severity"],
                    "guidance": rule["guidance"],
                })
        return method_rules
    
    def _matches(self,rules:dict,weather:dict,intent:dict):
        conditions = rules.get("conditions", {})
        for key, condition in conditions.items():
            value = weather.get(key)
            
            if value is None:
                value = intent.get(key)
            if value is None:
                return False
            
            if "greater_than" in condition:
                if value <= condition["greater_than"]:
                    return False
            
            if "greater_than_or_equal" in condition:
                if value < condition["greater_than_or_equal"]:
                    return False
            
            if "in" in condition:
                if value not in condition["in"]:
                    return False
        return True
        
        