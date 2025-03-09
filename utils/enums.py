from enum import Enum


class AssetType(Enum):
    STOCK = "акція"
    CRYPTO = "криптовалюта"
    FOREX = "валютна пара"
    COMMODITY = "сировина"


class TradeType(Enum):
    BUY = "купити"
    SELL = "продати"
    SHORT = "відкрити коротку позицію"
    COVER = "закрити коротку позицію"


class EventType(Enum):
    POLITICAL = "політична"
    ECONOMIC = "економічна"
    TECHNOLOGICAL = "технологічна"
    COMPANY = "корпоративна"


class RumorType(Enum):
    INSIDER = "інсайдерська"
    NEWS_LEAK = "витік новин"
    MARKET_SENTIMENT = "настрої ринку"
