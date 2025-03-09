from abc import ABC, abstractmethod
from typing import List, TYPE_CHECKING

if TYPE_CHECKING:
    from models.market import Market
    from models.player import Player
    from models.asset import Asset
    from patterns.command import TradeCommand


class TradingStrategy(ABC):
    @abstractmethod
    def execute(self, market: 'Market', player: 'Player', available_assets: List['Asset']) -> List['TradeCommand']:
        pass


class ValueInvestingStrategy(TradingStrategy):
    def execute(self, market: 'Market', player: 'Player', available_assets: List['Asset']) -> List['TradeCommand']:
        from patterns.command import TradeCommand
        from utils.enums import TradeType

        commands = []
        for asset in available_assets:
            if asset.current_price < asset.initial_price * 0.8:
                max_shares = int(player.capital * 0.2 / asset.current_price)
                if max_shares > 0:
                    commands.append(TradeCommand(
                        player, asset, TradeType.BUY, max_shares, asset.current_price
                    ))
        return commands


class TrendFollowingStrategy(TradingStrategy):
    def execute(self, market: 'Market', player: 'Player', available_assets: List['Asset']) -> List['TradeCommand']:
        from patterns.command import TradeCommand
        from utils.enums import TradeType

        commands = []
        for asset in available_assets:
            if len(asset.price_history) >= 2:
                prev_price = asset.price_history[-2][1]
                if asset.current_price > prev_price * 1.05:
                    max_shares = int(player.capital * 0.15 / asset.current_price)
                    if max_shares > 0:
                        commands.append(TradeCommand(
                            player, asset, TradeType.BUY, max_shares, asset.current_price
                        ))
        return commands
