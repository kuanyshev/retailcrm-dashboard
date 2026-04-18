import os
from dotenv import load_dotenv

load_dotenv()

RETAILCRM_URL = os.getenv("RETAILCRM_URL", "https://kuanyshevsu.retailcrm.ru")
RETAILCRM_API_KEY = os.getenv("RETAILCRM_API_KEY", "kDN39P8yo3c2JsN29elx63aKrGD6SmIR")

SUPABASE_URL = os.getenv("SUPABASE_URL", "https://fzhindouhwrbrlnpbbbi.supabase.co")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImZ6aGluZG91aHdyYnJsbnBiYmJpIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzY0MjMxMjksImV4cCI6MjA5MTk5OTEyOX0.9HiwDM8mriOcMQYz0l31gL6zhsTLQe_1fo7A7aJVQtk")

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "8700239511:AAE8gLJ3WcJOxiKt8n8AoZzwfWVHv3Xm7po")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "1236165411")