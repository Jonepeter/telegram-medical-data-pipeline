from fastapi import FastAPI, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import text
from src.database import get_db
from src.api.schemas import TopProductsResponse, ChannelActivityResponse, MessageSearchResponse
from typing import List, Optional
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Telegram Analytics API",
    description="API for analyzing Ethiopian medical business data from Telegram",
    version="1.0.0"
)

@app.get("/")
async def root():
    return {"message": "Telegram Analytics API", "version": "1.0.0"}

@app.get("/api/reports/top-products", response_model=List[TopProductsResponse])
async def get_top_products(
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """Get the most frequently mentioned medical products"""
    try:
        query = text("""
            SELECT 
                LOWER(TRIM(word)) as product_name,
                COUNT(*) as mention_count,
                COUNT(DISTINCT channel_id) as channel_count
            FROM (
                SELECT 
                    UNNEST(STRING_TO_ARRAY(LOWER(message_text), ' ')) as word,
                    channel_id
                FROM marts.fct_messages 
                WHERE message_text IS NOT NULL
            ) words
            WHERE LENGTH(word) > 3 
                AND word ~ '^[a-z]+$'
                AND word IN ('paracetamol', 'aspirin', 'ibuprofen', 'amoxicillin', 'vitamin', 'medicine', 'drug', 'tablet', 'capsule', 'syrup')
            GROUP BY LOWER(TRIM(word))
            ORDER BY mention_count DESC
            LIMIT :limit
        """)
        
        result = db.execute(query, {"limit": limit})
        return [
            TopProductsResponse(
                product_name=row.product_name,
                mention_count=row.mention_count,
                channel_count=row.channel_count
            )
            for row in result
        ]
    except Exception as e:
        logger.error(f"Error getting top products: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/api/channels/{channel_name}/activity", response_model=ChannelActivityResponse)
async def get_channel_activity(
    channel_name: str,
    db: Session = Depends(get_db)
):
    """Get posting activity for a specific channel"""
    try:
        query = text("""
            SELECT 
                c.channel_name,
                c.total_messages,
                c.messages_with_media,
                c.avg_message_length,
                c.first_message_date,
                c.last_message_date,
                COALESCE(daily_stats.avg_daily_messages, 0) as avg_daily_messages
            FROM marts.dim_channels c
            LEFT JOIN (
                SELECT 
                    channel_id,
                    AVG(daily_count) as avg_daily_messages
                FROM (
                    SELECT 
                        channel_id,
                        date_day,
                        COUNT(*) as daily_count
                    FROM marts.fct_messages
                    GROUP BY channel_id, date_day
                ) daily
                GROUP BY channel_id
            ) daily_stats ON c.channel_id = daily_stats.channel_id
            WHERE LOWER(c.channel_name) = LOWER(:channel_name)
        """)
        
        result = db.execute(query, {"channel_name": channel_name}).first()
        
        if not result:
            raise HTTPException(status_code=404, detail="Channel not found")
        
        return ChannelActivityResponse(
            channel_name=result.channel_name,
            total_messages=result.total_messages,
            messages_with_media=result.messages_with_media,
            avg_message_length=result.avg_message_length,
            first_message_date=result.first_message_date,
            last_message_date=result.last_message_date,
            avg_daily_messages=result.avg_daily_messages
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting channel activity: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/api/search/messages", response_model=List[MessageSearchResponse])
async def search_messages(
    query: str = Query(..., min_length=1),
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db)
):
    """Search for messages containing specific keywords"""
    try:
        sql_query = text("""
            SELECT 
                m.message_id,
                c.channel_name,
                m.message_text,
                m.date_day,
                m.has_media,
                m.detection_count
            FROM marts.fct_messages m
            JOIN marts.dim_channels c ON m.channel_id = c.channel_id
            WHERE LOWER(m.message_text) LIKE LOWER(:search_query)
            ORDER BY m.date_day DESC
            LIMIT :limit
        """)
        
        result = db.execute(sql_query, {
            "search_query": f"%{query}%",
            "limit": limit
        })
        
        return [
            MessageSearchResponse(
                message_id=row.message_id,
                channel_name=row.channel_name,
                message_text=row.message_text,
                date_day=row.date_day,
                has_media=row.has_media,
                detection_count=row.detection_count
            )
            for row in result
        ]
    except Exception as e:
        logger.error(f"Error searching messages: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/api/stats/overview")
async def get_overview_stats(db: Session = Depends(get_db)):
    """Get overview statistics"""
    try:
        query = text("""
            SELECT 
                COUNT(DISTINCT c.channel_name) as total_channels,
                COUNT(m.message_id) as total_messages,
                COUNT(CASE WHEN m.has_media THEN 1 END) as messages_with_media,
                COUNT(DISTINCT d.detection_id) as total_detections
            FROM marts.fct_messages m
            JOIN marts.dim_channels c ON m.channel_id = c.channel_id
            LEFT JOIN marts.fct_image_detections d ON m.message_id = d.message_id
        """)
        
        result = db.execute(query).first()
        
        return {
            "total_channels": result.total_channels,
            "total_messages": result.total_messages,
            "messages_with_media": result.messages_with_media,
            "total_detections": result.total_detections
        }
    except Exception as e:
        logger.error(f"Error getting overview stats: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)