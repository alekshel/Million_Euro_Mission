"""
Біржовий Симулятор - Інтерактивна гра про торгівлю на фінансових ринках
"""

import os
from game.trading_game import TradingGame
from game.interface import TextInterface
from game.scenario import create_default_scenario, create_hard_scenario, create_multiplayer_scenario


def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')


def main():
    clear_screen()
    print("=== БІРЖОВИЙ СИМУЛЯТОР ===")
    print("Ласкаво просимо до гри!")

    print("\n1. Нова гра (стандартний режим)")
    print("2. Нова гра (складний режим)")
    print("3. Нова гра (мультиплеєр)")
    print("4. Завантажити збережену гру")
    print("0. Вийти")

    choice = input("\nВаш вибір: ")

    if choice == "1":
        # Стандартний режим
        scenario_builder = create_default_scenario()
        game = TradingGame(scenario_builder)
        interface = TextInterface(game)
        interface.run_game()

    elif choice == "2":
        # Складний режим
        scenario_builder = create_hard_scenario()
        game = TradingGame(scenario_builder)
        interface = TextInterface(game)
        interface.run_game()

    elif choice == "3":
        # Мультиплеєр
        scenario_builder = create_multiplayer_scenario()
        game = TradingGame(scenario_builder)
        interface = TextInterface(game)
        interface.run_game()
    # Це if-else ladder, Conditional Complexity code smell. Треба застосовувати Chain of Responsibility

    elif choice == "4":
        # Завантаження гри
        saves_dir = "saves"

        # Створення директорії для збережень, якщо вона не існує
        if not os.path.exists(saves_dir):
            os.makedirs(saves_dir)

        save_files = [f for f in os.listdir(saves_dir) if f.endswith('.json')]
        # Опрацювання файлів, формат, що то за файли, де знаходяться - це деталі ралізації, що мають бути сховані в проміжних абстракціях - Pure Fabrication + Information Expert / Strategy Pattern

        if not save_files:
            print("Немає доступних збережених ігор!")
            input("Натисніть Enter для повернення в головне меню...")
            main()
            return

        print("\nДоступні збережені ігри:")
        for i, save_file in enumerate(save_files):
            print(f"{i+1}. {save_file}")

        save_choice = input("\nВиберіть файл для завантаження (або 0 для скасування): ")

        if save_choice == "0":
            main()
            return

        if not save_choice.isdigit() or int(save_choice) < 1 or int(save_choice) > len(save_files):
            print("Невірний вибір!")
            input("Натисніть Enter для повернення в головне меню...")
            main()
            return

        save_file = save_files[int(save_choice) - 1]
        save_path = os.path.join(saves_dir, save_file)

        game = TradingGame()
        success = game.load_game(save_path)

        if success:
            print(f"Гра успішно завантажена з файлу {save_file}")
            interface = TextInterface(game)
            interface.run_game()
        else:
            print("Не вдалося завантажити гру!")
            input("Натисніть Enter для повернення в головне меню...")
            main()

    elif choice == "0":
        print("До побачення!")

    else:
        print("Невідомий вибір!")
        input("Натисніть Enter для повернення в головне меню...")
        main()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nГра перервана. До побачення!")
    except Exception as e:
        print(f"\nСталася помилка: {e}")
        input("Натисніть Enter для закриття...")
