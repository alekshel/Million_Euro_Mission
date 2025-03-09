import uuid
import random
from datetime import datetime
from typing import List, TYPE_CHECKING
from utils.enums import EventType, RumorType

if TYPE_CHECKING:
    from models.market import Market


class Event:
    def __init__(self, event_type: EventType, title: str, description: str,
                 impact: float, duration: int, affected_assets: List[str]):
        self.id = str(uuid.uuid4())
        self.event_type = event_type
        self.title = title
        self.description = description
        self.impact = impact  # Позитивне або негативне значення, що вказує на вплив на ринок
        self.duration = duration  # Скільки ходів ця подія впливає на ринок
        self.affected_assets = affected_assets  # Список ID активів
        self.remaining_duration = duration

    def is_active(self) -> bool:
        return self.remaining_duration > 0

    def apply_effect(self, market: 'Market') -> None:
        if self.is_active():
            for asset_id in self.affected_assets:
                if asset_id in market.assets:
                    market.assets[asset_id].apply_event_impact(self.impact)
            self.remaining_duration -= 1


class Rumor:
    def __init__(self, creator_id: str, asset_id: str, rumor_type: RumorType,
                 content: str, is_true: bool, discovered_chance: float = 0.1):
        self.id = str(uuid.uuid4())
        self.creator_id = creator_id
        self.asset_id = asset_id
        self.rumor_type = rumor_type
        self.content = content
        self.is_true = is_true
        self.created_at = datetime.now()
        self.credibility = random.uniform(0.2, 0.8)  # Наскільки правдоподібна чутка
        self.discovered_chance = discovered_chance  # Шанс бути викритим, якщо неправда
        self.is_discovered = False

    def get_impact(self) -> float:
        # Вплив залежить від типу та достовірності
        base_impact = random.uniform(1.0, 5.0)

        # Неправдиві чутки можуть мати протилежний ефект, якщо розкриті
        if not self.is_true and self.is_discovered:
            return -base_impact * self.credibility
        else:
            return base_impact * self.credibility

    def check_discovery(self) -> bool:
        # Перевірка, чи розкрита неправдива чутка
        if not self.is_true and not self.is_discovered:
            if random.random() < self.discovered_chance:
                self.is_discovered = True
                return True
        return False
