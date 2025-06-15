# source .venv/bin/activate

import json
from software_specs_scrapers.game_specs_scrapers.league_of_legends_scraper import fetch_league_of_legends_specs
from software_specs_scrapers.game_specs_scrapers.fc_online_scraper import fetch_fc_online_specs

JSON_PATH = 'software_specs.json'

def update_json(json_path, new_specs):
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    for item in data:
        if item.get('id') == 1:
            minimum = item.get('minimum', {})

            for key, value in new_specs.items():
                if key in minimum:
                    minimum[key] = value
                else:
                    print(f"⚠️ '{key}'는 기존 minimum에 없어서 추가되지 않음")
            break

    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    league_of_legends = fetch_league_of_legends_specs()
    update_json(JSON_PATH, league_of_legends)
    print("✅ 리그 오브 레전드 시스템 사양 수집 완료:", league_of_legends)
    fetch_fc_online_specs()

