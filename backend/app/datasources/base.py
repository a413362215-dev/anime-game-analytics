from abc import ABC, abstractmethod
import pandas as pd

class BaseDataSource(ABC):
    """数据源适配器基类（阶段2起逐个实现）：
    每个游戏/来源一个子类，只负责把原始数据翻译成标准表结构，
    分析模块只读标准表，不感知数据来自哪个游戏。"""
    name: str = "base"
    supported: list[str] = []  # 能供的标准表，如 ["gacha_log", "player"]

    @abstractmethod
    def test_connection(self, config: dict) -> bool:
        raise NotImplementedError

    @abstractmethod
    def fetch_raw(self, config: dict):
        raise NotImplementedError

    @abstractmethod
    def transform(self, raw, mapping: dict) -> pd.DataFrame:
        raise NotImplementedError
