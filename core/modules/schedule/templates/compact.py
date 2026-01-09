from core.modules.schedule.templates.default import DefaultTemplate


class CompactTemplate(DefaultTemplate):
    def lesson_component(self, lesson: dict) -> str:
        title = self.get_short_lesson_name(lesson.get("title", ""))
        time = lesson.get("time", "")
        teacher = lesson.get("teacher", "")
        teacher_degree = lesson.get('teacher_degree', '')
        lesson_type = self.get_short_lesson_type(lesson.get("type", ""))
        location = lesson.get("location", "")
        subgroup = lesson.get("subgroup", "") or ""

        # Упрощаем локацию для дистанта
        if "Дистант" in location:
            location = "Дистант"

        if subgroup:
            time += f" | {subgroup}"

        return (
            f"┌ 🕒 <b>{time} | {location}</b>\n"
            f"│ 🎯 [{lesson_type}] {title}\n"
            f"└ 👨‍🏫 {teacher}"
        )
