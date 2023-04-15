import telebot
import psycopg2

from config import host, user, password, db_name
from telebot import types

try:
    connection = psycopg2.connect(
        host=host,
        user=user,
        password=password,
        database=db_name 
    )
    connection.autocommit = True


except Exception as _ex:
    print("[INFO] Error while working with PostgreSQL", _ex)


BOT_TOKEN = ("6080749671:AAEO_NOXWO6YQ_yHkt-YOQeertuNl1Kkq8Y")

bot = telebot.TeleBot(BOT_TOKEN, parse_mode=None)


@bot.message_handler(commands=['start'])
def send_welcome(message):
    if message.from_user.first_name and message.from_user.last_name:
        full_name = message.from_user.first_name + message.from_user.last_name
    elif message.from_user.first_name:
        full_name = message.from_user.first_name
    elif message.from_user.last_name:
        full_name = message.from_user.last_name
    else:
        full_name = ' '
    
    if connection:
        with connection.cursor() as cursor:
            cursor.execute(
                f"""SELECT * from users WHERE user_id = {message.from_user.id}"""
            )
            check = cursor.fetchone()

        if not check:
            with connection.cursor() as cursor:
                cursor.execute(
                    f"""INSERT INTO users(user_id, full_name, username) VALUES ({message.from_user.id}, '{full_name}', '{message.from_user.username}')"""
                )

    markup_inline = types.InlineKeyboardMarkup()
    item_ru = types.InlineKeyboardButton(text="Русский 🇷🇺", callback_data="ru")
    item_uz = types.InlineKeyboardButton(text="O'zbekcha 🇺🇿", callback_data="uz")
    markup_inline.add(item_ru, item_uz)
    bot.reply_to(message, "Добро пожаловать")
    bot.send_message(message.chat.id, "Выберите язык:", reply_markup=markup_inline)


@bot.callback_query_handler(func = lambda call: True)
def ansver(call):
    try:
        if connection:
            with connection.cursor() as cursor:
                cursor.execute(f"""SELECT * from users WHERE user_id = {call.from_user.id}""")
                from_user = cursor.fetchone()
                
        valyuta = from_user[4]
    except:
        valyuta = None  
    if from_user[11] == 'superadmin' or from_user[11] == 'admin':
        if call.data == 'ru':
            bot.send_message(call.message.chat.id, "Язык применен !")
        if call.data == 'uz':
            bot.send_message(call.message.chat.id, "Til qabul qilindi ! !")
    else:
        print(from_user[11])
        if call.data == 'uzs':
            if connection:
                with connection.cursor() as cursor:
                    cursor.execute(f"""UPDATE users SET currency = 'uzs' WHERE user_id = {call.from_user.id}""")
        elif call.data == 'rub':
            if connection:
                with connection.cursor() as cursor:
                    cursor.execute(f"""UPDATE users SET currency = 'rub' WHERE user_id = {call.from_user.id}""")


        if call.data == 'ru':
            lan = 'ru'
            markup_inline = types.InlineKeyboardMarkup()
            item_1 = types.InlineKeyboardButton(text="Pubg Mobile", callback_data="valyuta")
            markup_inline.add(item_1)
            bot.send_message(call.message.chat.id, "Выберите игру:", reply_markup=markup_inline)
        elif call.data == 'uz':
            lan = 'uz'
            markup_inline = types.InlineKeyboardMarkup()
            item_1 = types.InlineKeyboardButton(text="Pubg Mobile", callback_data="valyuta")
            markup_inline.add(item_1)
            bot.send_message(call.message.chat.id, "O'yinni tanlang:", reply_markup=markup_inline)
        elif call.data == 'valyuta':
            markup_inline = types.InlineKeyboardMarkup()
            item_1 = types.InlineKeyboardButton(text="UZS", callback_data="uzs")
            item_2 = types.InlineKeyboardButton(text="RUB", callback_data="rub")
            markup_inline.add(item_1, item_2)
            bot.send_message(call.message.chat.id, "Выберите валюту:", reply_markup=markup_inline)
        elif call.data == 'page_1' or call.data == 'uzs' or call.data == 'rub':
            if valyuta == "uzs":
                tsena = "💎66 UC - 11.000 UZS 💵\n💎132 UC - 21.000 UZS 💵\n💎198 UC - 30.000 UZS 💵\n💎355 UC - 51.000 UZS 💵\n💎420 UC - 62.000 UZS 💵"
            elif valyuta == 'rub':
                tsena = "💎66 UC - 78₽💵\n💎132 UC - 150₽💵\n💎198 UC - 214₽💵\n💎355 UC - 364₽💵\n💎420 UC - 445₽💵"
            photo = open('photo.jpg', 'rb')
            markup_inline = types.InlineKeyboardMarkup()
            item_1 = types.InlineKeyboardButton(text="💎66 UC", callback_data="66")
            item_2 = types.InlineKeyboardButton(text="💎132 UC", callback_data="132")
            item_3 = types.InlineKeyboardButton(text="💎198 UC", callback_data="198")
            item_4 = types.InlineKeyboardButton(text="💎355 UC", callback_data="355")
            item_5 = types.InlineKeyboardButton(text="💎420 UC", callback_data="420")
            item_6 = types.InlineKeyboardButton(text="<< Orqaga", callback_data="valyuta")
            item_7 = types.InlineKeyboardButton(text="Keyingi sahifa >>", callback_data="page_2")
            markup_inline.add(item_1, item_2, item_3, item_4, item_5, item_6, item_7)
            bot.send_photo(call.message.chat.id, photo, "💸PUBG MOBILE UC NARXLARI💸\n\n"+tsena, reply_markup=markup_inline)
        elif call.data == 'page_2':
            if valyuta == "uzs":
                tsena = "💎535 UC - 81.000 UZS 💵\n💎720 UC - 105.000 UZS 💵\n💎810 UC - 122.000 UZS 💵\n💎900 UC - 135.000 UZS 💵\n💎1075 UC - 156.000 UZS 💵"
            elif valyuta == "rub":
                tsena = "💎535 UC - 580₽💵\n💎720 UC - 750₽💵\n💎810 UC - 875₽💵\n💎900 UC - 965₽💵\n💎1075 UC - 1120₽💵"
            photo = open('photo.jpg', 'rb')
            markup_inline = types.InlineKeyboardMarkup()
            item_1 = types.InlineKeyboardButton(text="💎535 UC", callback_data="535")
            item_2 = types.InlineKeyboardButton(text="💎720 UC", callback_data="720")
            item_3 = types.InlineKeyboardButton(text="💎810 UC", callback_data="810")
            item_4 = types.InlineKeyboardButton(text="💎900 UC", callback_data="900")
            item_5 = types.InlineKeyboardButton(text="💎1075 UC", callback_data="1075")
            item_6 = types.InlineKeyboardButton(text="<< Orqaga", callback_data="page_1")
            item_7 = types.InlineKeyboardButton(text="Keyingi sahifa >>", callback_data="page_3")
            markup_inline.add(item_1, item_2, item_3, item_4, item_5, item_6, item_7)
            bot.send_photo(call.message.chat.id, photo, "💸PUBG MOBILE UC NARXLARI💸\n\n"+tsena, reply_markup=markup_inline)
        elif call.data == 'page_3':
            if valyuta == "uzs":
                tsena = "💎1440 UC - 210.000 UZS 💵\n💎1950 UC - 259.000 UZS 💵\n💎2305 UC - 310.000 UZS 💵\n💎3025 UC - 400.000 UZS 💵\n💎4000 UC - 490.000 UZS 💵"
            elif valyuta == "rub":
                tsena = "💎1440 UC - 1500₽💵\n💎1950 UC - 1850₽💵\n💎2305 UC - 2222₽💵\n💎3025 UC - 2860₽💵\n💎4000 UC - 3560₽💵"
            photo = open('photo.jpg', 'rb')
            markup_inline = types.InlineKeyboardMarkup()
            item_1 = types.InlineKeyboardButton(text="💎1440 UC", callback_data="1440")
            item_2 = types.InlineKeyboardButton(text="💎1950 UC", callback_data="1950")
            item_3 = types.InlineKeyboardButton(text="💎2305 UC", callback_data="2305")
            item_4 = types.InlineKeyboardButton(text="💎3025 UC", callback_data="3025")
            item_5 = types.InlineKeyboardButton(text="💎4000 UC", callback_data="4000")
            item_6 = types.InlineKeyboardButton(text="<< Orqaga", callback_data="page_2")
            item_7 = types.InlineKeyboardButton(text="Keyingi sahifa >>", callback_data="page_4")
            markup_inline.add(item_1, item_2, item_3, item_4, item_5, item_6, item_7)
            bot.send_photo(call.message.chat.id, photo, "💸PUBG MOBILE UC NARXLARI💸\n\n"+tsena, reply_markup=markup_inline)
        elif call.data == 'page_4':
            if valyuta == "uzs":
                tsena = "💎5075 UC - 625.000 UZS 💵\n💎8400 UC - 969.000 UZS 💵\n💎10350 UC - 1.228.000 UZS 💵\n💎16800 UC - 1.938.000 UZS 💵\n💎25200 UC - 2.790.000 UZS 💵"
            elif valyuta == "rub":
                tsena = "💎5075 UC - 4500₽💵\n💎8400 UC - 6925₽💵\n💎10350 UC - 8787₽💵\n💎16800 UC - 13850₽💵\n💎25200 UC - 19375₽💵"
            photo = open('photo.jpg', 'rb')
            markup_inline = types.InlineKeyboardMarkup()
            item_1 = types.InlineKeyboardButton(text="💎5075 UC", callback_data="5075")
            item_2 = types.InlineKeyboardButton(text="💎8400 UC", callback_data="8400")
            item_3 = types.InlineKeyboardButton(text="💎10350 UC", callback_data="10350")
            item_4 = types.InlineKeyboardButton(text="💎16800 UC", callback_data="16800")
            item_5 = types.InlineKeyboardButton(text="💎25200 UC", callback_data="25200")
            item_6 = types.InlineKeyboardButton(text="<< Orqaga", callback_data="page_3")
            markup_inline.add(item_1, item_2, item_3, item_4, item_5, item_6)
            bot.send_photo(call.message.chat.id, photo, "💸PUBG MOBILE UC NARXLARI💸\n\n"+tsena, reply_markup=markup_inline)
        elif call.data == "uzcard":
            photo = open('uzcard_photo.jpg', 'rb')
            markup_inline = types.InlineKeyboardMarkup()
            item_1 = types.InlineKeyboardButton(text="Оплатил ✅", callback_data="opcheck")
            markup_inline.add(item_1)
            bot.send_photo(call.message.chat.id, photo, f"{from_user[6]}\n\n8600 3141 6785 0751\nRAJABOVA UMIDA\nUlangan nomer +998933127053\n\n8600 0423 0682 2007\nRAJABOV MARUF\nUlangan nomer +998933127053", reply_markup=markup_inline)
        elif call.data == "humo":
            photo = open('humo_photo.jpg', 'rb')
            markup_inline = types.InlineKeyboardMarkup()
            item_1 = types.InlineKeyboardButton(text="Оплатил ✅", callback_data="opcheck")
            markup_inline.add(item_1)
            bot.send_photo(call.message.chat.id, photo, f"{from_user[6]}\n\n9860 0801 9358 6643\nRAJABOVA UMIDA\nUlangan nomer +998933127053\n\n4073 4200 6731 7366\nRAJABOVA UMIDA\nUlangan nomer +998933127053", reply_markup=markup_inline)
        elif call.data == "opcheck":
            if from_user[7]:
                markup_reply = types.ReplyKeyboardMarkup(resize_keyboard = True)
                button = types.KeyboardButton(f"{from_user[7]}")
                markup_reply.add(button)
                bot.send_message(call.message.chat.id, "To'lov qilgan karta raqamini yuboring :\n\nMasalan: card 0000 0000 0000 0000\n\n(Boshida \"card\" suzi bo'lishi shart)", reply_markup=markup_reply)
            else:
                bot.send_message(call.message.chat.id, "To'lov qilgan karta raqamini yuboring :\n\nMasalan: card 0000 0000 0000 0000\n\n(Boshida \"card\" suzi bo'lishi shart)", reply_markup=markup_reply)
        elif call.data == '66':
            uc = 66
            uzs = "11.000 UZS"
            rub = "78 RUB"
            tab_uc = True
        elif call.data == '132':
            uc = 132
            uzs = "21.000 UZS"
            rub = "150 RUB"
            tab_uc = True
        elif call.data == '198':
            uc = 198
            uzs = "30.000 UZS"
            rub = "364 RUB"
            tab_uc = True
        elif call.data == '355':
            uc = 355
            uzs = "51.000 UZS"
            rub = "364 RUB"
            tab_uc = True
        elif call.data == '420':
            uc = 420
            uzs = "62.000 UZS"
            rub = "445 RUB"
            tab_uc = True
        elif call.data == '535':
            uc = 535
            uzs = "81.000 UZS"
            rub = "580 RUB"
            tab_uc = True
        elif call.data == '720':
            uc = 720
            uzs = "105.000 UZS"
            rub = "750 RUB"
            tab_uc = True
        elif call.data == '810':
            uc = 810
            uzs = "122.000 UZS"
            rub = "875 RUB"
            tab_uc = True
        elif call.data == '900':
            uc = 900
            uzs = "135.000 UZS"
            rub = "965 RUB"
            tab_uc = True
        elif call.data == '1075':
            uc = 1075
            uzs = "156.000 UZS"
            rub = "1120 RUB"
            tab_uc = True
        elif call.data == '1440':
            uc = 1440
            uzs = "210.000 UZS"
            rub = "1500 RUB"
            tab_uc = True
        elif call.data == '1950':
            uc = 1950
            uzs = "259.000 UZS"
            rub = "1850 RUB"
            tab_uc = True
        elif call.data == '2305':
            uc = 2305
            uzs = "310.000 UZS"
            rub = "2222 RUB"
            tab_uc = True
        elif call.data == '3025':
            uc = 3025
            uzs = "400.000 UZS"
            rub = "2860 RUB"
            tab_uc = True
        elif call.data == '4000':
            uc = 4000
            uzs = "490.000 UZS"
            rub = "3560 RUB"
            tab_uc = True
        elif call.data == '5075':
            uc = 5075
            uzs = "625.000 UZS"
            rub = "4500 RUB"
            tab_uc = True
        elif call.data == '8400':
            uc = 8400
            uzs = "969.000 UZS"
            rub = "6925 RUB"
            tab_uc = True
        elif call.data == '10350':
            uc = 10350
            uzs = "1.228.000 UZS"
            rub = "8787 RUB"
            tab_uc = True
        elif call.data == '16800':
            uc = 16800
            uzs = "1.938.000 UZS"
            rub = "13850 RUB"
            tab_uc = True
        elif call.data == '25200':
            uc = 25200
            uzs = "2.790.000 UZS"
            rub = "19375 RUB"
            tab_uc = True
        
        if tab_uc:
            if connection:
                with connection.cursor() as cursor:
                    cursor.execute(f"""UPDATE users SET uc = {uc} WHERE user_id = {call.from_user.id}""")
                if valyuta == "uzs":
                    with connection.cursor() as cursor:
                        cursor.execute(f"""UPDATE users SET price = '{uzs}' WHERE user_id = {call.from_user.id}""")
                elif valyuta == "rub":
                    with connection.cursor() as cursor:
                        cursor.execute(f"""UPDATE users SET price = '{rub}' WHERE user_id = {call.from_user.id}""")
            markup_inline = types.InlineKeyboardMarkup()
            item_1 = types.InlineKeyboardButton(text="Uzcard", callback_data="uzcard")
            item_2 = types.InlineKeyboardButton(text="Humo", callback_data="humo")
            markup_inline.add(item_1, item_2)
            bot.send_message(call.message.chat.id, "Выберите способ оплаты:", reply_markup=markup_inline)

@bot.message_handler(content_types=['text', 'photo'])
def get_text(message):
    if connection:
        with connection.cursor() as cursor:
            cursor.execute(f"""SELECT * from users WHERE user_id = {message.from_user.id}""")
            from_user = cursor.fetchone()
    if from_user[11] == 'superadmin' or from_user[11] == 'admin':
        pass
    else:
        if message.text:
            if message.text.lower().startswith("card"):
                if from_user[6]:
                    if connection:
                        with connection.cursor() as cursor:
                            cursor.execute(f"""UPDATE users SET card = '{message.text.upper()}' WHERE user_id = {message.from_user.id}""")
                    bot.reply_to(message, "Karta raqami qabul qilindi ✅")
                    bot.send_message(message.chat.id, "To'lov chekini skrinshotini yuboring:\n\n(Skrinshot file formatida bo'lmasligi lozim)", reply_markup=types.ReplyKeyboardRemove())
                    # bot.send_sticker(call.message.chat.id, "CAACAgIAAxkBAAEIjgxkNrfCbktyzaZpKSm6wAeBsV-1PgACVyUAAl9weEuXcuNPf9dm4i8E")
            elif message.text.lower().startswith("id"):
                if from_user[8]:
                    if connection:
                        with connection.cursor() as cursor:
                            cursor.execute(f"""UPDATE users SET pubg_id = '{message.text.upper()}' WHERE user_id = {message.from_user.id}""")
                    if from_user[10]:
                        markup_reply = types.ReplyKeyboardMarkup(resize_keyboard = True)
                        button = types.KeyboardButton(f"{from_user[10]}")
                        markup_reply.add(button)
                        bot.reply_to(message, "ID qabul qilindi ✅")
                        bot.send_message(message.chat.id, "Endi sizning PUBG dagi nickname gizni yuboring :\n\nMasalan: nickname alyosha123\n\n(Boshida \"nickname\" suzi bo'lishi shart)", reply_markup=markup_reply)
                    else:
                        bot.reply_to(message, "ID qabul qilindi ✅")
                        bot.send_message(message.chat.id, "Endi sizning PUBG dagi nickname gizni yuboring :\n\nMasalan: nickname alyosha123\n\n(Boshida \"nickname\" suzi bo'lishi shart)")
            elif message.text.lower().startswith("nickname"):
                if from_user[9]:
                    if connection:
                        with connection.cursor() as cursor:
                            cursor.execute(f"""UPDATE users SET nickname = '{message.text}' WHERE user_id = {message.from_user.id}""")
                        with connection.cursor() as cursor:
                            cursor.execute(f"""SELECT user_id from users WHERE status = 'superadmin' or status = 'admin'""")
                            admins = cursor.fetchall()
                    bot.reply_to(message, "Nickname qabul qilindi ✅")
                    bot.send_message(message.chat.id, "Zakaz qabul qilindi UC tushishini kuting", reply_markup=types.ReplyKeyboardRemove())
                    photo_file = bot.get_file(from_user[8])
                    photo_bytes = bot.download_file(photo_file.file_path)
                    for admin in admins:
                        bot.send_photo(admin, photo_bytes, f"{from_user[7]}\n{from_user[9]}\nUC: {from_user[5]}\nPRICE: {from_user[6]}\n{from_user[10]}\n@{from_user[3]}")
        elif message.photo:
            if from_user[7]:
                photo_id = message.photo[-1].file_id
                if connection:
                    with connection.cursor() as cursor:
                        cursor.execute(f"""UPDATE users SET photo_id = '{photo_id}' WHERE user_id = {message.from_user.id}""")
                if from_user[9]:
                    markup_reply = types.ReplyKeyboardMarkup(resize_keyboard = True)
                    button = types.KeyboardButton(f"{from_user[9]}")
                    markup_reply.add(button)
                    bot.reply_to(message, "Chek qabul qilindi ✅")
                    bot.send_message(message.chat.id, "Sizning PUBG dagi ID gizni yuboring :\n\nMasalan: id 123456789\n\n(Boshida \"id\" suzi bo'lishi shart)", reply_markup=markup_reply)
                else:
                    bot.reply_to(message, "Chek qabul qilindi ✅")
                    bot.send_message(message.chat.id, "Sizning PUBG dagi ID gizni yuboring :\n\nMasalan: id 123456789\n\n(Boshida \"id\" suzi bo'lishi shart)")

                
        

bot.infinity_polling()