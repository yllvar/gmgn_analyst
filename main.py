from fastapi import FastAPI
import httpx
import json
from datetime import datetime

app = FastAPI()

async def get_top_pumping_tokens(limit=50):
    """
    Fetches the top pumping tokens on Solana using the GMGN API.

    Args:
    limit (int): The number of tokens to retrieve (default 50, max 50)

    Returns:
    list: A list of dictionaries containing information about the top pumping tokens
    """
    limit = min(50, max(1, limit))
    url = f"https://gmgn.ai/defi/quotation/v1/rank/sol/pump?limit={limit}&orderby=progress&direction=desc&pump=true"

    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url)
            response.raise_for_status()
            data = response.json()

            if isinstance(data, dict) and 'data' in data:
                if isinstance(data['data'], dict):
                    for key, value in data['data'].items():
                        if isinstance(value, list):
                            return value
                    print("No list found in the 'data' dictionary")
                else:
                    print(f"'data' value is not a dict, it's a {type(data['data'])}")
            else:
                print("Unexpected data format in the API response")
            
            print("Full API Response:")
            print(json.dumps(data, indent=2))
            return []

        except httpx.HTTPStatusError as e:
            print(f"API request failed with status code: {e.response.status_code}")
            return []
        except httpx.RequestError as e:
            print(f"An error occurred while fetching data: {e}")
            return []
        except json.JSONDecodeError as e:
            print(f"Error decoding JSON response: {e}")
            print("Raw response content:")
            print(response.text)
            return []

def format_token_info(token):
    """
    Formats the token information for display.

    Args:
    token (dict): A dictionary containing token information

    Returns:
    str: A formatted string with token details
    """
    created_time = datetime.fromtimestamp(token.get('created_timestamp', 0)).strftime('%Y-%m-%d %H:%M:%S')
    last_trade_time = datetime.fromtimestamp(token.get('last_trade_timestamp', 0)).strftime('%Y-%m-%d %H:%M:%S')
    
    return (f"Symbol: {token.get('symbol', 'N/A')}\n"
            f"Name: {token.get('name', 'N/A')}\n"
            f"Price: ${token.get('price', 'N/A'):.8f}\n"
            f"Market Cap: ${token.get('usd_market_cap', 'N/A'):,.2f}\n"
            f"Created: {created_time}\n"
            f"Last Trade: {last_trade_time}\n"
            f"Progress: {token.get('progress', 'N/A'):.2%}\n"
            f"Holder Count: {token.get('holder_count', 'N/A')}\n"
            f"Volume (1h): ${token.get('volume_1h', 'N/A'):,.2f}\n"
            f"Price Change (5m): {token.get('price_change_percent5m', 'N/A')}%\n"
            f"Website: {token.get('website', 'N/A')}\n"
            f"Twitter: {token.get('twitter', 'N/A')}\n"
            f"Telegram: {token.get('telegram', 'N/A')}\n"
            f"--------------------")

@app.get("/")
async def root():
    return {"message": "Welcome to the Top Pumping Tokens API"}

@app.get("/top-tokens/")
async def get_top_tokens(limit: int = 10):
    top_tokens = await get_top_pumping_tokens(limit)
    if top_tokens:
        formatted_tokens = [format_token_info(token) for token in top_tokens]
        return {"tokens": formatted_tokens}
    else:
        return {"error": "No token data retrieved."}