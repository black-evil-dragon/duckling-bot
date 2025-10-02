
from core.modules.schedule.templates.default import DefaultTemplate


class CompactTemplate(DefaultTemplate):
    
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
            
        return (
            f"🕒 <b>[  {time} {subgroup}   ]</b>\n"
            f"📚 {lesson_type} - {title}\n"
            f"📍 {location}"
        )
  