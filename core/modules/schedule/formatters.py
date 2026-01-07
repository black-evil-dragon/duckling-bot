from datetime import datetime, timedelta
from typing import Dict, List


def get_date_by_weekday(start_date, weekday):
    start = datetime.strptime(start_date, "%Y-%m-%d")
    delta = (weekday - 1) - start.weekday()

    if delta < 0:
        delta += 7

    target_date = start + timedelta(days=delta)

    return target_date.strftime("%d.%m.%Y")


def split_message(text: str, max_length=4096) -> List[str]:
    if len(text) <= max_length:
        return [text]

    parts = []
    while text:
        if len(text) <= max_length:
            parts.append(text)
            break

        # Ищем последний перенос строки в пределах лимита
        split_pos = text.rfind("\n", 0, max_length)

        # Если переноса строки нет, ищем последний пробел
        if split_pos == -1:
            split_pos = text.rfind(" ", 0, max_length)

        # Если и пробела нет, просто обрезаем по max_length
        if split_pos == -1:
            split_pos = max_length

        parts.append(text[:split_pos])
        text = text[split_pos:].lstrip()

    return parts
