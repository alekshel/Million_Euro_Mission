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
        from patterns.state import BullMarketState, BearMarketState, VolatileMarketState
        from models.asset import Stock, Cryptocurrency, ForexPair, Commodity
        from models.player import Player, Investor
        from models.event import Event, Rumor
        from utils.enums import EventType, RumorType

        game.market.day = game_state['day']

        if game_state['market_state'] == "Бичачий":
            game.market.current_state = BullMarketState()
        elif game_state['market_state'] == "Ведмежий":
            game.market.current_state = BearMarketState()
        elif game_state['market_state'] == "Волатильний":
            game.market.current_state = VolatileMarketState()

        game.market.assets = {}
        for asset_data in game_state['assets']:
            asset = None

            if asset_data['type'] == "Stock":
                asset = Stock(asset_data['name'], asset_data['ticker'], asset_data['initial_price'])
            elif asset_data['type'] == "Cryptocurrency":
                asset = Cryptocurrency(asset_data['name'], asset_data['ticker'], asset_data['initial_price'])
            elif asset_data['type'] == "ForexPair":
                asset = ForexPair(asset_data['name'], asset_data['ticker'], asset_data['initial_price'])
            elif asset_data['type'] == "Commodity":
                asset = Commodity(asset_data['name'], asset_data['ticker'], asset_data['initial_price'])

            asset.id = asset_data['id']
            asset.current_price = asset_data['current_price']
            game.market.assets[asset.id] = asset

        game.players = []
        for player_data in game_state['players']:
            player = Player(player_data['name'], player_data['capital'])
            player.id = player_data['id']
            player.portfolio = player_data['portfolio']
            player.short_positions = player_data['short_positions']
            player.reputation = player_data['reputation']
            player.investor_funds = player_data['investor_funds']
            player.game_over = player_data['game_over']
            player.prison = player_data['prison']
            game.players.append(player)
            game.market.attach(player)

        game.investors = []
        for investor_data in game_state['investors']:
            investor = Investor(
                investor_data['name'],
                investor_data['capital'],
                investor_data['risk_tolerance']
            )
            investor.id = investor_data['id']
            investor.satisfaction = investor_data['satisfaction']
            game.investors.append(investor)

        game.market.events = []
        for event_data in game_state['events']:
            event = Event(
                event_type=getattr(EventType, event_data['type']),
                title=event_data['title'],
                description=event_data['description'],
                impact=event_data['impact'],
                duration=event_data['duration'],
                affected_assets=event_data['affected_assets']
            )
            event.id = event_data['id']
            event.remaining_duration = event_data['remaining_duration']
            game.market.events.append(event)

        game.market.rumors = []
        for rumor_data in game_state['rumors']:
            rumor = Rumor(
                creator_id=rumor_data['creator_id'],
                asset_id=rumor_data['asset_id'],
                rumor_type=getattr(RumorType, rumor_data['type']),
                content=rumor_data['content'],
                is_true=rumor_data['is_true']
            )
            rumor.id = rumor_data['id']
            rumor.credibility = rumor_data['credibility']
            rumor.is_discovered = rumor_data['is_discovered']
            game.market.rumors.append(rumor)
