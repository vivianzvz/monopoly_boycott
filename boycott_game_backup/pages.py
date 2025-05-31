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

class RolePage(Page):
    def is_displayed(self):
        return self.round_number == 1

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
        return dict(monopolist_price=monopolist.field_maybe_none('price'))


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
        if self.timeout_happened and self.player.field_maybe_none('price') is None:
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
        price = getattr(monopolist, 'price', None)
        return dict(
            monopolist_price=price,
            show_price=price is not None
        )



class ResultsWaitPage(WaitPage):
    after_all_players_arrive = 'set_payoffs'

class Results(Page):
    def vars_for_template(self):
        monopolist = [p for p in self.group.get_players() if p.player_role == 'monopolist'][0]
        price = getattr(monopolist, 'price', None)

        consumers = [p for p in self.group.get_players() if p.player_role == 'consumer']
        consumer_values = [(p.id_in_group, p.endowment) for p in consumers]

        # Collect all prior rounds (including current one)
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

        return dict(
            price=price,
            consumer_values=consumer_values,
            history=history,
        )


class SessionSummary(Page):
    def is_displayed(self):
        return self.round_number == C.num_rounds

    def vars_for_template(self):
        total_points = sum([float(p.payoff) for p in self.player.in_all_rounds()])
        conversion_rate = 0.01
        earnings = total_points * conversion_rate
        return dict(
            total_points=int(total_points),
            conversion_rate=conversion_rate,
            earnings_formatted="{:.2f}".format(earnings)  # force 2 decimal display
        )




page_sequence = [
    InstructionsNoChat,
    RolePage,

    InstructionsWithChat,

    PriceDecision,
    WaitForMonopolist,   # ensure monopolist sets price before chat
    ChatPage,            # consumers chat after price is set
    BuyDecision,

    ResultsWaitPage,
    Results,

    SessionSummary,
]
