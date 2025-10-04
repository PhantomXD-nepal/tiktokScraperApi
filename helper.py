import re


def parse_count(s: str) -> int:
    """
    Parse a string representing a count with possible suffixes like 1.2M or 5.4K into an integer.
    """
    if not s:
        return 0

    s = s.strip().replace(",", "")
    m = re.match(r"^([\d,.]+)\s*([MKk]?)$", s)
    if not m:
        digits = re.findall(r"\d+", s)
        return int(digits[0]) if digits else 0
    number, suffix = m.groups()
    number = float(number)
    if suffix.upper() == "M":
        number *= 1_000_000
    elif suffix.upper() == "K":
        number *= 1_000
    return int(number)
