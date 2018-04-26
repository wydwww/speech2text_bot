import telegram
import logging
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from telegram import ChatAction
from tinytag import TinyTag
from google.cloud import speech
from google.cloud import storage
from google.cloud.speech import enums
from google.cloud.speech import types
import os
import io

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
    chat_id = update.message.chat_id
    bot.getFile(update.message.voice.file_id).download('voice.ogg')
#    lang = 'en-US'
    lang = 'zh-CN'
    tag = TinyTag.get('voice.ogg')
    length = tag.duration
    speech_client = speech.SpeechClient()

    to_gs = length > 58

    if to_gs:
        storage_client = storage.Client()

        bucket = storage_client.get_bucket(BUCKET_NAME)
        blob = bucket.blob('voice.ogg')
        blob.upload_from_filename('voice.ogg')
        audio = types.RecognitionAudio(uri='gs://' + BUCKET_NAME + '/voice.ogg')
    else:
        with io.open('voice.ogg', 'rb') as audio_file:
            content = audio_file.read()
            audio = types.RecognitionAudio(content=content)

    config = types.RecognitionConfig(
        encoding=enums.RecognitionConfig.AudioEncoding.OGG_OPUS,
        sample_rate_hertz=16000,
        language_code=lang)
    bot.send_chat_action(chat_id=chat_id, action=ChatAction.TYPING)

    if to_gs:
        response = speech_client.long_running_recognize(config, audio).result(timeout=500)
    else:
        response = speech_client.recognize(config, audio)
    for result in response.results:
        bot.send_message(update.message.chat_id, result.alternatives[0].transcript)

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

