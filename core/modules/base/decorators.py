from telegram import Update
from telegram.ext import ContextTypes

from core.db import Database
from core.models.user import User

from functools import wraps
from typing import Callable

from utils.logger import get_logger



log = get_logger()


def ensure_user_settings(is_await=True, need_update=False):
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def inner(
            update: "Update",
            context: "ContextTypes.DEFAULT_TYPE",
        ):
            if not context.user_data.get("is_user_loaded", False) or need_update:
                user = update.effective_user

                
                user_model: User = User.objects.get_or_create(user_id=user.id, defaults=dict(
                    is_bot=user.is_bot,
                    first_name=user.first_name,
                    last_name=user.last_name,
                    username=user.username,
                ))
                
                user_data = user_model.to_dict()
                
                user_data.update(dict(
                    is_user_loaded=True,
                    
                    user_model=user_model,
                    user_settings=user_model.get_user_settings(),
                    
                    **user_model.get_selected_data(),
                ))

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
