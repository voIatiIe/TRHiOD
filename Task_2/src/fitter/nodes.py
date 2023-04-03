import numpy as np
import pandas as pd

import matplotlib.pyplot as plt

from datetime import datetime

from settings import N_PARALLEL


def load_data(df: pd.DataFrame, start: str, end: str) -> pd.DataFrame:

    start, end = map(lambda x: datetime.strptime(x, '%d.%m.%Y'), (start, end))

    df = df.copy()

    df['timestamp'] = df['timestamp'].apply(lambda x: datetime.strptime(x, '%Y-%m-%dT%H:%M:%S').timestamp())
    df = df[(df['timestamp'] > start.timestamp()) & (df['timestamp'] < end.timestamp())]

    return [[df, proc_id] for proc_id in range(N_PARALLEL)]


def fit(data: list) -> dict:
    df, proc_id = data
    n_entries = len(df)

    i = int(n_entries / N_PARALLEL) * proc_id
    j = i + int(n_entries / N_PARALLEL) if proc_id != N_PARALLEL - 1 else n_entries

    parameters = []
    for idx in range(i, j):
        left, right = df[:idx], df[idx:]

        if len(left) < 2 or len(right) < 2: continue

        left_x, left_y = np.array(left['timestamp']), np.array(left['temp'])
        right_x, right_y = np.array(right['timestamp']), np.array(right['temp'])

        left_a, left_b = np.polyfit(left_x, left_y, 1)
        right_a, right_b = np.polyfit(right_x, right_y, 1)

        left_y_probe = left_a * left_x + left_b
        right_y_probe = right_a * right_x + right_b

        parameters.append({
            'id': idx,
            'timestamp': right_x[0],
            'left': [left_a, left_b],
            'right': [right_a, right_b],
            'loss': np.sqrt(((left_y_probe - left_y)**2).sum() + ((right_y_probe - right_y)**2).sum()),
        })

    return sorted(parameters, key=lambda x: x['loss'])[0]


def collect(*args):
    return sorted(args, key=lambda x: x['loss'])[0]


def report(best: dict, data: list):
    df, _ = data

    timestamps = df['timestamp']
    temps = df['temp']

    left_x, right_x = timestamps[:best['id']], timestamps[best['id']:]

    fig = plt.figure()
    plt.scatter(timestamps, temps, s=1)
    plt.plot(left_x, left_x*best['left'][0] + best['left'][1])
    plt.plot(right_x, right_x*best['right'][0] + best['right'][1])
    plt.close()

    fig.savefig('data_/intermediate/fit.jpg')

    with open('data_/intermediate/report.txt', 'w') as f:
        f.write('Report:')
        f.write(f'Best point: {datetime.utcfromtimestamp(best["timestamp"]).strftime("%d.%m.%Y %H:%M:%S")}\n')
        f.write(
            'Left parameters:\n'
            f'\t a = {best["left"][0]}\n'
            f'\t b = {best["left"][1]}\n'
        )
        f.write(
            'Right parameters:\n'
            f'\t a = {best["right"][0]}\n'
            f'\t b = {best["right"][1]}\n'
        )
        f.write(f'Loss: {best["loss"]}')
