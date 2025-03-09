from patterns.builder import ScenarioBuilder
from utils.enums import AssetType, EventType


def create_default_scenario() -> ScenarioBuilder:
    """Створення стандартного сценарію гри"""
    builder = ScenarioBuilder()

    builder.create_market()

    builder.add_player("Трейдер", 10000.0)

    assets_data = [
        {"type": AssetType.STOCK, "name": "Нафта і Газ Корпорація", "ticker": "НГК", "price": 125.50},
        {"type": AssetType.STOCK, "name": "ТехноІнновації", "ticker": "ТІНН", "price": 320.75},
        {"type": AssetType.STOCK, "name": "Промбанк", "ticker": "ПРБК", "price": 85.20},
        {"type": AssetType.CRYPTO, "name": "Біткоїн", "ticker": "BTC", "price": 28500.0},
        {"type": AssetType.CRYPTO, "name": "Етереум", "ticker": "ETH", "price": 1850.0},
        {"type": AssetType.FOREX, "name": "Євро/Гривня", "ticker": "EUR/UAH", "price": 43.25},
        {"type": AssetType.FOREX, "name": "Долар/Гривня", "ticker": "USD/UAH", "price": 40.10},
        {"type": AssetType.COMMODITY, "name": "Золото", "ticker": "XAU", "price": 2100.0},
        {"type": AssetType.COMMODITY, "name": "Нафта", "ticker": "OIL", "price": 78.35}
    ]
    builder.add_assets(assets_data)

    builder.add_investor("Олег Капітал", 50000.0, 0.3)  # Консервативний інвестор
    builder.add_investor("Інвест Груп", 75000.0, 0.6)  # Поміркований інвестор
    builder.add_investor("Ризик Венчурс", 25000.0, 0.9)  # Агресивний інвестор

    events_data = [
        {
            "type": EventType.POLITICAL,
            "title": "Зміна політичного курсу",
            "description": "Новий уряд оголосив про зміну економічного курсу країни.",
            "impact": 3.5,
            "duration": 5,
            "affected_assets": [assets_data[0]["ticker"], assets_data[2]["ticker"]]
        },
        {
            "type": EventType.ECONOMIC,
            "title": "Зміна процентної ставки",
            "description": "Центральний банк підвищив облікову ставку.",
            "impact": -2.0,
            "duration": 3,
            "affected_assets": [assets_data[2]["ticker"], assets_data[5]["ticker"], assets_data[6]["ticker"]]
        },
        {
            "type": EventType.TECHNOLOGICAL,
            "title": "Проривна технологія",
            "description": "Анонсовано проривну технологію у сфері штучного інтелекту.",
            "impact": 5.0,
            "duration": 4,
            "affected_assets": [assets_data[1]["ticker"]]
        },
        {
            "type": EventType.COMPANY,
            "title": "Скандал з банком",
            "description": "Викрито фінансові махінації у великому банку.",
            "impact": -7.0,
            "duration": 6,
            "affected_assets": [assets_data[2]["ticker"]]
        },
        {
            "type": EventType.ECONOMIC,
            "title": "Нафтова криза",
            "description": "Скорочення видобутку нафти призвело до зростання цін.",
            "impact": 4.5,
            "duration": 7,
            "affected_assets": [assets_data[0]["ticker"], assets_data[8]["ticker"]]
        }
    ]
    builder.add_events(events_data)

    return builder


def create_hard_scenario() -> ScenarioBuilder:
    """Створення складного сценарію гри"""
    builder = ScenarioBuilder()

    builder.create_market()

    builder.add_player("Початківець", 5000.0)

    assets_data = [
        {"type": AssetType.STOCK, "name": "Стартап Інновацій", "ticker": "СТРТ", "price": 45.75},
        {"type": AssetType.STOCK, "name": "Біотехнології", "ticker": "БІОТ", "price": 220.5},
        {"type": AssetType.CRYPTO, "name": "КриптоТокен", "ticker": "КТ", "price": 0.075},
        {"type": AssetType.CRYPTO, "name": "ДжиТокен", "ticker": "ДТ", "price": 12.5},
        {"type": AssetType.FOREX, "name": "Фунт/Гривня", "ticker": "GBP/UAH", "price": 52.15},
        {"type": AssetType.COMMODITY, "name": "Срібло", "ticker": "XAG", "price": 28.75}
    ]
    builder.add_assets(assets_data)

    builder.add_investor("ВенчурКапітал", 30000.0, 0.9)  # Агресивний інвестор з високими очікуваннями

    events_data = [
        {
            "type": EventType.ECONOMIC,
            "title": "Економічна криза",
            "description": "Раптова фінансова криза спричинила паніку на ринках.",
            "impact": -8.0,
            "duration": 8,
            "affected_assets": [asset["ticker"] for asset in assets_data]
        },
        {
            "type": EventType.POLITICAL,
            "title": "Геополітичний конфлікт",
            "description": "Міжнародний конфлікт призвів до нестабільності на ринках.",
            "impact": -5.0,
            "duration": 5,
            "affected_assets": [assets_data[4]["ticker"], assets_data[5]["ticker"]]
        }
    ]
    builder.add_events(events_data)

    return builder


def create_multiplayer_scenario() -> ScenarioBuilder:
    """Створення сценарію для кількох гравців"""
    builder = ScenarioBuilder()

    builder.create_market()

    builder.add_player("Гравець 1", 10000.0)
    builder.add_player("Гравець 2", 10000.0)

    assets_data = [
        {"type": AssetType.STOCK, "name": "Технологічна Компанія", "ticker": "ТК", "price": 150.25},
        {"type": AssetType.STOCK, "name": "Енергетика", "ticker": "ЕНГ", "price": 85.5},
        {"type": AssetType.CRYPTO, "name": "Блокчейн-токен", "ticker": "БТ", "price": 5.75},
        {"type": AssetType.FOREX, "name": "Євро/Долар", "ticker": "EUR/USD", "price": 1.12},
        {"type": AssetType.COMMODITY, "name": "Мідь", "ticker": "CU", "price": 4.55}
    ]
    builder.add_assets(assets_data)

    builder.add_investor("Банк Інвестицій", 100000.0, 0.5)  # Поміркований інвестор

    events_data = [
        {
            "type": EventType.TECHNOLOGICAL,
            "title": "Технологічний прорив",
            "description": "Новий винахід відкриває великі можливості для інвестицій.",
            "impact": 6.0,
            "duration": 4,
            "affected_assets": [assets_data[0]["ticker"], assets_data[2]["ticker"]]
        },
        {
            "type": EventType.COMPANY,
            "title": "Злиття компаній",
            "description": "Дві великі компанії оголосили про об'єднання.",
            "impact": 4.0,
            "duration": 5,
            "affected_assets": [assets_data[1]["ticker"]]
        }
    ]
    builder.add_events(events_data)

    return builder
