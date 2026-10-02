"""
Indonesia Multifinance Localized Bot Package.
"""
from q3_multilingual.indonesia.flow_engine import IndonesiaMultifinanceBot
from q3_multilingual.indonesia.system_prompt import get_indonesia_system_prompt
from q3_multilingual.indonesia.kb_data import ID_MULTIFINANCE_KB

__all__ = [
    "IndonesiaMultifinanceBot",
    "get_indonesia_system_prompt",
    "ID_MULTIFINANCE_KB"
]
