from asyncio.subprocess import PIPE
from redminelib import Redmine
from redminelib.exceptions import ResourceNotFoundError

import os
import subprocess
import json
import set_criticality_score_config
import sys

# GITHUB_AUTH_TOKENに値が指定されているかを確認
# GITHUB_AUTH_TOKENを設定することで、1時間ごとにgithub apiにアクセスできる上限は5000件になる
if set_criticality_score_config.GITHUB_AUTH_TOKEN != '':
    os.environ['GITHUB_AUTH_TOKEN'] = set_criticality_score_config.GITHUB_AUTH_TOKEN
else:
    print('エラー: GITHUB_AUTH_TOKEN needs to be set.')
    sys.exit()

redmine = Redmine(set_criticality_score_config.URL, username=set_criticality_score_config.LOGIN, password=set_criticality_score_config.PASSWORD, requests={'verify': False})

# 動作確認するためのチケットID
ticket_id = 1451
score = ''

def set_score(score):
    print('set_score')
    redmine.issue.update(
        ticket_id,
        custom_fields=[
            {
                "name": "OSP重要度スコア",
                "value": score
            }
        ]
    )

try:
    issues = redmine.issue.get(ticket_id)
    for custom_field in issues.custom_fields:
        # GitHub URLを取得
        if (custom_field.name == 'GitHub URL'):
            github_url = custom_field.value
            print(github_url)
            # 重要度スコアを取得
            try:
                # proc = subprocess.run(['criticality_score','--repo', github_url, "--format", "json"], stdout=subprocess.PIPE)
                # result = json.loads(proc.stdout.decode('utf-8'))
                # score = result['criticality_score']
                score = 0.233 # tmp
                print(type(score))
                # print(result)
                print(score)
                set_score(score)
            except:
                print('エラー: Failed to get criticality score of Ticket ID %s' % ticket_id)
except(ResourceNotFoundError):
    print('エラー: Ticket ID %s not found' % ticket_id)

