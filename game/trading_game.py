import random
from typing import Dict
from patterns.builder import ScenarioBuilder


class TradingGame:
    def __init__(self, scenario_builder: ScenarioBuilder = None):
        if scenario_builder is None:
            from models.market import Market

            self.market = Market()
            self.players = []
            self.investors = []
            self.story_events = []
        else:
            self.market, self.players, self.investors, self.story_events = scenario_builder.build()

        self.current_player_index = 0
        self.game_over = False

    def start_game(self) -> None:
        for event in self.story_events[:2]:  # Додаємо перші 2 події для початку гри
            self.market.add_event(event)
            self.story_events.remove(event)

    def next_day(self) -> None:
        self.market.update()
        self.market.generate_random_event()

        # Додавання запланованих сюжетних подій з певною ймовірністю
        if self.story_events and random.random() < 0.2:  # 20% шанс
            event = random.choice(self.story_events)
            self.market.add_event(event)
            self.story_events.remove(event)

        # Перевірка маржин-колів для всіх гравців
        for player in self.players:
            player.check_margin_call(self.market)

        self.check_game_over()

    def player_turn(self, player_index: int, action_type: str, **kwargs) -> bool:
        player = self.players[player_index]

        if player.game_over:
            return False

        if action_type == "buy":
            asset_id = kwargs.get("asset_id")
            quantity = kwargs.get("quantity", 0)

            if asset_id in self.market.assets:
                return player.buy_asset(
                    self.market.assets[asset_id],
                    quantity,
                    self.market.assets[asset_id].current_price
                )

        elif action_type == "sell":
            asset_id = kwargs.get("asset_id")
            quantity = kwargs.get("quantity", 0)

            if asset_id in self.market.assets:
                return player.sell_asset(
                    self.market.assets[asset_id],
                    quantity,
                    self.market.assets[asset_id].current_price
                )

        elif action_type == "short":
            asset_id = kwargs.get("asset_id")
            quantity = kwargs.get("quantity", 0)

            if asset_id in self.market.assets:
                return player.short_asset(
                    self.market.assets[asset_id],
                    quantity,
                    self.market.assets[asset_id].current_price
                )

        elif action_type == "cover":
            asset_id = kwargs.get("asset_id")
            quantity = kwargs.get("quantity", 0)

            if asset_id in self.market.assets:
                return player.cover_asset(
                    self.market.assets[asset_id],
                    quantity,
                    self.market.assets[asset_id].current_price
                )

        elif action_type == "spread_rumor":
            asset_id = kwargs.get("asset_id")
            rumor_type = kwargs.get("rumor_type")
            content = kwargs.get("content", "")
            is_true = kwargs.get("is_true", False)

            if asset_id in self.market.assets:
                return player.spread_rumor(
                    self.market,
                    self.market.assets[asset_id],
                    rumor_type,
                    content,
                    is_true
                )

        elif action_type == "get_investment":
            investor_id = kwargs.get("investor_id")
            amount = kwargs.get("amount", 0)

            for investor in self.investors:
                if investor.id == investor_id:
                    return investor.invest(player, amount)

        elif action_type == "return_investment":
            investor_id = kwargs.get("investor_id")
            amount = kwargs.get("amount", 0)

            for investor in self.investors:
                if investor.id == investor_id:
                    return player.return_investment(investor_id, amount)

        return False

    def check_game_over(self) -> None:
        # Гра закінчується, коли всі гравці виходять з гри
        all_game_over = True
        for player in self.players:
            if player.capital <= 0:
                player.game_over = True

            if not player.game_over:
                all_game_over = False

        self.game_over = all_game_over

    def save_game(self, filename: str) -> bool:
        from patterns.adapter import GameStateAdapter

        try:
            game_state = GameStateAdapter.serialize_game(self)

            with open(filename, 'w', encoding='utf-8') as f:
                import json
                json.dump(game_state, f, ensure_ascii=False, indent=2) # noqa

            return True
        except Exception as e:
            print(f"Помилка збереження гри: {e}")
            return False

    def load_game(self, filename: str) -> bool:
        from patterns.adapter import GameStateAdapter

        try:
            import json
            with open(filename, 'r', encoding='utf-8') as f:
                game_state = json.load(f)

            GameStateAdapter.deserialize_game(game_state, self)
            return True
        except Exception as e:
            print(f"Помилка завантаження гри: {e}")
            return False

    def modify_game_based_on_feedback(self, feedback_data: Dict) -> None:
        """Модифікація параметрів гри на основі зворотного зв'язку гравців"""

        # Налаштування складності
        if 'difficulty' in feedback_data:
            difficulty = feedback_data['difficulty']
            if difficulty == 'easier':
                # Зменшення волатильності ринку
                self.market.market_volatility *= 0.7
                # Збільшення стартового капіталу для нових гравців
                for player in self.players:
                    if player.capital < 5000:
                        player.capital = 5000
            elif difficulty == 'harder':
                # Збільшення волатильності ринку
                self.market.market_volatility *= 1.5
                # Зменшення шансу виявлення неправдивих чуток
                for rumor in self.market.rumors:
                    if not rumor.is_true:
                        rumor.discovered_chance *= 0.7

        # Коригування сюжетних подій
        if 'story_feedback' in feedback_data:
            story_feedback = feedback_data['story_feedback']

            # Додавання нових подій, якщо сюжет занадто передбачуваний
            if story_feedback == 'more_unpredictable':
                from models.event import Event
                from utils.enums import EventType

                # Додавання більш непередбачуваних подій з більшим впливом
                affected_assets = random.sample(list(self.market.assets.keys()),
                                                min(3, len(self.market.assets)))

                new_event = Event(
                    event_type=random.choice(list(EventType)),
                    title="Несподіваний поворот подій",
                    description="Раптова і неочікувана подія змінює стан ринку!",
                    impact=random.uniform(-10.0, 10.0),  # Значний вплив
                    duration=random.randint(3, 7),
                    affected_assets=affected_assets
                )

                self.story_events.append(new_event)

            # Видалення занадто нереалістичних подій
            elif story_feedback == 'more_realistic':
                # Фільтрування сюжетних подій, залишаючи лише більш реалістичні
                self.story_events = [e for e in self.story_events
                                     if abs(e.impact) < 5.0]  # Помірний вплив

        # Коригування механіки інвесторів
        if 'investor_mechanics' in feedback_data:
            investor_mechanics = feedback_data['investor_mechanics']

            if investor_mechanics == 'more_forgiving':
                # Робимо інвесторів більш лояльними
                for investor in self.investors:
                    investor.satisfaction = max(0.4, investor.satisfaction)
                    investor.risk_tolerance += 0.1

            elif investor_mechanics == 'more_demanding':
                # Робимо інвесторів більш вимогливими
                for investor in self.investors:
                    investor.satisfaction = min(0.8, investor.satisfaction)
                    investor.risk_tolerance -= 0.1
