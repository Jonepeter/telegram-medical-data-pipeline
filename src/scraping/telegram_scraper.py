import asyncio
import json
import os
from datetime import datetime
from telethon import TelegramClient
from telethon.tl.types import MessageMediaPhoto, MessageMediaDocument
from src.config import TELEGRAM_API_ID, TELEGRAM_API_HASH, TELEGRAM_PHONE, TELEGRAM_CHANNELS
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TelegramScraper:
    def __init__(self):
        self.client = TelegramClient('session', TELEGRAM_API_ID, TELEGRAM_API_HASH)
    
    async def scrape_channel(self, channel_name, limit=100):
        """Scrape messages from a Telegram channel"""
        messages_data = []
        
        try:
            await self.client.start(phone=TELEGRAM_PHONE)
            entity = await self.client.get_entity(channel_name)
            
            async for message in self.client.iter_messages(entity, limit=limit):
                message_data = {
                    'message_id': message.id,
                    'channel_name': channel_name,
                    'message_text': message.text or '',
                    'message_date': message.date.isoformat() if message.date else None,
                    'has_media': message.media is not None,
                    'media_type': self._get_media_type(message.media),
                    'scraped_at': datetime.now().isoformat(),
                    'raw_data': {
                        'views': getattr(message, 'views', 0),
                        'forwards': getattr(message, 'forwards', 0),
                        'replies': getattr(message.replies, 'replies', 0) if message.replies else 0
                    }
                }
                
                # Download media if present
                if message.media and isinstance(message.media, (MessageMediaPhoto, MessageMediaDocument)):
                    await self._download_media(message, channel_name)
                
                messages_data.append(message_data)
                
        except Exception as e:
            logger.error(f"Error scraping channel {channel_name}: {e}")
        
        return messages_data
    
    def _get_media_type(self, media):
        """Determine media type"""
        if not media:
            return None
        if isinstance(media, MessageMediaPhoto):
            return 'photo'
        elif isinstance(media, MessageMediaDocument):
            return 'document'
        return 'other'
    
    async def _download_media(self, message, channel_name):
        """Download media files"""
        try:
            date_str = message.date.strftime('%Y-%m-%d') if message.date else 'unknown'
            media_dir = f"data/raw/media/{channel_name}/{date_str}"
            os.makedirs(media_dir, exist_ok=True)
            
            # Get proper extension from media
            if isinstance(message.media, MessageMediaPhoto):
                ext = '.jpg'
            elif hasattr(message.media.document, 'mime_type'):
                mime_type = message.media.document.mime_type
                ext = '.jpg' if 'image/jpeg' in mime_type else '.png' if 'image/png' in mime_type else '.mp4' if 'video' in mime_type else ''
            else:
                ext = ''
            
            filename = f"{message.id}_{int(message.date.timestamp())}{ext}"
            await self.client.download_media(message, file=os.path.join(media_dir, filename))
            
        except Exception as e:
            logger.error(f"Error downloading media: {e}")
    
    def save_to_json(self, data, channel_name):
        """Save scraped data to JSON file"""
        date_str = datetime.now().strftime('%Y-%m-%d')
        output_dir = f"data/raw/telegram_messages/{date_str}"
        os.makedirs(output_dir, exist_ok=True)
        
        filename = f"{output_dir}/{channel_name}.json"
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        logger.info(f"Saved {len(data)} messages to {filename}")

async def main():
    scraper = TelegramScraper()
    
    for channel in TELEGRAM_CHANNELS:
        logger.info(f"Scraping channel: {channel}")
        messages = await scraper.scrape_channel(channel, limit=100)
        scraper.save_to_json(messages, channel)
    
    await scraper.client.disconnect()

if __name__ == "__main__":
    asyncio.run(main())