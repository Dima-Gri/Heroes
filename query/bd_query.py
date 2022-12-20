from create_bot import *


def get_nicknames_by_userid(user_id) -> list:
    row = db.select([person]).where(person.columns.UserID == user_id)
    if not connection.execute(row).fetchall():
        return []
    return [item[1] for item in connection.execute(row).fetchall()]


def insert_default_person(user_id, nickname):
    person_values = [user_id, nickname, '100', '100', '100', '10', '5', '0', '10', '0', '1', '1']
    insertion = person.insert().values([
        dict(zip(person_fields, person_values))
    ])
    connection.execute(insertion)


def select_by_user_id_nickname(user_id, nickname):
    row = db.select([person]).where(
        (person.columns.UserID == user_id) & (person.columns.Nickname == nickname))
    return connection.execute(row).fetchone()


def select_location_by_location_id(location_id):
    row = db.select([locations]).where(locations.columns.LocationID == str(location_id))
    return connection.execute(row).fetchone()


def select_all_locations():
    row = db.select([locations])
    return connection.execute(row).fetchall()


def update_by_user_id_nickname(user_id, nickname, new_location):
    row = db.update(person).where((person.columns.UserID == user_id) & (person.columns.Nickname == nickname)).values(
        CurHP='100', LocationID=new_location)
    connection.execute(row)


def update_price_by_user_id_nickname_buy(user_id, nickname, price, item_id):
    row = db.select([person]).where(
        (person.columns.UserID == user_id) & (person.columns.Nickname == nickname))

    person_ = connection.execute(row).fetchone()
    row = db.update(person).where((person.columns.UserID == user_id) & (person.columns.Nickname == nickname)).values(
        Money=int(person_[4]) - price)
    connection.execute(row)

    insertion = inventory.insert().values([
        dict(zip(['UserID', 'Nickname', 'ItemID', 'quantity', 'flag'], [user_id, nickname, item_id, 1, 'NOT']))
    ])
    connection.execute(insertion)
    return int(person_[4]) - price


def update_price_by_user_id_nickname_sale(user_id, nickname, price, item_id):
    row = db.select([person]).where(
        (person.columns.UserID == user_id) & (person.columns.Nickname == nickname))

    row1 = db.select([inventory]).where(
        (inventory.columns.UserID == user_id) & (inventory.columns.Nickname == nickname) & (
                inventory.columns.ItemID == item_id))
    item = connection.execute(row1).fetchone()
    person_ = connection.execute(row).fetchone()

    if item[-1] == 'YES':
        person_values = [user_id, nickname, '100', '100', '100', '10', '5', '0', '10', '0', '1', '1']
        default_values = dict(zip(person_fields, person_values))
        row = db.update(person).where(
            (person.columns.UserID == user_id) & (person.columns.Nickname == nickname)).values(
            Money=int(person_[4]) + price, Attack=int(default_values['Attack']),
            Magic_Attack=int(default_values['Magic_Attack']),
            Armour=int(default_values['Armour']),
            Magic_Armour=int(default_values['Magic_Armour']))
    else:
        row = db.update(person).where(
            (person.columns.UserID == user_id) & (person.columns.Nickname == nickname)).values(
            Money=int(person_[4]) + price)

    connection.execute(row)

    deletion = db.delete(inventory).where(
        (inventory.columns.UserID == user_id) & (inventory.columns.Nickname == nickname) & (
                inventory.columns.ItemID == item_id))
    connection.execute(deletion)
    return int(person_[4]) + price


def select_by_location_id_from_market(user_id, nickname, location_id):
    row = db.select([person]).where((person.columns.UserID == user_id) & (person.columns.Nickname == nickname))
    person_ = connection.execute(row).fetchone()

    row = db.select([market]).where(market.columns.LocationID == location_id)
    ls = []
    for loc_id, item_id in connection.execute(row):
        row = db.select([items]).where(items.columns.ItemID == item_id)
        current_item = connection.execute(row).fetchone()
        dic = dict(zip(items_fields, current_item))
        if int(dic['Cost']) < int(person_['Money']):
            ls.append(dic)
    return ls


def select_from_inventory(user_id, nickname):
    row = db.select([inventory]).where((inventory.columns.UserID == user_id) & (inventory.columns.Nickname == nickname))
    ls = []
    for UserID, Nickname, ItemID, quantity, flag in connection.execute(row):
        row = db.select([items]).where(items.columns.ItemID == ItemID)
        current_item = connection.execute(row).fetchone()
        dic = dict(zip(items_fields, current_item))
        ls.append((dic, flag))
    return ls


def update_inventory_flag(user_id, nickname, item_id, new_flag):
    row = db.update(inventory).where(
        (inventory.columns.UserID == user_id) & (inventory.columns.Nickname == nickname) & (
                inventory.columns.ItemID == item_id)).values(
        flag=new_flag)
    connection.execute(row)

    row = db.select([items]).where(items.columns.ItemID == item_id)
    item = connection.execute(row).fetchone()
    dic = dict(zip(items_fields, item))
    person_values = [user_id, nickname, '100', '100', '100', '10', '5', '0', '10', '0', '1', '1']
    default_values = dict(zip(person_fields, person_values))
    row = db.update(person).where((person.columns.UserID == user_id) & (person.columns.Nickname == nickname)).values(
        Attack=int(default_values['Attack']) + int(dic['Attack']),
        Magic_Attack=int(dic['Magic_Attack']) + int(default_values['Magic_Attack']),
        Armour=int(dic['Armour']) + int(default_values['Armour']),
        Magic_Armour=int(dic['Magic_Armour']) + int(default_values['Magic_Armour'])
    )
    connection.execute(row)


def set_cloth(user_id, nickname, item_id):
    row = db.select([inventory]).where(
        (inventory.columns.UserID == user_id) & (inventory.columns.Nickname == nickname) & (
                inventory.columns.flag == 'YES'))
    if connection.execute(row).fetchone():
        put_on = connection.execute(row).fetchone()
        update_inventory_flag(user_id, nickname, put_on[2], 'NOT')
    update_inventory_flag(user_id, nickname, item_id, 'YES')


def select_all_mobs(user_id, nickname):
    row = db.select([person]).where((person.columns.UserID == user_id) & (person.columns.Nickname == nickname))
    person_ = connection.execute(row).fetchone()
    person_ = dict(zip(person_fields, person_))
    row = db.select([mobs]).where(mobs.columns.ReqLevel == person_['Level'])
    return connection.execute(row).fetchall()


def select_potion(user_id, nickname):
    row = db.select([inventory]).where((inventory.columns.UserID == user_id) & (inventory.columns.Nickname == nickname))
    ls = []
    for UserID, Nickname, ItemID, quantity, flag in connection.execute(row).fetchall():
        row = db.select([items]).where((items.columns.ItemID == ItemID) & (items.columns.ItemType == 'зелье'))
        current_item = connection.execute(row).fetchone()
        dic = dict(zip(items_fields, current_item))
        ls.append(dic)
    return ls


def update_potions(user_id, nickname, item_id):
    row = db.select([items]).where(items.columns.ItemID == item_id)
    item = connection.execute(row).fetchone()
    item = dict(zip(items_fields, item))

    row = db.select([person]).where((person.columns.UserID == user_id) & (person.columns.Nickname == nickname))
    person_ = connection.execute(row).fetchone()
    person_ = dict(zip(person_fields, person_))

    row = db.update(person).where((person.columns.UserID == user_id) & (person.columns.Nickname == nickname)).values(
        Attack=int(person_['Attack']) + int(item['Attack']),
        Magic_Attack=int(person_['Magic_Attack']) + int(item['Magic_Attack']),
        Armour=int(person_['Armour']) + int(item['Armour']),
        Magic_Armour=int(person_['Magic_Armour']) + int(item['Magic_Armour'])
    )
    connection.execute(row)

    deletion = db.delete(inventory).where(
        (inventory.columns.UserID == user_id) & (inventory.columns.Nickname == nickname) & (
                inventory.columns.ItemID == item_id))
    connection.execute(deletion)


def select_dict_person(user_id, nickname):
    row = db.select([person]).where((person.columns.UserID == user_id) & (person.columns.Nickname == nickname))
    person_ = connection.execute(row).fetchone()
    person_ = dict(zip(person_fields, person_))
    return person_


def update_person_by_local_in_fight(person_):
    row = db.update(person).where(
        (person.columns.UserID == person_['UserID']) & (person.columns.Nickname == person_['Nickname'])).values(
        CurHP=person_['CurHP'], Attack=person_['Attack'], Magic_Attack=person_['Magic_Attack'],
        Armour=person_['Armour'], Magic_Armour=person_['Magic_Armour']
    )
    connection.execute(row)


def update_win(person_, xp):
    update_person_by_local_in_fight(person_)
    person_xp = int(person_['CurHP']) + int(xp)
    person_level = int(person_['Level']) + person_xp // 100
    person_xp %= 100
    person_money = int(person_['Money']) + int(xp)

    row = db.update(person).where(
        (person.columns.UserID == person_['UserID']) & (person.columns.Nickname == person_['Nickname'])).values(
        CurHP=person_xp, Money=person_money, Level=person_level
    )
    connection.execute(row)
