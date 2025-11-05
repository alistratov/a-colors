import math
import matplotlib.pyplot as plt
import numpy as np

INPUT_FILE = 'ratings-2025-11-05-13-08.tsv'


def error_in_record(line, msg):
    print(f"Error {msg} in line: {line}")


def parse_hex_color(color) -> tuple[int, int, int]:
    if len(color) != 7 or color[0] != '#':
        raise ValueError("color must be in #RRGGBB format")
    r = int(color[1:3], 16)
    g = int(color[3:5], 16)
    b = int(color[5:7], 16)
    return r, g, b


def analyze():
    data = {}
    uniq_names = set()
    uniq_sessions = set()
    longest_session_length = 0

    n_lines = 0
    n_incorrect = 0
    with open(INPUT_FILE, 'r', encoding='utf-8') as f:
        for line in f:
            n_lines += 1
            line = line.strip()
            # Format is ip\tts\tname\tcolorA\tcolorB\tscore

            parts = line.split('\t')
            if len(parts) != 6:
                n_incorrect += 1
                error_in_record(line, "wrong number of fields")
                continue
            ip, ts_str, name, colorA, colorB, score_str = parts
            try:
                ts = int(ts_str)
                score = int(score_str)
                if not (0 <= score <= 100):
                    raise ValueError("score out of range")
                colorA_rgb = parse_hex_color(colorA)
                colorB_rgb = parse_hex_color(colorB)
                # Order colors consistently
                if colorA_rgb > colorB_rgb:
                    colorA_rgb, colorB_rgb = colorB_rgb, colorA_rgb
            except ValueError as ve:
                n_incorrect += 1
                error_in_record(line, str(ve))
                continue

            uniq_names.add(name)
            uniq_sessions.add((ip, name))
            if name not in data:
                data[name] = {}
            if ip not in data[name]:
                data[name][ip] = []
            data[name][ip].append({
                'ts': ts,
                'a': colorA_rgb,
                'b': colorB_rgb,
                'score': score,
            })
            session_length = len(data[name][ip])
            if session_length > longest_session_length:
                longest_session_length = session_length

    print(f"Total lines processed: {n_lines}")
    print(f"Total incorrect lines: {n_incorrect}")
    print(f"Unique participant names: {len(uniq_names)}")
    print(f"Unique sessions (IP + name): {len(uniq_sessions)}")
    print(f"Longest session length (number of ratings): {longest_session_length}")

    # People with several sessions
    for name in data:
        n_sessions = len(data[name])
        if n_sessions > 1:
            print(f"Participant '{name}' has {n_sessions} sessions.")

    # Show very short sessions (less than 10 ratings), and remove them
    for name in data:
        for ip in data[name]:
            n_ratings = len(data[name][ip])
            if n_ratings < 10:
                print(f"Participant '{name}' from IP {ip} has a short session with {n_ratings} ratings.")
                # Remove short sessions
                data[name][ip] = []

    # Show untrusted sessions, and remove them
    for name in data:
        for ip in data[name]:
            # First case: all scores are identical
            scores = [record['score'] for record in data[name][ip]]
            if len(set(scores)) == 1 and len(scores) > 0:
                print(f"Participant '{name}' from IP {ip} has untrusted session with identical scores: {scores[0]}.")
                data[name][ip] = []
                continue

            # Second case: standard deviation of scores is very low
            if len(scores) > 1:
                mean_score = sum(scores) / len(scores)
                variance = sum((s - mean_score) ** 2 for s in scores) / (len(scores) - 1)
                stddev = math.sqrt(variance)
                if stddev < 5.0:
                    print(f"Participant '{name}' from IP {ip} has untrusted session with low score stddev: {stddev:.2f}.")
                    data[name][ip] = []
                    continue

    # print(data)

    # Show rates distribution
    just_scores = []
    for name in data:
        for ip in data[name]:
            for record in data[name][ip]:
                just_scores.append(record['score'])

    plt.figure(figsize=(8,4))
    plt.hist(just_scores, bins=200, alpha=0.5, label='Scores', density=True)
    plt.legend()
    plt.xlabel("Score")
    plt.ylabel("Density")
    plt.title("Distribution of scores")
    plt.grid(alpha=0.3)
    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    analyze()
