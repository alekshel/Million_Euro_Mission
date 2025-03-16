import unittest
from models.asset import Stock, Cryptocurrency, ForexPair, Commodity


class TestAssets(unittest.TestCase):
    def setUp(self):
        # Створюємо тестові активи для перевірки
        self.stock = Stock("Test Company", "TST", 100.0)
        self.crypto = Cryptocurrency("Test Coin", "TCC", 10000.0)
        self.forex = ForexPair("Euro/Dollar", "EUR/USD", 1.12)
        self.commodity = Commodity("Gold", "XAU", 1900.0)

    def test_asset_initialization(self):
        self.assertEqual(self.stock.name, "Test Company")
        self.assertEqual(self.stock.ticker, "TST")
        self.assertEqual(self.stock.current_price, 100.0)
        self.assertEqual(self.stock.initial_price, 100.0)

        # Перевірка створення унікальних ID
        self.assertNotEqual(self.stock.id, self.crypto.id)

    def test_price_history(self):
        self.assertEqual(len(self.stock.price_history), 1)
        initial_price = self.stock.price_history[0][1]
        self.assertEqual(initial_price, 100.0)

    def test_update_price(self):
        original_price = self.stock.current_price
        self.stock.update_price(10)  # 10% зростання

        # Перевірка нової ціни (з урахуванням коефіцієнту здоров'я компанії)
        self.assertGreater(self.stock.current_price, original_price)
        self.assertEqual(len(self.stock.price_history), 2)

    def test_negative_price_update(self):
        original_price = self.stock.current_price
        self.stock.update_price(-10)  # 10% падіння

        # Перевірка нової ціни
        self.assertLess(self.stock.current_price, original_price)

    def test_crypto_volatility(self):
        stock_original = self.stock.current_price
        crypto_original = self.crypto.current_price

        self.stock.update_price(5)
        self.crypto.update_price(5)

        # Зміна ціни криптовалюти повинна бути більшою через вищу волатильність
        stock_change = (self.stock.current_price - stock_original) / stock_original
        crypto_change = (self.crypto.current_price - crypto_original) / crypto_original

        self.assertGreater(crypto_change, stock_change)

    def test_forex_stability(self):
        forex_original = self.forex.current_price
        crypto_original = self.crypto.current_price

        percent_change = 5
        self.forex.update_price(percent_change)
        self.crypto.update_price(percent_change)

        # Зміна ціни форекса повинна бути меншою через вищу стабільність
        forex_change = (self.forex.current_price - forex_original) / forex_original
        crypto_change = (self.crypto.current_price - crypto_original) / crypto_original

        self.assertLess(forex_change, crypto_change)

    def test_event_impact(self):
        original_price = self.stock.current_price
        impact = 5.0  # 5% зростання

        self.stock.apply_event_impact(impact)

        # Перевірка нової ціни
        self.assertGreater(self.stock.current_price, original_price)

    def test_rumor_impact(self):
        # Спочатку скидаємо ціну до початкової
        self.stock.current_price = self.stock.initial_price

        # Застосовуємо вплив події
        event_impact = 10.0
        self.stock.apply_event_impact(event_impact)
        event_price = self.stock.current_price

        # Скидаємо ціну знову
        self.stock.current_price = self.stock.initial_price

        # Застосовуємо вплив чутки з таким самим значенням
        self.stock.apply_rumor_impact(event_impact)
        rumor_price = self.stock.current_price

        # Чутка має менший вплив
        event_change = (event_price - self.stock.initial_price)
        rumor_change = (rumor_price - self.stock.initial_price)

        self.assertLess(rumor_change, event_change)


if __name__ == '__main__':
    unittest.main()
