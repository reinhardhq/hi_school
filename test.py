# coding:utf-8

# import assets
from assets.hischool import fetch_school_info
from assets.hischool import NotFoundException
import traceback


SCHOOL_NAME = '城東'
try:
    # function call like this
    result_list = fetch_school_info(SCHOOL_NAME)
    print(result_list)
    for result in result_list:
        print(result)

except NotFoundException:
    print('存在しない学校です')

except:
    print(traceback.format_exc())
