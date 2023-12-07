from openai import OpenAI
from dotenv import load_dotenv
import os

def get_client() -> OpenAI:
    load_dotenv()
    return OpenAI(api_key= os.getenv('API_KEY'))