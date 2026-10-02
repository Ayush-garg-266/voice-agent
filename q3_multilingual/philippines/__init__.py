"""
Philippines Bancassurance Localized Bot Package.
"""
from q3_multilingual.philippines.flow_engine import PhilippinesBancassuranceBot
from q3_multilingual.philippines.system_prompt import get_philippines_system_prompt
from q3_multilingual.philippines.kb_data import PH_BANCASSURANCE_KB

__all__ = [
    "PhilippinesBancassuranceBot",
    "get_philippines_system_prompt",
    "PH_BANCASSURANCE_KB"
]
