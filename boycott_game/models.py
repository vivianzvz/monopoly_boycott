from otree.api import *
import random

doc = """
Monopolist Boycott Game:
- One monopolist, multiple consumers.
- No communication for rounds 1–5.
- Chat available to consumers in rounds 6–20.
- Monopolist sets price, consumers decide whether to buy.
"""

class C(BaseConstants):
    name_in_url = 'boycott_game'
    players_per_group = 3  # 1 monopolist + 2 consumers
    num_rounds = 10
Constants = C

class Subsession(BaseSubsession):
    def creating_session(self):
        players = self.get_players()

        # Assign roles: first player is monopolist, rest are consumers
        players[0].player_role = 'monopolist'
        for p in players[1:]:
            p.player_role = 'consumer'

        for p in players:
           if p.player_role == 'consumer':
               if self.round_number == 1:
                   p.participant.vars['endowment'] = random.choice([113, 116, 119, 122, 125])
               p.endowment = p.participant.vars['endowment']


class Group(BaseGroup):
    def set_payoffs(self):
        buyers = [p for p in self.get_players() if p.player_role == 'consumer' and p.buy_choice == 'buy']
        monopolist = [p for p in self.get_players() if p.player_role == 'monopolist'][0]
        num_buyers = len(buyers)

        # Safely access possibly null field
        price = getattr(monopolist, 'price', None)
        if price is None:
            # Avoid crashing; maybe set to 0 or log warning
            monopolist.payoff = 0
            for p in self.get_players():
                p.payoff = 0
            return

        for p in buyers:
            p.payoff = p.endowment - price
        for p in self.get_players():
            if p.role() == 'consumer' and p.buy_choice != 'buy':
                p.payoff = 0  # no purchase = no points

        monopolist.payoff = price * num_buyers

class Player(BasePlayer):
    player_role = models.StringField()

    # Only for consumers
    endowment = models.CurrencyField()
    buy_choice = models.StringField(
        choices=[('buy', 'Buy'), ('no_buy', 'No Buy')],
        widget=widgets.RadioSelect,
        label="Do you want to buy the monopolist's product?"
    )

    # Only for monopolist
    price = models.CurrencyField(blank=True)

    # Live chat: consumers only
    def live_chat(self, data):
        consumers = [p for p in self.group.get_players() if p.player_role == 'consumer']
        consumer_number = consumers.index(self) + 1  # 1-based index
        msg = f"Consumer {consumer_number}: {data['msg']}"
        return {
            p.id_in_group: {'msg': msg}
            for p in consumers
        }

    def role(self):
        return self.player_role
