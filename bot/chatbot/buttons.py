from telegram import InlineKeyboardButton

class ButtonBuilder:
    def __init__(self, name: str, id: int):
        self.text = None
        self.name = name
        self.id = id

    def build_conversation_choice_button(self):
        self.text = f'{self.name}'
        callback_data = f'ConversationOptions_{self.name}_{self.id}'
        return InlineKeyboardButton(self.text, callback_data=callback_data)
    
    def build_conversation_delete_button(self):
        self.text = f'Удалить диалог "{self.name}"'
        callback_data = f'ConversationDelete_{self.name}_{self.id}'
        return InlineKeyboardButton(self.text, callback_data=callback_data)
    
    def build_conversation_choose_button(self):
        self.text = f'Выбрать диалог "{self.name}" в качестве активного'
        callback_data = f'ConversationChoice_{self.name}_{self.id}'
        return InlineKeyboardButton(self.text, callback_data=callback_data)
    
    def build_conversation_create_button(self):
        self.text = f'Создать диалог'
        callback_data = f'ConversationCreate_{self.name}_{self.id}'
        return InlineKeyboardButton(self.text, callback_data=callback_data)
    
    def build_conversation_view_button(self):
        self.text = f'Просмотреть диалог "{self.name}"'
        callback_data = f'ConversationView_{self.name}_{self.id}'
        return InlineKeyboardButton(self.text, callback_data=callback_data)
    

class ButtonDirector:

    def __init__(self, name, id):
        self.name = name
        self.id = id
        
    def build_conversation_options_buttons(self):
        return [
            [ButtonBuilder(self.name, self.id).build_conversation_choose_button()],
            [ButtonBuilder(self.name, self.id).build_conversation_delete_button()],
            [ButtonBuilder(self.name, self.id).build_conversation_view_button()],
        ]
