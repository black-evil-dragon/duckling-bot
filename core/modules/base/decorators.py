from telegram import Update
from telegram.ext import ContextTypes

from core.models.user import User
from core.modules.base import messages
from utils.logger import get_logger

from functools import wraps
from typing import Callable, Tuple


log = get_logger()

# * UTILS _____________________________________________________________________
def get_update_context(args) -> Tuple["Update", "ContextTypes.DEFAULT_TYPE"]:
    for i in range(len(args) - 1, 0, -1):
        if (i > 0 and 
            isinstance(args[i-1], Update) and 
            hasattr(args[i], 'user_data')):
            return args[i-1], args[i]
    return None, None


async def handle_error(context: "ContextTypes.DEFAULT_TYPE", dialog_name: str = None) -> "ContextTypes.DEFAULT_TYPE":
    # user_id = context.user_data.get('user_id', None)
    # error: dict = context.user_data.get('error', {})
    
    # if user_id and error:
    #     await context.bot.send_message(
    #         chat_id=user_id,
    #         text=error.get('message', messages.unknown_error),
    #     )

    #     # Сбрасываем счетчик попыток и диалог
    #     context.user_data['dialog_branch__attempt'] = 0
    #     if dialog_name is not None:
    #         context.user_data[f'dialog_branch__{dialog_name}'] = False
        
    #     # Очищаем ошибку
    #     context.user_data['error'] = None
    
    return context



# * DECORATORS ___________________________________________________________________
def send_on_error():
    """
    # ! NOT TESTED

    Предполагается, что в контексте есть user_id
    
    Отправляет ошибку из контекста (если такова есть) пользователю

    """
    def decorator(func: Callable) -> Callable:        
        @wraps(func)
        async def wrapper(*args, **kwargs):
            _, context = get_update_context(args)
    
            context = handle_error(context)
            
            return await func(*args, **kwargs)

        
        return wrapper
    return decorator



def set_dialog_branch(dialog_name: str):
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            update, context = get_update_context(args)
            
            context.user_data[f'dialog_branch__{dialog_name}'] = True
            context.user_data['dialog_branch__attempt'] = 0
            context.user_data['error'] = None
            
            return func(*args, **kwargs)
        
        return wrapper
    return decorator



def ensure_dialog_branch(dialog_name: str, is_await=True, stop_after: bool = False, max_attempts: int = 3):
    """Декоратор для проверки диалоговой ветки"""
    
    def decorator(func: Callable) -> Callable:
        
        def count_attempts(context: "ContextTypes.DEFAULT_TYPE") -> int:
            current_attempt = context.user_data.get('dialog_branch__attempt', 0) + 1
            context.user_data['dialog_branch__attempt'] = current_attempt
            return current_attempt
        
        def is_dialog_process(dialog_name: str, context: "ContextTypes.DEFAULT_TYPE") -> bool:
            return context.user_data.get(f'dialog_branch__{dialog_name}', False)
        
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            update, context = get_update_context(args)
            
            # context = await handle_error(context, dialog_name)
            
            # Проверяем, активен ли диалог
            if is_dialog_process(dialog_name, context):
            #     # Проверяем количество попыток
            #     if count_attempts(context) > max_attempts:
            #         context.user_data['error'] = {
            #             'message': messages.attempts_error_message
            #         }
            #         context = await handle_error(context, dialog_name)
            #         return None
                
                result = await func(*args, **kwargs)
                

                if stop_after:
                    context.user_data[f'dialog_branch__{dialog_name}'] = False
                    context.user_data['dialog_branch__attempt'] = 0
                
                return result
                    
            #     except Exception as e:
            #         # Обработка исключений
            #         context.user_data['error'] = {
            #             'message': str(e)
            #         }
            #         context = await handle_error(context, dialog_name)
            #         return None
            # else:
            #     # Диалог не активен - пропускаем выполнение
            #     return None
            pass
        
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            # # Синхронная версия (аналогичная логика)
            # update, context = get_update_context(args)
            
            # if is_dialog_process(dialog_name, context):
            #     if count_attempts(context) > max_attempts:
            #         context.user_data['error'] = {
            #             'message': messages.attempts_error_message
            #         }
            #         return None
                
            #     result = func(*args, **kwargs)
                
            #     if stop_after:
            #         context.user_data[f'dialog_branch__{dialog_name}'] = False
            #         context.user_data['dialog_branch__attempt'] = 0
                
            #     return result
            # else:
            #     return None
            pass
        
        return async_wrapper if is_await else sync_wrapper
    
    return decorator



def ensure_user_settings(is_await=True, need_update=False):
    """
    
    Загружает в контекст user_data

    Args:
        is_await (bool, optional): Возвращает синхронную, либо ассинхронную функцию. Defaults to True.
        need_update (bool, optional): Жесткое обновление. Defaults to False.
    """
    def decorator(func: Callable) -> Callable:
        

        def load_user_data(update: "Update", context: "ContextTypes.DEFAULT_TYPE", need_update: bool = False) -> Tuple["Update", "ContextTypes.DEFAULT_TYPE"]:
            if not context.user_data.get("is_user_loaded", False) or need_update:
                user = update.effective_user

                user_model: User = User.objects.update_or_create(user_id=user.id, defaults=dict(
                    is_bot=user.is_bot,
                    first_name=user.first_name,
                    last_name=user.last_name,
                    username=user.username,
                ))

                context.user_data.update(dict(
                    is_user_loaded=True,
                    **user_model.get_user_data(),
                ))
            return update, context
        
        
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            update, context = get_update_context(args)
            load_user_data(update, context, need_update)
            return await func(*args, **kwargs)
        
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            update, context = get_update_context(args)
            load_user_data(update, context, need_update)
            return func(*args, **kwargs)
        
        return async_wrapper if is_await else sync_wrapper
    return decorator



# ! DEPRECATED
def command_process(is_run: bool = True, stop_after: bool = False):
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(update: 'Update', context: 'ContextTypes.DEFAULT_TYPE', **kwargs):
            log.warning(f'Deprecated: {func.__name__}. Не оптимизировано!')
            context.user_data['is_command_process'] = is_run
            
            result = await func(update, context, **kwargs)
            
            if stop_after:
                context.user_data['is_command_process'] = False
                
                
            return result
        
        return wrapper
    return decorator
# !END DEPRECATED