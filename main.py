import twitter
import os
import re
import time
import calendar
from collections import defaultdict
from sys import exit

hour = time.gmtime().tm_hour
if hour % 2 != 0:
    exit()
tweet_type = (hour // 2) % 4

re_score_zh = re.compile(r'^在樂曲(?P<song>.+)中取得(?P<grade>\w+) Grade。分數 (?P<score>\d{7}) \#Dynamix$')
re_score_ja = re.compile(r'^(?P<song>.+)で(?P<grade>\w+)ランク、(?P<score>\d{7})点を獲得しました。 \#Dynamix$')
re_score_en = re.compile(r'^(?P<grade>\w+) grade in (?P<song>.+)\. Score (?P<score>\d{7}) \#Dynamix$')
re_score = [re_score_zh, re_score_ja, re_score_en]
#valid_diffs = {'CASUAL', 'NORMAL', 'HARD', 'MEGA', 'GIGA'}
valid_sources = {'<a href="http://www.apple.com" rel="nofollow">iOS</a>',
                 '<a href="http://dynamix.c4-cat.com" rel="nofollow">Mobile Music Game - Dynamix</a>'}
now = time.time()
song_count = defaultdict(lambda: 0)
user_count = defaultdict(lambda: 0)
grade_count = defaultdict(lambda: 0)
score_count = 0

api = twitter.Api(consumer_key=os.environ['CSMR_KEY'],
                  consumer_secret=os.environ['CSMR_SCRT'],
                  access_token_key=os.environ['ACSS_KEY'],
                  access_token_secret=os.environ['ACSS_SCRT'])

query_str = 'q=%23Dynamix&result_type=recent&count=100'
results = api.GetSearch(raw_query=query_str)
oldest_time = now
oldest_id = 2 ** 63 - 1
while now - oldest_time < 86400:
    if len(results) == 0:
        break
    for res in results:
        ok = False
        for r in re_score:
            match_object = r.match(res.text)
            if match_object is not None:
                song, grade, score = match_object.group('song', 'grade', 'score')
                score = int(score)
                ok = True
                break
        if not ok:
            continue
        if res.source not in valid_sources:
            continue
        created_time = calendar.timegm(time.strptime(res.created_at, "%a %b %d %H:%M:%S %z %Y"))
        oldest_time = min(created_time, oldest_time)
        if now - created_time >= 86400:
            continue
        oldest_id = min(res.id, oldest_id)
        score_count += 1
        grade_count[grade] += 1
        song_count[song] += 1
        user_count[res.user.screen_name] += 1
    if now - oldest_time < 86400:
        results = api.GetSearch(raw_query=query_str + '&max_id={}'.format(oldest_id - 1))


if tweet_type == 0:
    text = '{} users tweeted {} #Dynamix scores in the past 24 hours!'.format(len(user_count), score_count)
elif tweet_type == 1:
    most_shared_song = max(song_count.items(), key=lambda p:p[1])
    text = '{}, being tweeted {} times, is the most tweeted #Dynamix song in the past 24 hours!'.format(most_shared_song[0], most_shared_song[1])
elif tweet_type == 2:
    most_shared_user =  max(user_count.items(), key=lambda p:p[1])
    text = 'The most active #Dynamix score tweeter in the past 24 hours is @{}, who tweeted {} scores!'.format(most_shared_user[0], most_shared_user[1])
elif tweet_type == 3:
    text = '#Dynamix players tweeted {} OMEGAs and {} PSIs in the past 24 hours. Congratulations!'.format(grade_count['OMEGA'], grade_count['PSI'])
print(text)
api.PostUpdate(text)
