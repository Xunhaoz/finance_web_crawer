import json
import os
import time
import logging
import requests
from datetime import datetime
import pandas as pd
from tqdm import tqdm
import json


def timestamp_to_date(timestamp):
    dt_object = datetime.fromtimestamp(timestamp)
    return dt_object.date()


def json_to_dict(json_form):
    dict_form = json.loads(json_form)
    return dict_form


def download_fund(fund_id):
    change = []
    changePercent = []
    nav = []
    tradeDate = []
    max_try = 3

    for each_try in range(max_try):
        # 藉由 API get 基金第一筆資料
        response = requests.get(
            f"https://fund.api.cnyes.com/fund/api/v1/funds/{fund_id}/nav?format=table&page=1",
            headers={
                "User-Agent": 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.0.0 Safari/537.36',
                'referer': 'https://fund.cnyes.com/'
            })

        try:
            current_page = json_to_dict(response.text)['items']['current_page']
            last_page = json_to_dict(response.text)['items']['last_page']
        except ValueError as v:
            logging.critical(f"{fund_id}: 404 not found, {v}")
            continue

        while current_page <= last_page:

            response = requests.get(
                f"https://fund.api.cnyes.com/fund/api/v1/funds/{fund_id}/nav?format=table&page={current_page}",
                headers={
                    "User-Agent": 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.0.0 Safari/537.36',
                    'referer': 'https://fund.cnyes.com/'
                })

            try:
                fund_datas = json_to_dict(response.text)['items']['data']

                for fund_data in fund_datas:
                    change.append(fund_data['change'])
                    changePercent.append(fund_data["changePercent"])
                    nav.append(fund_data["nav"])
                    tradeDate.append(timestamp_to_date(fund_data["tradeDate"]))

            except ValueError:
                logging.critical(f"{fund_id} api error.")
                break

            if current_page >= last_page:
                data_dict = {"tradeDate": tradeDate, "nav": nav, "change": change, "changePercent": changePercent}
                df = pd.DataFrame(data_dict)
                df = df.set_index("tradeDate")
                df.to_csv(f"fund_info_anue/{fund_id}.csv")
                logging.info(f"{fund_id} download successful.")
                return None

            else:
                current_page += 1


if __name__ == "__main__":
    logging.basicConfig(filename='fund_crawler.log', level=logging.DEBUG)

    df = pd.read_csv(r"no_problem.csv")['cnyesId_old']

    for fund_id in tqdm(df):
        download_fund(fund_id)

