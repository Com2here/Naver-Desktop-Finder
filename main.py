# source .venv/bin/activate

import json
from software_specs_scrapers.game_specs_scrapers.league_of_legends_scraper import fetch_league_of_legends_specs
from software_specs_scrapers.game_specs_scrapers.fc_online_scraper import fetch_fc_online_specs

JSON_PATH = 'software_specs.json'

def update_json(json_path, new_specs, target_id):
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    for item in data:
        if item.get('id') == target_id:
            minimum = item.get('minimum', {})

            # 순서 유지용 복사본
            updated_minimum = {}
            for key in minimum.keys():
                if key in new_specs:
                    updated_minimum[key] = new_specs[key]
                else:
                    updated_minimum[key] = minimum[key]

            item['minimum'] = updated_minimum
            break

    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    # league_of_legends = fetch_league_of_legends_specs()
    # update_json(JSON_PATH, league_of_legends, target_id=1)
    # print("✅ [리그 오브 레전드] 시스템 사양 수집 완료:", league_of_legends)
    fc_online = fetch_fc_online_specs()
    update_json(JSON_PATH, fc_online, target_id=2)
    print("✅ [FC 온라인] 시스템 사양 수집 완료:", fc_online)

