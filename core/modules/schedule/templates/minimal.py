from core.modules.schedule.templates.default import DefaultTemplate


class MinimalTemplate(DefaultTemplate):

    def get_subgroup(self, lesson: dict) -> str:
        return (lesson.get('subgroup', '') or "").replace('подгруппа', 'ПГ')

    def lesson_component(self, lesson: dict) -> str:
        title: str = self.get_short_lesson_name(lesson.get("title", ""))
        time: str = lesson.get("time", "")
        lesson_type: str = self.get_short_lesson_type(lesson.get("type", ""))
        location: str = lesson.get("location", "")
        subgroup: str = self.get_subgroup(lesson)

        # Упрощаем локацию для дистанта
        if "Дистант" in location:
            location = "Дистант"

        time, _ = time.split(' - ')

        if subgroup:
            time += f" | {subgroup}"

        return (
            f"┌ 🕒 <b>{time} | {location}</b>\n"
            f"└ 🎯 [{lesson_type}] {title}"
        )