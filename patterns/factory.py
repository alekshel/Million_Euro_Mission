import random
from typing import TYPE_CHECKING

from utils.enums import AssetType, EventType

if TYPE_CHECKING:
    from models.asset import Asset
    from models.event import Event
    from models.market import Market


class AssetFactory:
    @staticmethod
    def create_asset(asset_type: AssetType, name: str, ticker: str,
                     initial_price: float) -> 'Asset':
        from models.asset import Stock, Cryptocurrency, ForexPair, Commodity

        if asset_type == AssetType.STOCK:
            return Stock(name, ticker, initial_price)
        elif asset_type == AssetType.CRYPTO:
            return Cryptocurrency(name, ticker, initial_price)
        elif asset_type == AssetType.FOREX:
            return ForexPair(name, ticker, initial_price)
        elif asset_type == AssetType.COMMODITY:
            return Commodity(name, ticker, initial_price)
        else:
            raise ValueError(f"Непідтримуваний тип активу: {asset_type}")


class EventFactory:
    @staticmethod
    def create_random_event(market: 'Market') -> 'Event':
        from models.event import Event

        event_type = random.choice(list(EventType))

        severity = random.uniform(0.1, 1.0)
        duration = random.randint(1, 10)

        asset_count = random.randint(1, min(5, len(market.assets)))
        affected_assets = random.sample(list(market.assets.keys()), asset_count)

        impact = severity * (-1 if random.random() < 0.5 else 1)

        titles = []
        if event_type == EventType.POLITICAL:
            titles = [
                "Оголошено результати виборів",
                "Нова торгова політика",
                "Політичні заворушення",
                "Міжнародний конфлікт"
            ]
        elif event_type == EventType.ECONOMIC:
            titles = [
                "Зміна процентної ставки",
                "Звіт про зростання ВВП",
                "Дані про безробіття",
                "Сплеск інфляції"
            ]
        elif event_type == EventType.TECHNOLOGICAL:
            titles = [
                "Оголошено про великі інновації",
                "Порушення кібербезпеки",
                "Нове технологічне регулювання",
                "Запуск продукту"
            ]
        elif event_type == EventType.COMPANY:
            titles = [
                "Відставка CEO",
                "Звіт про прибутки",
                "Оголошення про злиття",
                "Відкликання продукту"
            ]

        title = random.choice(titles)
        description = f"{title}: Ця подія суттєво впливає на ринки."

        return Event(
            event_type=event_type,
            title=title,
            description=description,
            impact=impact,
            duration=duration,
            affected_assets=affected_assets
        )
