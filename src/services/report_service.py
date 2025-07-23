import discord
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import statistics
from src.config.config import NUTRITION_TARGETS, USER_PROFILE, TIMEZONE
from src.utils.logger import setup_logger

logger = setup_logger()

class ReportService:
    def __init__(self):
        self.targets = NUTRITION_TARGETS
        self.user_profile = USER_PROFILE
    
    def analyze_nutrition_data(self, meal_records: List[Dict]) -> Dict:
        """栄養データを分析"""
        if not meal_records:
            return {
                "total_meals": 0,
                "avg_calories": 0,
                "avg_nutrients": {"carbohydrates": 0, "protein": 0, "fat": 0},
                "total_nutrients": {"carbohydrates": 0, "protein": 0, "fat": 0},
                "meal_distribution": {"朝食": 0, "昼食": 0, "夕食": 0, "間食": 0, "その他": 0}
            }
        
        # データ集計
        calories = []
        nutrients = {"carbohydrates": [], "protein": [], "fat": []}
        meal_categories = {"朝食": 0, "昼食": 0, "夕食": 0, "間食": 0, "その他": 0}
        
        for record in meal_records:
            # カロリー
            cal = float(record.get("推定カロリー", 0))
            if cal > 0:
                calories.append(cal)
            
            # 栄養素
            carbs = float(record.get("炭水化物(g)", 0))
            protein = float(record.get("タンパク質(g)", 0))
            fat = float(record.get("脂質(g)", 0))
            
            if carbs > 0:
                nutrients["carbohydrates"].append(carbs)
            if protein > 0:
                nutrients["protein"].append(protein)
            if fat > 0:
                nutrients["fat"].append(fat)
            
            # カテゴリ
            category = record.get("カテゴリ", "その他")
            if category in meal_categories:
                meal_categories[category] += 1
        
        # 平均値計算
        avg_calories = statistics.mean(calories) if calories else 0
        avg_nutrients = {
            "carbohydrates": statistics.mean(nutrients["carbohydrates"]) if nutrients["carbohydrates"] else 0,
            "protein": statistics.mean(nutrients["protein"]) if nutrients["protein"] else 0,
            "fat": statistics.mean(nutrients["fat"]) if nutrients["fat"] else 0
        }
        
        # 合計値計算
        total_nutrients = {
            "carbohydrates": sum(nutrients["carbohydrates"]),
            "protein": sum(nutrients["protein"]),
            "fat": sum(nutrients["fat"])
        }
        
        return {
            "total_meals": len(meal_records),
            "avg_calories": round(avg_calories),
            "avg_nutrients": {k: round(v, 1) for k, v in avg_nutrients.items()},
            "total_nutrients": {k: round(v, 1) for k, v in total_nutrients.items()},
            "meal_distribution": meal_categories,
            "daily_avg_calories": round(sum(calories) / 7) if len(calories) > 0 else 0
        }
    
    def generate_health_advice(self, analysis: Dict, period: str = "weekly") -> List[str]:
        """健康アドバイスを生成"""
        advice = []
        
        # カロリー摂取量の評価
        if period == "weekly":
            daily_avg = analysis.get("daily_avg_calories", 0)
        else:
            daily_avg = analysis.get("avg_calories", 0) * analysis.get("total_meals", 0) / 30
        
        if daily_avg > 0:
            target_min = self.targets["calories"]["min"]
            target_max = self.targets["calories"]["max"]
            
            if daily_avg < target_min * 0.8:
                advice.append("⚠️ カロリー摂取量が目標値を大幅に下回っています。バランスの良い食事を心がけましょう。")
            elif daily_avg < target_min:
                advice.append("📊 カロリー摂取量がやや少なめです。もう少し食事量を増やしても良いでしょう。")
            elif daily_avg > target_max * 1.2:
                advice.append("⚠️ カロリー摂取量が目標値を大幅に上回っています。食事量の見直しを検討しましょう。")
            elif daily_avg > target_max:
                advice.append("📊 カロリー摂取量がやや多めです。運動量を増やすか、食事量を調整しましょう。")
            else:
                advice.append("✅ カロリー摂取量は適切な範囲内です。")
        
        # 栄養バランスの評価
        avg_nutrients = analysis.get("avg_nutrients", {})
        
        # タンパク質
        protein_avg = avg_nutrients.get("protein", 0)
        if protein_avg > 0:
            if protein_avg < self.targets["protein"]["min"] * 0.8:
                advice.append("🥩 タンパク質が不足しています。肉、魚、卵、大豆製品を積極的に摂りましょう。")
            elif protein_avg > self.targets["protein"]["max"] * 1.2:
                advice.append("🥩 タンパク質の摂取量が多めです。バランスを考慮しましょう。")
        
        # 食事回数の評価
        meal_dist = analysis.get("meal_distribution", {})
        total_main_meals = meal_dist.get("朝食", 0) + meal_dist.get("昼食", 0) + meal_dist.get("夕食", 0)
        
        if period == "weekly" and total_main_meals < 15:
            advice.append("🍽️ 欠食が多いようです。規則正しい食事を心がけましょう。")
        
        # 間食の評価
        snack_ratio = meal_dist.get("間食", 0) / max(analysis.get("total_meals", 1), 1)
        if snack_ratio > 0.3:
            advice.append("🍪 間食の割合が高めです。メインの食事を充実させましょう。")
        
        return advice if advice else ["✨ 全体的にバランスの良い食生活です。この調子で続けましょう！"]
    
    def create_weekly_report_embed(self, user_name: str, week_data: List[Dict], 
                                  start_date: datetime, end_date: datetime) -> discord.Embed:
        """週次レポートのEmbed作成"""
        analysis = self.analyze_nutrition_data(week_data)
        advice = self.generate_health_advice(analysis, "weekly")
        
        # Embed作成
        embed = discord.Embed(
            title="📊 週次食事レポート",
            description=f"**{user_name}** さんの週次レポート\n"
                       f"期間: {start_date.strftime('%Y/%m/%d')} - {end_date.strftime('%Y/%m/%d')}",
            color=discord.Color.blue(),
            timestamp=datetime.now(TIMEZONE)
        )
        
        # 基本統計
        embed.add_field(
            name="📈 基本統計",
            value=f"総食事回数: {analysis['total_meals']}回\n"
                  f"1日平均カロリー: {analysis['daily_avg_calories']} kcal\n"
                  f"目標範囲: {self.targets['calories']['min']}-{self.targets['calories']['max']} kcal",
            inline=False
        )
        
        # 栄養素平均
        avg_n = analysis['avg_nutrients']
        embed.add_field(
            name="🥗 平均栄養素（1食あたり）",
            value=f"炭水化物: {avg_n['carbohydrates']}g\n"
                  f"タンパク質: {avg_n['protein']}g\n"
                  f"脂質: {avg_n['fat']}g",
            inline=True
        )
        
        # 食事分布
        meal_dist = analysis['meal_distribution']
        dist_text = "\n".join([f"{k}: {v}回" for k, v in meal_dist.items() if v > 0])
        embed.add_field(
            name="⏰ 食事タイミング",
            value=dist_text if dist_text else "データなし",
            inline=True
        )
        
        # 健康アドバイス
        advice_text = "\n".join(advice[:3])  # 最大3つまで
        embed.add_field(
            name="💡 今週のアドバイス",
            value=advice_text,
            inline=False
        )
        
        # 目標達成度（視覚的に）
        daily_avg = analysis['daily_avg_calories']
        if daily_avg > 0:
            achievement = min(100, int((daily_avg / self.targets['calories']['min']) * 100))
            bar_length = 20
            filled = int(bar_length * achievement / 100)
            bar = "█" * filled + "░" * (bar_length - filled)
            embed.add_field(
                name="🎯 カロリー目標達成度",
                value=f"{bar} {achievement}%",
                inline=False
            )
        
        return embed
    
    def create_monthly_report_embed(self, user_name: str, month_data: List[Dict], 
                                   year: int, month: int) -> discord.Embed:
        """月次レポートのEmbed作成"""
        analysis = self.analyze_nutrition_data(month_data)
        advice = self.generate_health_advice(analysis, "monthly")
        
        # Embed作成
        embed = discord.Embed(
            title="📊 月次食事レポート",
            description=f"**{user_name}** さんの月次レポート\n"
                       f"期間: {year}年{month}月",
            color=discord.Color.green(),
            timestamp=datetime.now(TIMEZONE)
        )
        
        # 基本統計
        embed.add_field(
            name="📈 月間統計",
            value=f"総食事回数: {analysis['total_meals']}回\n"
                  f"1食平均カロリー: {analysis['avg_calories']} kcal\n"
                  f"推定月間カロリー: {analysis['avg_calories'] * analysis['total_meals']:,} kcal",
            inline=False
        )
        
        # 栄養素合計
        total_n = analysis['total_nutrients']
        embed.add_field(
            name="🥗 月間栄養素摂取量",
            value=f"炭水化物: {total_n['carbohydrates']:,.1f}g\n"
                  f"タンパク質: {total_n['protein']:,.1f}g\n"
                  f"脂質: {total_n['fat']:,.1f}g",
            inline=True
        )
        
        # 食事パターン
        meal_dist = analysis['meal_distribution']
        total_meals = sum(meal_dist.values())
        if total_meals > 0:
            pattern_text = "\n".join([
                f"{k}: {v}回 ({v/total_meals*100:.1f}%)" 
                for k, v in meal_dist.items() if v > 0
            ])
            embed.add_field(
                name="⏰ 食事パターン",
                value=pattern_text,
                inline=True
            )
        
        # 月間サマリー
        days_recorded = len(set(r.get("記録日時", "")[:10] for r in month_data))
        embed.add_field(
            name="📅 記録状況",
            value=f"記録日数: {days_recorded}日\n"
                  f"1日平均食事回数: {analysis['total_meals'] / max(days_recorded, 1):.1f}回",
            inline=False
        )
        
        # 健康アドバイス
        advice_text = "\n".join(advice)
        embed.add_field(
            name="💡 今月の総評とアドバイス",
            value=advice_text,
            inline=False
        )
        
        # 来月への目標
        embed.add_field(
            name="🎯 来月への目標提案",
            value=self._generate_next_month_goals(analysis),
            inline=False
        )
        
        return embed
    
    def _generate_next_month_goals(self, analysis: Dict) -> str:
        """来月の目標を生成"""
        goals = []
        
        daily_avg = analysis.get("daily_avg_calories", 0)
        if daily_avg < self.targets["calories"]["min"]:
            goals.append("• カロリー摂取量を1日2200kcal以上に増やす")
        elif daily_avg > self.targets["calories"]["max"]:
            goals.append("• カロリー摂取量を1日2400kcal以下に調整する")
        
        if analysis["avg_nutrients"]["protein"] < self.targets["protein"]["min"]:
            goals.append("• タンパク質摂取量を1日65g以上に増やす")
        
        meal_dist = analysis["meal_distribution"]
        if meal_dist["朝食"] < analysis["total_meals"] * 0.2:
            goals.append("• 朝食を欠かさず摂る習慣をつける")
        
        return "\n".join(goals) if goals else "• 現在の良い食習慣を維持する\n• 季節の食材を積極的に取り入れる"