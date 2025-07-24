# Oracle Cloud Discord Bot デプロイ手順

## 1. 事前準備

### Gitリポジトリの準備
```bash
# Gitリポジトリを初期化（まだしていない場合）
git init
git add .
git commit -m "Initial commit - Discord食事管理ボット"

# GitHubにリポジトリを作成してプッシュ
git remote add origin https://github.com/YOUR_USERNAME/discord-meal-bot.git
git push -u origin main
```

### 機密情報の確認
- `.gitignore`で`.env`ファイルが除外されていることを確認
- 本番用の環境変数を別途準備

## 2. Oracle Cloud アカウント設定

1. **アカウント作成**
   - https://www.oracle.com/cloud/free/ でアカウント作成
   - 無料トライアル（$300クレジット）を有効化
   - 永続無料リソースも利用可能

2. **VMインスタンス作成**
   - Shape: `VM.Standard.E2.1.Micro` (Always Free対象)
   - OS: Oracle Linux 8 または Ubuntu 20.04 LTS
   - Boot Volume: 50GB (無料枠内)
   - SSH公開鍵を設定

## 3. サーバーセットアップ

### SSH接続
```bash
ssh -i ~/.ssh/oci_key opc@[インスタンスのパブリックIP]
```

### 基本パッケージインストール
```bash
# システム更新
sudo yum update -y

# 必要なパッケージ
sudo yum install -y git python39 python39-pip

# Python 3.9をデフォルトに設定
sudo alternatives --install /usr/bin/python3 python3 /usr/bin/python3.9 1
```

## 4. アプリケーションデプロイ

### コードの取得

#### GitHub CLI インストール（Privateリポジトリ対応）
```bash
# Oracle Linux 8の場合
sudo dnf install -y 'dnf-command(config-manager)'
sudo dnf config-manager --add-repo https://cli.github.com/packages/rpm/gh-cli.repo
sudo dnf install -y gh

# Ubuntu 20.04の場合
curl -fsSL https://cli.github.com/packages/githubcli-archive-keyring.gpg | sudo dd of=/usr/share/keyrings/githubcli-archive-keyring.gpg
echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/githubcli-archive-keyring.gpg] https://cli.github.com/packages stable main" | sudo tee /etc/apt/sources.list.d/github-cli.list > /dev/null
sudo apt update
sudo apt install gh
```

#### GitHub認証とクローン
```bash
# GitHub CLI で認証
gh auth login
# → 対話形式で設定
# → GitHubのアカウントタイプ: GitHub.com
# → 認証方法: Login with a web browser（推奨）またはPaste an authentication token
# → Git操作プロトコル: HTTPS

# ホームディレクトリに移動
cd ~

# リポジトリをクローン（Privateリポジトリでも自動認証）
gh repo clone YOUR_USERNAME/discord-meal-bot
cd discord-meal-bot
```

### Python環境構築
```bash
# 仮想環境作成
python3 -m venv venv
source venv/bin/activate

# 依存関係インストール
pip install --upgrade pip
pip install -r requirements.txt
```

### 環境変数設定
```bash
# .envファイル作成
nano .env
```

以下の内容を入力：
```env
# Discord Bot Token
DISCORD_BOT_TOKEN=your_bot_token_here

# Google Gemini API Key
GEMINI_API_KEY=your_gemini_api_key_here

# Google Sheets API Credentials (1行で)
GOOGLE_SHEETS_CREDENTIALS={"type":"service_account",...}

# Google Sheets ID
GOOGLE_SHEETS_ID=your_spreadsheet_id_here

# Discord Channel IDs
MEAL_CHANNEL_ID=1393518102897234040
WEEKLY_REPORT_CHANNEL_ID=1393518129921003520
MONTHLY_REPORT_CHANNEL_ID=1393518170865795192

# Discord Server ID
DISCORD_SERVER_ID=1393517298358292540

# Timezone
TIMEZONE=Asia/Tokyo
```

## 5. サービス化（常時起動）

### systemdサービス作成
```bash
sudo nano /etc/systemd/system/discord-meal-bot.service
```

以下の内容を入力：
```ini
[Unit]
Description=Discord Meal Management Bot
After=network.target

[Service]
Type=simple
User=opc
WorkingDirectory=/home/opc/discord-meal-bot
Environment=PATH=/home/opc/discord-meal-bot/venv/bin
ExecStart=/home/opc/discord-meal-bot/venv/bin/python -m src.main
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
```

### サービス有効化・起動
```bash
# サービス有効化
sudo systemctl enable discord-meal-bot.service

# サービス起動
sudo systemctl start discord-meal-bot.service

# ステータス確認
sudo systemctl status discord-meal-bot.service

# ログ確認
sudo journalctl -u discord-meal-bot.service -f
```

## 6. ファイアウォール設定（必要に応じて）

```bash
# HTTPSアウトバウンドを許可（Discord API用）
sudo firewall-cmd --permanent --add-port=443/tcp
sudo firewall-cmd --reload
```

## 7. 自動更新スクリプト

```bash
# 更新用スクリプト作成
nano ~/update-bot.sh
```

```bash
#!/bin/bash
cd ~/discord-meal-bot
# GitHub CLIを使用してPrivateリポジトリからpull
gh repo sync
source venv/bin/activate
pip install -r requirements.txt
sudo systemctl restart discord-meal-bot.service
echo "Bot updated and restarted"
```

```bash
chmod +x ~/update-bot.sh
```

## 8. 監視・メンテナンス

### ログ確認
```bash
# サービスログ
sudo journalctl -u discord-meal-bot.service -n 50

# アプリケーションログ
tail -f ~/discord-meal-bot/logs/$(date +%Y%m%d).log
```

### ディスク使用量監視
```bash
df -h
du -sh ~/discord-meal-bot/logs/*
```

### 定期的なログローテーション
```bash
# crontabに追加
crontab -e

# 毎日深夜2時に30日以上前のログを削除
0 2 * * * find ~/discord-meal-bot/logs -name "*.log" -mtime +30 -delete
```

## 9. トラブルシューティング

### よくある問題と解決方法

1. **Bot起動失敗**
   ```bash
   # エラーログ確認
   sudo journalctl -u discord-meal-bot.service -n 20
   
   # 手動起動テスト
   cd ~/discord-meal-bot
   source venv/bin/activate
   python -m src.main
   ```

2. **Google Sheets接続エラー**
   - サービスアカウントの権限確認
   - スプレッドシートの共有設定確認

3. **メモリ不足**
   ```bash
   # メモリ使用量確認
   free -h
   htop
   ```

## 10. セキュリティ対策

```bash
# SSH設定強化
sudo nano /etc/ssh/sshd_config
# PasswordAuthentication no
# PermitRootLogin no

# 不要なサービス停止
sudo systemctl disable --now [不要なサービス名]

# 定期的なセキュリティ更新
sudo yum update -y
```

## 注意事項

- Oracle Cloudの無料インスタンスは60日程度で削除される場合があります
- 定期的なバックアップを推奨します
- ブートボリュームのバックアップも作成しておきましょう

## バックアップ手順

```bash
# 設定ファイルのバックアップ
tar -czf ~/bot-backup-$(date +%Y%m%d).tar.gz ~/discord-meal-bot/.env ~/discord-meal-bot/logs

# Oracle Cloud Console でブートボリュームのバックアップも作成
```