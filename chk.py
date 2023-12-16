import telebot
from telebot import types
import random
import re

# Inicializar el bot con su token
bot = telebot.TeleBot("6800462877:AAGB5Rvi2qz-UsHQ8Y6_7e4uqgym5NZC1rM")

# Listas de prefijos
lgen_prefixes = [
    ".em ", ".ppp ", ".pn ", ".ms ", ".sq ", ".bra ",
    ".ad ", ".ll ", ".qrt ", ".pfp ", ".mch ", ".mau "
]
ccn_prefixes = [".tn ", ".tk ", ".ts ", '.to ' , '.tz ' , 'tx ','.gn ', '.ac ','.tf ']
cvv_prefixes = [".pf ",".bra ",".ll " ,".mch " ,".pn ",".bra ", ".ad "]


# Imprime el DataFrame

index = 0
# Variables globales para mantener el estado
user_data = {}
current_function = None

# Función para manejar el comando '/start'
@bot.message_handler(commands=['start'])
def send_welcome(message):
    user_data[message.from_user.id] = {'document': None, 'extracted_cards': []}
    bot.send_message(message.chat.id, "Bienvenido al bot. Elige una opción:", reply_markup=main_menu())

# Función para crear el menú principal
def main_menu():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    markup.add('lgen', 'CVV Scrapper', 'CCN Charged', 'Limpiar')
    return markup

# Nuevo menú para CCN Charged con el botón '2'
def ccn_charged_menu():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    markup.add('2')
    return markup

def lgen_menu():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    markup.add('manda', 'atras')
    return markup

def cvv_menu():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    markup.add('compalta', 'mod', 'end')  # Added 'mod' button here
    return markup

# Función para procesar el documento enviado por el usuario
@bot.message_handler(content_types=['document'])
def document_handler(message):
    try:
        chat_id = message.chat.id
        user_id = message.from_user.id

        file_info = bot.get_file(message.document.file_id)
        downloaded_file = bot.download_file(file_info.file_path)

        # Mezclar líneas
        lines = downloaded_file.decode('utf-8').splitlines()
        random.shuffle(lines)

        # Agregar prefijos y enviar mensajes
        prefix_index = 0
        while lines:  # Mientras haya líneas en la lista
            prefix = lgen_prefixes[prefix_index]
            prefix_index = (prefix_index + 1) % len(lgen_prefixes)
            
            if prefix in [".mau ", ".mch "]:
                # Tomar las primeras 10 líneas y unirlas en un solo mensaje
                message_lines = lines[:10]
                message_text = prefix + '\n'.join(message_lines)
                bot.send_message(chat_id, message_text)
                # Remover las 10 líneas de la lista original
                lines = lines[10:]
            else:
                # Enviar la línea con el prefijo
                prefixed_line = prefix + lines.pop(0)
                bot.send_message(chat_id, prefixed_line)

        bot.send_message(chat_id, "Todas las líneas han sido enviadas.")
    except Exception as e:
        bot.reply_to(message, "Ocurrió un error: " + str(e))

# Handlers para lgen
@bot.message_handler(func=lambda message: message.text == 'lgen')
def lgen_handler(message):
    bot.send_message(message.chat.id, "Envía un documento por favor.", reply_markup=lgen_menu())

# Handlers para manda
@bot.message_handler(func=lambda message: message.text == 'manda')
def manda_handler(message):
    user_id = message.from_user.id
    if 'document' in user_data[user_id] and user_data[user_id]['document']:
        for line in user_data[user_id]['document']:
            bot.send_message(message.chat.id, line)
        user_data[user_id]['document'] = None  # Limpiar el documento procesado
    else:
        bot.send_message(message.chat.id, "Por favor, envía el documento primero.")
@bot.message_handler(func=lambda message: message.text == 'atras')
def atras_handler(message):
    bot.send_message(message.chat.id, "Regresando al menú principal...", reply_markup=main_menu())
    
# Handlers para CVV
@bot.message_handler(func=lambda message: message.text == 'CVV Scrapper')
def cvv_scrapper_handler(message):
    global current_function
    current_function = 'CVV Scrapper'
    bot.send_message(message.chat.id, "MANDA CVV.", reply_markup=cvv_menu())


# Handlers para end    
@bot.message_handler(func=lambda message: message.text == 'end')
def end_handler(message):
    global current_function
    if current_function == 'CVV Scrapper':
        current_function = None
        bot.send_message(message.chat.id, "Regresando al menú principal...", reply_markup=main_menu())

 # Handlers para CCN CHARGED   
@bot.message_handler(func=lambda message: message.text == 'CCN Charged')
def ccn_charged_handler(message):
    global current_function
    current_function = 'CCN Charged'
    bot.send_message(message.chat.id, "MANDA CCN", reply_markup=ccn_charged_menu())

# Handler para '2' que regresa al menú principal y termina la función de CCN Charged
@bot.message_handler(func=lambda message: message.text == '2')
def two_handler(message):
    global current_function
    if current_function == 'CCN Charged':
        current_function = None
        bot.send_message(message.chat.id, "Regresando al menú principal...", reply_markup=main_menu())

#GENERAL
@bot.message_handler(func=lambda m: True)
def handle_messages(message):
    global index, current_function
    if current_function == 'CVV Scrapper':
       if ' ' in message.text:
        card = re.search(r'\b(\d{16}|\d{15})[:|]\d{2}[:|](\d{4}|\d{2})[:|]\d{3}\b', message.text)
        if card:
            bot.reply_to(message, cvv_prefixes[index % len(cvv_prefixes)] + ' ' + card.group())
            index += 1
    elif message.text.lower() == 'listo':
        bot.reply_to(message, 'Todas las tarjetas han sido enviadas.')

    elif current_function == 'CCN Charged':
        if '?' in message.text:
            # Dividir el mensaje en líneas
            lines = message.text.split('\n')
            for i, line in enumerate(lines):
                if '?' in line:
                    # Buscar la tarjeta en la línea anterior
                    if i > 0:  # Asegurarse de que no es la primera línea
                        card = re.search(r'\b(\d{16}|\d{15})[:|]\d{2}[:|](\d{4}|\d{2})[:|]\d{3}\b', lines[i-1])
                        if card:
                            bot.reply_to(message, ccn_prefixes[index % len(ccn_prefixes)] + ' ' + card.group())
                            index += 1
    elif message.text.lower() == 'listo':
        bot.reply_to(message, 'Todas las tarjetas han sido enviadas.')   

    else:

         pass        
          
@bot.message_handler(func=lambda message: message.forward_from or message.forward_from_chat)
def message_forwarded(message):
    # Intenta eliminar el mensaje reenviado en el chat con el bot.
    try:
        bot.delete_message(message.chat.id, message.message_id)
        print("Mensaje reenviado eliminado.")
    except Exception as e:
        print(f"No se pudo eliminar el mensaje: {e}")

bot.polling()

#Global
@bot.message_handler(func=lambda m: True)
def echo_all(message):
    global index, current_function

    if current_function == 'CVV Scrapper':
        # Tu lógica para 'CVV Scrapper'
        pass  # Reemplaza esto con la lógica actual
    
    elif current_function == 'CCN Charged':
        # Tu lógica para 'CCN Charged'
        pass  # Reemplaza esto con la lógica actual      

bot.polling()
