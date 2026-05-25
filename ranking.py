import json
from os import path


RANKING_FILE = path.join(path.dirname(__file__), 'ranking.json')


def load_ranking():
    if not path.exists(RANKING_FILE):
        return []

    try:
        with open(RANKING_FILE, 'r', encoding='utf-8') as file:
            ranking = json.load(file)
    except (OSError, json.JSONDecodeError):
        return []

    if not isinstance(ranking, list):
        return []

    valid_entries = []
    for entry in ranking:
        if not isinstance(entry, dict):
            continue
        name = str(entry.get('name', 'Jogador')).strip() or 'Jogador'
        try:
            score = int(entry.get('score', 0))
        except (TypeError, ValueError):
            score = 0
        valid_entries.append({'name': name, 'score': score})
    return valid_entries


def save_score(player_name, score):
    ranking = load_ranking()
    name = str(player_name).strip() or 'Jogador'
    ranking.append({'name': name[:18], 'score': int(score)})

    with open(RANKING_FILE, 'w', encoding='utf-8') as file:
        json.dump(ranking, file, ensure_ascii=False, indent=2)

    return ranking


def sorted_ranking(limit=None):
    ranking = sorted(load_ranking(), key=lambda entry: entry['score'], reverse=True)
    if limit is None:
        return ranking
    return ranking[:limit]
