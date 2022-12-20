from random import randint

from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher.filters.state import StatesGroup, State
from query.bd_query import *
from create_bot import dp, person_fields, locations_fields
from keyboards.setting_keybords import *
from time import sleep

start_message = f'На данный момент вы находитесь в локации: <b>Возрождение</b>.\n' \
                f'На каждый ход у вас <b>60 секунд</b>(если не успеваете - проигрываете). Отсчет заканчивается, когда вы совершаете какое-то действие и сразу же начинается заново\n' \
                f'Поехали...'


class FSMLoop(StatesGroup):
    Nickname = State()
    move_to_location = State()
    move_process = State()
    pay = State()
    final_pay = State()
    final_sale = State()
    change_clothes = State()
    change_clothes_process = State()
    attack_type = State()
    potion = State()
    fight = State()
    my_sleep = State()


@dp.message_handler(Text("Статистика игр"))
async def get_stat(message: types.Message):
    ls = get_person_by_user_id(message.from_user.id)
    if not ls:
        await message.answer('Пока что вы не играли в нашу игру...', reply_markup=kb_start)
    else:
        for per in ls:
            await message.answer(
                f'<b>Nickname:</b> {per["Nickname"]}, <b>Money:</b> {per["Money"]}, <b>Опыт:</b> {per["XP"]}, <b>Максимальный уровень:</b> {per["Level"]}\n',
                parse_mode='HTML', reply_markup=kb_start)


@dp.message_handler(Text("Начать новую игру"))
async def start_game(message: types.Message):
    await FSMLoop.Nickname.set()
    await message.reply('Придумай своему персонажу ник', reply_markup=kb_nickname)


@dp.message_handler(Text("Сгенерировать рандомный ник"), state=FSMLoop.Nickname)
async def set_nick(message: types.Message, state: FSMContext):
    ls = get_nicknames_by_userid(int(message.from_user.id))

    await message.answer(f'Персонаж с ником: <b>user{len(ls) + 1}</b> создан\n' + start_message,
                         reply_markup=kb_in_location, parse_mode='HTML')
    insert_default_person(message.from_user.id, f'user{len(ls) + 1}')

    async with state.proxy() as data:
        data['nickname'] = f'user{len(ls) + 1}'
        data['current_location'] = "1"
        data['in_dungeon'] = False

    await FSMLoop.next()


@dp.message_handler(state=FSMLoop.Nickname)
async def set_nick(message: types.Message, state: FSMContext):
    ls = get_nicknames_by_userid(int(message.from_user.id))
    if message.text in ls:
        await message.reply(
            'Такой ник ты уже ранее использовал. Придумай что-то новое и отправь следующим сообщением...')
    else:
        await message.reply(f'Персонаж с ником: <b>{message.text}</b> создан\n' + start_message,
                            reply_markup=kb_in_location, parse_mode='HTML')
        insert_default_person(message.from_user.id, message.text)

        async with state.proxy() as data:
            data['nickname'] = message.text
            data['current_location'] = "1"
            data['in_dungeon'] = False
        await FSMLoop.next()


@dp.message_handler(Text("Информация о локации"), state=FSMLoop.move_to_location)
async def in_location(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        nickname = data['nickname']
    current_person = dict(zip(person_fields, select_by_user_id_nickname(message.from_user.id, nickname)))
    current_location = select_location_by_location_id(current_person['LocationID'])
    current_location = dict(zip(locations_fields, current_location))
    await message.answer(f'<b>Локация:</b> {current_location["Name"]}\n<b>Тип:</b> {current_location["LocationType"]}',
                         parse_mode='HTML', reply_markup=kb_in_location)


@dp.message_handler(Text("Зайти в магазин"), state=FSMLoop.move_to_location)
async def in_location(message: types.Message, state: FSMContext):
    await message.answer('Что хочешь в магазине', reply_markup=kb_market)
    await FSMLoop.pay.set()


@dp.message_handler(Text("Купить товары"), state=FSMLoop.pay)
async def buy_in_market(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        current_location = data['current_location']
        nickname = data['nickname']

    mes, index = '', 1
    ls = dict()
    flag = False
    for d in select_by_location_id_from_market(message.from_user.id, nickname, current_location):
        flag = True
        mes = f'{index}. <b>Товар:</b> {d["Name"]}, <b>тип товара:</b> {d["ItemType"]}, <b>стоимость:</b> {d["Cost"]}\n' \
              f'<b>Плюшки:</b>\n<b>Дополнительное HP:</b> {d["HP"]},\n' \
              f'<b>Дополнительная Мана:</b> {d["Mana"]}\n' \
              f'<b>Дополнительная атака:</b> {d["Attack"]}\n' \
              f'<b>Дополнительная магическая атака:</b> {d["Magic_Attack"]}\n' \
              f'<b>Дополнительная броня:</b> {d["Armour"]}\n' \
              f'<b>Дополнительная магическая броня:</b> {d["Magic_Armour"]}\n'
        await message.answer(mes, parse_mode='HTML')
        ls[index] = (d["ItemID"], d["Cost"])
        index += 1
    if not flag:
        await message.answer('Вы не можете ничего купить, так как у вас недостаточно деньжат', parse_mode='HTML',
                             reply_markup=kb_in_location)
        await FSMLoop.move_to_location.set()
    else:
        await message.answer('Напишите соответствующий индекс товара, который хотите приобрести', parse_mode='HTML',
                             reply_markup=kb_cancel)
        async with state.proxy() as data:
            data['available_items'] = ls
        await FSMLoop.next()


@dp.message_handler(Text("Отмена"), state=FSMLoop.final_pay)
async def cancel(message: types.Message, state: FSMContext):
    await message.answer('Вы вышли из магазина', reply_markup=kb_in_location)
    await FSMLoop.move_to_location.set()


@dp.message_handler(state=FSMLoop.final_pay)
async def buy(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        ls = data['available_items']
        nickname = data['nickname']
    try:
        itemID, itemCost = ls[int(message.text)]
    except:
        await message.answer('Неверный формат данных. Убедитесь, что вы ввели допустимое число и повторите попытку',
                             reply_markup=kb_cancel)
        return
    await FSMLoop.move_to_location.set()
    leaft_money = update_price_by_user_id_nickname_buy(message.from_user.id, nickname, int(itemCost), itemID)
    await message.answer(f'Товар приобретен, можете увидеть его в своем инвентаре\nУ вас осталось {leaft_money} денег',
                         reply_markup=kb_in_location)


@dp.message_handler(Text("Продать собственные товары"), state=FSMLoop.pay)
async def buy_in_market(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        nickname = data['nickname']

    mes, index = '', 1
    ls = dict()
    flag = False
    for d, put_on in select_from_inventory(message.from_user.id, nickname):
        flag = True
        mes = f'{index}. <b>Товар:</b> {d["Name"]}, <b>тип товара:</b> {d["ItemType"]}, <b>можно продать за:</b> {d["CostToSale"]}\n' \
              f'<b>Надет ли этот товар:</b> {put_on}\n' \
              f'<b>Плюшки:</b>\n<b>Дополнительное HP:</b> {d["HP"]},\n' \
              f'<b>Дополнительная Мана:</b> {d["Mana"]}\n' \
              f'<b>Дополнительная атака:</b> {d["Attack"]}\n' \
              f'<b>Дополнительная магическая атака:</b> {d["Magic_Attack"]}\n' \
              f'<b>Дополнительная броня:</b> {d["Armour"]}\n' \
              f'<b>Дополнительная магическая броня:</b> {d["Magic_Armour"]}\n'
        await message.answer(mes, parse_mode='HTML')
        ls[index] = (d["ItemID"], d["CostToSale"])
        index += 1
    if not flag:
        await message.answer('Ваш инвентарь пуст, продавать нечего', reply_markup=kb_in_location)
        await FSMLoop.move_to_location.set()
        return
    await message.answer('Напишите соответствующий индекс товара, который хотите продать', parse_mode='HTML',
                         reply_markup=kb_cancel)
    async with state.proxy() as data:
        data['available_items'] = ls
    await FSMLoop.final_sale.set()


@dp.message_handler(Text("Отмена"), state=FSMLoop.final_sale)
async def cancel(message: types.Message, state: FSMContext):
    await message.answer('Вы вышли из магазина', reply_markup=kb_in_location)
    await FSMLoop.move_to_location.set()


@dp.message_handler(state=FSMLoop.final_sale)
async def buy(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        ls = data['available_items']
        nickname = data['nickname']
    try:
        itemID, CostToSale = ls[int(message.text)]
    except:
        await message.answer('Неверный формат данных. Убедитесь, что вы ввели допустимое число и повторите попытку',
                             reply_markup=kb_cancel)
        return
    await FSMLoop.move_to_location.set()
    leaft_money = update_price_by_user_id_nickname_sale(message.from_user.id, nickname, int(CostToSale), itemID)
    await message.answer(f'Товар продан, в инвентаре его больше нет\nУ вас осталось {leaft_money} денег',
                         reply_markup=kb_in_location)


@dp.message_handler(Text("Зайти в инвентарь"), state=FSMLoop.move_to_location)
async def in_location(message: types.Message, state: FSMContext):
    mes, index = '', 1
    async with state.proxy() as data:
        nickname = data['nickname']
    flag = False
    ls = dict()
    for d, put_on in select_from_inventory(message.from_user.id, nickname):
        flag = True
        mes = f'{index}. <b>Товар:</b> {d["Name"]}, <b>тип товара:</b> {d["ItemType"]}, <b>можно продать за:</b> {d["CostToSale"]}\n' \
              f'<b>Надет ли этот товар:</b> {put_on}\n' \
              f'<b>Плюшки:</b>\n<b>Дополнительное HP:</b> {d["HP"]},\n' \
              f'<b>Дополнительная Мана:</b> {d["Mana"]}\n' \
              f'<b>Физическая атака:</b> {d["Attack"]}\n' \
              f'<b>Магическая атака:</b> {d["Magic_Attack"]}\n' \
              f'<b>Броня от физических атак:</b> {d["Armour"]}\n' \
              f'<b>Броня от магических атак:</b> {d["Magic_Armour"]}\n'
        ls[index] = d["ItemID"]
        index += 1
        await message.answer(mes, parse_mode='HTML')
    if not flag:
        async with state.proxy() as data:
            if data['in_dungeon']:
                await message.answer('Пока что инвентарь пуст', reply_markup=kb_in_dungeon)
            else:
                await message.answer('Пока что инвентарь пуст', reply_markup=kb_in_location)
    else:
        await message.answer('Выберите, что хотите сделать в инвентаре...', reply_markup=kb_change_clothes)
        async with state.proxy() as data:
            data['change_items'] = ls
        await FSMLoop.change_clothes.set()


@dp.message_handler(Text("Переодеться"), state=FSMLoop.change_clothes)
async def person_info(message: types.Message, state: FSMContext):
    await message.answer('Пришлите индекс товара, который хотели бы надеть', reply_markup=kb_cancel)
    await FSMLoop.next()


@dp.message_handler(Text("Отмена"), state=FSMLoop.change_clothes_process)
async def cancel(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        if data['in_dungeon']:
            await message.answer('Вы вышли из примерочной', reply_markup=kb_in_dungeon)
        else:
            await message.answer('Вы вышли из примерочной', reply_markup=kb_in_location)
    await FSMLoop.move_to_location.set()


@dp.message_handler(state=FSMLoop.change_clothes_process)
async def person_info(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        ls = data['change_items']
        nickname = data['nickname']
    try:
        set_cloth(message.from_user.id, nickname, ls[int(message.text)])
    except:
        await message.answer('Неверный формат данных. Убедитесь, что вы ввели допустимое число и повторите попытку',
                             reply_markup=kb_cancel)
        return
    async with state.proxy() as data:
        if data['in_dungeon']:
            await message.answer('Выбранный товар надет...', reply_markup=kb_in_dungeon)
        else:
            await message.answer('Выбранный товар надет...', reply_markup=kb_in_location)
    await FSMLoop.move_to_location.set()


@dp.message_handler(Text("Назад"), state=FSMLoop.change_clothes)
async def person_info(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        if data['in_dungeon']:
            await message.answer('Вы покинули инвентарь...', reply_markup=kb_in_dungeon)
        else:
            await message.answer('Вы покинули инвентарь...', reply_markup=kb_in_location)
    await FSMLoop.move_to_location.set()


@dp.message_handler(Text("Информация о персонаже"), state=FSMLoop.move_to_location)
async def person_info(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        nickname = data['nickname']
        if data['in_dungeon']:
            kb = kb_in_dungeon
        else:
            kb = kb_in_location
    info = dict(zip(person_fields, select_by_user_id_nickname(message.from_user.id, nickname)))
    await message.answer(f'<b>Персонаж:</b> {info["Nickname"]}, <b>текущее здоровье:</b> {info["CurHP"]}\n'
                         f'<b>Опыт и уровень:</b> {info["XP"]} опыта, {info["Level"]} уровень\n'
                         f'<b>В наличии:</b> {info["Money"]} денег\n'
                         f'<b>Физическая атака:</b> {info["Attack"]}\n'
                         f'<b>Магическая атака:</b> {info["Magic_Attack"]}\n'
                         f'<b>Броня от физических ударов:</b> {info["Armour"]}\n'
                         f'<b>Броня от магических ударов:</b> {info["Magic_Armour"]}\n',
                         reply_markup=kb, parse_mode='HTML')


@dp.message_handler(Text("Cоседние локации"), state=FSMLoop.move_to_location)
async def in_location(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        nickname = data['nickname']
    current_person = dict(zip(person_fields, select_by_user_id_nickname(message.from_user.id, nickname)))
    current_location = select_location_by_location_id(current_person['LocationID'])
    current_location = dict(zip(locations_fields, current_location))
    mes = ''
    for _, x, y, type, name in select_all_locations():
        dist = ((int(current_location['XCoord']) - int(x)) ** 2 + (
                int(current_location['YCoord']) - int(y)) ** 2) ** 0.5
        if dist <= 10 and dist != 0.0:
            mes += f'<b>Локация:</b> {name}, <b>Тип локации:</b> {type}, <b>Добираться:</b> {int(dist)} сек.\n'

    await message.answer(mes, parse_mode='HTML', reply_markup=kb_in_location)


@dp.message_handler(Text("Перейти в другую локацию"), state=FSMLoop.move_to_location)
async def in_location(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        nickname = data['nickname']

    current_person = dict(zip(person_fields, select_by_user_id_nickname(message.from_user.id, nickname)))
    current_location = select_location_by_location_id(current_person['LocationID'])
    current_location = dict(zip(locations_fields, current_location))
    mes, index = '', 1
    ls = dict()
    for LocationID, x, y, type, name in select_all_locations():
        dist = ((int(current_location['XCoord']) - int(x)) ** 2 + (
                int(current_location['YCoord']) - int(y)) ** 2) ** 0.5
        if dist <= 10 and dist != 0.0:
            mes += f'{index}. <b>Локация:</b> {name}, <b>Тип локации:</b> {type}, <b>Добираться:</b> {int(dist)} сек.\n'
            ls[index] = (LocationID, type, name, int(dist))
            index += 1

    async with state.proxy() as data:
        data['available_locations'] = ls
    mes += 'Напишите соответствующий индекс локации, в которую хотите попасть'
    await message.answer(mes, parse_mode='HTML', reply_markup=kb_cancel)
    await FSMLoop.next()


@dp.message_handler(Text("Отмена"), state=FSMLoop.move_process)
async def cancel(message: types.Message, state: FSMContext):
    await message.answer('Процесс перемещения отменен...', reply_markup=kb_in_location)
    await FSMLoop.move_to_location.set()


@dp.message_handler(state=FSMLoop.move_process)
async def in_location(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        nickname = data['nickname']
        ls = data['available_locations']
    try:
        location = ls[int(message.text)]
    except:
        await message.answer('Неверный формат данных. Убедитесь, что вы ввели допустимое число и повторите попытку',
                             reply_markup=kb_cancel)
        return
    await message.answer(f'Вы выдвинулись в локацию: <b>{location[2]}</b>({location[1]})\n'
                         f'Путь займет {location[3]} сек.\n'
                         f'Как персонаж доберется до локации, я вас уведомлю...', parse_mode='HTML')
    await FSMLoop.my_sleep.set()
    await asyncio.sleep(int(location[3]))
    update_by_user_id_nickname(message.from_user.id, nickname, location[0])
    if location[1] == 'подземелье':
        await message.answer(f'Вы прибыли в локацию: <b>{location[2]}</b>({location[1]})', reply_markup=kb_in_dungeon,
                             parse_mode='HTML')
        available_mobs = select_all_mobs(message.from_user.id, nickname)
        index = randint(0, len(available_mobs) - 1)
        mob = dict(zip(mobs_fields, available_mobs[index]))
        async with state.proxy() as data:
            data['mob'] = mob
            data['in_dungeon'] = True
            data['attack_type'] = 'Физическая'

        await message.answer(f'Тут вам предстоит битва с мобом <b>{mob["Name"]}</b>\n'
                             f'Бой началася, ход за вами(по умолчанию вид атаки физический)', parse_mode='HTML',
                             reply_markup=kb_in_dungeon)

    else:
        await message.answer(f'Вы прибыли в локацию: <b>{location[2]}</b>({location[1]})', reply_markup=kb_in_location,
                             parse_mode='HTML')

        async with state.proxy() as data:
            data['in_dungeon'] = False

    async with state.proxy() as data:
        data['current_location'] = location[0]
    await FSMLoop.move_to_location.set()


mobs_fields = ['MobID', 'HP', 'XP', 'ReqLevel', 'AttackType', 'Attack', 'Armour', 'Magic_Armour', 'Name']


@dp.message_handler(Text("Информация о мобе"), state=FSMLoop.move_to_location)
async def person_info(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        info = data['mob']
    await message.answer(f'<b>Моб:</b> {info["Name"]}, <b>текущее здоровье:</b> {info["HP"]}\n'
                         f'<b>Вы заработаете:</b> {info["XP"]} опыта и {info["XP"]} денег\n'
                         f'<b>Тип атаки:</b> {info["AttackType"]}\n'
                         f'<b>Базовая атака:</b> {info["Attack"]}\n'
                         f'<b>Физическая броня:</b> {info["Armour"]}\n'
                         f'<b>Магическая броня:</b> {info["Magic_Armour"]}\n',
                         reply_markup=kb_in_dungeon, parse_mode='HTML')


@dp.message_handler(Text("Выбрать тип атаки"), state=FSMLoop.move_to_location)
async def person_info(message: types.Message, state: FSMContext):
    await message.answer('Выберите тип атаки', reply_markup=kb_attack_type)
    await FSMLoop.attack_type.set()


@dp.message_handler(Text("Физическая"), state=FSMLoop.attack_type)
async def person_info(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['attack_type'] = 'Физическая'
    await message.answer('Тип атаки установлен...', reply_markup=kb_in_dungeon)
    await FSMLoop.move_to_location.set()


@dp.message_handler(Text("Магическая"), state=FSMLoop.attack_type)
async def person_info(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['attack_type'] = 'Магическая'
    await message.answer('Тип атаки установлен...', reply_markup=kb_in_dungeon)
    await FSMLoop.move_to_location.set()


@dp.message_handler(Text("Выпить зелье"), state=FSMLoop.move_to_location)
async def person_info(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        nickname = data['nickname']
    flag = False
    index = 1
    ls = dict()
    for d in select_potion(message.from_user.id, nickname):
        flag = True
        mes = f'{index}. <b>Товар:</b> {d["Name"]}, <b>тип товара:</b> {d["ItemType"]}\n' \
              f'<b>Плюшки:</b>\n<b>Дополнительное HP:</b> {d["HP"]},\n' \
              f'<b>Дополнительная Мана:</b> {d["Mana"]}\n' \
              f'<b>Физическая атака:</b> {d["Attack"]}\n' \
              f'<b>Магическая атака:</b> {d["Magic_Attack"]}\n' \
              f'<b>Броня от физических атак:</b> {d["Armour"]}\n' \
              f'<b>Броня от магических атак:</b> {d["Magic_Armour"]}\n'
        ls[index] = d["ItemID"]
        index += 1
        await message.answer(mes, parse_mode='HTML')

    if not flag:
        await message.answer('У вас нет зелий', reply_markup=kb_in_dungeon)
    else:
        await message.answer('Напишите номер зелья, которое хотите использовать', reply_markup=kb_cancel)
        async with state.proxy() as data:
            data['potions'] = ls
        await FSMLoop.potion.set()


@dp.message_handler(Text("Отмена"), state=FSMLoop.potion)
async def cancel(message: types.Message, state: FSMContext):
    await message.answer('Вы вышли из инвентаря для изучения зелий...', reply_markup=kb_in_dungeon)
    await FSMLoop.move_to_location.set()


@dp.message_handler(state=FSMLoop.potion)
async def cancel(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        nickname = data['nickname']
        try:
            potion = data['potions'][int(message.text)]
        except:
            await message.answer('Неверный формат данных. Убедитесь, что вы ввели допустимое число и повторите попытку',
                                 reply_markup=kb_cancel)
            return
    update_potions(message.from_user.id, nickname, potion)

    await message.answer('Зелье использовано...', reply_markup=kb_in_dungeon)
    await FSMLoop.move_to_location.set()


@dp.message_handler(Text("Атаковать моба"), state=FSMLoop.move_to_location)
async def person_info(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        mob = data['mob']
        nickname = data['nickname']
        attack_type = data['attack_type']
    person_ = select_dict_person(message.from_user.id, nickname)
    if attack_type == 'Магическая':
        person_attack = max(0, int(person_['Magic_Attack']) - int(mob['Magic_Armour']))
    else:
        person_attack = max(0, int(person_['Attack']) - int(mob['Armour']))

    mob_hp = int(mob['HP']) - person_attack
    if mob_hp <= 0:
        update_win(person_, mob['XP'])
        await message.answer(
            f'Вы победили, вам начислено {mob["XP"]} опыта и денег, теперь вы можете покинуть подземелье, чтобы восстановить здоровье',
            reply_markup=kb_after_win)
        return
    else:
        mob['HP'] = mob_hp

    await message.answer(f'Вы нанесли мобу {person_attack} урона', reply_markup=kb_in_dungeon)

    if mob['AttackType'] == 'Магическая':
        mob_attack = max(0, int(mob['Attack']) - int(person_['Magic_Armour']))
    else:
        mob_attack = max(0, int(mob['Attack']) - int(person_['Armour']))

    person_hp = int(person_['CurHP']) - mob_attack
    if person_hp <= 0:
        await state.finish()
        await message.answer('Вы проиграли!', reply_markup=kb_start)
        return
    else:
        person_['CurHP'] = person_hp

    await message.answer(f'Моб нанес вам {mob_attack} урона', reply_markup=kb_in_dungeon)

    update_person_by_local_in_fight(person_)


    async with state.proxy() as data:
        data['mob'] = mob
