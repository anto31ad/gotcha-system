import os

from pathlib import Path

CONFIG_DIR = Path('config')
if not CONFIG_DIR.exists():
    os.makedirs(CONFIG_DIR)

BASE_RULES_PATH = CONFIG_DIR / 'rules.pl'
BLACKLIST_PATH = CONFIG_DIR / 'blacklist.pl'

DATA_DIR = Path('data')
if not DATA_DIR.exists():
    os.makedirs(DATA_DIR)

FACTS_PATH = DATA_DIR / 'facts.pl'
TEST_LOG_PATH = DATA_DIR / 'test_log.csv'
EVENT_EXAMPLES_PATH = DATA_DIR / 'past-events.csv'

USER_MODELS_DIR = DATA_DIR / Path('users')
if not USER_MODELS_DIR.exists():
    os.makedirs(USER_MODELS_DIR)
