#!/usr/bin/python
#-*- coding: utf-8 -*-

import os
import tweepy
import httplib
import urllib
import json
import requests

#ssl_ignore-->>
import ssl
ssl._create_default_https_context = ssl._create_unverified_context
#ssl_ignore--<<

#twitterAPIの利用-->>
##アクセスTokenなど接続情報の指定-->>
consumer_key = "XXXXXXXXXXXXXXXXXXXXXXXXXX"
consumer_secret = "XXXXXXXXXXXXXXXXXXXXXXXXXX"
access_token = "XXXXXXXXXXXXXXXXXXXXXXXXXX"
access_secret = "XXXXXXXXXXXXXXXXXXXXXXXXXX"
auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_secret)
api = tweepy.API(auth)
f = open('sinceId.txt')
file_id = f.readline()
f.close()

#Microsoft Cognitive ComputerVisionAPIの利用-->>
##接続情報の指定-->>
image_url = ''
headers = {
        'Content-Type': 'application/json',
        'Ocp-Apim-Subscription-Key': 'XXXXXXXXXXXXXXXXXXXXXXXXXX',
}
params = urllib.urlencode({
        'visualFeatures': 'Description',
})

#GoogleTranslateAPIの利用-->>
##接続情報の指定-->>
gct_head = 'https://www.googleapis.com/language/translate/v2?key='
gct_key = 'XXXXXXXXXXXXXXXXXXXXXXXXXX'
gct_mid = '&target=ja&q='
gct_url = gct_head + gct_key + gct_mid

#body-->>
conn = httplib.HTTPSConnection('api.projectoxford.ai')
#sinceIdファイルのID以降のIDを持つ自分へのリプライツイートを指定
status = api.mentions_timeline(since_id=file_id)
try:
        if status[0]._json['id_str'] != '':
                f = open('sinceIdBef.txt','w')
                f.write(file_id)
                f.close()
                f = open('sinceId.txt','w')
                f.write(status[0]._json['id_str'])
                f.close()
except IndexError:
        pass
for index in range(len(status)):
        body = ""
        try:
                #リプライツイートの画像の有無を確認
                image_url = status[index]._json['entities']['media'][0]['media_url']
                print('img_url' + str(index) + ' >> ' + image_url)
                body = """{'url': '%s'}""" % (image_url)
        except KeyError:
                print("microsoft computer vision api KeyError")
                continue
        #リプライの送信元ユーザのユーザー名を格納
        scrn_name = status[index]._json[u'user'][u'screen_name']
        conn.request("POST", "/vision/v1.0/analyze?%s" % params, body, headers)
        cv_res = conn.getresponse()
        cv_res_data = cv_res.read()
        cv_res_json = json.loads(cv_res_data)
        try:
                cv_res_txt = cv_res_json[u'description'][u'captions'][0][u'text']
        except KeyError:
                print("google translation api KeyError")
                continue
        gct_req_url = gct_url + cv_res_txt
        gct_res = requests.post(gct_req_url)
        print(gct_req_url)
        gct_res_txt = gct_res.json()[u'data'][u'translations'][0][u'translatedText']
        #リプライの返信先を指定
        rep_txt = '@' + scrn_name + ' ' + gct_res_txt
        rep_id = status[index]._json['id_str']
        api.update_status(status=rep_txt, in_reply_to_status_id=rep_id)
#       print(gct_res_txt)
conn.close()
#body--<<
