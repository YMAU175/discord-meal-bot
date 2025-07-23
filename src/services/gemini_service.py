import google.generativeai as genai
from typing import Dict, Optional, Tuple
import asyncio
import aiohttp
from src.config.config import GEMINI_API_KEY, GEMINI_MODEL, MAX_RETRY_ATTEMPTS
from src.utils.logger import setup_logger
import json

logger = setup_logger()

# Gemini APIの設定
genai.configure(api_key=GEMINI_API_KEY)

class GeminiService:
    def __init__(self):
        self.model = genai.GenerativeModel(GEMINI_MODEL)
        self.prompt_template = """
        この画像の食事を分析してください。以下のJSON形式で回答してください：
        
        {
            "meal_description": "食事の詳細な説明",
            "estimated_calories": カロリー推定値（数値のみ）,
            "nutrients": {
                "carbohydrates": 炭水化物のグラム数（数値のみ）,
                "protein": タンパク質のグラム数（数値のみ）,
                "fat": 脂質のグラム数（数値のみ）,
                "fiber": 食物繊維のグラム数（数値のみ）,
                "sodium": ナトリウムのミリグラム数（数値のみ）
            },
            "meal_category": "朝食/昼食/夕食/間食/その他",
            "health_notes": "健康面でのアドバイスや注意点"
        }
        
        注意：
        - 数値は推定値で構いません
        - 画像が食事でない場合は、{"error": "食事の画像ではありません"}と返してください
        - 必ずJSON形式で返してください
        """
    
    async def analyze_meal_image(self, image_url: str) -> Tuple[bool, Optional[Dict]]:
        """
        食事画像を分析して栄養情報を抽出
        
        Args:
            image_url: 分析する画像のURL
            
        Returns:
            (成功フラグ, 分析結果または None)
        """
        for attempt in range(MAX_RETRY_ATTEMPTS + 1):
            try:
                # 画像をダウンロード
                async with aiohttp.ClientSession() as session:
                    async with session.get(image_url) as response:
                        if response.status != 200:
                            logger.error(f"画像ダウンロード失敗: {response.status}")
                            return False, None
                        
                        image_data = await response.read()
                
                # Geminiで分析（同期的な呼び出しを非同期でラップ）
                response = await asyncio.to_thread(
                    self._analyze_image_sync,
                    image_data
                )
                
                # JSON形式で結果をパース
                try:
                    # レスポンスからJSON部分を抽出
                    text = response.text.strip()
                    # マークダウンのコードブロックを除去
                    if text.startswith('```json'):
                        text = text[7:]
                    if text.startswith('```'):
                        text = text[3:]
                    if text.endswith('```'):
                        text = text[:-3]
                    
                    result = json.loads(text.strip())
                    
                    # エラーチェック
                    if "error" in result:
                        logger.warning(f"分析エラー: {result['error']}")
                        return False, {"error": result['error']}
                    
                    # 必須フィールドの確認
                    required_fields = ["meal_description", "estimated_calories", "nutrients"]
                    if all(field in result for field in required_fields):
                        logger.info("画像分析成功")
                        return True, result
                    else:
                        logger.error("必須フィールドが不足しています")
                        return False, None
                        
                except json.JSONDecodeError as e:
                    logger.error(f"JSON解析エラー: {e}")
                    logger.error(f"レスポンステキスト: {response.text}")
                    if attempt < MAX_RETRY_ATTEMPTS:
                        await asyncio.sleep(2 ** attempt)  # 指数バックオフ
                        continue
                    return False, None
                    
            except Exception as e:
                logger.error(f"画像分析エラー (試行 {attempt + 1}/{MAX_RETRY_ATTEMPTS + 1}): {e}")
                if attempt < MAX_RETRY_ATTEMPTS:
                    await asyncio.sleep(2 ** attempt)  # 指数バックオフ
                else:
                    return False, None
        
        return False, None
    
    def _analyze_image_sync(self, image_data: bytes):
        """同期的な画像分析（内部使用）"""
        # 画像をPIL形式に変換
        from PIL import Image
        import io
        
        image = Image.open(io.BytesIO(image_data))
        
        # Geminiで分析
        response = self.model.generate_content([self.prompt_template, image])
        return response