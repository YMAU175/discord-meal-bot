# Google サービスアカウントキーの作成手順

## 1. Google Cloud Consoleにアクセス
1. https://console.cloud.google.com/ にアクセス
2. Googleアカウントでログイン

## 2. プロジェクトの作成（既存のプロジェクトがない場合）
1. 上部のプロジェクトセレクターをクリック
2. 「新しいプロジェクト」をクリック
3. プロジェクト名を入力（例：discord-meal-bot）
4. 「作成」をクリック

## 3. Google Sheets APIを有効化
1. 左側メニューから「APIとサービス」→「ライブラリ」を選択
2. 検索バーに「Google Sheets API」と入力
3. 「Google Sheets API」をクリック
4. 「有効にする」ボタンをクリック

## 4. サービスアカウントの作成
1. 左側メニューから「APIとサービス」→「認証情報」を選択
2. 「+ 認証情報を作成」→「サービスアカウント」を選択
3. サービスアカウントの詳細を入力：
   - サービスアカウント名：discord-meal-bot
   - サービスアカウントID：自動生成されます
   - 説明：Discord食事管理ボット用
4. 「作成して続行」をクリック
5. ロールの選択で「編集者」を選択（またはより制限的な「Sheets編集者」）
6. 「続行」→「完了」をクリック

## 5. キーの作成とダウンロード
1. 作成したサービスアカウントをクリック
2. 「キー」タブを選択
3. 「鍵を追加」→「新しい鍵を作成」をクリック
4. 「JSON」を選択して「作成」をクリック
5. JSONファイルが自動的にダウンロードされます

## 6. スプレッドシートの作成と共有
1. Google Sheetsで新しいスプレッドシートを作成
2. スプレッドシートのURLから ID を取得
   - URL例：https://docs.google.com/spreadsheets/d/【ここがID】/edit
3. スプレッドシートの共有設定：
   - 右上の「共有」ボタンをクリック
   - ダウンロードしたJSONファイル内の`client_email`のメールアドレスを追加
   - 権限を「編集者」に設定
   - 「送信」をクリック

## 7. 環境変数の設定
1. ダウンロードしたJSONファイルを開く
2. 内容全体をコピー
3. `.env`ファイルの`GOOGLE_SHEETS_CREDENTIALS`に貼り付け（1行で）
4. スプレッドシートのIDを`GOOGLE_SHEETS_ID`に設定

### 例：
```
GOOGLE_SHEETS_CREDENTIALS={"type":"service_account","project_id":"discord-meal-bot","private_key_id":"...","private_key":"-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----\n","client_email":"discord-meal-bot@discord-meal-bot.iam.gserviceaccount.com","client_id":"...","auth_uri":"https://accounts.google.com/o/oauth2/auth","token_uri":"https://oauth2.googleapis.com/token","auth_provider_x509_cert_url":"https://www.googleapis.com/oauth2/v1/certs","client_x509_cert_url":"..."}
GOOGLE_SHEETS_ID=1234567890abcdefghijklmnopqrstuvwxyz
```

## 注意事項
- JSONファイルは機密情報なので、絶対に公開しないでください
- `.gitignore`に`.env`が含まれていることを確認してください
- サービスアカウントのメールアドレスは必ずスプレッドシートに共有してください