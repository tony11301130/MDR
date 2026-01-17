"""
Response Skills - 處置類劇本

包含各種自動化處置相關的劇本，如：
- 主機隔離與解除隔離
- 行程終止
- IP/Domain 封鎖
- 自動化修復
"""

from .isolation import isolate_endpoint, unisolate_endpoint

__all__ = [
    'isolate_endpoint',
    'unisolate_endpoint',
]
