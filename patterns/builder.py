from typing import List, Dict, Tuple, TYPE_CHECKING

if TYPE_CHECKING:
    from models.market import Market
    from models.player import Player, Investor
    from models.event import Event


class ScenarioBuilder:
    def __init__(self):
        from models.market import Market

        self.market = Market()
        self.players = []
        self.investors = []
        self.events = []

    def reset(self) -> None:
        from models.market import Market

        self.market = Market()
        self.players = []
        self.investors = []
        self.events = []

    def create_market(self) -> 'ScenarioBuilder':
        from models.market import Market

        self.market = Market()
        return self

    def add_player(self, name: str, initial_capital: float) -> 'ScenarioBuilder':
        from models.player import Player

        player = Player(name, initial_capital)
        self.players.append(player)
        self.market.attach(player)
        return self

    def add_investor(self, name: str, capital: float, risk_tolerance: float) -> 'ScenarioBuilder':
        from models.player import Investor

        investor = Investor(name, capital, risk_tolerance)
        self.investors.append(investor)
        return self

    def add_assets(self, assets_data: List[Dict]) -> 'ScenarioBuilder':
        from patterns.factory import AssetFactory

        for data in assets_data:
            asset = AssetFactory.create_asset(
                asset_type=data['type'],
                name=data['name'],
                ticker=data['ticker'],
                initial_price=data['price']
            )
            self.market.add_asset(asset)
        return self

    def add_events(self, events_data: List[Dict]) -> 'ScenarioBuilder':
        from models.event import Event

        for data in events_data:
            event = Event(
                event_type=data['type'],
                title=data['title'],
                description=data['description'],
                impact=data['impact'],
                duration=data['duration'],
                affected_assets=data['affected_assets']
            )
            self.events.append(event)
        return self

    def build(self) -> Tuple['Market', List['Player'], List['Investor'], List['Event']]:
        return self.market, self.players, self.investors, self.events
