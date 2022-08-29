import json
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
    current_page = 1
    last_page = 200
    change = []
    changePercent = []
    nav = []
    tradeDate = []

    while 1:
        max_try = 3
        re_try = 0
        while re_try < max_try:

            response = requests.get(
                f"https://fund.api.cnyes.com/fund/api/v1/funds/{fund_id}/nav?format=table&page={str(current_page)}")
            time.sleep(0.01)
            try:
                current_page = json_to_dict(response.text)['items']['current_page']
                last_page = json_to_dict(response.text)['items']['last_page']
            except ValueError as v:
                logging.critical(f"{fund_id}: 404 not found, {v}")
                current_page = last_page = 0
                break

            try:
                fund_datas = json_to_dict(response.text)['items']['data']

                for fund_data in fund_datas:
                    change.append(fund_data['change'])
                    changePercent.append(fund_data["changePercent"])
                    nav.append(fund_data["nav"])
                    tradeDate.append(timestamp_to_date(fund_data["tradeDate"]))
                # print(f"{fund_id} page: {current_page} success")
                break
            except Exception as e:
                re_try += 1
                logging.critical(
                    "fail: https://fund.api.cnyes.com/fund/api/v1/funds/A16013/nav?format=table&page=" + str(
                        current_page))
                logging.warning(e)
                continue

        if current_page >= last_page:
            data_dict = {"tradeDate": tradeDate, "nav": nav, "change": change, "changePercent": changePercent}
            df = pd.DataFrame(data_dict)
            df = df.set_index("tradeDate")
            df.to_csv(f"fund_info_anue\\{fund_id}.csv")
            break
        else:
            current_page += 1


if __name__ == "__main__":
    logging.basicConfig(filename='fund_crawler.log', level=logging.WARNING)
    df = pd.read_csv(r"fund_info_new.csv")['cnyesId']
    for fund_id in tqdm(df):
        download_fund(fund_id)
