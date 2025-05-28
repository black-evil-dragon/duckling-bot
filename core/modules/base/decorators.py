from functools import wraps
from typing import Callable

from telegram import Update
from telegram.ext import ContextTypes

from core.db import Database


def ensure_user_settings(is_await=True, need_update=False):
    def decorator(func: Callable) -> Callable:
        @wraps(func)

        def inner(update: 'Update', context: 'ContextTypes.DEFAULT_TYPE',):
            if not context.user_data.get('is_user_loaded', False) or need_update:
                if context.bot_data.get('db'):
                    db: 'Database' = context.bot_data.get('db')
                    user = update.effective_user
                
                    user_data = {
                        "id": user.id,
                        "is_bot": user.is_bot,
                        "first_name": user.first_name,
                        "last_name": user.last_name,
                        "username": user.username,
                    }

                    saved_data = db.get_user(user.id)
                    if saved_data:
                        user_data.update(dict(
                            selected_group=saved_data.get('group_id'),
                            selected_subgroup=saved_data.get('subgroup_id'),
                            user_settings=saved_data.get('user_settings', {}),
                            is_user_loaded=True,
                        ))

                    db.add_or_update_user(user_data)
                    context.user_data.update({**user_data})
            return update, context
        

        if is_await:
            async def wrapper(*args, **kwargs):
                update = args[-2]
                context = args[-1]

                new_args = list(args)
                new_update, new_context = inner(update, context)
                new_args[-2:] = [new_update, new_context]
                
                return await func(*new_args, **kwargs)
        else:
            def wrapper(*args, **kwargs):
                update = args[-2]
                context = args[-1]
                
                new_args = list(args)
                new_update, new_context = inner(update, context)
                new_args[-2:] = [new_update, new_context]
                
                return func(*new_args, **kwargs)
            

        return wrapper
    return decorator