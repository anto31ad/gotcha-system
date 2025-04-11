from pathlib import Path

DATA_DIR = Path('data')

RULES_PATH = DATA_DIR / 'rules.pl'

GENERATED_DATA_DIR = DATA_DIR / 'generated'
FACTS_PATH = GENERATED_DATA_DIR / 'facts.pl'
MODEL_PATH = GENERATED_DATA_DIR / 'model.pkl'
TEST_LOG_PATH = GENERATED_DATA_DIR / 'test_log.csv'
