
from core.modules.schedule.templates.default import DefaultTemplate


class CompactTemplate(DefaultTemplate):
    
    
    def weekday_name_component(self, weekday_name):
        return f"<b>📚 {weekday_name}</b>"
    
    def lesson_component(self, lesson: dict) -> str:
        title = lesson.get('title', '')
        time = lesson.get('time', '')
        teacher = lesson.get('teacher', '')
        lesson_type = self.get_short_lesson_type(lesson.get('type', ''))
        location = lesson.get('location', '')
        subgroup = lesson.get('subgroup', '') or ''
        
        # Упрощаем локацию для дистанта
        if 'Дистант' in location:
            location = 'Дистант'
            
        if subgroup:
            time += f" {subgroup}"
            
        return (
            # ┌
            f"🕒- <b>[  {time}  ]</b>\n"
            f"  ├ {lesson_type} - {title}\n"
            f"  └ {location}"
        )
  