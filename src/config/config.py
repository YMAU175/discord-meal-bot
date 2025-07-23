import os
from dotenv import load_dotenv
import pytz

load_dotenv()

# Discord設定
DISCORD_BOT_TOKEN = os.getenv('DISCORD_BOT_TOKEN')
DISCORD_SERVER_ID = int(os.getenv('DISCORD_SERVER_ID', '1393517298358292540'))
MEAL_CHANNEL_ID = int(os.getenv('MEAL_CHANNEL_ID', '1393518102897234040'))
WEEKLY_REPORT_CHANNEL_ID = int(os.getenv('WEEKLY_REPORT_CHANNEL_ID', '1393518129921003520'))
MONTHLY_REPORT_CHANNEL_ID = int(os.getenv('MONTHLY_REPORT_CHANNEL_ID', '1393518170865795192'))

# Google API設定
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
GOOGLE_SHEETS_CREDENTIALS = os.getenv('GOOGLE_SHEETS_CREDENTIALS')
GOOGLE_SHEETS_ID = os.getenv('GOOGLE_SHEETS_ID')

# Geminiモデル設定（無料枠で最適）
# Gemini 2.0 Flash: 最新の高速モデル
GEMINI_MODEL = 'gemini-2.0-flash-exp'

# タイムゾーン設定
TIMEZONE = pytz.timezone(os.getenv('TIMEZONE', 'Asia/Tokyo'))

# ユーザー設定
USER_PROFILE = {
    'birth_date': '1989-12-28',
    'gender': 'male',
    'weight': 65,
    'age': 34
}

# 栄養目標値（34歳男性、体重65kg基準）
NUTRITION_TARGETS = {
    'calories': {'min': 2200, 'max': 2400},
    'carbohydrates': {'min': 280, 'max': 364},  # g
    'protein': {'min': 65, 'max': 80},  # g
    'fat': {'min': 49, 'max': 73}  # g
}

# システム設定
MAX_RETRY_ATTEMPTS = 2
IMAGE_ANALYSIS_TIMEOUT = 30  # seconds
REPORT_GENERATION_TIMEOUT = 10  # seconds

# レポートスケジュール設定
WEEKLY_REPORT_SCHEDULE = {
    'day_of_week': 6,  # 0=Monday, 6=Sunday
    'hour': 23,
    'minute': 0
}

MONTHLY_REPORT_SCHEDULE = {
    'hour': 23,
    'minute': 0
}