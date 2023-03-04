import csv
import datetime
import redis


def to_dict(data):
    return {
        int(datetime.datetime.strptime(el[0], "%Y-%m-%dT%H:%M:%S").timestamp()): {
            'temperature': el[1],
            'pressure': el[2],
            'humidity': el[3],
        } for el in data
    }

def report(iter, total):
    print ('\033[A\033[A')
    print(f'{100*(iter+1)/total:.2f}%')

t = datetime.datetime.now()

with open('./svtl_meteo_20190424-20230223.csv', 'r') as f:
    reader = csv.reader(f, delimiter='\t')
    rows = list(reader)[2:]

    shard_1 = to_dict(rows[:int(len(rows)/2)])
    shard_2 = to_dict(rows[int(len(rows)/2):])

    print('\n')

    progress = 0

    r = redis.StrictRedis(host='localhost', port=7000, db=0, password='pass_word').ts()
    for ts, data in shard_1.items():
        for key, value in data.items():
            r.add(key, ts, value, labels={'observatory': 'svetloye'}, duplicate_policy='first')
        report(progress, len(rows))
        progress += 1

    r = redis.StrictRedis(host='localhost', port=7003, db=0, password='pass_word').ts()
    for ts, data in shard_2.items():
        for key, value in data.items():
            r.add(key, ts, value, labels={'observatory': 'svetloye'}, duplicate_policy='first')
        report(progress, len(rows))
        progress += 1

print((datetime.datetime.now() - t).seconds)