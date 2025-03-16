import unittest
from unittest.mock import MagicMock
from models.player import Player, Investor
from models.asset import Stock


class TestPlayer(unittest.TestCase):
    def setUp(self):
        self.mock_mediator = MagicMock()
        self.player = Player("Test Player", 10000.0)
        self.player.capital = 10000.0

        self.test_asset = Stock("Test Company", "TST", 100.0)

    def test_player_initialization(self):
        self.assertEqual(self.player.name, "Test Player")
        self.assertEqual(self.player.capital, 10000.0)
        self.assertEqual(self.player.reputation, 0.5)
        self.assertFalse(self.player.game_over)
        self.assertFalse(self.player.prison)
        self.assertEqual(len(self.player.portfolio), 0)

    def test_buy_asset(self):
        initial_capital = self.player.capital

        quantity = 10
        result = self.player.buy_asset(self.test_asset, quantity, self.test_asset.current_price)

        self.assertTrue(result)
        self.assertEqual(self.player.capital, initial_capital - (quantity * self.test_asset.current_price))
        self.assertIn(self.test_asset.id, self.player.portfolio)
        self.assertEqual(self.player.portfolio[self.test_asset.id], quantity)

    def test_buy_asset_insufficient_funds(self):
        self.player.capital = 50.0

        quantity = 10
        result = self.player.buy_asset(self.test_asset, quantity, self.test_asset.current_price)

        self.assertFalse(result)
        self.assertEqual(self.player.capital, 50.0)
        self.assertNotIn(self.test_asset.id, self.player.portfolio)

    def test_sell_asset(self):
        quantity = 10
        self.player.buy_asset(self.test_asset, quantity, self.test_asset.current_price)

        capital_after_purchase = self.player.capital

        sell_quantity = 5
        result = self.player.sell_asset(self.test_asset, sell_quantity, self.test_asset.current_price)

        self.assertTrue(result)
        self.assertEqual(self.player.capital, capital_after_purchase + (sell_quantity * self.test_asset.current_price))
        self.assertEqual(self.player.portfolio[self.test_asset.id], quantity - sell_quantity)

    def test_sell_asset_not_owned(self):
        result = self.player.sell_asset(self.test_asset, 5, self.test_asset.current_price)
        self.assertFalse(result)

    def test_sell_asset_insufficient_quantity(self):
        # Спочатку купуємо актив
        quantity = 3
        self.player.buy_asset(self.test_asset, quantity, self.test_asset.current_price)

        # Спроба продати більше, ніж у нас є
        result = self.player.sell_asset(self.test_asset, quantity + 2, self.test_asset.current_price)

        # Перевірка результатів
        self.assertFalse(result)
        self.assertEqual(self.player.portfolio[self.test_asset.id], quantity)

    def test_net_worth_calculation(self):
        # Купуємо актив
        quantity = 10
        self.player.buy_asset(self.test_asset, quantity, self.test_asset.current_price)

        mock_market = MagicMock()
        mock_market.assets = {self.test_asset.id: self.test_asset}

        # Змінюємо ціну активу
        self.test_asset.current_price = 120.0

        # Отримуємо чисту вартість
        net_worth = self.player.calculate_net_worth(mock_market)

        # Очікувана чиста вартість = капітал + вартість портфеля
        expected_portfolio_value = quantity * self.test_asset.current_price
        expected_net_worth = self.player.capital + expected_portfolio_value

        self.assertEqual(net_worth, expected_net_worth)

    def test_receive_investment(self):
        investor_id = "inv123"
        amount = 5000.0
        initial_capital = self.player.capital

        result = self.player.receive_investment(investor_id, amount)

        self.assertTrue(result)
        self.assertEqual(self.player.capital, initial_capital + amount)
        self.assertIn(investor_id, self.player.investor_funds)
        self.assertEqual(self.player.investor_funds[investor_id], amount)

    def test_return_investment(self):
        # Спочатку отримуємо інвестицію
        investor_id = "inv123"
        amount = 5000.0
        self.player.receive_investment(investor_id, amount)

        # Запам'ятовуємо стан після отримання інвестиції
        capital_with_investment = self.player.capital

        # Повертаємо частину інвестиції
        return_amount = 2000.0
        result = self.player.return_investment(investor_id, return_amount)

        # Перевірка результатів
        self.assertTrue(result)
        self.assertEqual(self.player.capital, capital_with_investment - return_amount)
        self.assertEqual(self.player.investor_funds[investor_id], amount - return_amount)

    def test_return_investment_more_than_received(self):
        # Спочатку отримуємо інвестицію
        investor_id = "inv123"
        amount = 1000.0
        self.player.receive_investment(investor_id, amount)

        # Спроба повернути більше, ніж було отримано
        result = self.player.return_investment(investor_id, amount + 500.0)

        # Перевірка результатів
        self.assertFalse(result)
        self.assertEqual(self.player.investor_funds[investor_id], amount)

    def test_return_investment_insufficient_funds(self):
        # Спочатку отримуємо інвестицію
        investor_id = "inv123"
        amount = 5000.0
        self.player.receive_investment(investor_id, amount)

        # Зменшуємо капітал гравця
        self.player.capital = 1000.0

        # Спроба повернути більше, ніж є у гравця
        result = self.player.return_investment(investor_id, 2000.0)

        # Перевірка результатів
        self.assertFalse(result)
        self.assertEqual(self.player.investor_funds[investor_id], amount)


class TestInvestor(unittest.TestCase):
    def setUp(self):
        self.investor = Investor("Test Investor", 50000.0, 0.5)
        self.player = Player("Test Player", 10000.0)

    def test_investor_initialization(self):
        self.assertEqual(self.investor.name, "Test Investor")
        self.assertEqual(self.investor.capital, 50000.0)
        self.assertEqual(self.investor.risk_tolerance, 0.5)
        self.assertEqual(self.investor.satisfaction, 1.0)
        self.assertEqual(len(self.investor.investment_history), 0)

    def test_invest(self):
        amount = 10000.0
        initial_investor_capital = self.investor.capital
        initial_player_capital = self.player.capital

        self.player.receive_investment = MagicMock(return_value=True)

        result = self.investor.invest(self.player, amount)

        self.assertTrue(result)
        self.assertEqual(self.investor.capital, initial_investor_capital - amount)
        self.player.receive_investment.assert_called_once_with(self.investor.id, amount)
        self.assertEqual(len(self.investor.investment_history), 1)

    def test_invest_insufficient_funds(self):
        amount = 60000.0  # Більше, ніж є в інвестора

        result = self.investor.invest(self.player, amount)

        self.assertFalse(result)
        self.assertEqual(self.investor.capital, 50000.0)
        self.assertEqual(len(self.investor.investment_history), 0)

    def test_update_satisfaction_better_than_expected(self):
        # Встановлюємо початкову задоволеність
        self.investor.satisfaction = 0.5

        # Очікувана прибутковість для ризику 0.5 = 0.05 + (0.5 * 0.15) = 0.125 = 12.5%
        # Якщо повернення вище - задоволеність зростає
        self.investor.update_satisfaction(0.15)  # 15%

        # Перевірка, що задоволеність зросла, але не більше 1.0
        self.assertGreater(self.investor.satisfaction, 0.5)
        self.assertLessEqual(self.investor.satisfaction, 1.0)

    def test_update_satisfaction_worse_than_expected(self):
        # Встановлюємо початкову задоволеність
        self.investor.satisfaction = 0.8

        # Очікувана прибутковість для ризику 0.5 = 0.05 + (0.5 * 0.15) = 0.125 = 12.5%
        # Якщо повернення нижче - задоволеність падає
        self.investor.update_satisfaction(0.09)  # 9%

        # Перевірка, що задоволеність зменшилась, але не менше 0.0
        self.assertLess(self.investor.satisfaction, 0.8)
        self.assertGreaterEqual(self.investor.satisfaction, 0.0)


if __name__ == '__main__':
    unittest.main()
