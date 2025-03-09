from abc import ABC, abstractmethod
import random
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from models.market import Market
    from models.event import Event, Rumor


class MarketState(ABC):
    @abstractmethod
    def update_prices(self, market: 'Market') -> None:
        pass

    @abstractmethod
    def process_event(self, market: 'Market', event: 'Event') -> None:
        pass

    @abstractmethod
    def process_rumor(self, market: 'Market', rumor: 'Rumor') -> None:
        pass

    @abstractmethod
    def get_name(self) -> str:
        pass


class BullMarketState(MarketState):
    def update_prices(self, market: 'Market') -> None:
        # У бичачому ринку ціни мають тенденцію до зростання
        for asset in market.assets.values():
            # Більше активів зростають, ніж падають, з більшою амплітудою
            change = random.uniform(-0.5, 1.5)
            asset.update_price(change)

    def process_event(self, market: 'Market', event: 'Event') -> None:
        # Бичачий ринок посилює позитивні події і пом'якшує негативні
        impact = event.impact
        if impact > 0:
            impact *= 1.5
        else:
            impact *= 0.7

        for asset_id in event.affected_assets:
            if asset_id in market.assets:
                market.assets[asset_id].apply_event_impact(impact)

    def process_rumor(self, market: 'Market', rumor: 'Rumor') -> None:
        # У бичачому ринку чутки мають сильніший позитивний вплив
        impact = rumor.get_impact()
        if impact > 0:
            impact *= 1.3

        if rumor.asset_id in market.assets:
            market.assets[rumor.asset_id].apply_rumor_impact(impact)

    def get_name(self) -> str:
        return "Бичачий"


class BearMarketState(MarketState):
    def update_prices(self, market: 'Market') -> None:
        # У ведмежому ринку ціни мають тенденцію до падіння
        for asset in market.assets.values():
            # Більше активів падають, ніж зростають, з більшою амплітудою
            change = random.uniform(-1.5, 0.5)
            asset.update_price(change)

    def process_event(self, market: 'Market', event: 'Event') -> None:
        # Ведмежий ринок посилює негативні події і пом'якшує позитивні
        impact = event.impact
        if impact < 0:
            impact *= 1.5
        else:
            impact *= 0.7

        for asset_id in event.affected_assets:
            if asset_id in market.assets:
                market.assets[asset_id].apply_event_impact(impact)

    def process_rumor(self, market: 'Market', rumor: 'Rumor') -> None:
        # У ведмежому ринку чутки мають сильніший негативний вплив
        impact = rumor.get_impact()
        if impact < 0:
            impact *= 1.3

        if rumor.asset_id in market.assets:
            market.assets[rumor.asset_id].apply_rumor_impact(impact)

    def get_name(self) -> str:
        return "Ведмежий"


class VolatileMarketState(MarketState):
    def update_prices(self, market: 'Market') -> None:
        # У волатильному ринку ціни змінюються драматично
        for asset in market.assets.values():
            # Значні коливання в обох напрямках
            change = random.uniform(-2.0, 2.0)
            asset.update_price(change)

    def process_event(self, market: 'Market', event: 'Event') -> None:
        # Волатильний ринок посилює всі події
        impact = event.impact * 1.8

        for asset_id in event.affected_assets:
            if asset_id in market.assets:
                market.assets[asset_id].apply_event_impact(impact)

    def process_rumor(self, market: 'Market', rumor: 'Rumor') -> None:
        # У волатильному ринку чутки мають драматичний вплив
        impact = rumor.get_impact() * 2.0
        if rumor.asset_id in market.assets:
            market.assets[rumor.asset_id].apply_rumor_impact(impact)

    def get_name(self) -> str:
        return "Волатильний"
