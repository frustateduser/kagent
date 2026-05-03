import os
import httpx
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

def get_api_key() -> str:
    """Get the GNews API key from environment variables"""
    api_key = os.getenv("GNEWS_API_KEY")
    if not api_key:
        raise ValueError(
            "GNEWS_API_KEY environment variable is required. "
            "Get your free API key from https://gnews.io/"
        )
    return api_key

async def make_news_request(endpoint: str, params: dict) -> dict:
    api = get_api_key()
    # Add API key to parameters
    params["apikey"] = api
    
    # Base URL for GNews API
    base_url = "https://gnews.io/api/v4"
    url = f"{base_url}/{endpoint}"
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url, params=params)
            
            if response.status_code == 200:
                data = response.json()
                return data
            else:
                error_msg = f"GNews API error: {response.status_code}"
                try:
                    error_data = response.json()
                    if "errors" in error_data:
                        error_msg += f" - {error_data['errors']}"
                except:
                    error_msg += f" - {response.text}"
                
                raise Exception(error_msg)
                
    except httpx.RequestError as e:
        error_msg = f"Network error connecting to GNews API: {str(e)}"
        raise Exception(error_msg)