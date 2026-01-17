"""
Investigation Skills - 調查類劇本

包含各種調查相關的複合式劇本，如：
- 主機深度調查
- 網路連線分析
- 檔案行為分析
- 告警初篩與富化
"""

from .host_investigation import deep_investigate_host, triage_alert

__all__ = [
    'deep_investigate_host',
    'triage_alert',
]
