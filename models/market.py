import random
from typing import Dict, List, Optional, TYPE_CHECKING
from patterns.observer import Subject
from patterns.state import MarketState, BullMarketState, BearMarketState, VolatileMarketState
from utils.enums import RumorType
from models.asset import Asset
from models.event import Rumor

if TYPE_CHECKING:
    from models.player import Player
    from models.event import Event


class Market(Subject):
    def __init__(self):
        super().__init__()
        self.assets: Dict[str, Asset] = {}
        self.events: List['Event'] = []
        self.rumors: List[Rumor] = []
        self.day = 1
        self.current_state: MarketState = BullMarketState()
        self.market_volatility = 0.5  # 0.0 (стабільний) до 1.0 (дуже волатильний)

    def add_asset(self, asset: Asset) -> None:
        self.assets[asset.id] = asset

    def create_rumor(self, player: 'Player', asset: Asset, rumor_type: RumorType,
                     content: str, is_true: bool) -> Optional[Rumor]:
        # Перевірка достатньої репутації для поширення
        if player.reputation < 0.2:
            return None

        discovery_chance = 0.1
        if not is_true:
            discovery_chance = 0.4 - (player.reputation * 0.3)  # 0.1-0.4 залежно від репутації

        rumor = Rumor(
            creator_id=player.id,
            asset_id=asset.id,
            rumor_type=rumor_type,
            content=content,
            is_true=is_true,
            discovered_chance=discovery_chance
        )

        self.rumors.append(rumor)

        # Обробка впливу чутки через поточний стан ринку
        self.current_state.process_rumor(self, rumor)

        self.notify(rumor=rumor)

        return rumor

    def add_event(self, event: 'Event') -> None:
        self.events.append(event)

        # Обробка впливу події через поточний стан ринку
        self.current_state.process_event(self, event)

        self.notify(event=event)

    def change_state(self, new_state: MarketState) -> None:
        self.current_state = new_state
        # Повідомлення гравців
        self.notify(market_state=self.current_state.get_name())

    def update(self) -> None:
        self.day += 1

        for event in [e for e in self.events if e.is_active()]:
            event.apply_effect(self)

        # Перевірка розкриття чуток
        for rumor in self.rumors:
            if rumor.check_discovery():
                self.notify(rumor=rumor, discovered=True)

        # Оновлення цін через поточний стан ринку
        self.current_state.update_prices(self)

        # Випадкова зміна стану ринку
        if random.random() < 0.05:  # 5% шанс зміни стану ринку щодня
            states = [BullMarketState(), BearMarketState(), VolatileMarketState()]
            new_state = random.choice([s for s in states if not isinstance(s, type(self.current_state))])
            self.change_state(new_state)

        # Повідомлення про оновлення ринку
        self.notify(day=self.day)

    def generate_random_event(self) -> None:
        from patterns.factory import EventFactory

        if random.random() < 0.3:  # 30% шанс нової події щодня
            event = EventFactory.create_random_event(self)
            self.add_event(event)
