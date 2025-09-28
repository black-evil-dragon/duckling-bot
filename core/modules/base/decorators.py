from telegram import ReplyKeyboardMarkup, Update
from telegram.ext import ContextTypes

from core.models.user import User
from core.modules.base import messages
from utils.logger import get_logger

from functools import wraps
from typing import Callable, Tuple


log = get_logger()

# * UTILS _____________________________________________________________________

# Вообще странная штуковина, получилось вот так
class ContextManage:
    context: "ContextTypes.DEFAULT_TYPE"
    update: "Update"
    
    def set_context(self, context: "ContextTypes.DEFAULT_TYPE") -> None:
        self.context = context
    
    def set_context_from_args(self, args):
        self.update, self.context = self.get_update_context(args)
        
    def get_update_context(self, args) -> None:
        for i in range(len(args) - 1, 0, -1):
            if (i > 0 and 
                isinstance(args[i-1], Update) and 
                hasattr(args[i], 'user_data')):
                
                return args[i-1], args[i]
        return None, None

    def get_context(self) -> "ContextTypes.DEFAULT_TYPE":
        return self.context
    
    def get_update(self) -> "Update":
        return self.update


    # * ERROR MANAGER
    def set_error(self, error: dict) -> "ContextTypes.DEFAULT_TYPE":
        self.context.user_data['error'] = error
        
        
    # * ATTEMPT MANAGER
    def current_attempt(self) -> int:
        return self.context.user_data.get('attempt', 0)
    
    def increment_context_attempt(self) -> "ContextTypes.DEFAULT_TYPE":
        attempt = self.current_attempt() + 1
        self.context.user_data['attempt'] = attempt
        
        return self.context
    
    def reset_context_attempt(self) -> "ContextTypes.DEFAULT_TYPE":
        self.context.user_data['attempt'] = 0
        return self.context
    
    
    # * DIALOG MANAGER
    def set_dialog_process(self, value: bool, dialog_name: str) -> "ContextTypes.DEFAULT_TYPE":
        self.context.user_data[f'dialog_branch__{dialog_name}'] = value
        return self.context

    def is_dialog_process(self, dialog_name: str) -> bool:
        return self.context.user_data.get(f'dialog_branch__{dialog_name}', False)
              
              
                
def get_update_context(args) -> Tuple["Update", "ContextTypes.DEFAULT_TYPE"]:
    for i in range(len(args) - 1, 0, -1):
        if (i > 0 and 
            isinstance(args[i-1], Update) and 
            hasattr(args[i], 'user_data')):
            return args[i-1], args[i]
    return None, None



async def handle_error(context: "ContextTypes.DEFAULT_TYPE", dialog_name: str = None) -> "ContextTypes.DEFAULT_TYPE":
    user_id = context.user_data.get('user_id', None)
    error: dict = context.user_data.get('error', {})
    
    reply_markup = ReplyKeyboardMarkup(context.bot_data.get('command_keyboard'), one_time_keyboard=True, resize_keyboard=True)
    
    if user_id and error:
        await context.bot.send_message(
            chat_id=user_id,
            text=error.get('message', messages.unknown_error),
            reply_markup=reply_markup,
        )
        context.user_data['error'] = None
    
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
            manager = ContextManage()
            manager.set_context_from_args(args)
    
            await handle_error(manager.get_context())
            
            return await func(*args, **kwargs)

        
        return wrapper
    return decorator




def set_dialog_branch(dialog_name: str, value: bool = True, reset_attempt: bool = False):
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
    
            manager = ContextManage()
            manager.set_context_from_args(args)
            
            if reset_attempt:
                manager.reset_context_attempt()

            manager.set_dialog_process(value, dialog_name)
            
            return func(*args, **kwargs)
        
        return wrapper
    return decorator


def ensure_dialog_branch(dialog_name: str, stop_after: bool = False, max_attempts: int = 2):
    """Декоратор для проверки диалоговой ветки"""
    
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            
            manager = ContextManage()
            manager.set_context_from_args(args)
            
            log.debug(f'Run ensure_dialog_branch, attempt {manager.current_attempt()}')
            
            # * Проверяем, активен ли диалог
            if manager.is_dialog_process(dialog_name):
                result = await func(*args, **kwargs)
                data = dict(
                    stop_dialog=True
                )
                    
                if result is not None:
                    if isinstance(result, dict):
                        data.update(**result)
    
                    if stop_after and data.get('stop_dialog', True):
                        log.debug('Stop dialog')
                        manager.set_dialog_process(False, dialog_name)
                        
                    manager.reset_context_attempt()
                    
                    log.debug('Leave dialog branch')
                    
                    return result
                
                if result is None:
                    log.debug('Result is None')
                    manager.increment_context_attempt()
                    
                    log.debug(f'New attempt count {manager.current_attempt()}')
                    
                    if manager.current_attempt() > max_attempts:
                        log.debug('Max try reached')
                        manager.reset_context_attempt()
                        
                        manager.set_error(dict(
                            message=messages.attempts_error_message
                        ))
                                                
                        await handle_error(manager.get_context())
                        manager.set_dialog_process(False, dialog_name)
        

                    return result
        
        return wrapper
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