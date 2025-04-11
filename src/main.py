from paths import TEST_LOG_PATH, FACTS_PATH, RULES_PATH
from parser import parse_log
from inference import infer

if __name__ == "__main__":

    print("\n🔍 Anomalie rilevate:\n")
    parse_log(TEST_LOG_PATH, FACTS_PATH)
    print(infer(FACTS_PATH, RULES_PATH, user='alice'))

