import telebot
from telebot import types
import sqlite3
import pandas as pd
import random
import os
import time  # Importing time for simulating delay
from datetime import datetime

# Replace 'YOUR_BOT_TOKEN' with your actual bot token obtained from BotFather
bot = telebot.TeleBot('7280241870:AAFkYsIc0bd1Nf5Eb82uWc4igSqk09mehAM')

help_number = '+996 700 123 456'


# List of admin user IDs
admin_users = [1466032078, 987654321]  # Replace with actual admin user IDs

# Default warehouse address
default_warehouse_address = "16699582668\n广东省佛山市南海区里水镇\n里水镇国宏产业园C区102B"

# Connect to SQLite database
conn = sqlite3.connect('bot_database.db', check_same_thread=False)
cursor = conn.cursor()

# Create tables if they don't exist
cursor.execute('''CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY,
                    chat_id INTEGER UNIQUE,
                    name TEXT,
                    person_code TEXT,
                    phone TEXT,
                    region TEXT
                  )''')
cursor.execute('''CREATE TABLE IF NOT EXISTS products (
                    id INTEGER PRIMARY KEY,
                    product_code TEXT UNIQUE,
                    weight TEXT,
                    type TEXT
                  )''')

conn.commit()

# Handling /start command
@bot.message_handler(commands=['start'])
def send_welcome(message):
    chat_id = message.chat.id
    cursor.execute("SELECT * FROM users WHERE chat_id=?", (chat_id,))
    user = cursor.fetchone()
    
    markup = types.InlineKeyboardMarkup()

    if not user:
        itembtn_register_person = types.InlineKeyboardButton('🔑 Получить клиентский код', callback_data='register_person')
        markup.add(itembtn_register_person)
    
    itembtn_search_product = types.InlineKeyboardButton('🔎 Отследить посылку', callback_data='search_product')
    itembtn_myprofile = types.InlineKeyboardButton('👤 Мой профиль', callback_data='my_profile')
    itembtn_sendaddress = types.InlineKeyboardButton('🏢 Адрес в Китае', callback_data='send_address')
    markup.add(itembtn_search_product)
    markup.add(itembtn_myprofile)
    markup.add(itembtn_sendaddress)
    
    if chat_id in admin_users:
        itembtn_register_product = types.InlineKeyboardButton('➕ Добавить товары', callback_data='register_product')
        itembtn_user_list = types.InlineKeyboardButton('📄 Список клиентов', callback_data='user_list')
        itembtn_product_list = types.InlineKeyboardButton('📄 Список товаров', callback_data='product_list')
        itembtn_template_file = types.InlineKeyboardButton('📄 Шаблон для Excel файл', callback_data='template_file')
        markup.add(itembtn_register_product)
        markup.add(itembtn_user_list)
        markup.add(itembtn_product_list)
        markup.add(itembtn_template_file)
    
    bot.send_message(chat_id, "Привет и добро пожаловать в этот телеграм-бот. \n Меню 👇", reply_markup=markup)

# Handling /help command
@bot.message_handler(commands=['help'])
def send_help(message):
    chat_id = message.chat.id
    cursor.execute("SELECT * FROM users WHERE chat_id=?", (chat_id,))
    user = cursor.fetchone()
    
    markup = types.InlineKeyboardMarkup()

    if not user:
        itembtn_register_person = types.InlineKeyboardButton('🔑 Получить клиентский код', callback_data='register_person')
        markup.add(itembtn_register_person)
    
    itembtn_search_product = types.InlineKeyboardButton('🔎 Отследить посылку', callback_data='search_product')
    itembtn_myprofile = types.InlineKeyboardButton('👤 Мой профиль', callback_data='my_profile')
    itembtn_sendaddress = types.InlineKeyboardButton('🏢 Адрес в Китае', callback_data='send_address')
    markup.add(itembtn_search_product)
    markup.add(itembtn_myprofile)
    markup.add(itembtn_sendaddress)
    
    if chat_id in admin_users:
        itembtn_register_product = types.InlineKeyboardButton('➕ Добавить товары', callback_data='register_product')
        itembtn_user_list = types.InlineKeyboardButton('📄 Список клиентов', callback_data='user_list')
        itembtn_product_list = types.InlineKeyboardButton('📄 Список товаров', callback_data='product_list')
        markup.add(itembtn_register_product)
        markup.add(itembtn_user_list)
        markup.add(itembtn_product_list)
    
    bot.send_message(chat_id, "Привет и добро пожаловать в этот телеграм-бот.", reply_markup=markup)

# Callback query handler
@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    chat_id = call.message.chat.id
    #рекгистрация клиентов
    if call.data == 'register_person':
        msg = bot.send_message(chat_id, "Пожалуйста, введите Ваше имя:")
        bot.register_next_step_handler(msg, process_name_step)
    #Регистрация посылки
    elif call.data == 'register_product':
        if chat_id in admin_users:
            bot.send_message(chat_id, "Пожалуйста, загрузите файл Excel с товарами.")
        else:
            bot.send_message(chat_id, "У вас нет прав на добавление товаров.")
    #Поиск трек-кодов
    elif call.data == 'search_product':
        msg = bot.send_message(chat_id, "Введите трек-код для отслеживания:")
        bot.register_next_step_handler(msg, process_search_product)
    #Отправка список клиентов
    elif call.data == 'user_list':
        if chat_id in admin_users:
            send_user_list(call.message)
        else:
            bot.send_message(chat_id, "У вас нет прав на просмотр списка пользователей.")
    #Отправка список посылки
    elif call.data == 'product_list':
        if chat_id in admin_users:
            send_product_list(call.message)
        else:
            bot.send_message(chat_id, "У вас нет прав на просмотр списка товаров.")
    #Отправка Шаблон файл Excel
    elif call.data == 'template_file':
        if chat_id in admin_users:
            send_template_file(call.message)
        else:
            bot.send_message(chat_id, "У вас нет прав на просмотр списка товаров.")
    #Отправка Мой профиль
    elif call.data == 'my_profile':
        send_profile(call.message)
    #Отправка адрес в китае
    elif call.data == 'send_address':
        send_default_warehouse_address(call.message)
    #Отправка главная меню
    elif call.data == 'cancel':
        send_welcome(call.message)
    #Отправка Выбрать регион
    elif call.data.startswith('region_'):
        region = call.data.split('_')[1]
        chat_id = call.message.chat.id
        cursor.execute("UPDATE users SET region=? WHERE chat_id=?", (region, chat_id))
        conn.commit()
        bot.send_message(chat_id, f"Ваш регион был установлен на {region}. \nПожалуйста, введите свой номер телефона: 996778050105 в этом формате")
        bot.register_next_step_handler(call.message, process_phone_step)

def process_name_step(message):
    try:
        chat_id = message.chat.id
        user_data = {}
        user_data['name'] = message.text

        # Generate a random person code (ABC-123456 format)
        user_data['person_code'] = generate_person_code()

        cursor.execute("INSERT INTO users (chat_id, name, person_code) VALUES (?, ?, ?)",
                       (chat_id, user_data['name'], user_data['person_code']))
        conn.commit()

        markup = types.InlineKeyboardMarkup()
        regions = ["🇰🇬 Ош", "🇰🇬 Бишкек", "🇰🇬 Кара-Суу", "🇰🇬 Кадамжай"]
        for region in regions:
            itembtn_region = types.InlineKeyboardButton(region, callback_data=f'region_{region}')
            markup.add(itembtn_region)
        bot.send_message(chat_id, "Пожалуйста, выберите ваш регион:", reply_markup=markup)
    except Exception as e:
        bot.send_message(chat_id, 'Что-то пошло не так. Попробуйте еще раз.')

def process_phone_step(message):
    try:
        chat_id = message.chat.id
        user_data = {}
        user_data['phone'] = message.text

        cursor.execute("UPDATE users SET phone=? WHERE chat_id=?", (user_data['phone'], chat_id))
        conn.commit()

        # Registration successful message
        cursor.execute("SELECT * FROM users WHERE chat_id=?", (chat_id,))
        user = cursor.fetchone()
        registration_message = f"✅ Регистрация успешно завершена! \n \n 👤Ваше имя: {user[2]}\n🔑Клиентский код: {user[3]}\n📞Телефон: {user[4]}\n🏙️Регион: {user[5]}."
        bot.send_message(message.chat.id, registration_message)

        # Update keyboard markup to remove /register button
        send_welcome(message)
    except Exception as e:
        bot.send_message(message.chat.id, 'Что-то пошло не так. Попробуйте еще раз.')


# Handling document uploads (for admin users)
@bot.message_handler(content_types=['document'])
def handle_document(message):
    try:
        if message.from_user.id not in admin_users:
            bot.send_message(message.chat.id, "У вас нет прав на добавление товаров.")
            return

        # Sending loading message
        loading_message = bot.send_message(message.chat.id, '⏳ Пожалуйста, подождите. Обработка файла...')

        file_info = bot.get_file(message.document.file_id)
        file_path = f"https://api.telegram.org/file/bot{bot.token}/{file_info.file_path}"

        # Simulating a delay for loading
        time.sleep(2)

        # Assuming the file is in xlsx format
        df = pd.read_excel(file_path)

        # Process each row in the dataframe
        for index, row in df.iterrows():
            product_code = str(row['Product Code'])
            product_weight = str(row['Product Weight'])
            product_type = str(row['Product Type'])

            try:
                cursor.execute("INSERT INTO products (product_code, weight, type) VALUES (?, ?, ?)",
                               (product_code, product_weight, product_type))
                conn.commit()
            except sqlite3.IntegrityError:
                bot.send_message(message.chat.id, f"🚫Ошибка: Посылка с трек-кодом {product_code} уже существует в базе данных.")

        # Update loading message with success message
        bot.edit_message_text("✅ Посылки успешно добавлены из загруженного файла.", chat_id=message.chat.id, message_id=loading_message.message_id)
    except Exception as e:
        bot.send_message(message.chat.id, '❗️Что-то пошло не так. Попробуйте еще раз.')

# Function to search for a product by its code
def process_search_product(message):
    loading_message = bot.send_message(message.chat.id, '⏳ Пожалуйста, подождите. Идет поиск трек-кода...')

    # Simulating a delay for loading
    time.sleep(2)
    
    product_code = message.text.strip()

    cursor.execute("SELECT * FROM products WHERE product_code=?", (product_code,))
    product = cursor.fetchone()

    if product:
        result_message = f"✅Трек-код успешно найден\n\n📦Трек-код: _{product[1]}_\n📦Тип посылка: {product[3]}\n⚖️Вес: {product[2]}"
    else:
        result_message = "🚫 Трек-код не найден."

    # Update loading message with the result
    bot.edit_message_text(result_message, chat_id=message.chat.id, message_id=loading_message.message_id, parse_mode="Markdown")

    # Add a button to trigger /search_product again
    markup = types.InlineKeyboardMarkup()
    itembtn_search_product = types.InlineKeyboardButton('🔎 Искать еще раз', callback_data='search_product')
    itembtn_cancel = types.InlineKeyboardButton('❌ Отмена', callback_data='cancel')
    markup.add(itembtn_search_product,itembtn_cancel)
    bot.send_message(message.chat.id, "Хотите найти другой трек-код?", reply_markup=markup)

# Function to generate a random person code
def generate_person_code():
    letters = 'ABC'
    digits = '0123456789'
    code = ''.join((letters)) + '-' + ''.join(random.choice(digits) for _ in range(6))
    return code

def send_template_file(message):
    try:
        template_file_path = "Шаблон.xlsx"  # Path to your template file
        with open(template_file_path, 'rb') as template_file:
            bot.send_document(message.chat.id, template_file)
        
        bot.send_message(message.chat.id, "Пожалуйста, используйте этот шаблон для добавления товаров и загрузите заполненный файл.")
    except Exception as e:
        bot.send_message(message.chat.id, '❗️Не удалось отправить файл шаблона. Попробуйте еще раз.')

# Function to send user profile information
def send_profile(message):
    loading_message = bot.send_message(message.chat.id, '⏳ Пожалуйста, подождите. Получение профиля...')
    
    # Simulating a delay for loading
    time.sleep(2)
    
    chat_id = message.chat.id
    cursor.execute("SELECT * FROM users WHERE chat_id=?", (chat_id,))
    user = cursor.fetchone()
    
    if user:
        profile_message = f"👤Мой профиль\n🆔TG-id: `{user[1]}`\n*================* \n\n👤Ваше имя: *{user[2]}* \n🔑 Клиентский код: *{user[3]}*\n 📞Телефон: {user[4]}\n 🏙️Регион ПВЗ: {user[5]} "
        markup = types.InlineKeyboardMarkup()
        itembtn_cancel = types.InlineKeyboardButton('📄 Главная меню', callback_data='cancel')
        markup.add(itembtn_cancel)
        bot.edit_message_text(profile_message, chat_id=message.chat.id, message_id=loading_message.message_id, reply_markup=markup, parse_mode='Markdown')
    else:
        bot.edit_message_text("⚠️Вы не зарегистрированы. Пожалуйста, сначала зарегистрируйтесь.", chat_id=message.chat.id, message_id=loading_message.message_id)

# Function to send the list of registered users (for admin)
def send_user_list(message):
    loading_message = bot.send_message(message.chat.id, '⏳ Пожалуйста, подождите. Получение списка клиентов...')
    
    # Simulating a delay for loading
    time.sleep(2)
    
    try:
        cursor.execute("SELECT * FROM users")
        users = cursor.fetchall()
        
        if not users:
            bot.edit_message_text("⚠️Ни один пользователь не зарегистрирован.", chat_id=message.chat.id, message_id=loading_message.message_id)
            return

        user_list = []

        for user in users:
            user_list.append({
                'Chat-id': user[1],
                'Имя клиента': user[2],
                'Клиентский код': user[3],
                'Телефон': user[4],
                'Регион ПВЗ': user[5]
            })

        df = pd.DataFrame(user_list)
        current_datetime = datetime.now().strftime('%d-%m-%Y %H-%M-%S')
        # Save the DataFrame to an Excel file
        file_path = f"Список клиентов от {current_datetime}.xlsx"
        df.to_excel(file_path, index=False)

        with open(file_path, 'rb') as file:
            bot.send_document(message.chat.id, file)
            markup = types.InlineKeyboardMarkup()
            itembtn_cancel = types.InlineKeyboardButton('📄 Главная меню', callback_data='cancel')
            markup.add(itembtn_cancel)
            bot.send_message(message.chat.id, "📂 Вы можете сохранить и скачать файл!", reply_markup=markup)

        # Remove the file after sending
        os.remove(file_path)

        # Update loading message with success message
        bot.edit_message_text("✅ Список клиентов успешно получен.", chat_id=message.chat.id, message_id=loading_message.message_id)
    except Exception as e:
        bot.edit_message_text('⚠️Что-то пошло не так.', chat_id=message.chat.id, message_id=loading_message.message_id)

def send_product_list(message):
    loading_message = bot.send_message(message.chat.id, '⏳ Пожалуйста, подождите. Получение списка товаров...')
    
    # Simulating a delay for loading
    time.sleep(2)
    
    try:
        cursor.execute("SELECT * FROM products")
        products = cursor.fetchall()
        
        if not products:
            bot.edit_message_text("Ни один товар не зарегистрирован.", chat_id=message.chat.id, message_id=loading_message.message_id)
            return

        product_list = []

        for product in products:
            product_list.append({
                'Трек-код': product[1],
                'Вес, кг': product[2],
                'Тип товара': product[3]
            })

        df = pd.DataFrame(product_list)

        # Save the DataFrame to an Excel file
        current_datetime = datetime.now().strftime('%d-%m-%Y %H-%M-%S')
        file_path = f"Список товаров {current_datetime}.xlsx"
        df.to_excel(file_path, index=False)

        with open(file_path, 'rb') as file:
            bot.send_document(message.chat.id, file)
            markup = types.InlineKeyboardMarkup()
            itembtn_cancel = types.InlineKeyboardButton('📄 Главная меню', callback_data='cancel')
            markup.add(itembtn_cancel)
            bot.send_message(message.chat.id, "📂 Вы можете сохранить и скачать файл!", reply_markup=markup)

        

        # Remove the file after sending
        os.remove(file_path)

        # Update loading message with success message
        bot.edit_message_text("✅ Список товаров успешно получен.", chat_id=message.chat.id, message_id=loading_message.message_id)
    except Exception as e:
        bot.edit_message_text('Что-то пошло не так.', chat_id=message.chat.id, message_id=loading_message.message_id)

# Function to send the default warehouse address with client details
def send_default_warehouse_address(message):
    loading_message = bot.send_message(message.chat.id, '⏳ Пожалуйста, подождите. Получение адреса склада...')
    
    # Simulating a delay for loading
    time.sleep(2)
    
    chat_id = message.chat.id
    cursor.execute("SELECT * FROM users WHERE chat_id=?", (chat_id,))
    user = cursor.fetchone()
    
    if user:
        address_message = f"{user[3]}\n{default_warehouse_address}\n{user[2]} ({user[4]})"
        markup = types.InlineKeyboardMarkup()
        itembtn_cancel = types.InlineKeyboardButton('📄 Главная меню', callback_data='cancel')
        markup.add(itembtn_cancel)
        bot.edit_message_text(address_message, chat_id=message.chat.id, reply_markup=markup,message_id=loading_message.message_id)
    else:
        bot.edit_message_text("Для получения полного адреса, пожалуйста, получите клиентский код.", chat_id=message.chat.id, message_id=loading_message.message_id)

# Start polling
bot.polling()
