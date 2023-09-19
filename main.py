from telebot import TeleBot, types
from options.config import get_token
from options.parser import Parser
from telebot_calendar import Calendar, RUSSIAN_LANGUAGE
import datetime
from background import keep_alive

ERROR = 'ERROR'
main_menu_text = 'Привет, <b>студент БФУ</b>.\nВ этом боте ты можешь найти своё расписание. Просто кликай по кнопкам и следуй инструкциям.'
items_per_page = 15
bot = TeleBot(get_token())
parser = Parser()
all_groups = parser.get_groups()

calendar = Calendar(language=RUSSIAN_LANGUAGE)

def wrap_text(text, symbol):
    wrapped_text = symbol * len(text) + '\n'
    wrapped_text += text + '\n'
    wrapped_text += symbol * len(text)
    return wrapped_text

def create_keyboard_for_get_group(page, num):
    data_array = sorted(all_groups[num])
    keyboard = types.InlineKeyboardMarkup(row_width=3)
    start_idx = (page - 1) * items_per_page
    end_idx = min(start_idx + items_per_page, len(data_array))
    
    for i in range(start_idx, end_idx):
        keyboard.add(types.InlineKeyboardButton(text=data_array[i], callback_data=f"group-{data_array[i]}"))
    
    # Добавляем кнопки для переключения между страницами
    buttons = []
    if page > 1:
        buttons.append(types.InlineKeyboardButton(text="<", callback_data=f"prev_page_get_group_{num}_{page - 1}"))
    else:
        buttons.append(types.InlineKeyboardButton(text=" ", callback_data=f"None_prev_page"))
    buttons.append(types.InlineKeyboardButton(text=f'{page}', callback_data='None'))
    if end_idx < len(data_array):
        buttons.append(types.InlineKeyboardButton(text=">", callback_data=f"next_page_get_group_{num}_{page + 1}"))
    else:
        buttons.append(types.InlineKeyboardButton(text=" ", callback_data=f"None_next_page"))
    keyboard.row(*buttons)
    keyboard.add(types.InlineKeyboardButton('В главное меню', callback_data=f'main_menu'))

    return keyboard

def move_menu(message, new_text, keyboard,  new_photo = None, parse_mode=None):
        try:
            bot.delete_message(message.chat.id, message.id)
        except:
            pass
        if new_text:
            if new_photo:
                bot.send_photo(message.chat.id, types.InputFile(new_photo), new_text,
                            reply_markup=keyboard)
            else:
                bot.send_message(message.chat.id, new_text,
                                reply_markup=keyboard, parse_mode=parse_mode)
        else:
            bot.send_photo(message.chat.id, types.InputFile(new_photo),
                        reply_markup=keyboard)

def main_menu(message):
    keyboard = types.InlineKeyboardMarkup(row_width=1)
    keyboard.add(types.InlineKeyboardButton('Получить расписание', callback_data=f'get_num'))
    keyboard.add(types.InlineKeyboardButton('Сказать спасибо автору', callback_data=f'donate'))
    text = main_menu_text
    move_menu(message, text, keyboard, parse_mode='html')

@bot.message_handler(commands=['start'])
def start(message):
    main_menu(message)

@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call):
    if call.message:
        if call.data == 'main_menu':
            main_menu(call.message)
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
            move_menu(call.message, text, keyboard, new_photo=parser.get_image_groups())
        if call.data == 'donate':
            keyboard = types.InlineKeyboardMarkup()
            keyboard.add(types.InlineKeyboardButton('Назад', callback_data='main_menu'))
            text = 'Если вам нравится этот бот и вы хотите чтобы он существовал и развивался дальше, вы можете поддержать автра:\n\n💳 - 2200 7007 2020 6035'
            move_menu(call.message, text, keyboard)
        if call.data.startswith('group-'):
            _, group = call.data.split('-')
            now = datetime.datetime.now()
            text = 'Выберите дату:'
            keyboard = calendar.create_calendar(name=f'calendar-{group}', year=now.year, month=now.month)
            move_menu(call.message, text, keyboard)
        if call.data.startswith('calendar'):
            name, action, year, month, day = call.data.split(':')
            group = name.split('-')[1]
            date = calendar.calendar_query_handler(bot=bot, call=call, name=name, action=action, year=year, month=month, day=day)
            if action == 'DAY':
                selected_date = date.strftime('%d.%m.%Y')
                callback_inline(types.CallbackQuery(id=call.id, from_user=call.from_user, chat_instance=call.chat_instance, json_string=None, message=call.message, data=f'daygroup-{group}-{selected_date}'))
            if action == 'CANCEL':
                callback_inline(types.CallbackQuery(id=call.id, from_user=call.from_user, chat_instance=call.chat_instance, json_string=None, message=call.message, data='main_menu'))
        if call.data.startswith('daygroup-'):
            message = bot.send_message(call.message.chat.id, 'Подождите пару секунд... Составляем ваше расписание...')
            _, group, day = call.data.split('-')
            schedule = parser.get_week_lessons(group, day)
            keyboard = types.InlineKeyboardMarkup(row_width=1)
            keyboard.add(types.InlineKeyboardButton('Назад', callback_data=f'group-{group}'))
            keyboard.add(types.InlineKeyboardButton('В главное меню', callback_data=f'main_menu'))
            text = f'Расписание для группы: {group}\n'
            if schedule and schedule != ERROR:
                for date, lessons in schedule.items():
                    if lessons and lessons != ERROR:
                        text += f'<b>{date}</b>\n'
                        for lesson in lessons:
                            text += f'<b>{lesson["number"]}</b>\n{lesson["time"]}\n{lesson["name"]}\n{lesson["teacher"]}\n{lesson["class"]}\n{lesson["group"]}\n\n'
                        text += '\n\n'
            move_menu(message, text, keyboard, parse_mode='html')
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
 

if __name__ == '__main__':
    started = False
    keep_alive()
    while True:
        try:
            if not started:
                bot.polling(non_stop=True, interval=0)
        except Exception:
            bot.stop_polling()
            started = False
    

    bot.stop_polling
