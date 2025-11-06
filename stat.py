import math
import matplotlib.pyplot as plt
import numpy as np
from scipy.stats import pearsonr, spearmanr

from colors import RGBDisplay, HSV, HLS
from colors import (
    rgbd_to_rgbl,
    rgb_to_yiq,
    rgb_to_hsv,
    hsv_to_rgbd,
    hsv_to_rgbl,
    rgb_to_hls,
    hls_to_rgbd,
    hls_to_rgbl,
    rgb_to_lab76,
    rgb_to_lab2k,
)


"""
Total valid scores: 3226
Total unique color pairs rated: 47
RGBD       | Pearson r =  0.843 (p=1.04e-13),  Spearman ρ =  0.871 (p=1.74e-15)
RGBL       | Pearson r =  0.865 (p=4.67e-15),  Spearman ρ =  0.884 (p=1.88e-16)
HSV        | Pearson r =  0.635 (p=1.64e-06),  Spearman ρ =  0.651 (p=7.35e-07)
Lab ΔE76   | Pearson r =  0.713 (p=1.85e-08),  Spearman ρ =  0.797 (p=1.98e-11)
Lab ΔE2000 | Pearson r =  0.801 (p=1.39e-11),  Spearman ρ =  0.846 (p=7.37e-14)

Total valid scores: 3612
Total unique color pairs rated: 47
RGBD       | Pearson r =  0.847 (p=6.14e-14),  Spearman ρ =  0.878 (p=4.99e-16)
RGBL       | Pearson r =  0.868 (p=2.64e-15),  Spearman ρ =  0.891 (p=4.74e-17)
HSV        | Pearson r =  0.632 (p=1.86e-06),  Spearman ρ =  0.650 (p=7.80e-07)
Lab ΔE76   | Pearson r =  0.717 (p=1.40e-08),  Spearman ρ =  0.804 (p=9.99e-12)
Lab ΔE2000 | Pearson r =  0.807 (p=7.16e-12),  Spearman ρ =  0.857 (p=1.58e-14)

.. via rgbl (linearized)
...
HSV        | Pearson r =  0.662 (p=4.05e-07),  Spearman ρ =  0.667 (p=3.04e-07)
Lab ΔE76   | Pearson r =  0.824 (p=1.12e-12),  Spearman ρ =  0.937 (p=4.00e-22)
Lab ΔE2000 | Pearson r =  0.871 (p=1.82e-15),  Spearman ρ =  0.909 (p=1.11e-18)
"""

INPUT_FILE = 'results/ratings-2025-11-06-15-33.tsv'

MIN_SESSION_LENGTH = 15

PREDEFINED_PAIRS = [
    ['#FFD700', '#FFD700'],
    ['#964600', '#964600'],
    ['#14960A', '#14960A'],
    ['#000000', '#FFFFFF'],
    ['#FF0000', '#00FFFF'],
    ['#0057B7', '#FFD700'],
    ['#191919', '#E5E5E5'],
    ['#333333', '#CCCCCC'],
    ['#4C4C4C', '#B2B2B2'],
    ['#666666', '#999999'],
    ['#002FA7', '#00005C'],
    ['#FF00FF', '#DF00FF'],
    ['#C41E3A', '#DF73FF'],
    ['#C3B091', '#BDB76B'],
    ['#808000', '#9AB973'],
    ['#40E0D0', '#99FF99'],
    ['#FF7F50', '#B7410E'],
    ['#964B00', '#D2B48C'],
    ['#000080', '#0F52BA'],
    ['#FFF8E7', '#FFFDD0'],
    ['#BDFCC9', '#F5FFFA'],
    ['#E6E6FA', '#D8BFD8'],
    ['#FA8072', '#FFA07A'],
    ['#FFD700', '#CC7722'],
    ['#C0FF00', '#FFBA00'],
    ['#FF7F7F', '#99FF7F'],
    ['#2D77E5', '#E52D9C'],
    ['#CBFF00', '#F4FFCC'],
    ['#2800CC', '#9B8ECC'],
    ['#11B252', '#6BB287'],
    ['#A3BFCC', '#008ECC'],
    ['#B2A0AB', '#B22379'],
    ['#00FF66', '#004C1E'],
    ['#E52D9C', '#661445'],
    ['#CC923D', '#33240F'],
    ['#E59C2D', '#7F5619'],
    ['#5B92E5', '#284166'],
    ['#CC8214', '#5B994C'],
    ['#4C607F', '#E52D9C'],
    ['#787878', '#828282'],
    ['#F0F0E6', '#FAFAF0'],
    ['#001900', '#E5FFE5'],
    ['#111110', '#4016E5'],
    ['#494854', '#ABF60D'],
    ['#1AF000', '#0B09F2'],
    ['#CB00D6', '#07EB1D'],
    ['#B98602', '#4904E4'],
]


def predefined_set():
    result = set()
    for pair in PREDEFINED_PAIRS:
        a_rgb = parse_hex_color(pair[0])
        b_rgb = parse_hex_color(pair[1])
        if a_rgb > b_rgb:
            a_rgb, b_rgb = b_rgb, a_rgb
        if (a_rgb, b_rgb) in result:
            print(f"Duplicate predefined pair: {pair[0]}, {pair[1]}")
        result.add((a_rgb, b_rgb))
    # print(f"Predefined orig pairs count: {len(PREDEFINED_PAIRS)}")
    # print(f"Predefined uniq pairs count: {len(result)}")
    return result


def error_in_record(line, msg):
    print(f"Error {msg} in line: {line}")


def parse_hex_color(color) -> tuple[int, int, int]:
    if len(color) != 7 or color[0] != '#':
        raise ValueError("color must be in #RRGGBB format")
    r = int(color[1:3], 16)
    g = int(color[3:5], 16)
    b = int(color[5:7], 16)
    return r, g, b


def row_stat(row):
    # For list of numbers, return count, mean, stddev
    n = len(row)
    if n == 0:
        return 0, 0.0, 0.0
    mean = sum(row) / n
    variance = sum((x - mean) ** 2 for x in row) / n
    stddev = math.sqrt(variance)

    # Trimmed mean and stddev (remove top and bottom 10%)
    trimmed_row = sorted(row)[n // 10: n - n // 10]
    if len(trimmed_row) < 2:
        raise ValueError("not enough data for trimmed statistics")

    t_n = len(trimmed_row)
    t_mean = sum(trimmed_row) / t_n
    t_variance = sum((x - t_mean) ** 2 for x in trimmed_row) / t_n
    t_stddev = math.sqrt(t_variance)

    return n, mean, stddev, t_n, t_mean, t_stddev


def analyze():
    data = {}
    uniq_names = set()
    uniq_sessions = set()
    longest_session_length = 0

    predefined = predefined_set()

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
            session_id = (name, ip)
            uniq_sessions.add(session_id)
            if session_id not in data:
                data[session_id] = []
            data[session_id].append({
                'ts': ts,
                'a': colorA_rgb,
                'b': colorB_rgb,
                'score': score,
            })
            session_length = len(data[session_id])
            if session_length > longest_session_length:
                longest_session_length = session_length

    print(f"Total lines processed: {n_lines}")
    if n_incorrect > 0:
        print(f"Total incorrect lines: {n_incorrect}")
    print(f"Unique participant names: {len(uniq_names)}")
    print(f"Unique sessions (IP + name): {len(uniq_sessions)}")
    print(f"Longest session length (number of ratings): {longest_session_length}")

    # Filter sessions, determined as untrusted
    for session_id in data:
        if session_id in (
            ("Alex", "185.44.87.128"),  # low score for identical colors
            ("nermosh", "31.146.201.207"),  # low score for identical colors
            ("Andrew", "194.19.228.171"),  # low score for identical colors
            ("FR", "89.248.83.23"),  # high score for different colors
            ("Богдан Мазницький", "185.209.57.133"),  # high score for different colors
        ):
            # print(f"Session {session_id} is blacklisted: {data[session_id]}")
            data[session_id] = []

    # People with several sessions
    # for name in data:
    #     n_sessions = len(data[name])
    #     if n_sessions > 1:
    #         print(f"Participant '{name}' has {n_sessions} sessions.")

    # Show very short sessions (less than MIN_SESSION_LENGTH ratings), and remove them
    for session_id in data:
        n_ratings = len(data[session_id])
        if n_ratings and n_ratings < MIN_SESSION_LENGTH:
            # print(f"Session {session_id} is too short with {n_ratings} ratings.")
            # Remove short sessions
            data[session_id] = []

    # Show untrusted sessions, and remove them
    for session_id in data:
        if len(data[session_id]) == 0:
            continue

        scores = [record['score'] for record in data[session_id]]
        assert len(scores) > 1

        # First case: all scores are identical
        if len(set(scores)) == 1:
            print(f"Session {session_id} is untrusted with identical scores: {scores[0]}.")
            data[session_id] = []
            continue

        # Second case: standard deviation of scores is very low
        mean_score = sum(scores) / len(scores)
        variance = sum((s - mean_score) ** 2 for s in scores) / (len(scores) - 1)
        stddev = math.sqrt(variance)
        # TODO: stddev > 50 is too high?
        if stddev < 10.0:
            print(f"Session {session_id} is untrusted with low score stddev: {stddev:.2f}.")
            data[session_id] = []
            continue

        # Case 3: Frequency of clicks
        timestamps = [x['ts'] for x in data[session_id]]
        min_ts = min(timestamps)
        max_ts = max(timestamps)
        duration_sec = max_ts - min_ts
        if duration_sec < 10:
            print(f"Session {session_id} is untrusted with too short duration: {duration_sec} sec for {len(timestamps)} ratings.")
            data[session_id] = []
            continue

        rate = len(timestamps) / duration_sec
        if rate > 0.5:
            print(f"Session {session_id} is untrusted with too high rate: {rate:.2f} ratings/sec, duration {duration_sec} sec for {len(timestamps)} ratings.")
            data[session_id] = []
            continue

        # Case 4: too many neutral scores
        count_50 = sum(1 for record in data[session_id] if record['score'] == 50)
        if count_50 > len(data[session_id]) * 0.5:
            print(f"Session {session_id} is untrusted with too many 50 scores: {count_50} out of {len(data[session_id])}.")
            data[session_id] = []
            continue

    # Search for strange records
    close_pairs = {
        ((120, 120, 120), (130, 130, 130)),
        ((223, 0, 255), (255, 0, 255)),
        ((240, 240, 230), (250, 250, 240)),
    }

    for session_id in data:
        for r in data[session_id]:
            pair = (r['a'], r['b'])
            a = r['a']
            b = r['b']
            score = r['score']

            # Color pairs outside predefined set
            if pair not in predefined:
                print(f"[!] Session {session_id} has non-predefined color pair: {pair[0]}, {pair[1]}")

            # Identical colors but low score
            if a == b and score < 75:
                print(f"SUSP - Session {session_id} has low score for identical colors: {a}, score: {score}")
                continue

            # Different colors but high score
            if a != b and score == 100 and pair not in close_pairs:
                print(f"SUSP - Session {session_id} has high score for different colors: {a}, {b}, score: {score}")
                continue

    # Search when within session the same pair was rated very differently
    for session_id in data:
        pair_scores = {}
        for r in data[session_id]:
            pair = (r['a'], r['b'])
            score = r['score']
            if pair not in pair_scores:
                pair_scores[pair] = []
            pair_scores[pair].append(score)

        badly_rated_n = 0
        for pair in pair_scores:
            scores = pair_scores[pair]
            # If min and max differ more than by 50
            if max(scores) - min(scores) >= 50:
                # print(f"SUSP - Session {session_id} has inconsistent scores for pair {pair[0]}, {pair[1]}: scores = {scores}")
                badly_rated_n += 1

        # TODO: consider allowing one badly rated pair
        if badly_rated_n > 1:
            data[session_id] = []

    # print(data)

    # # Remove scores for identical colors
    # for session_id in data:
    #     filtered_records = []
    #     for record in data[session_id]:
    #         if record['a'] == record['b']:
    #             continue
    #         filtered_records.append(record)
    #     data[session_id] = filtered_records

    # # Remove 0 scores
    # for session_id in data:
    #     filtered_records = []
    #     for record in data[session_id]:
    #         if record['score'] == 0:
    #             continue
    #         filtered_records.append(record)
    #     data[session_id] = filtered_records

    # # Remove 0, 50 and 100 scores
    # for session_id in data:
    #     filtered_records = []
    #     for record in data[session_id]:
    #         if record['score'] in (0, 50, 100):
    #             continue
    #         filtered_records.append(record)
    #     data[session_id] = filtered_records

    # Remove empty sessions
    sessions_to_remove = []
    for session_id in data:
        if len(data[session_id]) == 0:
            sessions_to_remove.append(session_id)
    for session_id in sessions_to_remove:
        del data[session_id]

    # Normalize all scores from [100, 0] to 0..1
    for session_id in data:
        for record in data[session_id]:
            record['score'] = (100 - record['score']) / 100.0

    # Show rates distribution
    just_scores = []
    for session_id in data:
        for record in data[session_id]:
            just_scores.append(record['score'])
    print('Total valid scores:', len(just_scores))

    # plt.figure(figsize=(8,4))
    # plt.hist(just_scores, bins=200, alpha=0.5, label='Scores', density=True)
    # plt.legend()
    # plt.xlabel("Score")
    # plt.ylabel("Density")
    # plt.title("Distribution of scores")
    # plt.grid(alpha=0.3)
    # plt.tight_layout()
    # plt.show()

    # Ok. Now, for each color pair, we aggregate scores
    pair_scores = {}
    for session_id in data:
        for r in data[session_id]:
            pair = (r['a'], r['b'])
            score = r['score']
            if pair not in pair_scores:
                pair_scores[pair] = []
            pair_scores[pair].append(score)

    # Collect distances
    distances = {}

    # Stat for each pair
    print(f"Total unique color pairs rated: {len(pair_scores)}")
    for pair in pair_scores:
        n, mean, stddev, t_n, t_mean, t_stddev = row_stat(pair_scores[pair])
        # print(f"Pair {pair[0]}, {pair[1]}: n={n}, mean={mean:.2f}, stddev={stddev:.2f}, trimmed_n={t_n}, trimmed_mean={t_mean:.2f}, trimmed_stddev={t_stddev:.2f}")
        # if t_stddev > 22.0:
        #     print(f"SUSP - Pair {pair[0]}, {pair[1]} has high t_stddev: {t_stddev:.2f} (mean={t_mean:.2f})")
        distances[pair] = {'human': t_mean}

    # Calculate distances
    for pair in distances:
        a_rgbd = RGBDisplay.from_8bit(pair[0][0], pair[0][1], pair[0][2])
        b_rgbd = RGBDisplay.from_8bit(pair[1][0], pair[1][1], pair[1][2])
        rgbd_dist = a_rgbd.distance(b_rgbd)

        a_rgbl = rgbd_to_rgbl(a_rgbd)
        b_rgbl = rgbd_to_rgbl(b_rgbd)
        rgbl_dist = a_rgbl.distance(b_rgbl)

        a_hsv = rgb_to_hsv(a_rgbl)
        b_hsv = rgb_to_hsv(b_rgbl)
        hsv_dist = a_hsv.distance(b_hsv)

        a_lab76 = rgb_to_lab76(a_rgbl)
        b_lab76 = rgb_to_lab76(b_rgbl)
        lab76_dist = a_lab76.distance(b_lab76)

        a_lab2k = rgb_to_lab2k(a_rgbl)
        b_lab2k = rgb_to_lab2k(b_rgbl)
        lab2k_dist = a_lab2k.distance(b_lab2k)

        distances[pair]['rgbd'] = rgbd_dist
        distances[pair]['rgbl'] = rgbl_dist
        distances[pair]['hsv'] = hsv_dist
        distances[pair]['lab76'] = lab76_dist
        distances[pair]['lab2k'] = lab2k_dist

    # Show correlation
    def show_correlation(x_values, y_values, x_label, y_label):
        plt.figure(figsize=(6,6))
        plt.scatter(x_values, y_values, alpha=0.5)
        plt.xlabel(x_label)
        plt.ylabel(y_label)
        plt.title(f"Correlation between {x_label} and {y_label}")
        plt.grid(alpha=0.3)
        plt.tight_layout()
        plt.show()

    rgbd_x = []
    rgbd_y = []
    rgbl_x = []
    rgbl_y = []
    hsv_x = []
    hsv_y = []
    lab76_x = []
    lab76_y = []
    lab2k_x = []
    lab2k_y = []
    for pair in distances:
        human_dist = distances[pair]['human']
        rgbd_dist = distances[pair]['rgbd']
        rgbl_dist = distances[pair]['rgbl']
        hsv_dist = distances[pair]['hsv']
        lab76_dist = distances[pair]['lab76']
        lab2k_dist = distances[pair]['lab2k']

        rgbd_x.append(rgbd_dist)
        rgbd_y.append(human_dist)

        rgbl_x.append(rgbl_dist)
        rgbl_y.append(human_dist)

        hsv_x.append(hsv_dist)
        hsv_y.append(human_dist)

        lab76_x.append(lab76_dist)
        lab76_y.append(human_dist)

        lab2k_x.append(lab2k_dist)
        lab2k_y.append(human_dist)
    # show_correlation(rgbd_x, rgbd_y, "RGBD Distance", "Human Perceived Distance")
    # show_correlation(rgbl_x, rgbl_y, "RGBL Distance", "Human Perceived Distance")
    # show_correlation(hsv_x, hsv_y, "HSV Distance", "Human Perceived Distance")
    # show_correlation(lab76_x, lab76_y, "ΔE76 Distance", "Human Perceived Distance")
    # show_correlation(lab2k_x, lab2k_y, "ΔE2000 Distance", "Human Perceived Distance")

    def corr_summary(name, x, y):
        pearson_r, pearson_p = pearsonr(x, y)
        spearman_r, spearman_p = spearmanr(x, y)
        print(f"{name:10s} | Pearson r = {pearson_r:6.3f} (p={pearson_p:.2e}),  Spearman ρ = {spearman_r:6.3f} (p={spearman_p:.2e})")

    corr_summary("RGBD", rgbd_x, rgbd_y)
    corr_summary("RGBL", rgbl_x, rgbl_y)
    corr_summary("HSV", hsv_x, hsv_y)
    corr_summary("Lab ΔE76", lab76_x, lab76_y)
    corr_summary("Lab ΔE2000", lab2k_x, lab2k_y)


if __name__ == "__main__":
    analyze()
