"""
Skills Layer - API 劇本層

本模組包含 MDR 系統的業務邏輯編排層，負責將多個 Adapter 原子操作組合成完整的調查劇本。

目錄結構:
- investigation/: 調查類劇本（主機調查、網路分析、檔案分析等）
- response/: 處置類劇本（隔離、封鎖、修復等）
- enrichment/: 富化類劇本（情資比對、資產上下文等）
- registry.py: 工具註冊中心，供 AI Engine 使用
- tools.py: 工具註冊模組，自動註冊所有 Skills 工具
"""

from .registry import SkillsRegistry, skills_registry
# 匯入 tools 模組以觸發工具註冊
from . import tools

__all__ = ['SkillsRegistry', 'skills_registry']
