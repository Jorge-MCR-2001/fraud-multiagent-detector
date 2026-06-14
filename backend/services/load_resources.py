import json
from typing import List, Dict, Any
from settings.paths import FRAUD_POLICY_DIR


def load_json_file() ->  List[Dict[str, Any]]:

    with open(FRAUD_POLICY_DIR, "r", encoding="utf-8") as json_file:
        policies = json.load(json_file)
        return policies