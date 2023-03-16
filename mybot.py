import asyncio
import pyrogram
import logging
from video_info1 import get_video_info
from pyrogram.types import InputMediaVideo
from pyrogram import filters, Client
from config import (
    api_id,
    api_hash,
    bot_token
)

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# Create a Pyrogram client object and start the bot.
app = Client('my_bot', api_id, api_hash, bot_token=bot_token)
video_path = '[AUM] Kanojo, Okarishimasu - 01 [1080p].mp4'


@app.on_message(filters.command('upload'))
async def upload_video(client, message):
    # Get the video dimensions and upload the video file to Telegram.
    dimensions = get_video_info(video_path)
    if dimensions:
        width, height, duration = dimensions
        print(width)
        print(height)
        video = InputMediaVideo(
            media=video_path,
            width=width,
            height=height,
            duration=duration,
            supports_streaming=True
        )
        await app.send_video(message.chat.id, video)
    else:
        print('Error getting video dimensions')

# Start the bot.
app.run()

