# Discordߋ����

Discord
gߋn���?Y�`QgGemini AIL�Մk
�1��WGoogle Sheetsk2Y����gY1!�!ge����Ȃ���W~Y

## _�

### <} ߋ�_�
- ߋ��������Y�h���
- Gemini 2.0 Flash k��ؾ�jߋ���
 ��
- �����4i��ѯ�����
- Google Sheetsk��2

### =� ����_�
- **1!����**: �1���23Bk���
  - 1�nߋq�
�
  - e���Ф���T�
- **!����**: � B�23Bk���
  - �n�U��ߋѿ���
  - exn��H

### <� � i
- 34s7'�S�65kg��n
�$
- tb�'%�S�k�eO�hB��
- ����餺U�_e���Ф�

## �S��ï

- ** �**: Python 3.13
- **Bot Framework**: discord.py
- **AI�**: Google Gemini 2.0 Flash API
- **����X**: Google Sheets API
- **�������**: APScheduler
- **۹ƣ�**: Oracle Cloud (!��)

## ��Ȣ��

### 1. �X��n�����
```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. ��	pn-�
`.env.example`�`.env`k���Wf��-�

```env
DISCORD_BOT_TOKEN=your_discord_bot_token
GEMINI_API_KEY=your_gemini_api_key
GOOGLE_SHEETS_CREDENTIALS={"type":"service_account",...}
GOOGLE_SHEETS_ID=your_spreadsheet_id
```

### 3. Google Services-�
1. [Google Cloud Console](https://console.cloud.google.com/)g������\
2. Sheets API�	�
3. ��ӹ�����\�JSON��������
4. ����ɷ��\���ӹ�����kq	

s0: [docs/google-service-account-setup.md](docs/google-service-account-setup.md)

### 4. Discord Bot-�
1. [Discord Developer Portal](https://discord.com/developers/applications)g�������\
2. Bot����֗
3. ����kۅŁj)P: �û���ա����ꢯ�����	

## (��

### ����L
```bash
# ��1: �����(
./run.sh

# ��2: ���L
source venv/bin/activate && python -m src.main
```

### ����
- `!ping` - �\��
- `!status` - Bot�K��  
- `!weekly` - 1!����K�
- `!monthly` - !����K�

### ߋ2
�W_�����kߋ���?Y�`Qg����2U�~Y

## ����

Oracle Cloud!��gn����K: [docs/oracle-cloud-deployment.md](docs/oracle-cloud-deployment.md)

## ������� 

```
discored-meal/
   src/
      config/          # -�ա��
      services/        # ��ӹ#:
      utils/           # ��ƣ�ƣ
      main.py         # ��ա��
      scheduler.py    # ���ȹ������
   docs/               # ɭ����
   requirements.txt    # �X��
   .env.example       # ��	p������
```

## 餻�

Sn������oMIT餻�ngl�U�fD~Y

## �.

��ꯨ�Ȅ����n1J�S�W~Y

## ��

- Gemini APIn!��6PkT�O`UD1�1,500ꯨ��	
- Oracle Cloud!����o60��gJdU��4LB�~Y
- ,j��go��j�ï��ג�hW~Y