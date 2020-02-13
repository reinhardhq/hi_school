# coding:utf-8

import os
import traceback
import time
import logging
import argparse
import requests
import pandas as pd
import urllib.parse
from retry import retry
from bs4 import BeautifulSoup
from urllib.parse import urljoin


############################################################
#
# みんなの高校情報
#
############################################################
WEB_SITE = 'https://www.minkou.jp/hischool/'


############################################################
#
# 前処理
#
############################################################
logger = logging.getLogger(__name__)
fmt = "%(asctime)s %(levelname)s %(name)s :%(message)s"
logging.basicConfig(level=logging.INFO, filename='hischool_app.log', format=fmt)

# コマンドライン実行引数処理
parser = argparse.ArgumentParser()
parser.add_argument("--output", help="--output is choice csv filename ")
parser.add_argument("--init", help="--init is new empty output csv file and add header" ,action="store_true")
args = parser.parse_args()

# 入力ファイルの指定
if args.output is None:
    RESULT_CSV = os.path.dirname(os.path.abspath(__file__)) + '/' + 'hischool_detail.csv'
else:
    RESULT_CSV = os.path.dirname(os.path.abspath(__file__)) + '/' + args.output

# pandas csv header
INPUT_SHCOOL_NAME = '入力高校名'
ENTRY_SHOOL_NAME = '学校名'
SCHOOL_AREA = '都道府県'
SCHOOL_DETAIL_AREA = '市区町村'
PUBLIC_OR_PRIVATE = '公立・私立'
COED_OR_ONLY = '共学・男子校・女子校'
DEVIATION_VALUE = '偏差値'
# エリア内
AREA_RANK_TITLE = 'ランキングタイトル'
AREA_RANK_NUMERATE = 'ランキング分子'
AREA_RANK_DENOMINATOR = 'ランキング分母'
# 私立・公立
AREA_BY_TYPE_TITLE = '県内公立・私立ランキングタイトル'
AREA_BY_TYPE_RANK_NUMERATE = 'ランキング分子'
AREA_BY_TYPE_RANK_DENOMINATOR = 'ランキング分母'
# 全国
COUNTRY_RANK_TITLE = '全国ランキングタイトル'
COUNTRY_RANK_NUMERATE = 'ランキング分子'
COUNTRY_RANK_DENOMINATOR = 'ランキング分母'

columns = [INPUT_SHCOOL_NAME, ENTRY_SHOOL_NAME, SCHOOL_AREA, SCHOOL_DETAIL_AREA, PUBLIC_OR_PRIVATE, COED_OR_ONLY, DEVIATION_VALUE,
           AREA_RANK_TITLE, AREA_RANK_NUMERATE, AREA_RANK_DENOMINATOR,
           AREA_BY_TYPE_TITLE, AREA_BY_TYPE_RANK_NUMERATE, AREA_BY_TYPE_RANK_DENOMINATOR,
           COUNTRY_RANK_TITLE, COUNTRY_RANK_NUMERATE, COUNTRY_RANK_DENOMINATOR]


############################################################
#
# 独自例外の定義
#
############################################################
class NotFoundException(Exception):
    pass


############################################################
#
# util.csv初期化処理(Header定義)
#
############################################################
def init_csv():
    df = pd.DataFrame(columns=columns)
    df.to_csv(RESULT_CSV, mode='w', header=True,
              index=False, encoding='utf-8')


############################################################
#
# util.csv書き込み
#
############################################################
def add_row_to_csv(write_list):

    if len(write_list) != len(columns):
        not_enough_columns = len(columns) - len(write_list)

        not_enough_list = [' '] * not_enough_columns
        write_list = write_list + not_enough_list
        df = pd.DataFrame([write_list], columns=columns)

    else:
        df = pd.DataFrame([write_list], columns=columns)

    df.to_csv(RESULT_CSV, mode='a', header=False,
              index=False, encoding='utf-8')


############################################################
#
# 1.文字列から高校名検索
#
############################################################
""" shcool info """
def fetch_school_info(school_name):

    result_list = []

    result_list.append(school_name)

    encoded_school_name = urllib.parse.quote(school_name)

    request_endpoint = WEB_SITE + 'search/k=' + encoded_school_name

    res = requests.get(request_endpoint)

    soup = BeautifulSoup(res.text, 'lxml')

    if is_404(soup):
        raise NotFoundException

    else:

        school_list_a = soup.find_all('a')

        for a_tag in school_list_a:

            # bs4.element.Tagをstr変換した上で比較
            # hischool linkのみ取得
            if '/hischool/school/' in str(a_tag):

                hischool_info = a_tag

                hischool_href = hischool_info.get('href')

                hischool_detail_url = urljoin(WEB_SITE, hischool_href)

                res_hischool_detail = requests.get(hischool_detail_url)

                bsoup = BeautifulSoup(res_hischool_detail.text, 'lxml')

                ########################################################
                # 学校名
                ########################################################
                school_name_class = bsoup.select('#main > div.mod-school > div.mod-school-inner > div.mod-school-r > div.mod-school-top > h1 > span')

                system_school_name = school_name_class[0].string

                result_list.append(system_school_name)

                ########################################################
                # 県・エリア・公立/私立・共学／男子校／女子校
                ########################################################
                school_infos_class = bsoup.find(class_='mod-school-spec')

                for info in school_infos_class:

                    info_string = info.string.strip()

                    if '/' in info_string or not info_string:
                        pass

                    else:
                        result_list.append(info_string)

                ########################################################
                # 偏差値
                ########################################################
                hensa_parent = bsoup.find(class_='mod-school-hensa')

                hensa_element = hensa_parent.contents

                hensa = hensa_element[1].string

                result_list.append(hensa)

                ########################################################
                # ランキング
                ########################################################
                ranking_elements = bsoup.find(class_='schMod-rank').strings

                # print(ranking_elements)

                for rank in ranking_elements:
                    rank_striped = rank.strip()

                    if not rank_striped:
                        pass

                    else:
                        result_list.append(rank_striped)

                break

            else:
                pass

        add_row_to_csv(result_list)

        return result_list


############################################################
#
# 高校 is Not Found
#
############################################################
def is_404(soup):

    is_not_exist = False

    result_box_msg = soup.find(class_='result_box')

    if result_box_msg is None:
        return is_not_exist

    else:
        for msg in result_box_msg:
            result = msg.string.strip()

            if 'ありません' in result:
                is_not_exist = True
                break
            else:
                is_not_exist = False

        return is_not_exist


############################################################
#
# main
#   main関数
#
############################################################
if __name__ == '__main__':

    try:
        school_name = '城東'

        if args.init:
            init_csv()

        list = fetch_school_info(school_name)

    except:
        print(traceback.format_exc())
        logger.error(traceback.format_exc())