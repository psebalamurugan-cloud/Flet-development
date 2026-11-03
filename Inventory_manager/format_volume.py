import re


def format_unit(text: str) -> str:
  # Matches a number, optional spaces, and 'mg' or 'gm' (case-insensitive)
  match = re.match(r"^(\d+)\s*(ml|gm|lt)$", text.strip(), re.IGNORECASE)
  if match:
    number, unit = match.groups()
    return f"{number} {unit.lower()}"
  return text

