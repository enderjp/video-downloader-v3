from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, validator
import logging
from scraper_selenium import get_scraper_instance, close_scraper_instance
import atexit

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Facebook Selenium Scraper API",
    description="API para scrapear Facebook usando Selenium (sin login)",
    version="3.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)


class PostURLRequest(BaseModel):
    url: str = Field(..., description="URL completa del post de Facebook")
    
    @validator('url')
    def validate_facebook_url(cls, v):
        if 'facebook.com' not in v.lower():
            raise ValueError('La URL debe ser de Facebook')
        return v


class PageRequest(BaseModel):
    page_url: str = Field(..., description="URL o nombre de la página")
    num_posts: int = Field(default=10, ge=1, le=20, description="Número de posts")


# Cerrar scraper al apagar la aplicación
@app.on_event("shutdown")
def shutdown_event():
    logger.info("🔄 Cerrando scraper...")
    close_scraper_instance()

atexit.register(close_scraper_instance)


@app.get("/")
def root():
    return {
        "status": "online",
        "message": "Facebook Selenium Scraper API",
        "version": "3.0.0",
        "scraper": "Selenium (sin login)",
        "endpoints": {
            "POST /scrape": "Scrapear un post por URL",
            "GET /scrape?url=...": "Scrapear un post (GET)",
            "POST /scrape/images-only": "Solo URLs de imágenes",
            "POST /scrape/page": "Scrapear múltiples posts de una página",
            "GET /scrape/video?url=...": "URL del video (GET)",
            "POST /scrape/video": "URL del video (POST)",
            "GET /health": "Health check"
        }
    }


@app.get("/health")
def health():
    return {"status": "healthy", "version": "3.0.0", "scraper": "Selenium"}


@app.post("/scrape")
def scrape_post(request: PostURLRequest):
    try:
        logger.info(f"📬 POST /scrape - URL: {request.url}")
        scraper = get_scraper_instance(headless=True)
        result = scraper.scrape_post_by_url(request.url)
        
        if not result['success']:
            raise HTTPException(
                status_code=404,
                detail=result.get('error', 'Post no encontrado')
            )
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/scrape")
def scrape_get(url: str = Query(..., description="URL del post de Facebook")):
    try:
        logger.info(f"📬 GET /scrape - URL: {url}")
        
        if 'facebook.com' not in url.lower():
            raise HTTPException(status_code=400, detail="Debe ser URL de Facebook")
        
        scraper = get_scraper_instance(headless=True)
        result = scraper.scrape_post_by_url(url)
        
        if not result['success']:
            raise HTTPException(status_code=404, detail=result.get('error'))
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/scrape/images-only")
def scrape_images_only(request: PostURLRequest):
    try:
        scraper = get_scraper_instance(headless=True)
        result = scraper.scrape_post_by_url(request.url)
        
        if not result['success']:
            raise HTTPException(status_code=404, detail=result.get('error'))
        
        image_urls = [img['url'] for img in result['post']['images']] if result['post'] else []
        
        return {
            'success': True,
            'url': request.url,
            'total_images': len(image_urls),
            'images': image_urls
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/scrape/page")
def scrape_page(request: PageRequest):
    try:
        logger.info(f"📄 Scrapeando página: {request.page_url}")
        scraper = get_scraper_instance(headless=True)
        result = scraper.scrape_page_posts(request.page_url, request.num_posts)
        
        if not result['success']:
            raise HTTPException(status_code=500, detail=result.get('error'))
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/scrape/video")
def scrape_video_get(url: str = Query(..., description="URL del post de Facebook")):
    try:
        logger.info(f"📬 GET /scrape/video - URL: {url}")

        if 'facebook.com' not in url.lower():
            raise HTTPException(status_code=400, detail="Debe ser URL de Facebook")

        scraper = get_scraper_instance(headless=True)
        result = scraper.scrape_video_by_url(url)

        if not result.get('success'):
            raise HTTPException(status_code=404, detail=result.get('error'))

        return result

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/scrape/video")
def scrape_video_post(request: PostURLRequest):
    try:
        logger.info(f"📬 POST /scrape/video - URL: {request.url}")
        scraper = get_scraper_instance(headless=True)
        result = scraper.scrape_video_by_url(request.url)

        if not result.get('success'):
            raise HTTPException(status_code=404, detail=result.get('error', 'Video no encontrado'))

        return result

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
