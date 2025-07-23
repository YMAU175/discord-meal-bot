from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from datetime import datetime, timedelta
import discord
from src.config.config import (
    WEEKLY_REPORT_SCHEDULE,
    MONTHLY_REPORT_SCHEDULE,
    WEEKLY_REPORT_CHANNEL_ID,
    MONTHLY_REPORT_CHANNEL_ID,
    TIMEZONE
)
from src.services.sheets_service import SheetsService
from src.services.report_service import ReportService
from src.utils.logger import setup_logger
import calendar

logger = setup_logger()

class ReportScheduler:
    def __init__(self, bot):
        self.bot = bot
        self.scheduler = AsyncIOScheduler(timezone=TIMEZONE)
        self.sheets_service = SheetsService()
        self.report_service = ReportService()
        self.setup_jobs()
    
    def setup_jobs(self):
        """定期実行ジョブの設定"""
        # 週次レポート（毎週日曜日23時）
        weekly_trigger = CronTrigger(
            day_of_week=WEEKLY_REPORT_SCHEDULE['day_of_week'],
            hour=WEEKLY_REPORT_SCHEDULE['hour'],
            minute=WEEKLY_REPORT_SCHEDULE['minute'],
            timezone=TIMEZONE
        )
        self.scheduler.add_job(
            self.generate_weekly_report,
            trigger=weekly_trigger,
            id='weekly_report'
        )
        
        # 月次レポート（毎月最終日23時）
        self.scheduler.add_job(
            self.generate_monthly_report,
            trigger=CronTrigger(
                day='last',
                hour=MONTHLY_REPORT_SCHEDULE['hour'],
                minute=MONTHLY_REPORT_SCHEDULE['minute'],
                timezone=TIMEZONE
            ),
            id='monthly_report'
        )
        
        logger.info("レポートスケジューラーを設定しました")
    
    def start(self):
        """スケジューラーを開始"""
        self.scheduler.start()
        logger.info("レポートスケジューラーを開始しました")
    
    def stop(self):
        """スケジューラーを停止"""
        self.scheduler.shutdown()
        logger.info("レポートスケジューラーを停止しました")
    
    async def generate_weekly_report(self):
        """週次レポートを生成"""
        try:
            logger.info("週次レポート生成開始")
            
            # レポートチャンネルを取得
            channel = self.bot.get_channel(WEEKLY_REPORT_CHANNEL_ID)
            if not channel:
                logger.error(f"週次レポートチャンネルが見つかりません: {WEEKLY_REPORT_CHANNEL_ID}")
                return
            
            # 期間計算（先週の月曜日から日曜日）
            today = datetime.now(TIMEZONE)
            start_date = today - timedelta(days=today.weekday() + 7)
            end_date = start_date + timedelta(days=6)
            start_date = start_date.replace(hour=0, minute=0, second=0, microsecond=0)
            end_date = end_date.replace(hour=23, minute=59, second=59, microsecond=999999)
            
            # データ取得（ハードコーディングされたユーザーID）
            # TODO: 将来的には複数ユーザー対応
            user_id = "878488075196584018"  # あなたのDiscordユーザーID
            week_data = await self.sheets_service.get_weekly_data(
                user_id,
                start_date,
                end_date
            )
            
            if not week_data:
                await channel.send(
                    "📊 **週次レポート**\n"
                    f"期間: {start_date.strftime('%Y/%m/%d')} - {end_date.strftime('%Y/%m/%d')}\n"
                    "今週は記録がありませんでした。来週は食事記録を頑張りましょう！"
                )
                return
            
            # レポート生成
            # ユーザー名取得
            user = self.bot.get_user(int(user_id))
            user_name = user.display_name if user else "ユーザー"
            
            embed = self.report_service.create_weekly_report_embed(
                user_name,
                week_data,
                start_date,
                end_date
            )
            
            await channel.send(embed=embed)
            logger.info("週次レポート送信完了")
            
        except Exception as e:
            logger.error(f"週次レポート生成エラー: {e}")
            if channel:
                await channel.send("⚠️ 週次レポート生成中にエラーが発生しました。")
    
    async def generate_monthly_report(self):
        """月次レポートを生成"""
        try:
            logger.info("月次レポート生成開始")
            
            # レポートチャンネルを取得
            channel = self.bot.get_channel(MONTHLY_REPORT_CHANNEL_ID)
            if not channel:
                logger.error(f"月次レポートチャンネルが見つかりません: {MONTHLY_REPORT_CHANNEL_ID}")
                return
            
            # 今月のデータを取得
            today = datetime.now(TIMEZONE)
            year = today.year
            month = today.month
            
            # データ取得
            user_id = "878488075196584018"  # あなたのDiscordユーザーID
            month_data = await self.sheets_service.get_monthly_data(
                user_id,
                year,
                month
            )
            
            if not month_data:
                await channel.send(
                    "📊 **月次レポート**\n"
                    f"{year}年{month}月\n"
                    "今月は記録がありませんでした。来月は食事記録を頑張りましょう！"
                )
                return
            
            # レポート生成
            user = self.bot.get_user(int(user_id))
            user_name = user.display_name if user else "ユーザー"
            
            embed = self.report_service.create_monthly_report_embed(
                user_name,
                month_data,
                year,
                month
            )
            
            await channel.send(embed=embed)
            logger.info("月次レポート送信完了")
            
        except Exception as e:
            logger.error(f"月次レポート生成エラー: {e}")
            if channel:
                await channel.send("⚠️ 月次レポート生成中にエラーが発生しました。")
    
    async def force_weekly_report(self, ctx):
        """手動で週次レポートを生成（コマンド用）"""
        await ctx.send("週次レポートを生成中...")
        await self.generate_weekly_report()
    
    async def force_monthly_report(self, ctx):
        """手動で月次レポートを生成（コマンド用）"""
        await ctx.send("月次レポートを生成中...")
        await self.generate_monthly_report()