#coding:utf-8
import telegram
import logging
import tempfile, requests, subprocess
import pydub
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters

# Enable logging
logging.basicConfig(filename='speech.log',
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

TOKEN = "566437247:AAH1rLQyW2Sb-5sljOBwPYkZbgO2oQSZfC0"

def start(bot, update):
    """Send a message when the command /start is issued."""
    update.message.reply_text('Hi!')


def help(bot, update):
    """Send a message when the command /help is issued."""
    update.message.reply_text('Help!')


def echo(bot, update):
    """Echo the user message."""
    update.message.reply_text(update.message.text)


def error(bot, update, error):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s"caused error"%s"', update, error)


def speech2text(bot, update):
    keys = '78736a862d724cd68845c9da96c81b10'
    chat_id = update.message.chat_id
    bot.getFile(update.message.voice.file_id).download('voice.ogg')
#    lang = 'en-US'
    lang = 'zh-CN'
    file = open('voice.ogg', 'rb')
    print('open voice file')

    audio = pydub.AudioSegment.from_file(file)
    audio = audio.set_frame_rate(16000)
    audio.export('voice.wav', format="wav")
    print('wav exported')
    other_program = './cruzhacks2018/client.py'
    script = ['/home/wydwww/py3/bin/python', other_program, keys, lang, 'simple', 'conversation', './voice.wav']
    print('run script')
    proc = subprocess.Popen(script, stdout=subprocess.PIPE)
    output = proc.stdout.readlines()[-2]
    print(output.decode('UTF-8')[22:])
    update.message.reply_text(output.decode('UTF-8')[22:])
    print('message sent')


def main():
    """Start the bot."""
    # Create the EventHandler and pass it your bot's token.
    updater = Updater(TOKEN)

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # on different commands - answer in Telegram
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", help))

    # on noncommand i.e message - echo the message on Telegram
    dp.add_handler(MessageHandler(Filters.text, echo))

    # voice message
    dp.add_handler(MessageHandler(Filters.voice, speech2text))

    # log all errors
    dp.add_error_handler(error)

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()

