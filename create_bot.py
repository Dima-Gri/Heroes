import asyncio
import sqlalchemy as db

from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.utils import executor

storage = MemoryStorage()
bot = Bot(token='5862925288:AAEKXz5_Uh9Vm3WnksKphoObqIwSOuPwVhc')
dp = Dispatcher(bot, storage=storage)

engine = db.create_engine('sqlite:///data_base.db')
connection = engine.connect()
metadata = db.MetaData()

person_fields = ['UserID', 'Nickname', 'HP', 'CurHP', 'Money', 'Attack', 'Magic_Attack', 'XP', 'Armour',
                 'Magic_Armour', 'LocationID', 'Level']
locations_fields = ['LocationID', 'XCoord', 'YCoord', 'LocationType', 'Name']

items_fields = ['ItemID', 'Cost', 'CostToSale', 'ItemType', 'HP',
                'Mana', 'Attack', 'Magic_Attack', 'Armour', 'Magic_Armour', 'ReqLevel', 'Name']

person = db.Table(
    'person',
    metadata,
    db.Column('UserID', db.Text),
    db.Column('Nickname', db.Text),
    db.Column('HP', db.Text),
    db.Column('CurHP', db.Text),
    db.Column('Money', db.Text),
    db.Column('Attack', db.Text),
    db.Column('Magic_Attack', db.Text),
    db.Column('XP', db.Text),
    db.Column('Armour', db.Text),
    db.Column('Magic_Armour', db.Text),
    db.Column('LocationID', db.Text),
    db.Column('Level', db.Text),
)

mobs = db.Table(
    'mobs',
    metadata,
    db.Column('MobID', db.Text),
    db.Column('HP', db.Text),
    db.Column('XP', db.Text),
    db.Column('ReqLevel', db.Text),
    db.Column('AttackType', db.Text),
    db.Column('Attack', db.Text),
    db.Column('Armour', db.Text),
    db.Column('Magic_Armour', db.Text),
    db.Column('Name', db.Text)
)

locations = db.Table(
    'subjects',
    metadata,
    db.Column('LocationID', db.Text),
    db.Column('XCoord', db.Text),
    db.Column('YCoord', db.Text),
    db.Column('LocationType', db.Text),
    db.Column('Name', db.Text)
)

items = db.Table(
    'items',
    metadata,
    db.Column('ItemID', db.Text),
    db.Column('Cost', db.Text),
    db.Column('CostToSale', db.Text),
    db.Column('ItemType', db.Text),
    db.Column('HP', db.Text),
    db.Column('Mana', db.Text),
    db.Column('Attack', db.Text),
    db.Column('Magic_Attack', db.Text),
    db.Column('Armour', db.Text),
    db.Column('Magic_Armour', db.Text),
    db.Column('ReqLevel', db.Text),
    db.Column('Name', db.Text),
)

inventory = db.Table(
    'inventory',
    metadata,
    db.Column('UserID', db.Text),
    db.Column('Nickname', db.Text),
    db.Column('ItemID', db.Text),
    db.Column('quantity', db.Text),
    db.Column('flag', db.Text)
)

market = db.Table(
    'market',
    metadata,
    db.Column('LocationID', db.Text),
    db.Column('ItemID', db.Text),
)

metadata.create_all(engine)

insertion_query = locations.insert().values([
    {"LocationID": "1", "XCoord": "0", "YCoord": "0", "LocationType": "??????????", "Name": "??????????????????????"},
    {"LocationID": "2", "XCoord": "10", "YCoord": "5", "LocationType": "????????????????????", "Name": "?????????????????? ??????????"},
    {"LocationID": "3", "XCoord": "-3", "YCoord": "7", "LocationType": "??????????", "Name": "??????????????"},
    {"LocationID": "4", "XCoord": "2", "YCoord": "9", "LocationType": "????????????????????", "Name": "????????????"},
    {"LocationID": "5", "XCoord": "2", "YCoord": "-3", "LocationType": "??????????", "Name": "???????????????????????? ??????????????????"},

])

insertion_query1 = items.insert().values([
    {'ItemID': '1', 'Cost': '25', 'CostToSale': '20', 'ItemType': '??????????', 'HP': '0', 'Mana': '0', 'Attack': '0',
     'Magic_Attack': '0', 'Armour': '10', 'Magic_Armour': '0', 'ReqLevel': '1', 'Name': '?????????????? ???????????? ????????????'},
    {'ItemID': '2', 'Cost': '30', 'CostToSale': '20', 'ItemType': '????????????', 'HP': '0', 'Mana': '0', 'Attack': '10',
     'Magic_Attack': '0', 'Armour': '10', 'Magic_Armour': '0', 'ReqLevel': '1', 'Name': '?????????????? ????????????'},
    {'ItemID': '3', 'Cost': '15', 'CostToSale': '10', 'ItemType': '????????', 'HP': '0', 'Mana': '0', 'Attack': '0',
     'Magic_Attack': '0', 'Armour': '5', 'Magic_Armour': '0', 'ReqLevel': '1', 'Name': '?????????????? ???????????? ????????????'},
    {'ItemID': '4', 'Cost': '15', 'CostToSale': '10', 'ItemType': '????????????', 'HP': '0', 'Mana': '0', 'Attack': '0',
     'Magic_Attack': '0', 'Armour': '5', 'Magic_Armour': '0', 'ReqLevel': '1', 'Name': '?????????????? ???????????? ??????'},
    {'ItemID': '5', 'Cost': '15', 'CostToSale': '10', 'ItemType': '????????????', 'HP': '0', 'Mana': '0', 'Attack': '0',
     'Magic_Attack': '0', 'Armour': '5', 'Magic_Armour': '0', 'ReqLevel': '1', 'Name': '????????????????????'},
    {'ItemID': '6', 'Cost': '35', 'CostToSale': '20', 'ItemType': '??????????', 'HP': '10', 'Mana': '10', 'Attack': '10',
     'Magic_Attack': '10', 'Armour': '0', 'Magic_Armour': '0', 'ReqLevel': '2', 'Name': '?????????? ?????? ??????????'},
    {'ItemID': '7', 'Cost': '55', 'CostToSale': '20', 'ItemType': '??????????', 'HP': '15', 'Mana': '15', 'Attack': '0',
     'Magic_Attack': '0', 'Armour': '10', 'Magic_Armour': '10', 'ReqLevel': '2', 'Name': '?????????? ?????? ????????????'},
    {'ItemID': '8', 'Cost': '30', 'CostToSale': '20', 'ItemType': '??????????', 'HP': '0', 'Mana': '0', 'Attack': '0',
     'Magic_Attack': '0', 'Armour': '15', 'Magic_Armour': '0', 'ReqLevel': '1', 'Name': '?????????????????? ???????????? ????????'}
])

insertion_query2 = market.insert().values([
    {"LocationID": "1", "ItemID": "1"},
    {"LocationID": "1", "ItemID": "2"},
    {"LocationID": "1", "ItemID": "3"},

    {"LocationID": "2", "ItemID": "1"},
    {"LocationID": "2", "ItemID": "8"},
    {"LocationID": "2", "ItemID": "3"},
    {"LocationID": "2", "ItemID": "6"},

    {"LocationID": "3", "ItemID": "4"},
    {"LocationID": "3", "ItemID": "6"},
    {"LocationID": "3", "ItemID": "7"},
    {"LocationID": "3", "ItemID": "8"},

    {"LocationID": "4", "ItemID": "1"},
    {"LocationID": "4", "ItemID": "2"},
    {"LocationID": "4", "ItemID": "7"},

    {"LocationID": "5", "ItemID": "6"},
    {"LocationID": "5", "ItemID": "7"},
])

mobs_fields = ['MobID', 'HP', 'XP', 'ReqLevel', 'AttackType', 'Attack', 'Armour', 'Magic_Armour', 'Name']

insertion_query3 = mobs.insert().values([
    {'MobID': '1', 'HP': '70', 'XP': '20', 'ReqLevel': '1', 'AttackType': '????????????????????', 'Attack': '10', 'Armour': '5',
     'Magic_Armour': '0', 'Name': '??????????????????'},
    {'MobID': '2', 'HP': '70', 'XP': '20', 'ReqLevel': '1', 'AttackType': '????????????????????', 'Attack': '5', 'Armour': '5',
     'Magic_Armour': '0', 'Name': '????????????'},
    {'MobID': '3', 'HP': '80', 'XP': '30', 'ReqLevel': '1', 'AttackType': '????????????????????', 'Attack': '5', 'Armour': '10',
     'Magic_Armour': '0', 'Name': '??????'},
    {'MobID': '4', 'HP': '50', 'XP': '10', 'ReqLevel': '1', 'AttackType': '????????????????????', 'Attack': '15', 'Armour': '5',
     'Magic_Armour': '5', 'Name': '????????????'},
    {'MobID': '5', 'HP': '100', 'XP': '10', 'ReqLevel': '2', 'AttackType': '????????????????????', 'Attack': '30', 'Armour': '10',
     'Magic_Armour': '20', 'Name': '????????'}

])
connection.execute(insertion_query)
connection.execute(insertion_query1)
connection.execute(insertion_query2)
connection.execute(insertion_query3)

