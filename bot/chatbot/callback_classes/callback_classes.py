from .callback_interface import CallbackInterface
from ..utils import user_checker_decorator


class Start(CallbackInterface):

    @user_checker_decorator(with_message=True)
    async def handle(self, update, context):
            await context.bot.send_message(chat_id=update.effective_chat.id, text=self.MESSAGES['start']['message'])
