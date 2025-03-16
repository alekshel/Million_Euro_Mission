import unittest
from unittest.mock import MagicMock, patch
from models.market import Market
from models.asset import Stock
from patterns.state import BullMarketState, BearMarketState, VolatileMarketState
from utils.enums import RumorType


class TestMarket(unittest.TestCase):
    def setUp(self):
        self.market = Market()

        self.test_asset = Stock("Test Company", "TST", 100.0)
        self.market.add_asset(self.test_asset)

        self.mock_player = MagicMock()
        self.mock_player.id = "player123"
        self.mock_player.reputation = 0.8

        self.market.attach(self.mock_player)

    def test_market_initialization(self):
        self.assertEqual(self.market.day, 1)
        self.assertIsInstance(self.market.current_state, BullMarketState)
        self.assertEqual(self.market.market_volatility, 0.5)
        self.assertEqual(len(self.market.assets), 1)
        self.assertEqual(len(self.market._observers), 1)

    def test_add_asset(self):
        new_asset = Stock("Another Company", "ANTR", 200.0)
        self.market.add_asset(new_asset)

        self.assertEqual(len(self.market.assets), 2)
        self.assertIn(new_asset.id, self.market.assets)

    def test_create_rumor_true(self):
        content = "Компанія планує збільшити дивіденди"

        # Встановлюємо високу репутацію для успішного створення чутки
        self.mock_player.reputation = 0.8

        self.market.rumors = []

        with patch.object(self.market, 'notify') as mock_notify:
            with patch.object(self.market.current_state, 'process_rumor') as mock_process:
                result = self.market.create_rumor(
                    self.mock_player,
                    self.test_asset,
                    RumorType.INSIDER,
                    content,
                    is_true=True
                )

                self.assertIsNotNone(result)

                self.assertEqual(len(self.market.rumors), 1)
                self.assertIs(self.market.rumors[0], result)

                created_rumor = self.market.rumors[0]
                self.assertEqual(created_rumor.creator_id, self.mock_player.id)
                self.assertEqual(created_rumor.asset_id, self.test_asset.id)
                self.assertEqual(created_rumor.content, content)
                self.assertEqual(created_rumor.is_true, True)

                mock_process.assert_called_once()

                mock_notify.assert_called_once()

    def test_create_rumor_false_low_reputation(self):
        self.mock_player.reputation = 0.1

        rumor = self.market.create_rumor(
            self.mock_player,
            self.test_asset,
            RumorType.NEWS_LEAK,
            "Фальшива новина",
            is_true=False
        )

        self.assertIsNone(rumor)

    def test_update_prices_bull_market(self):
        initial_price = self.test_asset.current_price

        self.market.update()

        self.assertEqual(self.market.day, 2)

        self.assertNotEqual(self.test_asset.current_price, initial_price)

    def test_change_market_state(self):
        # Початковий стан - бичачий
        self.assertIsInstance(self.market.current_state, BullMarketState)

        # Змінюємо на ведмежий
        bear_state = BearMarketState()
        self.market.change_state(bear_state)

        # Перевіряємо, що стан змінився і сповіщення відправлено
        self.assertIs(self.market.current_state, bear_state)
        self.mock_player.update.assert_called_with(self.market, market_state=bear_state.get_name())

    def test_price_changes_in_different_states(self):
        bull_state = BullMarketState()
        bear_state = BearMarketState()
        volatile_state = VolatileMarketState()

        asset1 = MagicMock()
        asset2 = MagicMock()
        asset3 = MagicMock()

        bull_market = MagicMock()
        bear_market = MagicMock()
        volatile_market = MagicMock()

        bull_market_assets = MagicMock()
        bull_market_assets.values.return_value = [asset1]
        bull_market.assets = bull_market_assets

        bear_market_assets = MagicMock()
        bear_market_assets.values.return_value = [asset2]
        bear_market.assets = bear_market_assets

        volatile_market_assets = MagicMock()
        volatile_market_assets.values.return_value = [asset3]
        volatile_market.assets = volatile_market_assets

        bull_state.update_prices(bull_market)
        bear_state.update_prices(bear_market)
        volatile_state.update_prices(volatile_market)

        asset1.update_price.assert_called_once()
        asset2.update_price.assert_called_once()
        asset3.update_price.assert_called_once()

        self.assertTrue(asset2.update_price.called, "Метод update_price не був викликаний для ведмежого ринку")

        with patch('random.uniform') as mock_uniform:
            mock_uniform.side_effect = [2.0, -1.5, 3.0]

            bull_state.update_prices(bull_market)
            bear_state.update_prices(bear_market)
            volatile_state.update_prices(volatile_market)

            bull_args = asset1.update_price.call_args_list[1][0][0]
            bear_args = asset2.update_price.call_args_list[1][0][0]
            volatile_args = asset3.update_price.call_args_list[1][0][0]

            self.assertGreater(bull_args, 0, "Бичачий ринок повинен давати позитивні зміни цін")
            self.assertLess(bear_args, 0, "Ведмежий ринок повинен давати негативні зміни цін")
            self.assertEqual(volatile_args, 3.0, "Волатильний ринок повинен давати очікувані зміни цін")


if __name__ == '__main__':
    unittest.main()
