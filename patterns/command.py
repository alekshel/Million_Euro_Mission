from abc import ABC, abstractmethod
import uuid
from typing import TYPE_CHECKING

from utils.enums import TradeType, RumorType

if TYPE_CHECKING:
    from models.player import Player
    from models.market import Market
    from models.asset import Asset


class Command(ABC):
    @abstractmethod
    def execute(self) -> bool:
        pass


class TradeCommand(Command):
    def __init__(self, player: 'Player', asset: 'Asset', trade_type: TradeType,
                 quantity: float, price: float):
        self.player = player
        self.asset = asset
        self.trade_type = trade_type
        self.quantity = quantity
        self.price = price
        self.executed = False
        self.trade_id = str(uuid.uuid4())

    def execute(self) -> bool:
        if self.executed:
            return False

        result = False
        if self.trade_type == TradeType.BUY:
            result = self.player.buy_asset(self.asset, self.quantity, self.price)
        elif self.trade_type == TradeType.SELL:
            result = self.player.sell_asset(self.asset, self.quantity, self.price)
        elif self.trade_type == TradeType.SHORT:
            result = self.player.short_asset(self.asset, self.quantity, self.price)
        elif self.trade_type == TradeType.COVER:
            result = self.player.cover_asset(self.asset, self.quantity, self.price)

        self.executed = result
        return result


class SpreadRumorCommand(Command):
    def __init__(self, player: 'Player', market: 'Market',
                 asset: 'Asset', rumor_type: RumorType,
                 content: str, is_true: bool):
        self.player = player
        self.market = market
        self.asset = asset
        self.rumor_type = rumor_type
        self.content = content
        self.is_true = is_true
        self.rumor = None
        self.executed = False

    def execute(self) -> bool:
        if self.executed:
            return False

        self.rumor = self.market.create_rumor(
            self.player, self.asset, self.rumor_type,
            self.content, self.is_true
        )

        if self.rumor:
            self.executed = True
            return True
        return False
