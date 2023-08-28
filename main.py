from telebot import TeleBot, types
from options.config import get_token
from options.parser import Parser
from telebot_calendar import Calendar, RUSSIAN_LANGUAGE
import datetime

ERROR = 'ERROR'
main_menu_text = 'Привет, студент (дописать)'
items_per_page = 15

bot = TeleBot(get_token('token.txt'))
parser = Parser()
all_groups = parser.get_groups()
calendar = Calendar(language=RUSSIAN_LANGUAGE)


def create_keyboard_for_get_group(page, num):
    data_array = sorted(all_groups[num])
    keyboard = types.InlineKeyboardMarkup()
    start_idx = (page - 1) * items_per_page
    end_idx = min(start_idx + items_per_page, len(data_array))
    
    for i in range(start_idx, end_idx):
        keyboard.add(types.InlineKeyboardButton(text=data_array[i], callback_data=f"group-{data_array[i]}"))
    
    # Добавляем кнопки для переключения между страницами
    if page > 1:
        keyboard.add(types.InlineKeyboardButton(text="<-", callback_data=f"prev_page_get_group_{num}_{page - 1}"))
    keyboard.add(types.InlineKeyboardButton(text=f'{page}', callback_data='None'))
    if end_idx < len(data_array):
        keyboard.add(types.InlineKeyboardButton(text="->", callback_data=f"next_page_get_group_{num}_{page + 1}"))
    
    keyboard.add(types.InlineKeyboardButton('В главное меню', callback_data=f'main_menu'))

    return keyboard

def move_menu(message, new_text, keyboard,  new_photo = None):
        bot.delete_message(message.chat.id, message.id)
        if new_text:
            if new_photo:
                bot.send_photo(message.chat.id, types.InputFile(new_photo), new_text,
                            reply_markup=keyboard)
            else:
                bot.send_message(message.chat.id, new_text,
                                reply_markup=keyboard)
        else:
            bot.send_photo(message.chat.id, types.InputFile(new_photo),
                        reply_markup=keyboard)


@bot.message_handler(commands=['start'])
def main_menu(message):
    keyboard = types.InlineKeyboardMarkup(row_width=1)
    keyboard.add(types.InlineKeyboardButton('Получить расписание', callback_data=f'get_num'))
    keyboard.add(types.InlineKeyboardButton('Сказать спасибо автору', callback_data=f'donate'))
    text = main_menu_text
    move_menu(message, text, keyboard)

@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call):
    if call.message:
        print(call.data)
        if call.data == 'main_menu':
            keyboard = types.InlineKeyboardMarkup(row_width=1)
            keyboard.add(types.InlineKeyboardButton('Получить расписание', callback_data=f'get_num'))
            keyboard.add(types.InlineKeyboardButton('Сказать спасибо автору', callback_data=f'donate'))
            text = 'Привет, студент (дописать)'
            move_menu(call.message, text, keyboard)
        if call.data == 'get_num':
            keyboard = types.InlineKeyboardMarkup(row_width=1)
            keyboard.add(types.InlineKeyboardButton('Бакалвриат', callback_data=f'get_group_03'))
            keyboard.add(types.InlineKeyboardButton('Магистратура', callback_data=f'get_group_04'))
            keyboard.add(types.InlineKeyboardButton('Магистратура', callback_data=f'get_group_05'))
            keyboard.add(types.InlineKeyboardButton('Аспирантура', callback_data=f'get_group_06'))
            keyboard.add(types.InlineKeyboardButton('Ординатура', callback_data=f'get_group_08'))
            text = 'Выберите уровень образования:'
            move_menu(call.message, text, keyboard)
        if call.data.startswith('get_group'):
            page = 1
            num = call.data.split('_')[-1]
            keyboard = create_keyboard_for_get_group(page, num)
            text = 'Выберите нужную группу:'
            move_menu(call.message, text, keyboard)
        if call.data == 'donate':
            pass
        if call.data.startswith('group-'):
            group = call.data.split('-')[1]
            print(group)
        if call.data.startswith('day-group-'):
            pass
        if call.data.startswith("prev_page_get_group_"):
            chat_id = call.message.chat.id
            message_id = call.message.message_id
            num = call.data.split('_')[-2]
            page = int(call.data.split("_")[-1])
            keyboard = create_keyboard_for_get_group(page, num)
            bot.edit_message_reply_markup(chat_id=chat_id, message_id=message_id, reply_markup=keyboard)
        if call.data.startswith("next_page_get_group_"):
            chat_id = call.message.chat.id
            message_id = call.message.message_id
            num = call.data.split('_')[-2]
            page = int(call.data.split("_")[-1])
            keyboard = create_keyboard_for_get_group(page, num)
            bot.edit_message_reply_markup(chat_id=chat_id, message_id=message_id, reply_markup=keyboard)


bot.infinity_polling()
            
    
        