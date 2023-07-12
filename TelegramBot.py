from telegram import ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
import requests
import threading
import asyncio
import time
import asyncio
from telegram import Bot
import os

TELEGRAM_TOKEN = '6271137920:AAEO313YP07bHHy00nQOXsOhSdkEieT4nhg'
CMC_API_KEY = '92eb5721-3dcb-40e5-805d-3593c696f3d1'
PORT = int(os.environ.get('PORT', '8443'))

bot = Bot(token=TELEGRAM_TOKEN)


def get_eth_price():
    url = 'https://pro-api.coinmarketcap.com/v1/cryptocurrency/quotes/latest'
    headers = {
        'Accepts': 'application/json',
        'X-CMC_PRO_API_KEY': CMC_API_KEY,
    }
    parameters = {
        'symbol': 'ETH'
    }
    response = requests.get(url, headers=headers, params=parameters)
    data = response.json()
    return data['data']['ETH']['quote']['USD']['price']

async def send_message(chat_id, text):
    await bot.send_message(chat_id=chat_id, text=text)

def start(update, context):
    keyboard = [[KeyboardButton("/start_tracking"), KeyboardButton("/stop_tracking"), KeyboardButton("/help")]]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True)
    update.message.reply_text('Welcome to the Bot. Please choose a command:', reply_markup=reply_markup)

def help(update, context):
    update.message.reply_text("Available Commands:\n/"
                             "start\n/help\n/start_tracking\n/stop_tracking")

def start_tracking(update, context):
    global is_tracking
    is_tracking = True
    thread = threading.Thread(target=track_price, args=(update, context))
    thread.start()

import datetime

def track_price(update, context):
    last_price = None
    while is_tracking:
        price = get_eth_price()
        price_rounded = round(price, 2)
        if last_price is not None:
            percent_change = ((price_rounded - last_price) / last_price) * 100
            if abs(percent_change) >= 0.3:
                if last_price > price_rounded:
                    context.bot.send_message(chat_id=update.effective_chat.id, text=f'🟢 - Last price of Ethereum is: ${last_price} ⬆️\n \n🔴 - Current price of Ethereum is: ${price_rounded} ⬇️')
                else:
                    context.bot.send_message(chat_id=update.effective_chat.id, text=f'🔴 - Last price of Ethereum is: ${last_price} ⬇️\n \n🟢 - Current price of Ethereum is: ${price_rounded} ⬆️')
        else:
            last_price = price_rounded
        seconds_until_next_minute = 60 - datetime.datetime.now().second
        time.sleep(seconds_until_next_minute)

def stop_tracking(update, context):
    global is_tracking
    is_tracking = False
    update.message.reply_text("Tracking stopped.")

def unknown(update, context):
    update.message.reply_text("Sorry '%s' is not a valid command" % update.message.text)

def unknown_text(update, context):
    update.message.reply_text("Sorry I can't recognize you, you said '%s'" % update.message.text)

updater = Updater(TELEGRAM_TOKEN, use_context=True)
dispatcher = updater.dispatcher

dispatcher.add_handler(CommandHandler('start', start))
dispatcher.add_handler(CommandHandler('help', help))
dispatcher.add_handler(CommandHandler('start_tracking', start_tracking, pass_args=True))
dispatcher.add_handler(CommandHandler('stop_tracking', stop_tracking))
dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, unknown_text))
dispatcher.add_handler(MessageHandler(Filters.command, unknown))

updater = Updater(TELEGRAM_TOKEN, use_context=True)
dispatcher = updater.dispatcher

dispatcher.add_handler(CommandHandler('start', start))
dispatcher.add_handler(CommandHandler('help', help))
dispatcher.add_handler(CommandHandler('start_tracking', start_tracking, pass_args=True))
dispatcher.add_handler(CommandHandler('stop_tracking', stop_tracking))
dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, unknown_text))
dispatcher.add_handler(MessageHandler(Filters.command, unknown))

# Start the webhook
updater.start_webhook(listen="0.0.0.0",
                      port=PORT,
                      url_path=TELEGRAM_TOKEN,
                      webhook_url='https://your-heroku-app-name.herokuapp.com/' + TELEGRAM_TOKEN)

async def main():
    while True:
        await asyncio.sleep(0.1)

asyncio.run(main())
