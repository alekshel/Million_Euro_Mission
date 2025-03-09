import os
from typing import TYPE_CHECKING

from utils.enums import RumorType

if TYPE_CHECKING:
    from game.trading_game import TradingGame


class TextInterface:
    def __init__(self, game: 'TradingGame'):
        self.game = game

    @staticmethod
    def clear_screen():
        os.system('cls' if os.name == 'nt' else 'clear')

    def display_market(self) -> str:
        """Відображення стану ринку"""
        output = [f"{'=' * 60}", f"{'БІРЖОВИЙ СИМУЛЯТОР':^60}", f"{'=' * 60}",
                  f"ДЕНЬ: {self.game.market.day:<10} СТАН РИНКУ: {self.game.market.current_state.get_name()}",
                  f"{'-' * 60}", f"{'АКТИВИ:':<60}", f"{'-' * 60}",
                  f"{'НАЗВА':<30} {'ТІКЕР':<10} {'ЦІНА':<10} {'ЗМІНА':>8}", f"{'-' * 60}"]

        for asset in self.game.market.assets.values():
            price_change = 0
            if len(asset.price_history) > 1:
                prev_price = asset.price_history[-2][1]
                price_change = ((asset.current_price - prev_price) / prev_price) * 100

            change_str = f"{price_change:+.2f}%"
            output.append(f"{asset.name:<30} {asset.ticker:<10} ₴{asset.current_price:<10.2f} {change_str:>8}")

        output.append("\nПОДІЇ:")
        active_events = [e for e in self.game.market.events if e.is_active()]

        if active_events:
            for event in active_events:
                output.append(f"- {event.title}: {event.description} "
                              f"(Вплив: {event.impact:+.2f}%, "
                              f"Залишилось днів: {event.remaining_duration})")
        else:
            output.append("- Немає активних подій")

        output.append("\nЧУТКИ:")
        recent_rumors = self.game.market.rumors[-3:]  # Останні 3 чутки

        if recent_rumors:
            for rumor in recent_rumors:
                status = "Спростовано" if rumor.is_discovered else "Активна"

                asset_name = "Невідомий актив"
                if rumor.asset_id in self.game.market.assets:
                    asset_name = self.game.market.assets[rumor.asset_id].name

                output.append(f"- {rumor.content} (Актив: {asset_name}, Статус: {status})")
        else:
            output.append("- Немає активних чуток")

        return "\n".join(output)

    def display_player_info(self, player_index: int) -> str:
        player = self.game.players[player_index]

        net_worth = player.calculate_net_worth(self.game.market)

        output = [
            f"{'-' * 60}",
            f"{'ІНФОРМАЦІЯ ПРО ГРАВЦЯ':^60}",
            f"{'-' * 60}",
            f"ГРАВЕЦЬ: {player.name:<20}",
            f"КАПІТАЛ: ₴{player.capital:<15.2f} РЕПУТАЦІЯ: {player.reputation:.2f}",
            f"ЧИСТА ВАРТІСТЬ: ₴{net_worth:<15.2f}",
            f"{'-' * 60}",
            f"{'ПОРТФЕЛЬ АКТИВІВ':^60}",
            f"{'-' * 60}"
        ]

        if player.portfolio:
            for asset_id, quantity in player.portfolio.items():
                if asset_id in self.game.market.assets:
                    asset = self.game.market.assets[asset_id]
                    value = quantity * asset.current_price
                    output.append(f"- {asset.name} ({asset.ticker}): {quantity} акцій = ₴{value:.2f}")
        else:
            output.append("- Порожній портфель")

        output.append("\nІНВЕСТИЦІЇ:")
        if player.investor_funds:
            for investor_id, amount in player.investor_funds.items():
                investor_name = "Невідомий інвестор"
                for investor in self.game.investors:
                    if investor.id == investor_id:
                        investor_name = investor.name
                output.append(f"- Від {investor_name}: ₴{amount:.2f}")
        else:
            output.append("- Немає залучених інвестицій")

        output.append("\nПОВІДОМЛЕННЯ:")
        if player.notifications:
            for notification in player.notifications[-5:]:  # Останні 5 повідомлень
                output.append(f"- {notification}")
        else:
            output.append("- Немає нових повідомлень")

        return "\n".join(output)

    @staticmethod
    def display_menu() -> str:
        return (
            "\nДОСТУПНІ ДІЇ:\n"
            "1. Купити актив\n"
            "2. Продати актив\n"
            "3. Поширити чутку\n"
            "4. Залучити інвестиції\n"
            "5. Повернути інвестиції\n"
            "6. Наступний день\n"
            "7. Зберегти гру\n"
            "0. Вийти з гри\n"
            "\nВаш вибір: "
        )

    def process_menu_choice(self, choice: str, player_index: int) -> bool:
        player = self.game.players[player_index]

        if player.game_over:
            print(f"{player.name} вибув з гри!")
            return True

        if choice == "1":
            print("\nДоступні активи:")
            for i, asset in enumerate(self.game.market.assets.values()):
                print(f"{i + 1}. {asset.name} ({asset.ticker}): ₴{asset.current_price:.2f}")

            asset_choice = input("Виберіть номер активу (або 0 для скасування): ")
            if asset_choice == "0" or not asset_choice.isdigit():
                return False

            asset_index = int(asset_choice) - 1
            if 0 <= asset_index < len(self.game.market.assets):
                asset = list(self.game.market.assets.values())[asset_index]

                max_shares = int(player.capital / asset.current_price)
                print(f"У вас є ₴{player.capital:.2f}. Ви можете купити до {max_shares} акцій.")

                quantity_str = input(f"Скільки акцій {asset.ticker} ви хочете купити?: ")
                if not quantity_str.isdigit():
                    return False

                quantity = int(quantity_str)
                if quantity <= 0:
                    return False

                success = self.game.player_turn(
                    player_index,
                    "buy",
                    asset_id=asset.id,
                    quantity=quantity
                )

                if success:
                    print(f"Успішно куплено {quantity} акцій {asset.ticker} за ₴{asset.current_price * quantity:.2f}")
                else:
                    print("Не вдалося виконати покупку. Перевірте, чи вистачає коштів.")
                input("\nНатисніть Enter для продовження...")

        elif choice == "2":
            if not player.portfolio:
                print("У вас немає активів для продажу!")
                return False

            print("\nВаш портфель:")
            portfolio_assets = []

            for i, (asset_id, quantity) in enumerate(player.portfolio.items()):
                if asset_id in self.game.market.assets:
                    asset = self.game.market.assets[asset_id]
                    portfolio_assets.append(asset)
                    value = quantity * asset.current_price
                    print(f"{i + 1}. {asset.name} ({asset.ticker}): {quantity} акцій = ₴{value:.2f}")

            asset_choice = input("Виберіть номер активу для продажу (або 0 для скасування): ")
            if asset_choice == "0" or not asset_choice.isdigit():
                return False

            asset_index = int(asset_choice) - 1
            if 0 <= asset_index < len(portfolio_assets):
                asset = portfolio_assets[asset_index]
                current_quantity = player.portfolio[asset.id]

                quantity_str = input(f"Скільки акцій {asset.ticker} ви хочете продати? (У вас є {current_quantity}): ")
                if not quantity_str.isdigit():
                    return False

                quantity = int(quantity_str)
                if quantity <= 0 or quantity > current_quantity:
                    return False

                success = self.game.player_turn(
                    player_index,
                    "sell",
                    asset_id=asset.id,
                    quantity=quantity
                )

                if success:
                    print(f"Успішно продано {quantity} акцій {asset.ticker} за ₴{asset.current_price * quantity:.2f}")
                else:
                    print("Не вдалося виконати продаж.")
                input("\nНатисніть Enter для продовження...")

        elif choice == "3":
            # Поширення чутки
            print("\nПоширення чутки про актив")
            print("Ваша репутація:", player.reputation)

            if player.reputation < 0.2:
                print("Ваша репутація занадто низька, щоб поширювати чутки!")
                return False

            print("\nВиберіть актив для чутки:")
            for i, asset in enumerate(self.game.market.assets.values()):
                print(f"{i + 1}. {asset.name} ({asset.ticker})")

            asset_choice = input("Виберіть номер активу (або 0 для скасування): ")
            if asset_choice == "0" or not asset_choice.isdigit():
                return False

            asset_index = int(asset_choice) - 1
            if 0 <= asset_index < len(self.game.market.assets):
                asset = list(self.game.market.assets.values())[asset_index]

                print("\nТип чутки:")
                for i, rumor_type in enumerate(RumorType):
                    print(f"{i + 1}. {rumor_type.value}")

                rumor_type_choice = input("Виберіть тип чутки: ")
                if not rumor_type_choice.isdigit():
                    return False

                rumor_type_index = int(rumor_type_choice) - 1
                if 0 <= rumor_type_index < len(RumorType):
                    rumor_type = list(RumorType)[rumor_type_index]

                    content = input("Введіть зміст чутки: ")
                    if not content:
                        return False

                    truth_choice = input("Це правдива чутка? (т/н): ").lower()
                    is_true = truth_choice == "т"

                    success = self.game.player_turn(
                        player_index,
                        "spread_rumor",
                        asset_id=asset.id,
                        rumor_type=rumor_type,
                        content=content,
                        is_true=is_true
                    )

                    if success:
                        print(f"Чутка успішно поширена!")
                        if not is_true:
                            print("УВАГА: Якщо ця неправдива чутка буде розкрита, ваша репутація постраждає!")
                    else:
                        print("Не вдалося поширити чутку.")
                    input("\nНатисніть Enter для продовження...")

        elif choice == "4":
            # Залучення інвестицій
            if not self.game.investors:
                print("Немає доступних інвесторів!")
                return False

            print("\nДоступні інвестори:")
            for i, investor in enumerate(self.game.investors):
                satisfaction_status = "Дуже задоволений" if investor.satisfaction > 0.8 else \
                    "Задоволений" if investor.satisfaction > 0.5 else \
                        "Незадоволений"

                risk_profile = "Агресивний" if investor.risk_tolerance > 0.7 else \
                    "Поміркований" if investor.risk_tolerance > 0.3 else \
                        "Консервативний"

                print(f"{i + 1}. {investor.name}: ₴{investor.capital:.2f} доступно, "
                      f"Статус: {satisfaction_status}, Профіль ризику: {risk_profile}")

            investor_choice = input("Виберіть номер інвестора (або 0 для скасування): ")
            if investor_choice == "0" or not investor_choice.isdigit():
                return False

            investor_index = int(investor_choice) - 1
            if 0 <= investor_index < len(self.game.investors):
                investor = self.game.investors[investor_index]

                amount_str = input(f"Скільки ви хочете залучити від {investor.name}? "
                                   f"(Доступно: ₴{investor.capital:.2f}): ")
                try:
                    amount = float(amount_str)
                except ValueError:
                    return False

                if amount <= 0 or amount > investor.capital:
                    return False

                success = self.game.player_turn(
                    player_index,
                    "get_investment",
                    investor_id=investor.id,
                    amount=amount
                )

                if success:
                    print(f"Успішно залучено ₴{amount:.2f} від {investor.name}!")
                    print("УВАГА: Ви повинні будете повернути ці кошти інвестору в майбутньому.")
                else:
                    print("Не вдалося залучити інвестиції.")

        elif choice == "5":
            # Повернення інвестицій
            if not player.investor_funds:
                print("У вас немає залучених інвестицій для повернення!")
                return False

            print("\nЗалучені інвестиції:")
            investors_data = []

            for i, (investor_id, amount) in enumerate(player.investor_funds.items()):
                investor_name = "Невідомий інвестор"
                for investor in self.game.investors:
                    if investor.id == investor_id:
                        investor_name = investor.name
                        investors_data.append((investor, amount))

                print(f"{i + 1}. {investor_name}: ₴{amount:.2f}")

            investor_choice = input("Виберіть номер інвестора для повернення коштів (або 0 для скасування): ")
            if investor_choice == "0" or not investor_choice.isdigit():
                return False

            investor_index = int(investor_choice) - 1
            if 0 <= investor_index < len(investors_data):
                investor, total_amount = investors_data[investor_index]

                amount_str = input(f"Скільки ви хочете повернути {investor.name}? "
                                   f"(Загальний борг: ₴{total_amount:.2f}): ")
                try:
                    amount = float(amount_str)
                except ValueError:
                    return False

                if amount <= 0 or amount > total_amount or amount > player.capital:
                    return False

                success = self.game.player_turn(
                    player_index,
                    "return_investment",
                    investor_id=investor.id,
                    amount=amount
                )

                if success:
                    print(f"Успішно повернуто ₴{amount:.2f} інвестору {investor.name}!")
                else:
                    print("Не вдалося повернути інвестиції.")

        elif choice == "6":
            # Наступний день
            self.game.next_day()

            # Очищення повідомлень у гравця
            player.notifications = []

            return True

        elif choice == "7":
            # Збереження гри
            filename = input("Введіть ім'я файлу для збереження: ")
            if not filename:
                filename = "trading_game_save.json"

            success = self.game.save_game(filename)
            if success:
                print(f"Гра успішно збережена у файл {filename}")
            else:
                print("Помилка при збереженні гри!")

        elif choice == "0":
            # Вихід з гри
            confirm = input("Ви впевнені, що хочете вийти з гри? (т/н): ").lower()
            if confirm == "т":
                print("Дякуємо за гру!")
                return True

        else:
            print("Невідомий вибір!")

        return False

    def run_game(self) -> None:
        self.game.start_game()

        running = True

        while running and not self.game.game_over:
            self.clear_screen()
            print("\n" + "=" * 50)
            print(self.display_market())

            # Перемикання між гравцями
            current_player_index = self.game.current_player_index

            print(self.display_player_info(current_player_index))

            next_turn = False
            while not next_turn:
                choice = input(self.display_menu())
                next_turn = self.process_menu_choice(choice, current_player_index)

                if self.game.game_over:
                    running = False
                    break

                if choice == "0" and next_turn:
                    running = False
                    break

            # Перехід до наступного гравця
            self.game.current_player_index = (current_player_index + 1) % len(self.game.players)

        # Завершення гри
        if self.game.game_over:
            print("\n=== ГРА ЗАКІНЧЕНА ===")

            # Рейтинг гравців за чистою вартістю
            players_ranking = []
            for player in self.game.players:
                net_worth = player.calculate_net_worth(self.game.market)
                status = "В'язниця" if player.prison else \
                    "Банкрут" if player.capital <= 0 else \
                        "Активний"
                players_ranking.append((player, net_worth, status))

            # Сортування за чистою вартістю у зворотному порядку
            players_ranking.sort(key=lambda x: x[1], reverse=True)

            print("\nРЕЙТИНГ ГРАВЦІВ:")
            for i, (player, net_worth, status) in enumerate(players_ranking):
                print(f"{i + 1}. {player.name}: Чиста вартість ₴{net_worth:.2f}, Статус: {status}")

            print("\nДякуємо за гру!")
