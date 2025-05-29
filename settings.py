from os import environ

SESSION_CONFIGS = [
    dict(
        name='monopoly_boycott',
        display_name="Monopoly Boycott Game",
        num_demo_participants=3,
        app_sequence=['monopoly_boycott_app'],
    ),
]

SESSION_CONFIG_DEFAULTS = dict(
    real_world_currency_per_point=0.01,
    participation_fee=0.00,
    doc=""
)

LANGUAGE_CODE = 'en'
REAL_WORLD_CURRENCY_CODE = 'USD'
USE_POINTS = True

INSTALLED_APPS = ['otree']
