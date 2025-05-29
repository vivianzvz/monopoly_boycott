from os import environ

SESSION_CONFIGS = [
    dict(
        name='monopoly_boycott',
        display_name="Monopoly Boycott Game",
        app_sequence=['monopoly_boycott_app'],
        num_demo_participants=3,
        demand_slope='step',
        use_chat=True,
    ),
]

SESSION_CONFIG_DEFAULTS = dict(
    real_world_currency_per_point=1.00, participation_fee=0.00, doc=""
)

PARTICIPANT_FIELDS = []
SESSION_FIELDS = []

LANGUAGE_CODE = 'en'
REAL_WORLD_CURRENCY_CODE = 'USD'
USE_POINTS = True

ROOMS = [
    dict(
        name='label',
        display_name='with labels',
        participant_label_file='_rooms_labeled.txt',
    ),
    dict(name='live_demo', display_name='Room for live demo'),
]

ADMIN_USERNAME = 'admin'
ADMIN_PASSWORD = environ.get('OTREE_ADMIN_PASSWORD')

DEMO_PAGE_INTRO_HTML = "Here are some oTree games."
SECRET_KEY = '1554698864068'
INSTALLED_APPS = ['otree']
