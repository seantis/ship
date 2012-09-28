"""Combines all *.geo.json files into switzerland.json"""

import os
import json

result = {"type": "FeatureCollection", "features": [],}

for _, _, files in os.walk('.'):
    for fn in files:
        if fn.endswith('.geo.json'):
            with open(fn) as f:
                data = json.loads(f.read())
            features = data['features']
            features[0]['id'] = fn[0:2]
            result['features'].append(features[0])

with open('switzerland.json', 'w') as f:
    f.write(json.dumps(result))
