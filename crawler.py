import pandas as pd
import requests
import json
from tqdm import tqdm

"""
search cnyesId by isin
https://ess.api.cnyes.com/ess/api/v1/siteSearch/main?q=TW000T4717G9&category=TW,FUND,US,CC,INDEX,FUTURE,ETF,FX,EOD,CHK&limit=1

result
{
  "statusCode": 200,
  "message": "OK",
  "data": {
    "quoteFunds": [
      {
        "objectType": "FUND",
        "cnyesId": "A1BDLmt",
        "isin": "<mark>TW000T4717G9</mark>",
        "displayNameLocal": "台新北美收益資產證券化基金(後收月配息型)—新臺幣",
        "displayName": "Taishin North American Income Trust Fund TWD N"
      }
    ],
    "news": [],
    "oldDrivers": [
      {
        "objectType": "OLD_DRIVER",
        "driverId": "696B1A1BCCE73B5DD5DD298380C5CED7C5CBF108",
        "nickname": "<mark>G</mark>",
        "avatarPicture": "",
        "return1Year": 0.0,
        "yearLowestPerformance": 0.0,
        "assetLevel": "未滿20萬",
        "riskLevel": ""
      }
    ]
  }
}

"""


def search_cnyesId_by_isin(isin):
    url = f"https://ess.api.cnyes.com/ess/api/v1/siteSearch/main?q={isin}\
&category=FUND&limit=1"
    response = requests.get(url)
    dic = json.loads(response.text)
    cnyesId = dic['data']['quoteFunds'][0]['cnyesId']
    return cnyesId


if __name__ == "__main__":
    df = pd.read_csv('fund_info_old.csv')
    ids = []
    isins = []
    cnyesIds = []
    with tqdm(total=6000) as pbar:
        pbar.set_description('Processing:')

        for key, isin in enumerate(df['isin']):
            pbar.update(1)
            ids.append(key)
            isins.append(isin)
            cnyesIds.append(search_cnyesId_by_isin(isin))
        pd.DataFrame(data={"id": ids, "isin": isins, "cnyesId": cnyesIds}).to_csv('fund_info_new.csv')
