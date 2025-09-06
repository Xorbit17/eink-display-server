from openai import OpenAI
from dashboard.services.app_settings import settings

key = settings().openai_key

openai_client = OpenAI(api_key=key) if key else None
