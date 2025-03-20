from abc import ABC
import uuid
import random
from datetime import datetime


class Asset(ABC):
    def __init__(self, name: str, ticker: str, initial_price: float):
        self.id = str(uuid.uuid4())
        self.name = name
        self.ticker = ticker
        self.current_price = initial_price
        self.initial_price = initial_price
        self.price_history = [(datetime.now(), initial_price)]
        # Недотримання інкапсуляції дає можливість випадково міняти ціни

    def update_price(self, percent_change: float) -> None:
        change_factor = 1 + (percent_change / 100)
        self.current_price *= change_factor
        self.price_history.append((datetime.now(), self.current_price))

    def apply_event_impact(self, impact: float) -> None:
        self.update_price(impact)

    def apply_rumor_impact(self, impact: float) -> None:
        self.update_price(impact / 2)  # Чутки мають вдвічі менший вплив, ніж реальні події


class Stock(Asset):
    def __init__(self, name: str, ticker: str, initial_price: float):
        super().__init__(name, ticker, initial_price)
        self.company_health = random.uniform(0.5, 1.0)  # Фактор здоров'я компанії

    def update_price(self, percent_change: float) -> None:
        # На акції впливає здоров'я компанії
        modified_change = percent_change * self.company_health
        super().update_price(modified_change)


class Cryptocurrency(Asset):
    def __init__(self, name: str, ticker: str, initial_price: float):
        super().__init__(name, ticker, initial_price)
        self.volatility = random.uniform(1.5, 3.0)  # Крипто більш волатильна

    def update_price(self, percent_change: float) -> None:
        # Криптовалюти більш волатильні
        modified_change = percent_change * self.volatility
        super().update_price(modified_change)


class ForexPair(Asset):
    def __init__(self, name: str, ticker: str, initial_price: float):
        super().__init__(name, ticker, initial_price)
        self.stability = random.uniform(0.5, 1.0)  # Фактор стабільності форекса

    def update_price(self, percent_change: float) -> None:
        # Валютні пари менш волатильні
        modified_change = percent_change * self.stability
        super().update_price(modified_change)


class Commodity(Asset):
    def __init__(self, name: str, ticker: str, initial_price: float):
        super().__init__(name, ticker, initial_price)
        self.supply_elasticity = random.uniform(0.3, 0.8)  # Як швидко пристосовується постачання

    def update_price(self, percent_change: float) -> None:
        # На товари впливає еластичність постачання
        modified_change = percent_change * (1 - self.supply_elasticity)
        super().update_price(modified_change)
