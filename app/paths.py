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

PREDICTORS_DIR = DATA_DIR / Path('predictors')
if not PREDICTORS_DIR.exists():
    os.makedirs(PREDICTORS_DIR)

PREDICTOR_PLOTS_DIR = DATA_DIR / Path('plots')
if not PREDICTOR_PLOTS_DIR.exists():
    os.makedirs(PREDICTOR_PLOTS_DIR)
