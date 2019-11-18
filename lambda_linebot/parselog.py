import os 
import sys
venvPath = os.path.dirname(os.path.dirname(os.path.realpath(__file__))) + '\.pyenv\env_linebot\Lib\site-packages'
sys.path.insert(0, venvPath)
import json
import pandas as pd

with open(sys.argv[1]) as f:
    logs = json.load(f)

records = []
for log in logs:
    try:
        logMsg = json.loads(log['message'])
        if logMsg.get('logType') == 'MessageEvent':
            records.append({
                'timestamp': log['timestamp'],
                **logMsg
            })

    except json.JSONDecodeError:
        continue

df_records = pd.DataFrame.from_records(records)
print(df_records)
