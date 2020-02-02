#coding: utf-8

import requests,time,os,logging,json
from dotenv import load_dotenv,find_dotenv
import pandas as pd

load_dotenv(find_dotenv())
token_line = os.environ.get('token_lineNotify_labu')
toekn_cwb = os.environ.get('toekn_cwb')

locs = ['新竹縣','臺中市','南投縣','雲林縣']
# locs = ['新竹縣','雲林縣','臺中市','南投縣']
dict_loc = []
Wx = [] #天氣狀態 晴時多雲偶陣雨 
PoP = [] #降雨機率
MinT = [] #最低溫度
CI = [] #體感
MaxT = [] #最高溫度
pushtext_list = []
weather_dicts = {
                'locationName': dict_loc,
                'Wx': Wx,
                'PoP': PoP,
                'MinT': MinT,
                'CI': CI,
                'MaxT': MaxT
            }

def fetch_weather(loc):
    logging.info('Start to fetch data from cwb_api, please wait...')
    url_cwb = 'https://opendata.cwb.gov.tw/api/v1/rest/datastore/F-C0032-001?Authorization='+toekn_cwb+'&locationName='+loc
    headers = { 'user-agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 \
                 (KHTML, like Gecko) Chrome/79.0.3945.117 Safari/537.36'}
  
    dict_loc.append(loc)

    res = requests.get(url_cwb,headers=headers)
    if res.status_code == requests.codes.ok:
        data = res.json()
        if data.get('success') == 'true':
            for elem in data['records']['location']:
                dict_data = elem['weatherElement']
                Wx_dict = dict_data[0]['time']
                Wx_dict_parameter = Wx_dict[1]['parameter']
                Wx.append(Wx_dict_parameter['parameterName'])

                PoP_dict = dict_data[1]['time']
                PoP_dict_parameter = PoP_dict[1]['parameter']
                PoP.append(PoP_dict_parameter['parameterName'])

                MinT_dict = dict_data[2]['time']
                MinT_dict_parameter = MinT_dict[1]['parameter']
                MinT.append(MinT_dict_parameter['parameterName'])

                CI_dict = dict_data[3]['time']
                CI_dict_parameter = CI_dict[1]['parameter']
                CI.append(CI_dict_parameter['parameterName'])

                MaxT_dict = dict_data[4]['time']
                MaxT_dict_parameter = MaxT_dict[1]['parameter']
                MaxT.append(MaxT_dict_parameter['parameterName'])
        
        else:
            print('fetch cwb is not success!')
            return()
    else:
        print('requests url is error!')
        return()

def dict_to_pd(weather_dicts):
    weather_dicts_df = pd.DataFrame()
    weather_dicts_df = weather_dicts_df.append(weather_dicts,ignore_index=True)
    return weather_dicts_df
    
def output_text(weather_dicts_df):
    for i in range(len(weather_dicts_df.iloc[0,0])):
        pushtext = '明天'+str(weather_dicts_df.iloc[0,5][i])+' 天氣:'+str(weather_dicts_df.iloc[0,4][i])+\
                    '('+str(weather_dicts_df.iloc[0,0][i])+')'+' 降雨機率:'+str(weather_dicts_df.iloc[0,3][i])+'% 溫度'+\
                        str(weather_dicts_df.iloc[0,2][i])+'-'+str(weather_dicts_df.iloc[0,1][i])+'度'
        pushtext_list.append(pushtext)
        

def lineNotifyMessage(token, msg):
      headers = {
          "Authorization": "Bearer " + token, 
          "Content-Type" : "application/x-www-form-urlencoded"
      }
      payload = {'message': msg}
      r = requests.post("https://notify-api.line.me/api/notify", headers = headers, params = payload)
      return r.status_code

def main():
    dict_loc.clear()
    Wx.clear()
    PoP.clear()
    MinT.clear()
    CI.clear()
    MaxT.clear()
    pushtext_list.clear()
    for i in range(len(locs)):
        fetch_weather(locs[i])
    output_text(dict_to_pd(weather_dicts))
    for i in range(len(pushtext_list)):
        #print(pushtext_list[i])
        lineNotifyMessage(token_line, pushtext_list[i]+'\n')


if __name__ == '__main__':
    starttime = time.time()
    main()
    print('-----------')
    print('RunTime:')
    print(time.time()-starttime)