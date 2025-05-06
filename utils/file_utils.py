from typing import List


def read_lines(filename: str) -> List[str]:
    lines = []
    with open(filename, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                lines.append(line)
    return lines