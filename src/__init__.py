# audioop-ltsをaudioopとしてインポート（Python 3.13対応）
import sys
try:
    import audioop
except ModuleNotFoundError:
    import audioop_lts as audioop
    sys.modules['audioop'] = audioop