import telegram
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters

bot = telegram.Bot(token='6273405056:AAEYDEwJgYAvLU9nkq7U6WUW3l1GJ66WnDA')

# Define a function to handle the /link command
def link_command_handler(update, context):
    # Get the chat ID from the update object
    chat_id = update.message.chat_id
    
    # Send a message to the user explaining how to use the command
    context.bot.send_message(chat_id=chat_id, text="Sending the video, please wait")
    
    # Replace PATH_TO_VIDEO_FILE with the path to the video file on your server
    video = open('[Nekomoe kissaten][Nijiyon Animation][10][1080p][JPTC].mp4', 'rb')

    # Replace USER_ID with the ID of the user you want to send the video to
    bot.send_video(chat_id=chat_id, video=video, supports_streaming=True, timeout=1000)


# Create an Updater object and pass your bot token to it
updater = Updater("6273405056:AAEYDEwJgYAvLU9nkq7U6WUW3l1GJ66WnDA")

# Get the Dispatcher object from the Updater object
dispatcher = updater.dispatcher

# Add a CommandHandler to the Dispatcher object to handle the /link command
dispatcher.add_handler(CommandHandler("lee", link_command_handler))

# Start the bot
updater.start_polling()

# Run the bot until you press Ctrl-C
updater.idle()

