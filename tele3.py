import libtorrent as lt
import time
import requests
import os
import telegram
import speedtest
import subprocess
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters

# Replace YOUR_API_TOKEN with your actual Telegram Bot API token
TOKEN = '6273405056:AAEYDEwJgYAvLU9nkq7U6WUW3l1GJ66WnDA'
bot = telegram.Bot(token=TOKEN)

def delete_files(files):
    for f in files:
        os.remove(f)

def run_speed_test(download=True, upload=True, ping=True):
    st = speedtest.Speedtest()
    st.get_best_server()
    results = ""

    if download:
        download_speed = st.download() / 1_000_000
        results += f"Download speed: {download_speed:.2f} Mbps\n"

    if upload:
        upload_speed = st.upload() / 1_000_000
        results += f"Upload speed: {upload_speed:.2f} Mbps\n"

    if ping:
        ping_time = subprocess.Popen(['ping', '-c', '1', 'google.com'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        out, error = ping_time.communicate()
        ping_time = out.decode().split('\n')[1].split('time=')[1].split()[0]
        results += f"Ping time: {ping_time} ms\n"

    return results.strip()

def start(update, context):
    chat_id = update.effective_chat.id
    message = "Hello! I can check the speed test of this server. Just send /speedtest to test all or /ping to test the ping only and /leech to download torrent"
    context.bot.send_message(chat_id=chat_id, text=message)

def speedtest_command(update, context):
    chat_id = update.effective_chat.id
    message = run_speed_test()
    context.bot.send_message(chat_id=chat_id, text=message)

def ping_command(update, context):
    chat_id = update.effective_chat.id
    message = run_speed_test(download=False, upload=False, ping=True)
    context.bot.send_message(chat_id=chat_id, text=message)
    
# Define a function to handle the /link command
def link_command_handler(update, context):
    # Get the chat ID from the update object
    chat_id = update.message.chat_id
    
    # Send a message to the user explaining how to use the command
    context.bot.send_message(chat_id=chat_id, text="Please send a direct download link to torrent file")

    # Add a MessageHandler to the Dispatcher object to handle links
    context.dispatcher.add_handler(MessageHandler(Filters.text, link_handler))

# Define a function to handle messages containing links
def link_handler(update, context):
    # Get the chat ID and message text from the update object
    chat_id = update.message.chat_id
    text = update.message.text
    
    # Check if the message contains a link
    if "http" in text:
        # Send the link back to the user
        context.bot.send_message(chat_id=chat_id, text=text)
        try:
            if not os.path.exists('temp'):
                os.makedirs('temp')

            # Send a GET request to the link to download the torrent file
            response = requests.get(text)

            # Extract the filename from the link
            filename = os.path.basename(text)
            input_file_path = os.path.join('temp', filename)

            # Save the response content to a file with the same filename as the link
            with open(input_file_path, "wb") as f:
                f.write(response.content)

            # Load the torrent file
            with open(input_file_path, 'rb') as f:
                torrent_data = f.read()

            # Create a torrent info object
            torrent_info = lt.torrent_info(torrent_data)

            # Create a magnet link from the torrent info object
            magnet_link = lt.make_magnet_uri(torrent_info)

            # Delete torrent file
            os.remove(input_file_path)

            params = {
                'save_path': 'temp',
                'storage_mode': lt.storage_mode_t(2),
            }

            handle = lt.add_magnet_uri(ses, magnet_link, params)
            ses.start_dht()

            context.bot.send_message(chat_id=update.effective_chat.id, text="Downloading your torrent file...")

            while (not handle.has_metadata()):
                time.sleep(1)

            while (handle.status().state != lt.torrent_status.seeding):
                time.sleep(3)

            context.bot.send_message(chat_id=update.effective_chat.id, text="Torrent Downloaded")
            
            # Once the torrent is fully downloaded, send the file back to the user
            #with open(handle.name(), 'rb') as f:
                #context.bot.send_document(chat_id=update.effective_chat.id, document=f)

            #context.bot.send_video(chat_id=update.effective_chat.id, video=open('temp/' + handle.name(), 'rb'), supports_streaming=True)
            time.sleep(3)
            video = open('temp/' + handle.name(), 'rb')
            bot.send_video(chat_id=USER_ID, video=video, supports_streaming=True, timeout=1000, multipart=True)
            
            ses.pause()
            ses.remove_torrent(handle)

            files = [os.path.join('temp', f) for f in os.listdir('temp')]
            delete_files(files)

        except Exception as e:
            context.bot.send_message(chat_id=update.effective_chat.id, text="An error occurred while downloading your file.")
            files = [os.path.join('temp', f) for f in os.listdir('temp')]
            delete_files(files)
            context.bot.send_message(chat_id=update.effective_chat.id, text="Download file has been deleted")

    else:
        # Send an error message to the user
        context.bot.send_message(chat_id=chat_id, text="Invalid link!, Please send a valid link.")

# Start the libtorrent session
ses = lt.session()
ses.listen_on(6881, 6891)

if __name__ == '__main__':

    # Replace YOUR_API_TOKEN with your actual Telegram Bot API token
    updater = Updater(token=TOKEN, use_context=True)

    dispatcher = updater.dispatcher

    start_handler = CommandHandler('start', start)
    speedtest_handler = CommandHandler('speedtest', speedtest_command)
    ping_handler = CommandHandler('ping', ping_command)

    dispatcher.add_handler(start_handler)
    dispatcher.add_handler(speedtest_handler)
    dispatcher.add_handler(ping_handler)
    dispatcher.add_handler(CommandHandler("leech", link_command_handler))

    updater.start_polling()
    updater.idle()

