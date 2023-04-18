import telebot
import pymysql

from config import host, user, password, db_name
from telebot import types

try:
    connection = pymysql.connect(
        host=host,
        port=3306,
        user=user,
        password=password,
        database=db_name,
        cursorclass=pymysql.cursors.DictCursor
    )

except Exception as ex:
    print("connection refursed ...")
    print(ex)

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
                f"""SELECT * from `users` WHERE user_id = {message.from_user.id}"""
            )
            check = cursor.fetchone()

        if not check:
            with connection.cursor() as cursor:
                cursor.execute(
                    f"""INSERT INTO `users`(user_id, full_name, username) VALUES ({message.from_user.id}, '{full_name}', '{message.from_user.username}')"""
                )
                connection.commit()
        else:
            with connection.cursor() as cursor:
                cursor.execute(f"""DELETE FROM `operations` WHERE status IS NULL and user_id = {check['id']};""")
                connection.commit()
    bot.reply_to(message, "Добро пожаловать")
    if check:
        if check['language'] == 'ru':
            markup_inline = types.InlineKeyboardMarkup()
            item_1 = types.InlineKeyboardButton(text="Pubg Mobile", callback_data="menu")
            markup_inline.add(item_1)
            bot.send_message(message.chat.id, "Выберите игру:", reply_markup=markup_inline)
        elif check['language'] == 'uz':
            markup_inline = types.InlineKeyboardMarkup()
            item_1 = types.InlineKeyboardButton(text="Pubg Mobile", callback_data="menu")
            markup_inline.add(item_1)
            bot.send_message(message.chat.id, "O'yinni tanlang:", reply_markup=markup_inline)
        elif check['status'] == "admin" or check['status'] == "superadmin":
            pass
        else:
            markup_inline = types.InlineKeyboardMarkup()
            item_ru = types.InlineKeyboardButton(text="Русский 🇷🇺", callback_data="ru")
            item_uz = types.InlineKeyboardButton(text="O'zbekcha 🇺🇿", callback_data="uz")
            markup_inline.add(item_ru, item_uz)
            bot.send_message(message.chat.id, "Выберите язык:", reply_markup=markup_inline)
    else:
        markup_inline = types.InlineKeyboardMarkup()
        item_ru = types.InlineKeyboardButton(text="Русский 🇷🇺", callback_data="ru")
        item_uz = types.InlineKeyboardButton(text="O'zbekcha 🇺🇿", callback_data="uz")
        markup_inline.add(item_ru, item_uz)
        bot.send_message(message.chat.id, "Выберите язык:", reply_markup=markup_inline)


@bot.callback_query_handler(func = lambda call: True)
def ansver(call):
    try:
        if connection:
            with connection.cursor() as cursor:
                cursor.execute(f"""SELECT * from `users` WHERE user_id = {call.from_user.id}""")
                from_user = cursor.fetchone()
                cursor.execute(f"""SELECT * from `operations` WHERE user_id = {from_user['id']} and status is not null""")
                operations = cursor.fetchall()
                operation_num = len(operations)
                cursor.execute(f"""SELECT * from `operations` WHERE user_id = {from_user['id']} and operation_id = {operation_num+1}""")
                operation = cursor.fetchone()
                cursor.execute(f"""SELECT * from `operations` WHERE user_id = {from_user['id']} and operation_id = {operation_num}""")
                previous_operation = cursor.fetchone()
            valyuta = operation['currency']
    except:
        valyuta = None
    if from_user['status'] == "active":
        menu = types.ReplyKeyboardMarkup(resize_keyboard = True)
        if call.data == "uz":
            menu_uc = types.KeyboardButton("UC sotib olish")
            menu_story = types.KeyboardButton("Buyurtmalar tarixi")
            menu_language = types.KeyboardButton("Tilni o'zgartirish")
        elif call.data == "ru":
            menu_uc = types.KeyboardButton("Купить UC")
            menu_story = types.KeyboardButton("История операций")
            menu_language = types.KeyboardButton("Язык")
        elif from_user['language'] == "uz":
            menu_uc = types.KeyboardButton("UC sotib olish")
            menu_story = types.KeyboardButton("Buyurtmalar tarixi")
            menu_language = types.KeyboardButton("Tilni o'zgartirish")
        elif from_user['language'] == "ru":
            menu_uc = types.KeyboardButton("Купить UC")
            menu_story = types.KeyboardButton("История операций")
            menu_language = types.KeyboardButton("Язык")
        menu.add(menu_uc).row(menu_story, menu_language)
    if from_user['status'] == 'superadmin' or from_user['status'] == 'admin':
        if call.data == 'ru':
            bot.send_message(call.message.chat.id, "Язык применен !", reply_markup=types.ReplyKeyboardRemove())
        elif call.data == 'uz':
            bot.send_message(call.message.chat.id, "Til qabul qilindi !", reply_markup=types.ReplyKeyboardRemove())
        elif call.data.startswith("success_"):
            opr_id = call.data
            operation_id = opr_id[8:]
            if connection:
                with connection.cursor() as cursor:
                    cursor.execute(f"""SELECT * from `operations` WHERE id = {operation_id}""")
                    uc_operation = cursor.fetchone()
                if uc_operation['status'] == "progress":
                    with connection.cursor() as cursor:
                        cursor.execute(f"""SELECT * from `users` WHERE id = {uc_operation['user_id']}""")
                        uc_user = cursor.fetchone()
                    with connection.cursor() as cursor:
                        cursor.execute(f"""UPDATE `operations` SET status = 'delivered' WHERE id = {operation_id}""")
                        connection.commit()
                    bot.send_sticker(uc_user["user_id"], "CAACAgIAAxkBAAEInHRkPFODAAHCjXaANQb7WXbZGLy7TCoAAlklAALD8YBLj5S-b5wyYbMvBA")
                    if uc_user['language'] == "uz":
                        bot.send_message(uc_user["user_id"], f"Buyurtma #{uc_operation['operation_id']}\n{uc_operation['uc']} UC\nNICK:{uc_operation['nickname']}\n{uc_operation['pubg_id']}\nTushdi ✅")
                    elif uc_user['language'] == "ru":
                        bot.send_message(uc_user["user_id"], f"Заказ #{uc_operation['operation_id']}\n{uc_operation['uc']} UC\nNICK:{uc_operation['nickname']}\n{uc_operation['pubg_id']}\nПоступили ✅")
                    bot.send_message(call.message.chat.id, f"Операция № \"{operation_id}\" подтверждена")
                elif uc_operation['status'] == "delivered":
                    bot.send_message(call.message.chat.id, "Эта операция уже подтвержена")
                else:
                    bot.send_message(call.message.chat.id, "Эта операция уже отклонена")

        elif call.data.startswith("reject_"):
            opr_id = call.data
            operation_id = opr_id[7:]
            if connection:
                with connection.cursor() as cursor:
                    cursor.execute(f"""SELECT * from `operations` WHERE id = {operation_id}""")
                    uc_operation = cursor.fetchone()
                if uc_operation['status'] == "progress":
                    with connection.cursor() as cursor:
                        cursor.execute(f"""SELECT * from `users` WHERE id = {uc_operation['user_id']}""")
                        uc_user = cursor.fetchone()
                    with connection.cursor() as cursor:
                        cursor.execute(f"""UPDATE `operations` SET status = 'rejected' WHERE id = {operation_id}""")
                        connection.commit()
                    bot.send_message(uc_user["user_id"], f"Buyurtma #{uc_operation['operation_id']}\nFormasi xato to'ldirilgan iltimos tekshirip qayta urinib ko'ring !")
                    bot.send_message(call.message.chat.id, f"Операция № \"{operation_id}\" отклонена")
                elif uc_operation['status'] == "delivered":
                    bot.send_message(call.message.chat.id, "Эта операция уже подтвержена")
                else:
                    bot.send_message(call.message.chat.id, "Эта операция уже отклонена")
    else:
        if call.data == "menu":
            bot.send_message(call.message.chat.id, "Меню",reply_markup=menu)
        elif call.data == 'uzs':
            if connection:
                with connection.cursor() as cursor:
                    cursor.execute(f"""DELETE FROM `operations` WHERE status IS NULL and user_id = {from_user['id']};""")
                    connection.commit()
                with connection.cursor() as cursor:
                    cursor.execute(f"""INSERT INTO `operations` (user_id, operation_id, currency) VALUES ({from_user['id']},{operation_num+1}, 'uzs');""")
                    connection.commit()
        elif call.data == 'rub':
            if connection:
                with connection.cursor() as cursor:
                    cursor.execute(f"""DELETE FROM `operations` WHERE status IS NULL and user_id = {from_user['id']};""")
                    connection.commit()
                with connection.cursor() as cursor:
                    cursor.execute(f"""INSERT INTO `operations` (user_id, operation_id, currency) VALUES ({from_user['id']},{operation_num+1}, 'rub');""")
                    connection.commit()

        tab_uc = False
        if call.data == 'ru':
            if connection:
                with connection.cursor() as cursor:
                    cursor.execute(f"""UPDATE `users` SET language = 'ru' WHERE user_id = {call.from_user.id}""")
                    connection.commit()
            if from_user['language']:
                bot.send_message(call.message.chat.id, "Язык успешно изменен на русский", reply_markup=menu)
            else:
                markup_inline = types.InlineKeyboardMarkup()
                item_1 = types.InlineKeyboardButton(text="Pubg Mobile", callback_data="menu")
                markup_inline.add(item_1)
                bot.send_message(call.message.chat.id, "Выберите игру:", reply_markup=markup_inline)
        elif call.data == 'uz':
            if connection:
                with connection.cursor() as cursor:
                    cursor.execute(f"""UPDATE `users` SET language = 'uz' WHERE user_id = {call.from_user.id}""")
                    connection.commit()
            if from_user['language']:
                bot.send_message(call.message.chat.id, "Til o'zbek tiliga muvaffaqiyatli o'zgartirildi", reply_markup=menu)
            else:
                markup_inline = types.InlineKeyboardMarkup()
                item_1 = types.InlineKeyboardButton(text="Pubg Mobile", callback_data="menu")
                markup_inline.add(item_1)
                bot.send_message(call.message.chat.id, "Выберите игру:", reply_markup=markup_inline)
        elif call.data == 'page_1' or call.data == 'uzs' or call.data == 'rub':
            if call.data == "uzs":
                tsena = "💎60 UC - 11.000 UZS 💵\n💎120 UC - 21.000 UZS 💵\n💎180 UC - 30.000 UZS 💵\n💎355 UC - 51.000 UZS 💵\n💎420 UC - 62.000 UZS 💵"
            elif call.data == 'rub':
                tsena = "💎60 UC - 78₽💵\n💎120 UC - 150₽💵\n💎180 UC - 214₽💵\n💎355 UC - 364₽💵\n💎420 UC - 445₽💵"
            elif valyuta == "uzs":
                tsena = "💎60 UC - 11.000 UZS 💵\n💎120 UC - 21.000 UZS 💵\n💎180 UC - 30.000 UZS 💵\n💎355 UC - 51.000 UZS 💵\n💎420 UC - 62.000 UZS 💵"
            elif valyuta == "rub":
                tsena = "💎60 UC - 78₽💵\n💎120 UC - 150₽💵\n💎180 UC - 214₽💵\n💎355 UC - 364₽💵\n💎420 UC - 445₽💵"

            photo = open('photo.jpg', 'rb')
            markup_inline = types.InlineKeyboardMarkup()
            item_1 = types.InlineKeyboardButton(text="💎60 UC", callback_data="66")
            item_2 = types.InlineKeyboardButton(text="💎120 UC", callback_data="132")
            item_3 = types.InlineKeyboardButton(text="💎180 UC", callback_data="198")
            item_4 = types.InlineKeyboardButton(text="💎355 UC", callback_data="355")
            item_5 = types.InlineKeyboardButton(text="💎420 UC", callback_data="420")
            if from_user['language'] == "uz": 
                item_6 = types.InlineKeyboardButton(text="⬅️Orqaga", callback_data="valyuta")
                item_7 = types.InlineKeyboardButton(text="Keyingi sahifa➡️", callback_data="page_2")
            elif from_user['language'] == "ru":
                item_6 = types.InlineKeyboardButton(text="⬅️Назад", callback_data="valyuta")
                item_7 = types.InlineKeyboardButton(text="Дальше➡️", callback_data="page_2")
            markup_inline.add(item_1, item_2, item_3, item_4, item_5, item_6, item_7)
            if from_user['language'] == "uz": 
                bot.send_photo(call.message.chat.id, photo, "💸PUBG MOBILE UC NARXLARI💸\n\n"+tsena, reply_markup=markup_inline)
            elif from_user['language'] == "ru":
                bot.send_photo(call.message.chat.id, photo, "💸PUBG MOBILE UC ЦЕНЫ💸\n\n"+tsena, reply_markup=markup_inline)
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
            if from_user['language'] == "uz": 
                item_6 = types.InlineKeyboardButton(text="⬅️Orqaga", callback_data="page_1")
                item_7 = types.InlineKeyboardButton(text="Keyingi sahifa➡️", callback_data="page_3")
            elif from_user['language'] == "ru":
                item_6 = types.InlineKeyboardButton(text="⬅️Назад", callback_data="page_1")
                item_7 = types.InlineKeyboardButton(text="Дальше➡️", callback_data="page_3")
            markup_inline.add(item_1, item_2, item_3, item_4, item_5, item_6, item_7)
            if from_user['language'] == "uz": 
                bot.send_photo(call.message.chat.id, photo, "💸PUBG MOBILE UC NARXLARI💸\n\n"+tsena, reply_markup=markup_inline)
            elif from_user['language'] == "ru":
                bot.send_photo(call.message.chat.id, photo, "💸PUBG MOBILE UC ЦЕНЫ💸\n\n"+tsena, reply_markup=markup_inline)
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
            if from_user['language'] == "uz": 
                item_6 = types.InlineKeyboardButton(text="⬅️Orqaga", callback_data="page_2")
                item_7 = types.InlineKeyboardButton(text="Keyingi sahifa➡️", callback_data="page_4")
            elif from_user['language'] == "ru":
                item_6 = types.InlineKeyboardButton(text="⬅️Назад", callback_data="page_2")
                item_7 = types.InlineKeyboardButton(text="Дальше➡️", callback_data="page_4")
            markup_inline.add(item_1, item_2, item_3, item_4, item_5, item_6, item_7)
            if from_user['language'] == "uz": 
                bot.send_photo(call.message.chat.id, photo, "💸PUBG MOBILE UC NARXLARI💸\n\n"+tsena, reply_markup=markup_inline)
            elif from_user['language'] == "ru":
                bot.send_photo(call.message.chat.id, photo, "💸PUBG MOBILE UC ЦЕНЫ💸\n\n"+tsena, reply_markup=markup_inline)
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
            if from_user['language'] == "uz": 
                item_6 = types.InlineKeyboardButton(text="⬅️Orqaga", callback_data="page_3")
            elif from_user['language'] == "ru":
                item_6 = types.InlineKeyboardButton(text="⬅️Назад", callback_data="page_3")
            markup_inline.add(item_1, item_2, item_3, item_4, item_5, item_6)
            if from_user['language'] == "uz": 
                bot.send_photo(call.message.chat.id, photo, "💸PUBG MOBILE UC NARXLARI💸\n\n"+tsena, reply_markup=markup_inline)
            elif from_user['language'] == "ru":
                bot.send_photo(call.message.chat.id, photo, "💸PUBG MOBILE UC ЦЕНЫ💸\n\n"+tsena, reply_markup=markup_inline)
        elif call.data == "uzcard":
            photo = open('uzcard_photo.jpg', 'rb')
            markup_inline = types.InlineKeyboardMarkup()
            if from_user['language'] == "uz": 
                item_1 = types.InlineKeyboardButton(text="Tõladim ✅", callback_data="opcheck")
            elif from_user['language'] == "ru":
                item_1 = types.InlineKeyboardButton(text="Оплатил ✅", callback_data="opcheck")
            markup_inline.add(item_1)
            if from_user['language'] == "uz": 
                bot.send_photo(call.message.chat.id, photo, f"{operation['price']}\n\n8600 3141 6785 0751\nRAJABOVA UMIDA\nUlangan nomer +998933127053\n\n8600 0423 0682 2007\nRAJABOV MARUF\nUlangan nomer +998933127053", reply_markup=markup_inline)
            elif from_user['language'] == "ru":
                bot.send_photo(call.message.chat.id, photo, f"{operation['price']}\n\n8600 3141 6785 0751\nRAJABOVA UMIDA\nПривязанный номер +998933127053\n\n8600 0423 0682 2007\nRAJABOV MARUF\nПривязанный номер +998933127053", reply_markup=markup_inline)
        elif call.data == "humo":
            photo = open('humo_photo.jpg', 'rb')
            markup_inline = types.InlineKeyboardMarkup()
            if from_user['language'] == "uz": 
                item_1 = types.InlineKeyboardButton(text="Tõladim ✅", callback_data="opcheck")
            elif from_user['language'] == "ru":
                item_1 = types.InlineKeyboardButton(text="Оплатил ✅", callback_data="opcheck")
            markup_inline.add(item_1)
            if from_user['language'] == "uz":
                bot.send_photo(call.message.chat.id, photo, f"{operation['price']}\n\n9860 0801 9358 6643\nRAJABOVA UMIDA\nUlangan nomer +998933127053\n\n4073 4200 6731 7366\nRAJABOVA UMIDA\nUlangan nomer +998933127053", reply_markup=markup_inline)
            elif from_user['language'] == "ru":
                bot.send_photo(call.message.chat.id, photo, f"{operation['price']}\n\n9860 0801 9358 6643\nRAJABOVA UMIDA\nПривязанный номер +998933127053\n\n4073 4200 6731 7366\nRAJABOVA UMIDA\nПривязанный номер +998933127053", reply_markup=markup_inline)
        elif call.data == "opcheck":
            if previous_operation:
                markup_reply = types.ReplyKeyboardMarkup(resize_keyboard = True, one_time_keyboard = True)
                button = types.KeyboardButton(f"{previous_operation['card']}")
                button2 = types.KeyboardButton("Меню")
                markup_reply.add(button).row(button2)
                if from_user['language'] == "uz":
                    bot.send_message(call.message.chat.id, "To'lov qilgan karta raqamini yuboring :\n\nMasalan: card 0000 0000 0000 0000\n\n(Boshida \"card\" suzi bo'lishi shart)", reply_markup=markup_reply)
                elif from_user['language'] == "ru":
                    bot.send_message(call.message.chat.id, "После оплаты киньте номер карты :\n\nНапример: card 0000 0000 0000 0000\n\n(В начале \"card\" обьзательно)", reply_markup=markup_reply)
            else:
                markup_reply = types.ReplyKeyboardMarkup(resize_keyboard = True)
                button = types.KeyboardButton("Меню")
                markup_reply.add("Меню")
                if from_user['language'] == "uz":
                    bot.send_message(call.message.chat.id, "To'lov qilgan karta raqamini yuboring :\n\nMasalan: card 0000 0000 0000 0000\n\n(Boshida \"card\" suzi bo'lishi shart)", reply_markup=markup_reply)
                elif from_user['language'] == "ru":
                    bot.send_message(call.message.chat.id, "После оплаты киньте номер карты :\n\nНапример: card 0000 0000 0000 0000\n\n(В начале \"card\" обьзательно)", reply_markup=markup_reply)
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
                    cursor.execute(f"""UPDATE `operations` SET uc = {uc} WHERE id = {operation['id']};""")
                    connection.commit()
                if valyuta == "uzs":
                    with connection.cursor() as cursor:
                        cursor.execute(f"""UPDATE `operations` SET price = '{uzs}' WHERE id = {operation['id']};""")
                        connection.commit()
                elif valyuta == "rub":
                    with connection.cursor() as cursor:
                        cursor.execute(f"""UPDATE `operations` SET price = '{rub}' WHERE id = {operation['id']};""")
                        connection.commit()
            markup_inline = types.InlineKeyboardMarkup()
            item_1 = types.InlineKeyboardButton(text="Uzcard", callback_data="uzcard")
            item_2 = types.InlineKeyboardButton(text="Humo", callback_data="humo")
            markup_inline.add(item_1, item_2)
            if from_user['language'] == "ru":
                bot.send_message(call.message.chat.id, "Выберите способ оплаты:", reply_markup=markup_inline)
            elif from_user['language'] == "uz":
                bot.send_message(call.message.chat.id, "To'lov usulini tanlang:", reply_markup=markup_inline)

@bot.message_handler(content_types=['text', 'photo'])
def get_text(message):
    if connection:
        with connection.cursor() as cursor:
            cursor.execute(f"""SELECT * from `users` WHERE user_id = {message.from_user.id}""")
            from_user = cursor.fetchone()
            cursor.execute(f"""SELECT * from `operations` WHERE user_id = {from_user['id']} AND status is not NULL""")
            operations = cursor.fetchall()
            operation_num = len(operations)
            cursor.execute(f"""SELECT * from `operations` WHERE user_id = {from_user['id']} and operation_id = {operation_num+1}""")
            operation = cursor.fetchone()
            cursor.execute(f"""SELECT * from `operations` WHERE user_id = {from_user['id']} and operation_id = {operation_num}""")
            previous_operation = cursor.fetchone()
    menu = types.ReplyKeyboardMarkup(resize_keyboard = True)
    if from_user['language'] == "uz":
        menu_uc = types.KeyboardButton("UC sotib olish")
        menu_story = types.KeyboardButton("Buyurtmalar tarixi")
        menu_language = types.KeyboardButton("Tilni o'zgartirish")
    elif from_user['language'] == "ru":
        menu_uc = types.KeyboardButton("Купить UC")
        menu_story = types.KeyboardButton("История операций")
        menu_language = types.KeyboardButton("Язык")
    menu.add(menu_uc).row(menu_story, menu_language)
    if from_user['status'] == 'superadmin' or from_user['status'] == 'admin':
        pass
    else:
        if message.text:
            if message.text == "Меню":
                bot.send_message(message.chat.id, "Меню",reply_markup=menu)
            elif message.text == "Купить UC" or message.text == "UC sotib olish":
                markup_inline = types.InlineKeyboardMarkup()
                item_1 = types.InlineKeyboardButton(text="UZS", callback_data="uzs")
                item_2 = types.InlineKeyboardButton(text="RUB", callback_data="rub")
                markup_inline.add(item_1, item_2)
                if from_user['language'] == "uz":
                    bot.send_message(message.chat.id, "Valyutani tanlang:", reply_markup=markup_inline)
                elif from_user['language'] == "ru":
                    bot.send_message(message.chat.id, "Выберите валюту:", reply_markup=markup_inline)
            elif message.text == "История операций" or message.text == "Buyurtmalar tarixi":
                story = ""
                for opr in operations:
                    if opr['status']:
                        if from_user['language'] == "ru":
                            if opr['status'] == "progress":
                                opr_status = "В процессее ⏳"
                            elif opr['status'] == "rejected":
                                opr_status = "Отклонено ❌"
                            elif opr['status'] == "delivered":
                                opr_status = "Подтверждено ✅"
                            story += f"\nЗаказ #{opr['operation_id']}\nЦена: {opr['price']}\nТовар: {opr['uc']} UC\nКарта:{opr['card'][4:]}\n{opr['pubg_id']}\nNICK:{opr['nickname']}\nСтатус: {opr_status}\n"
                        elif from_user['language'] == "uz":
                            if opr['status'] == "progress":
                                opr_status = "Jarayonda ⏳"
                            elif opr['status'] == "rejected":
                                opr_status = "Rad etilgan ❌"
                            elif opr['status'] == "delivered":
                                opr_status = "Tasdiqlangan ✅"
                            story += f"\nBuyurtma #{opr['operation_id']}\nNarxi: {opr['price']}\nMahsulot: {opr['uc']} UC\nKarta:{opr['card'][4:]}\n{opr['pubg_id']}\nNICK:{opr['nickname']}\nHolat: {opr_status}\n"
                if story:
                    bot.send_message(message.chat.id, story)
                else:
                    if from_user['language'] == "ru":
                        bot.send_message(message.chat.id, "Вы ещё не совершили не одной операции")
                    elif from_user['language'] == "uz":
                        bot.send_message(message.chat.id, "Siz hali hech qanday tranzaksiyani tugatmagansiz")
            elif message.text == "Язык" or message.text == "Tilni o'zgartirish":
                markup_inline = types.InlineKeyboardMarkup()
                item_ru = types.InlineKeyboardButton(text="Русский 🇷🇺", callback_data="ru")
                item_uz = types.InlineKeyboardButton(text="O'zbekcha 🇺🇿", callback_data="uz")
                markup_inline.add(item_ru, item_uz)
                bot.send_message(message.chat.id, "Выберите язык:", reply_markup=markup_inline)
            elif message.text.lower().startswith("card"):
                if operation['price']:
                    if connection:
                        with connection.cursor() as cursor:
                            cursor.execute(f"""UPDATE `operations` SET card = '{message.text.upper()}' WHERE id = {operation['id']};""")
                            connection.commit()
                    markup_reply = types.ReplyKeyboardMarkup(resize_keyboard=True)
                    button = types.KeyboardButton("Меню")
                    markup_reply.add(button)
                    if from_user['language'] == "uz":
                        bot.reply_to(message, "Karta raqami qabul qilindi ✅")
                        bot.send_message(message.chat.id, "To'lov chekini skrinshotini yuboring:\n\n(Skrinshot file formatida bo'lmasligi lozim)", reply_markup=markup_reply)
                    elif from_user['language'] == 'ru':
                        bot.reply_to(message, "Карта принята ✅")
                        bot.send_message(message.chat.id, "Отправьте криншот чека оплаты:\n\n(Скриншот не должен быть в файловом формате)", reply_markup=markup_reply)
            elif message.text.lower().startswith("id"):
                if operation['photo_id']:
                    if connection:
                        with connection.cursor() as cursor:
                            cursor.execute(f"""UPDATE `operations` SET pubg_id = '{message.text.upper()}' WHERE id = {operation['id']};""")
                            connection.commit()
                    if previous_operation:
                        markup_reply = types.ReplyKeyboardMarkup(resize_keyboard = True, one_time_keyboard = True)
                        button = types.KeyboardButton(f"NICK {previous_operation['nickname']}")
                        button2 = types.KeyboardButton("Меню")
                        markup_reply.add(button).row(button2)
                        if from_user['language'] == "uz":
                            bot.reply_to(message, "ID qabul qilindi ✅")
                            bot.send_message(message.chat.id, "Endi sizning PUBG dagi nickname gizni yuboring :\n\nMasalan: nick alyosha123\n\n(Boshida \"nick\" suzi bo'lishi shart)", reply_markup=markup_reply)
                        elif from_user['language'] == 'ru':
                            bot.reply_to(message, "ID принят✅")
                            bot.send_message(message.chat.id, "Отправьте ваш игровой ник в PUBG :\n\nНапример: nick Andrey\n\n(В начале слово \"nick\" обьзательно)", reply_markup=markup_reply)
                    else:
                        markup_reply = types.ReplyKeyboardMarkup(resize_keyboard = True)
                        button = types.KeyboardButton("Меню")
                        markup_reply.add("Меню")
                        bot.reply_to(message, "ID qabul qilindi ✅")
                        bot.send_message(message.chat.id, "Endi sizning PUBG dagi nickname gizni yuboring :\n\nMasalan: nick alyosha123\n\n(Boshida \"nick\" suzi bo'lishi shart)", reply_markup=markup_reply)
            elif message.text.lower().startswith("nick"):
                if operation['pubg_id']:
                    if connection:
                        with connection.cursor() as cursor:
                            cursor.execute(f"""UPDATE `operations` SET nickname = '{message.text[4:]}', status = 'progress' WHERE id = {operation['id']};""")
                            connection.commit()
                        with connection.cursor() as cursor:
                            cursor.execute(f"""SELECT user_id from `users` WHERE status = 'superadmin' or status = 'admin'""")
                            admins = cursor.fetchall()
                    if from_user['language'] == "uz":
                        bot.reply_to(message, "Nickname qabul qilindi ✅")
                        bot.send_message(message.chat.id, "Zakaz qabul qilindi UC tushishini kuting", reply_markup=menu)
                    elif from_user['language'] == 'ru':
                        bot.reply_to(message, "Nickname принят ✅")
                        bot.send_message(message.chat.id, "Ваш заказ принят ждите пополнения UC", reply_markup=menu)
                    markup_inline = types.InlineKeyboardMarkup()
                    item = types.InlineKeyboardButton(text="Подтвердить", callback_data=f"success_{operation['id']}")
                    item2 = types.InlineKeyboardButton(text="Отклонить", callback_data=f"reject_{operation['id']}")
                    markup_inline.add(item2, item)
                    photo_file = bot.get_file(operation['photo_id'])
                    photo_bytes = bot.download_file(photo_file.file_path)
                    for admin in admins:
                        bot.send_photo(admin['user_id'], photo_bytes, f"{operation['card']}\n{operation['pubg_id']}\nUC: {operation['uc']}\nPRICE: {operation['price']}\nNICK:{message.text[4:]}\n@{from_user['username']}", reply_markup=markup_inline)
        elif message.photo:
            if operation['card']:
                photo_id = message.photo[-1].file_id
                if connection:
                    with connection.cursor() as cursor:
                        cursor.execute(f"""UPDATE `operations` SET photo_id = '{photo_id}' WHERE id = {operation['id']};""")
                        connection.commit()
                if previous_operation:
                    markup_reply = types.ReplyKeyboardMarkup(resize_keyboard = True, one_time_keyboard = True)
                    button = types.KeyboardButton(f"{previous_operation['pubg_id']}")
                    button2 = types.KeyboardButton("Меню")
                    markup_reply.add(button).row(button2)
                    if from_user['language'] == "uz":
                        bot.reply_to(message, "Chek qabul qilindi ✅")
                        bot.send_message(message.chat.id, "Sizning PUBG dagi ID gizni yuboring :\n\nMasalan: id 123456789\n\n(Boshida \"id\" suzi bo'lishi shart)", reply_markup=markup_reply)
                    elif from_user['language'] == "ru":
                        bot.reply_to(message, "Чек принят ✅")
                        bot.send_message(message.chat.id, "Отправьте ваш игровой ID :\n\nНапример: id 123456789\n\n(В начале слово \"id\" обьзательно)", reply_markup=markup_reply)
                else:
                    markup_reply = types.ReplyKeyboardMarkup(resize_keyboard = True)
                    button = types.KeyboardButton("Меню")
                    markup_reply.add("Меню")
                    if from_user['language'] == "uz":
                        bot.reply_to(message, "Chek qabul qilindi ✅")
                        bot.send_message(message.chat.id, "Sizning PUBG dagi ID gizni yuboring :\n\nMasalan: id 123456789\n\n(Boshida \"id\" suzi bo'lishi shart)", reply_markup=markup_reply)
                    elif from_user['language'] == "ru":
                        bot.reply_to(message, "Чек принят ✅")
                        bot.send_message(message.chat.id, "Отправьте ваш игровой ID :\n\nНапример: id 123456789\n\n(В начале слово \"id\" обьзательно)", reply_markup=markup_reply)
            
    
bot.infinity_polling()