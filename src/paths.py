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
MODEL_PATH = DATA_DIR / 'model.pkl'
TEST_LOG_PATH = DATA_DIR / 'test_log.csv'
PAST_DECISIONS_PATH = DATA_DIR / 'past-decisions.csv'