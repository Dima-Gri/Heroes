from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

kb_start = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
btn1 = KeyboardButton("Начать новую игру")
btn2 = KeyboardButton('Статистика игр')
kb_start.add(btn1, btn2)

kb_nickname = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
btn1 = KeyboardButton("Сгенерировать рандомный ник")
kb_nickname.add(btn1)

kb_in_location = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
btn1 = KeyboardButton("Информация о локации")
btn1_1 = KeyboardButton("Информация о персонаже")
btn2 = KeyboardButton("Зайти в магазин")
btn3 = KeyboardButton('Зайти в инвентарь')
btn4 = KeyboardButton("Cоседние локации")
btn5 = KeyboardButton('Перейти в другую локацию')
kb_in_location.add(btn1, btn1_1, btn2, btn3, btn4, btn5)

kb_in_dungeon = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
btn1 = KeyboardButton("Информация о персонаже")
btn2 = KeyboardButton("Информация о мобе")
btn3 = KeyboardButton('Зайти в инвентарь')
btn4 = KeyboardButton('Выпить зелье')
btn5 = KeyboardButton('Выбрать тип атаки')
btn6 = KeyboardButton('Атаковать моба')
kb_in_dungeon.add(btn1, btn2, btn3, btn4, btn5, btn6)

kb_attack_type = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
btn1 = KeyboardButton("Физическая")
btn2 = KeyboardButton("Магическая")
kb_attack_type.add(btn1, btn2)

kb_after_win = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
btn1 = KeyboardButton("Информация о персонаже")
btn2 = KeyboardButton('Перейти в другую локацию')
kb_after_win.add(btn1, btn2)


kb_market = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
btn1 = KeyboardButton("Продать собственные товары")
btn2 = KeyboardButton('Купить товары')
kb_market.add(btn1, btn2)

kb_cancel = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
btn1 = KeyboardButton("Отмена")
kb_cancel.add(btn1)

kb_change_clothes = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
btn1 = KeyboardButton("Переодеться")
btn2 = KeyboardButton("Назад")
kb_change_clothes.add(btn1, btn2)
