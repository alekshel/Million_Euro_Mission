from typing import Dict, TYPE_CHECKING

if TYPE_CHECKING:
    from game.trading_game import TradingGame


class GameStateAdapter:
    @staticmethod
    def serialize_game(game: 'TradingGame') -> Dict:
        game_state = {
            'day': game.market.day,
            'market_state': game.market.current_state.get_name(),
            'assets': [],
            'players': [],
            'investors': [],
            'events': [],
            'rumors': []
        }

        for asset in game.market.assets.values():
            asset_data = {
                'id': asset.id,
                'name': asset.name,
                'ticker': asset.ticker,
                'current_price': asset.current_price,
                'initial_price': asset.initial_price,
                'type': type(asset).__name__
            }
            game_state['assets'].append(asset_data)

        for player in game.players:
            player_data = {
                'id': player.id,
                'name': player.name,
                'capital': player.capital,
                'portfolio': player.portfolio,
                'short_positions': player.short_positions,
                'reputation': player.reputation,
                'investor_funds': player.investor_funds,
                'game_over': player.game_over,
                'prison': player.prison
            }
            game_state['players'].append(player_data)

        for investor in game.investors:
            investor_data = {
                'id': investor.id,
                'name': investor.name,
                'capital': investor.capital,
                'risk_tolerance': investor.risk_tolerance,
                'satisfaction': investor.satisfaction
            }
            game_state['investors'].append(investor_data)

        for event in game.market.events:
            if event.is_active():
                event_data = {
                    'id': event.id,
                    'type': event.event_type.name,
                    'title': event.title,
                    'description': event.description,
                    'impact': event.impact,
                    'duration': event.duration,
                    'remaining_duration': event.remaining_duration,
                    'affected_assets': event.affected_assets
                }
                game_state['events'].append(event_data)

        for rumor in game.market.rumors:
            rumor_data = {
                'id': rumor.id,
                'creator_id': rumor.creator_id,
                'asset_id': rumor.asset_id,
                'type': rumor.rumor_type.name,
                'content': rumor.content,
                'is_true': rumor.is_true,
                'credibility': rumor.credibility,
                'is_discovered': rumor.is_discovered
            }
            game_state['rumors'].append(rumor_data)

        return game_state

    @staticmethod
    def deserialize_game(game_state: Dict, game: 'TradingGame') -> None:
        """Відновлює стан гри з серіалізованого формату"""
        from patterns.state import MarketState
        from models.asset import Asset

        game.market.day = game_state['day']

        market_states = {
            cls.get_name(): cls for cls in [
                cls() for cls in MarketState.__subclasses__()
            ]
        }

        if game_state['market_state'] in market_states:
            game.market.current_state = market_states[game_state['market_state']]
        else:
            game.market.current_state = next(iter(market_states.values()))

        game.market.assets = {}
        for asset_data in game_state['assets']:
            asset_classes = {
                cls.__name__: cls for cls in Asset.__subclasses__()
            }

            if asset_data['type'] in asset_classes:
                asset_class = asset_classes[asset_data['type']]
                asset = asset_class(
                    asset_data['name'],
                    asset_data['ticker'],
                    asset_data['initial_price']
                )

                asset.id = asset_data['id']
                asset.current_price = asset_data['current_price']
                game.market.assets[asset.id] = asset
