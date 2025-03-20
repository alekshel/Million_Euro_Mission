import uuid
from datetime import datetime
from typing import Dict, Tuple, TYPE_CHECKING
from patterns.observer import Observer, Subject
from utils.enums import RumorType, TradeType
from patterns.command import SpreadRumorCommand
from patterns.strategy import TradingStrategy

if TYPE_CHECKING:
    from models.asset import Asset
    from models.market import Market


class Investor:
    def __init__(self, name: str, capital: float, risk_tolerance: float):
        self.id = str(uuid.uuid4())
        self.name = name
        self.capital = capital
        self.risk_tolerance = risk_tolerance  # 0.0 (консервативний) до 1.0 (агресивний)
        self.investment_history = []
        self.satisfaction = 1.0  # 0.0 (незадоволений) до 1.0 (дуже задоволений)

    def invest(self, player: 'Player', amount: float) -> bool:
        if amount > self.capital:
            return False

        self.capital -= amount
        player.receive_investment(self.id, amount)
        self.investment_history.append((datetime.now(), amount, player.id))
        return True

    def withdraw(self, player: 'Player', amount: float) -> bool:
        if player.return_investment(self.id, amount):
            self.capital += amount
            self.investment_history.append((datetime.now(), -amount, player.id))
            return True
        return False

    def update_satisfaction(self, return_rate: float) -> None:
        # Оновлення на основі очікуваної прибутковості vs фактичної
        expected_return = 0.05 + (self.risk_tolerance * 0.15)  # 5-20% залежно від толерантності до ризику

        if return_rate >= expected_return:
            self.satisfaction = min(1.0, self.satisfaction + 0.1)
        else:
            self.satisfaction = max(0.0, self.satisfaction - 0.2)


class Player(Observer):
    def __init__(self, name: str, initial_capital: float):
        self.id = str(uuid.uuid4())
        self.name = name
        self.capital = initial_capital
        self.portfolio: Dict[str, float] = {}  # ID активу до кількості
        self.short_positions: Dict[str, Tuple[float, float]] = {}  # ID активу до (кількість, ціна)
        self.trade_history = []
        self.reputation = 0.5  # 0.0 (кримінальний) до 1.0 (довірений)
        self.investor_funds: Dict[str, float] = {}  # ID інвестора до інвестованої суми
        self.strategy = None
        self.game_over = False
        self.prison = False
        self.notifications = []

    def update(self, subject: Subject, **kwargs) -> None:
        # Реагування на оновлення ринку
        if subject.__class__.__name__ == 'Market':
            if 'event' in kwargs:
                event = kwargs['event']
                self.notifications.append(f"ПОДІЯ: {event.title}")
            elif 'rumor' in kwargs:
                rumor = kwargs['rumor']
                self.notifications.append(f"ЧУТКА: {rumor.content}")
                if 'discovered' in kwargs and kwargs['discovered']:
                    self.notifications.append("Чутка була розкрита як неправдива!")
        # А що заважає реагувати окремо на події, а окремо на чутки? Бо виникають вони окремо, в notify точно відомо що це було. Тоді updateEvent/updateRumor позбудуться цих перевірок та Conditional Complexity smell
        # Схоже так виходить виключно за бажання уніфікувати патерн Observer, а так не треба, він не передбачає уніфікування.

    def set_strategy(self, strategy: TradingStrategy) -> None:
        self.strategy = strategy

    def execute_strategy(self, market: 'Market') -> None:
        if self.strategy:
            assets = list(market.assets.values())
            commands = self.strategy.execute(market, self, assets)
            for command in commands:
                command.execute()

    def buy_asset(self, asset: 'Asset', quantity: float, price: float) -> bool:
        cost = quantity * price
        if cost > self.capital:
            return False

        self.capital -= cost

        if asset.id in self.portfolio:
            self.portfolio[asset.id] += quantity
        else:
            self.portfolio[asset.id] = quantity

        self.trade_history.append((
            datetime.now(),
            TradeType.BUY,
            asset.id,
            quantity,
            price
        ))

        return True

    def sell_asset(self, asset: 'Asset', quantity: float, price: float) -> bool:
        if asset.id not in self.portfolio or self.portfolio[asset.id] < quantity:
            return False

        self.portfolio[asset.id] -= quantity
        if self.portfolio[asset.id] == 0:
            del self.portfolio[asset.id]

        self.capital += quantity * price

        self.trade_history.append((
            datetime.now(),
            TradeType.SELL,
            asset.id,
            quantity,
            price
        ))

        return True

    def short_asset(self, asset: 'Asset', quantity: float, price: float) -> bool:
        # Переконатись, що гравець має достатньо капіталу як заставу (50% позиції)
        collateral_required = quantity * price * 0.5
        if collateral_required > self.capital:
            return False

        self.capital -= collateral_required

        if asset.id in self.short_positions:
            current_qty, avg_price = self.short_positions[asset.id]
            total_value = (current_qty * avg_price) + (quantity * price)
            new_qty = current_qty + quantity
            new_avg_price = total_value / new_qty
            self.short_positions[asset.id] = (new_qty, new_avg_price)
        else:
            self.short_positions[asset.id] = (quantity, price)

        self.trade_history.append((
            datetime.now(),
            TradeType.SHORT,
            asset.id,
            quantity,
            price
        ))

        return True

    def cover_asset(self, asset: 'Asset', quantity: float, price: float) -> bool:
        if asset.id not in self.short_positions:
            return False

        current_qty, short_price = self.short_positions[asset.id]

        if quantity > current_qty:
            return False

        # Розрахунок прибутку/збитку
        profit = quantity * (short_price - price)
        # Повернення застави (50% від початкової позиції) + прибуток
        collateral_return = (quantity * short_price * 0.5) + profit

        self.capital += collateral_return

        if quantity == current_qty:
            del self.short_positions[asset.id]
        else:
            self.short_positions[asset.id] = (current_qty - quantity, short_price)

        self.trade_history.append((
            datetime.now(),
            TradeType.COVER,
            asset.id,
            quantity,
            price
        ))

        return True

    def receive_investment(self, investor_id: str, amount: float) -> bool:
        self.capital += amount

        if investor_id in self.investor_funds:
            self.investor_funds[investor_id] += amount
        else:
            self.investor_funds[investor_id] = amount

        return True

    def return_investment(self, investor_id: str, amount: float) -> bool:
        if investor_id not in self.investor_funds or self.investor_funds[investor_id] < amount:
            return False

        if amount > self.capital:
            return False

        self.capital -= amount
        self.investor_funds[investor_id] -= amount

        if self.investor_funds[investor_id] == 0:
            del self.investor_funds[investor_id]

        return True

    def spread_rumor(self, market: 'Market', asset: 'Asset', rumor_type: RumorType,
                     content: str, is_true: bool) -> bool:
        # Шанс розкриття прив'язаний до репутації; логіка використовується в Rumor

        command = SpreadRumorCommand(
            self, market, asset, rumor_type, content, is_true
        )

        if command.execute():
            # Неправдиві чутки погіршують репутацію, якщо розкриті
            if not is_true and command.rumor.is_discovered:
                self.reputation = max(0.0, self.reputation - 0.2)
                # Можливий арешт, якщо репутація занадто погана
                if self.reputation == 0.0:
                    self.prison = True
                    self.game_over = True
            return True
        return False

    def calculate_net_worth(self, market: 'Market') -> float:
        net_worth = self.capital

        # Додавання вартості портфеля
        for asset_id, quantity in self.portfolio.items():
            if asset_id in market.assets:
                net_worth += quantity * market.assets[asset_id].current_price

        # Віднімання короткої позиції
        for asset_id, (quantity, _) in self.short_positions.items():
            if asset_id in market.assets:
                # Зобов'язання покрити короткі позиції за поточною ціною
                net_worth -= quantity * market.assets[asset_id].current_price

        # Віднімання інвестиційних зобов'язань
        for investor_id, amount in self.investor_funds.items():
            net_worth -= amount

        return net_worth

    def check_margin_call(self, market: 'Market') -> bool:
        # Перевірка, чи не впав капітал нижче мінімальної застави для коротких позицій
        required_margin = 0

        for asset_id, (quantity, _) in self.short_positions.items():
            if asset_id in market.assets:
                required_margin += quantity * market.assets[asset_id].current_price * 0.4

        if required_margin > 0 and self.capital < required_margin:
            # Автоматична ліквідація коротких позицій
            for asset_id, (quantity, _) in list(self.short_positions.items()):
                if asset_id in market.assets:
                    self.cover_asset(market.assets[asset_id], quantity, market.assets[asset_id].current_price)

            # Перевірка банкрутства
            if self.capital <= 0:
                self.game_over = True

            return True
        return False
