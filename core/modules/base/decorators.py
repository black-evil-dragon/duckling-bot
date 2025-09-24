from telegram import Update
from telegram.ext import ContextTypes

from core.models.user import User

from functools import wraps
from typing import Callable, Tuple

from utils.logger import get_logger



log = get_logger()

# * UTILS _____________________________________________________________________
def get_update_context(args) -> Tuple["Update", "ContextTypes.DEFAULT_TYPE"]:
    for i in range(len(args) - 1, 0, -1):
        if (i > 0 and 
            isinstance(args[i-1], Update) and 
            hasattr(args[i], 'user_data')):
            return args[i-1], args[i]
    return None, None
        
        

# * DECORATORS ___________________________________________________________________
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



def set_dialog_branch(dialog_name: str, is_await=True):
    """
    # ! NOT TESTED

    Args:
        dialog_name (str): _description_
        is_await (bool, optional): _description_. Defaults to True.
    """
    def decorator(func: Callable) -> Callable:        
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            update, context = get_update_context(args)
    
            context.user_data.update({
                f'dialog_branch__{dialog_name}': True
            })
            
            return await func(*args, **kwargs)
        
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            update, context = get_update_context(args)
            
            context.user_data.update({
                f'dialog_branch__{dialog_name}': True
            })
            
            return func(*args, **kwargs)
        
        return async_wrapper if is_await else sync_wrapper
    return decorator



def ensure_dialog_branch(dialog_name: str, is_await=True, stop_after: bool = False):
    """
    # ! NOT TESTED
    Проверка на наличие диалога в контексте user_data
        
    Если "is_(dialog_name)" продолжаем, иначе прерываем выполнение

    Args:
        dialog_name (str): _description_
        is_await (bool, optional): _description_. Defaults to True.
    """    

    def decorator(func: Callable) -> Callable:
        
        def is_dialog_process(dialog_name: str, context: "ContextTypes.DEFAULT_TYPE") -> bool:
            return context.user_data.get(f'dialog_branch__{dialog_name}', False)
        
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            update, context = get_update_context(args)
    
            if is_dialog_process(dialog_name, context):
                result = await func(*args, **kwargs)
                
                if stop_after and result:
                    context.user_data.update({f'dialog_branch__{dialog_name}': False})
                return result
        
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            update, context = get_update_context(args)
            
            if is_dialog_process(dialog_name, context):
                result = func(*args, **kwargs)
                
                if stop_after and result:
                    context.user_data.update({f'dialog_branch__{dialog_name}': False})
                    
                return result
        
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
