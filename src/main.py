# Python 3.13対応
import src

import discord
from discord.ext import commands
from src.config.config import DISCORD_BOT_TOKEN, MEAL_CHANNEL_ID
from src.utils.logger import setup_logger
from src.services.gemini_service import GeminiService
from src.services.sheets_service import SheetsService
from src.scheduler import ReportScheduler

# ロガーの設定
logger = setup_logger()

# サービスの初期化
gemini_service = GeminiService()
sheets_service = SheetsService()

# Intentsの設定
intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True

# Botの初期化
bot = commands.Bot(command_prefix='!', intents=intents)

# スケジューラーの初期化（Bot初期化後）
report_scheduler = None

@bot.event
async def on_ready():
    """Bot起動時の処理"""
    global report_scheduler
    logger.info(f'{bot.user} として起動しました')
    logger.info(f'サーバー数: {len(bot.guilds)}')
    
    # レポートスケジューラー開始
    report_scheduler = ReportScheduler(bot)
    report_scheduler.start()
    
@bot.event
async def on_message(message):
    """メッセージ受信時の処理"""
    # Bot自身のメッセージは無視
    if message.author == bot.user:
        return
    
    # 食事写真チャンネルでの処理
    if message.channel.id == MEAL_CHANNEL_ID:
        # 画像が添付されているかチェック
        if message.attachments:
            for attachment in message.attachments:
                if any(attachment.filename.lower().endswith(ext) for ext in ['.png', '.jpg', '.jpeg', '.gif', '.webp']):
                    logger.info(f"画像を受信しました: {attachment.filename} from {message.author}")
                    
                    # 処理中を示すリアクション
                    await message.add_reaction('👀')
                    
                    try:
                        # 画像URLを取得
                        image_url = attachment.url
                        
                        # Geminiで画像分析
                        analysis_msg = await message.channel.send(f"{message.author.mention} 画像を分析中です...")
                        success, result = await gemini_service.analyze_meal_image(image_url)
                        
                        if success and result:
                            # エラーチェック
                            if "error" in result:
                                await analysis_msg.edit(content=f"{message.author.mention} {result['error']}")
                                await message.add_reaction('❌')
                                continue
                            
                            # スプレッドシートに記録
                            sheet_success = await sheets_service.add_meal_record(
                                str(message.author.id),
                                result,
                                image_url
                            )
                            
                            if sheet_success:
                                # 成功メッセージ
                                embed = discord.Embed(
                                    title="食事分析完了",
                                    description=result.get("meal_description", ""),
                                    color=discord.Color.green()
                                )
                                embed.add_field(
                                    name="推定カロリー",
                                    value=f"{result.get('estimated_calories', 0)} kcal",
                                    inline=True
                                )
                                
                                nutrients = result.get("nutrients", {})
                                embed.add_field(
                                    name="栄養素",
                                    value=f"炭水化物: {nutrients.get('carbohydrates', 0)}g\n"
                                          f"タンパク質: {nutrients.get('protein', 0)}g\n"
                                          f"脂質: {nutrients.get('fat', 0)}g",
                                    inline=True
                                )
                                
                                if result.get("health_notes"):
                                    embed.add_field(
                                        name="健康アドバイス",
                                        value=result.get("health_notes"),
                                        inline=False
                                    )
                                
                                await analysis_msg.edit(content=f"{message.author.mention}", embed=embed)
                                await message.add_reaction('✅')
                            else:
                                await analysis_msg.edit(content=f"{message.author.mention} 記録の保存に失敗しました。")
                                await message.add_reaction('⚠️')
                        else:
                            await analysis_msg.edit(content=f"{message.author.mention} 画像の分析に失敗しました。もう一度お試しください。")
                            await message.add_reaction('❌')
                            
                    except Exception as e:
                        logger.error(f"画像処理エラー: {e}")
                        await message.channel.send(f"{message.author.mention} エラーが発生しました。")
                        await message.add_reaction('❌')
    
    # コマンド処理を継続
    await bot.process_commands(message)

@bot.command(name='ping')
async def ping(ctx):
    """動作確認用コマンド"""
    await ctx.send('Pong!')

@bot.command(name='status')
async def status(ctx):
    """ステータス確認コマンド"""
    embed = discord.Embed(
        title="Discord食事管理ボット ステータス",
        color=discord.Color.green()
    )
    embed.add_field(name="稼働状況", value="正常", inline=True)
    embed.add_field(name="サーバー数", value=len(bot.guilds), inline=True)
    embed.add_field(name="レイテンシ", value=f"{round(bot.latency * 1000)}ms", inline=True)
    await ctx.send(embed=embed)

@bot.command(name='weekly')
async def force_weekly_report(ctx):
    """手動で週次レポートを生成"""
    if report_scheduler:
        await report_scheduler.force_weekly_report(ctx)
    else:
        await ctx.send("⚠️ スケジューラーが初期化されていません。")

@bot.command(name='monthly')
async def force_monthly_report(ctx):
    """手動で月次レポートを生成"""
    if report_scheduler:
        await report_scheduler.force_monthly_report(ctx)
    else:
        await ctx.send("⚠️ スケジューラーが初期化されていません。")

def main():
    """メイン関数"""
    try:
        bot.run(DISCORD_BOT_TOKEN)
    except Exception as e:
        logger.error(f"Bot起動エラー: {e}")
    finally:
        # スケジューラー停止
        if report_scheduler:
            report_scheduler.stop()

if __name__ == "__main__":
    main()