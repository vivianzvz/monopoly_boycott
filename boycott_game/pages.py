from otree.api import *
from . import *
from .models import C
from ._builtin import Page


class InstructionsNoChat(Page):
    def is_displayed(self):
        return self.round_number == 1

class InstructionsWithChat(Page):
    def is_displayed(self):
        return self.round_number == 6

class RolePageMonopolist(Page):
    def is_displayed(self):
        return self.round_number == 1 and self.player.player_role == 'monopolist'
    
class RolePageConsumer(Page):
    def is_displayed(self):
        return self.round_number == 1 and self.player.player_role == 'consumer'

class WaitForConsumers(WaitPage):
    def is_displayed(self):
        return self.player.player_role == 'consumer'

class ChatPage(Page):
    live_method = 'live_chat'
    timeout_seconds = 90

    def is_displayed(self):
        return self.player.player_role == 'consumer' and self.round_number >= 6

    def vars_for_template(self):
        monopolist = [p for p in self.group.get_players() if p.player_role == 'monopolist'][0]
        return dict(
            monopolist_price=getattr(monopolist, 'price', None),
            consumer_value=self.player.endowment
        )



class PriceDecision(Page):
    form_model = 'player'
    form_fields = ['price']
    timeout_seconds = 60

    def is_displayed(self):
        return self.player.player_role == 'monopolist'

    def vars_for_template(self):
        consumers = [p for p in self.group.get_players() if p.player_role == 'consumer']
        prior_rounds = self.player.in_previous_rounds()
        monopolist = [p for p in self.group.get_players() if p.player_role == 'monopolist'][0]

        history = []
        for past_player in prior_rounds:
            past_group = past_player.group
            past_monop = [p for p in past_group.get_players() if p.player_role == 'monopolist'][0]
            past_consumers = [p for p in past_group.get_players() if p.player_role == 'consumer']

            past_price = getattr(past_monop, 'price', None)
            past_profit = getattr(past_monop, 'payoff', None)


            if past_price is not None:
                row = dict(
                    round_number=past_group.round_number,
                    price=past_price,
                    units_sold=sum(1 for c in past_consumers if c.buy_choice == 'buy'),
                    profit=past_profit,
                    earnings=[getattr(c, 'payoff', None) for c in past_consumers]
                )
                history.append(row)

        return dict(
            consumer_values=[(c.id_in_group, c.endowment) for c in consumers],
            round_number=self.round_number,
            player_id=self.player.id_in_group,
            block_number=((self.round_number - 1) // 5) + 1,
            history=history
            )


    def before_next_page(self):
        if self.timeout_happened and getattr(self.player, 'price', None) is None:
            self.player.price = 0  # or any reasonable default




class WaitForMonopolist(WaitPage):
    def is_displayed(self):
        return self.player.player_role == 'consumer'

    def is_ready(self):
        monopolist = [p for p in self.group.get_players() if p.player_role == 'monopolist'][0]
        return monopolist.price is not None

class BuyDecision(Page):
    form_model = 'player'
    form_fields = ['buy_choice']

    def is_displayed(self):
        return self.player.player_role == 'consumer'


    def vars_for_template(self):
            monopolist = [p for p in self.group.get_players() if p.player_role == 'monopolist'][0]
            price = monopolist.field_maybe_none('price')
            return dict(
                monopolist_price=price,
                show_price=price is not None
            )

#    def vars_for_template(self):
#        monopolist = [p for p in self.group.get_players() if p.player_role == 'monopolist'][0]
#        price = getattr(monopolist, 'price', None)
#        return dict(
#            monopolist_price=price,
#            show_price=price is not None
#        )



class ResultsWaitPage(WaitPage):
    after_all_players_arrive = 'set_payoffs'

class Results(Page):
    def vars_for_template(self):
        group = self.group

        # 1) Get the monopolist and its current price
        monopolist = [p for p in group.get_players() if p.player_role == 'monopolist'][0]
        price = getattr(monopolist, 'price', None)

        # 2) Build a list of all consumer players (for the table)
        consumers = [p for p in group.get_players() if p.player_role == 'consumer']

        # 3) If you want each consumer's (id, endowment) for the history header
        consumer_values = [(c.id_in_group, c.endowment) for c in consumers]

        # 4) Build a history of all past rounds (including the current one)
        #    so the template can render the “History” table.
        prior_rounds = self.player.in_previous_rounds() + [self.player]
        history = []
        for past_player in prior_rounds:
            past_group = past_player.group
            past_monop = [p for p in past_group.get_players() if p.player_role == 'monopolist'][0]
            past_consumers = [p for p in past_group.get_players() if p.player_role == 'consumer']

            past_price = getattr(past_monop, 'price', None)
            past_profit = getattr(past_monop, 'payoff', None)

            if past_price is not None:
                row = dict(
                    round_number=past_group.round_number,
                    price=past_price,
                    units_sold=sum(1 for c in past_consumers if c.buy_choice == 'buy'),
                    profit=past_profit,
                    earnings=[getattr(c, 'payoff', None) for c in past_consumers],
                )
                history.append(row)

        # 5) Return all variables the Results.html template needs:
        return dict(
            price=price,
            other_consumers=consumers,
            consumer_values=consumer_values,
            history=history,
        )


class SessionSummary(Page):
    def is_displayed(self):
        return self.round_number == C.NUM_ROUNDS

    def vars_for_template(self):
        total_points = sum([float(p.payoff) for p in self.player.in_all_rounds()])
        conversion_rate = 0.05
        earnings = total_points * conversion_rate
        return dict(
            total_points=int(total_points),
            conversion_rate=conversion_rate,
            earnings_formatted="{:.2f}".format(earnings)  # force 2 decimal display
        )




page_sequence = [
    InstructionsNoChat,
    RolePageMonopolist,
    RolePageConsumer,

    InstructionsWithChat,

    PriceDecision,
    WaitForMonopolist,   # ensure monopolist sets price before chat
    ChatPage,            # consumers chat after price is set
    BuyDecision,

    ResultsWaitPage,
    Results,

    SessionSummary,
]
