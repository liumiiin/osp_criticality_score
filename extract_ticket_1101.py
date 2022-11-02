from asyncio.subprocess import PIPE
from asyncio.windows_events import NULL
from nturl2path import url2pathname
from urllib.error import URLError
from redminelib import Redmine
from redminelib.exceptions import ResourceNotFoundError

import os
import subprocess
import json
import set_criticality_score_config
import datetime # 新規追加_2022/11/01
import sys # 新規追加_2022/11/01

# 新規追加_2022/11/01
# GITHUB_AUTH_TOKENに値が指定されているかを確認
# GITHUB_AUTH_TOKENを設定することで、1時間ごとにgithub apiにアクセスできる上限は5000件になる
if set_criticality_score_config.GITHUB_AUTH_TOKEN != '':
    os.environ['GITHUB_AUTH_TOKEN'] = set_criticality_score_config.GITHUB_AUTH_TOKEN
else:
    print('エラー: GITHUB_AUTH_TOKEN needs to be set.')
    sys.exit()

redmine = Redmine(set_criticality_score_config.URL, username=set_criticality_score_config.LOGIN, password=set_criticality_score_config.PASSWORD, requests={'verify': False})

# チケット一覧を取得する
def get_all_tickets(redmine):
    issues = redmine.issue.all()
    return issues

# チケット中のURLを抽出して、リストに格納する
def get_all_urls(redmine):
    issues = get_all_tickets(redmine)
    issue_info = []
    for issue in issues:
        for custom_field in issue.custom_fields:
            if (custom_field.name == 'GitHub URL'):
                try:
                    github_url = custom_field.value
                    # 新規追加_2022/11/01
                    if github_url != '':
                        issue_info.append({"id":issue.id,"subject":issue.subject,"url":github_url})
                    else:
                        print('Info: URL of Ticket ID %s is empty' % issue.id)
                except:
                    print('Info: URL of Ticket ID %s is not found' % issue.id)
    return issue_info

# スコアを取得する
def get_score(redmine):
    issue_info = get_all_urls(redmine)
    start_time = datetime.datetime.now()
    print('get_score start: ', start_time)
    for info in issue_info:
        if info['id'] < 1665 : # tmp
            exec_time = datetime.datetime.now()
            print('exec: ', exec_time)
            try:
                proc = subprocess.run(['criticality_score','--repo', info["url"], "--format", "json"], stdout=subprocess.PIPE)
                result = json.loads(proc.stdout.decode('utf-8'))
                score = result['criticality_score']
                info['criticality_score'] = score
                print(info)
            except:
                print('Error: Failed to get criticality score of Ticket ID %s' % info['id'])
    finish_time = datetime.datetime.now()
    print('get_score finished: ', finish_time)
    
    return issue_info

# 新規追加_2022/11/02
# スコアをRedmineに反映する
# def set_score(issue_info):
#     print('set_score start')
#     for info in issue_info:
#         try:
#             redmine.issue.update(
#                 info['id'],
#                 custom_fields=[
#                     {
#                         "name": "OSP重要度スコア",
#                         "value": info['criticality_score']
#                     }
#                 ]
#             )
#         except:
#             print('Error: Failed to set criticality score of Ticket ID %s' % info['id'])

score_list = get_score(redmine)
b = json.dumps(score_list)
score_list = open("score_list.json","w")
score_list.write(b)


