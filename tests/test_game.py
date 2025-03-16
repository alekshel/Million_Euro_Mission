import unittest
from unittest.mock import MagicMock, patch
import json
import os
import tempfile
from game.trading_game import TradingGame
from patterns.builder import ScenarioBuilder


class TestTradingGame(unittest.TestCase):
    def setUp(self):
        self.mock_builder = MagicMock(spec=ScenarioBuilder)

        self.mock_market = MagicMock()
        self.mock_players = [MagicMock()]
        self.mock_investors = [MagicMock()]
        self.mock_events = [MagicMock()]

        self.mock_builder.build.return_value = (
            self.mock_market,
            self.mock_players,
            self.mock_investors,
            self.mock_events
        )

        self.game = TradingGame(self.mock_builder)

    def test_game_initialization(self):
        self.assertEqual(self.game.market, self.mock_market)
        self.assertEqual(self.game.players, self.mock_players)
        self.assertEqual(self.game.investors, self.mock_investors)
        self.assertEqual(self.game.story_events, self.mock_events)
        self.assertEqual(self.game.current_player_index, 0)
        self.assertFalse(self.game.game_over)

    def test_start_game(self):
        self.game.story_events = [MagicMock(), MagicMock(), MagicMock()]

        self.game.start_game()

        self.mock_market.add_event.assert_called()
        self.assertEqual(self.mock_market.add_event.call_count, 2)

        self.assertEqual(len(self.game.story_events), 1)

    def test_next_day(self):
        mock_player = MagicMock()
        mock_player.capital = 1000.0
        mock_player.game_over = False
        self.game.players = [mock_player]

        self.game.next_day()

        self.mock_market.update.assert_called_once()
        self.mock_market.generate_random_event.assert_called_once()

        mock_player.check_margin_call.assert_called_once_with(self.mock_market)

    def test_player_turn_buy(self):
        mock_player = MagicMock()
        mock_player.game_over = False
        mock_player.buy_asset.return_value = True

        mock_asset = MagicMock()
        mock_asset.current_price = 100.0

        self.game.players = [mock_player]
        self.game.market.assets = {"asset1": mock_asset}

        result = self.game.player_turn(0, "buy", asset_id="asset1", quantity=10)

        self.assertTrue(result)
        mock_player.buy_asset.assert_called_once_with(mock_asset, 10, mock_asset.current_price)

    def test_player_turn_sell(self):
        mock_player = MagicMock()
        mock_player.game_over = False
        mock_player.sell_asset.return_value = True

        mock_asset = MagicMock()
        mock_asset.current_price = 120.0

        self.game.players = [mock_player]
        self.game.market.assets = {"asset1": mock_asset}

        result = self.game.player_turn(0, "sell", asset_id="asset1", quantity=5)

        self.assertTrue(result)
        mock_player.sell_asset.assert_called_once_with(mock_asset, 5, mock_asset.current_price)

    def test_player_turn_game_over(self):
        mock_player = MagicMock()
        mock_player.game_over = True

        self.game.players = [mock_player]

        result = self.game.player_turn(0, "buy", asset_id="asset1", quantity=10)

        self.assertFalse(result)

    def test_check_game_over(self):
        mock_player1 = MagicMock()
        mock_player1.capital = 0.0  # Банкрут
        mock_player1.game_over = False

        mock_player2 = MagicMock()
        mock_player2.capital = 10000.0  # Активний гравець
        mock_player2.game_over = False

        self.game.players = [mock_player1, mock_player2]

        self.game.check_game_over()

        self.assertTrue(mock_player1.game_over)
        self.assertFalse(mock_player2.game_over)
        self.assertFalse(self.game.game_over)

        mock_player2.game_over = True

        self.game.check_game_over()

        self.assertTrue(self.game.game_over)

    def test_save_game(self):
        with patch('patterns.adapter.GameStateAdapter') as mock_adapter:
            mock_adapter.serialize_game.return_value = {"test": "data"}

            with tempfile.NamedTemporaryFile(mode='w+', delete=False) as temp:
                try:
                    self.game.save_game(temp.name)

                    mock_adapter.serialize_game.assert_called_once_with(self.game)

                    with open(temp.name, 'r') as f:
                        saved_data = json.load(f)
                        self.assertEqual(saved_data, {"test": "data"})
                finally:
                    os.unlink(temp.name)

    def test_load_game(self):
        with patch('patterns.adapter.GameStateAdapter') as mock_adapter:
            with tempfile.NamedTemporaryFile(mode='w+', delete=False) as temp:
                try:
                    json.dump({"test": "data"}, temp)
                    temp.flush()

                    result = self.game.load_game(temp.name)

                    mock_adapter.deserialize_game.assert_called_once()
                    args = mock_adapter.deserialize_game.call_args
                    self.assertEqual(args[0][0], {"test": "data"})
                    self.assertEqual(args[0][1], self.game)

                    self.assertTrue(result)
                finally:
                    os.unlink(temp.name)

    def test_modify_game_based_on_feedback(self):
        mock_rumor1 = MagicMock()
        mock_rumor1.is_true = False
        mock_rumor1.discovered_chance = 0.3

        mock_rumor2 = MagicMock()
        mock_rumor2.is_true = True

        self.mock_market.rumors = [mock_rumor1, mock_rumor2]
        self.mock_market.market_volatility = 1.0

        mock_player = MagicMock()
        mock_player.capital = 1000.0
        self.game.players = [mock_player]

        mock_investor = MagicMock()
        mock_investor.satisfaction = 0.3
        mock_investor.risk_tolerance = 0.5
        self.game.investors = [mock_investor]

        feedback_data = {
            'difficulty': 'easier',
            'investor_mechanics': 'more_forgiving'
        }

        self.game.modify_game_based_on_feedback(feedback_data)

        # Перевірка змін складності гри
        self.assertEqual(self.mock_market.market_volatility, 0.7)  # Зменшено на 30%
        self.assertEqual(mock_player.capital, 5000.0)  # Збільшено до мінімуму 5000

        # Перевірка змін механіки інвесторів
        self.assertEqual(mock_investor.satisfaction, 0.4)  # Збільшено до мінімуму 0.4
        self.assertEqual(mock_investor.risk_tolerance, 0.6)  # Збільшено на 0.1


if __name__ == '__main__':
    unittest.main()
