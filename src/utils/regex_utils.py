import pandas as pd
import re
from typing import Optional


def _extract_with_regex(text: Optional[str], pattern: str) -> Optional[str]:
    match = re.search(pattern, str(text))
    if match:
        if match.groups():
            return match.group(1)
        return match.group(0)
    return None
