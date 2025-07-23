import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime
import json
from typing import List, Dict, Optional
from src.config.config import GOOGLE_SHEETS_CREDENTIALS, GOOGLE_SHEETS_ID, TIMEZONE
from src.utils.logger import setup_logger

logger = setup_logger()

class SheetsService:
    def __init__(self):
        self.sheet_id = GOOGLE_SHEETS_ID
        self.client = None
        self.sheet = None
        self._initialize_sheets()
    
    def _initialize_sheets(self):
        """Google Sheetsの初期化"""
        try:
            # 認証情報をJSONとして解析
            creds_dict = json.loads(GOOGLE_SHEETS_CREDENTIALS)
            
            # スコープの設定
            scope = [
                'https://spreadsheets.google.com/feeds',
                'https://www.googleapis.com/auth/drive'
            ]
            
            # 認証
            creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
            self.client = gspread.authorize(creds)
            
            # スプレッドシートを開く
            self.sheet = self.client.open_by_key(self.sheet_id)
            
            # ワークシートの初期化
            self._setup_worksheets()
            
            logger.info("Google Sheets接続成功")
            
        except Exception as e:
            logger.error(f"Google Sheets初期化エラー: {e}")
            raise
    
    def _setup_worksheets(self):
        """必要なワークシートを作成"""
        worksheet_names = [ws.title for ws in self.sheet.worksheets()]
        
        # 食事記録シート
        if "食事記録" not in worksheet_names:
            ws = self.sheet.add_worksheet(title="食事記録", rows=1000, cols=20)
            headers = [
                "記録日時", "ユーザーID", "食事内容", "カテゴリ", 
                "推定カロリー", "炭水化物(g)", "タンパク質(g)", "脂質(g)",
                "食物繊維(g)", "ナトリウム(mg)", "健康メモ", "画像URL"
            ]
            ws.append_row(headers)
            logger.info("食事記録シートを作成しました")
    
    async def add_meal_record(self, user_id: str, meal_data: Dict, image_url: str) -> bool:
        """食事記録を追加"""
        try:
            worksheet = self.sheet.worksheet("食事記録")
            
            # 現在時刻（JST）
            now = datetime.now(TIMEZONE)
            
            # 記録データの準備
            row_data = [
                now.strftime("%Y-%m-%d %H:%M:%S"),
                user_id,
                meal_data.get("meal_description", ""),
                meal_data.get("meal_category", "その他"),
                meal_data.get("estimated_calories", 0),
                meal_data.get("nutrients", {}).get("carbohydrates", 0),
                meal_data.get("nutrients", {}).get("protein", 0),
                meal_data.get("nutrients", {}).get("fat", 0),
                meal_data.get("nutrients", {}).get("fiber", 0),
                meal_data.get("nutrients", {}).get("sodium", 0),
                meal_data.get("health_notes", ""),
                image_url
            ]
            
            # データを追加
            worksheet.append_row(row_data)
            logger.info(f"食事記録を追加: {user_id} - {meal_data.get('meal_description', '')}")
            return True
            
        except Exception as e:
            logger.error(f"食事記録追加エラー: {e}")
            return False
    
    async def get_weekly_data(self, user_id: str, start_date: datetime, end_date: datetime) -> List[Dict]:
        """週次データを取得"""
        try:
            worksheet = self.sheet.worksheet("食事記録")
            all_records = worksheet.get_all_records()
            
            # 指定期間のユーザーデータをフィルタリング
            weekly_data = []
            for record in all_records:
                record_date = datetime.strptime(record["記録日時"], "%Y-%m-%d %H:%M:%S")
                record_date = TIMEZONE.localize(record_date)
                
                if (record["ユーザーID"] == user_id and 
                    start_date <= record_date <= end_date):
                    weekly_data.append(record)
            
            return weekly_data
            
        except Exception as e:
            logger.error(f"週次データ取得エラー: {e}")
            return []
    
    async def get_monthly_data(self, user_id: str, year: int, month: int) -> List[Dict]:
        """月次データを取得"""
        try:
            worksheet = self.sheet.worksheet("食事記録")
            all_records = worksheet.get_all_records()
            
            # 指定月のユーザーデータをフィルタリング
            monthly_data = []
            for record in all_records:
                record_date = datetime.strptime(record["記録日時"], "%Y-%m-%d %H:%M:%S")
                
                if (record["ユーザーID"] == user_id and 
                    record_date.year == year and 
                    record_date.month == month):
                    monthly_data.append(record)
            
            return monthly_data
            
        except Exception as e:
            logger.error(f"月次データ取得エラー: {e}")
            return []