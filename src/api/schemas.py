from pydantic import BaseModel
from datetime import datetime, date
from typing import Optional

class TopProductsResponse(BaseModel):
    product_name: str
    mention_count: int
    channel_count: int

class ChannelActivityResponse(BaseModel):
    channel_name: str
    total_messages: int
    messages_with_media: int
    avg_message_length: float
    first_message_date: Optional[datetime]
    last_message_date: Optional[datetime]
    avg_daily_messages: float

class MessageSearchResponse(BaseModel):
    message_id: int
    channel_name: str
    message_text: str
    date_day: date
    has_media: bool
    detection_count: int

class DetectionResponse(BaseModel):
    detection_id: int
    message_id: int
    channel_name: str
    detected_class: str
    confidence_score: float
    date_day: date