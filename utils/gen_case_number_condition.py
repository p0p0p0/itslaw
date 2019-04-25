import json
from time import sleep
from datetime import datetime
from urllib.parse import urlencode, urlparse

from redis import Redis

r = Redis()
base_url = "https://www.itslaw.com/api/v1/caseFiles?"

def gen_url(count):
    year = 2016
    code = "陕0821执"
    parameters = {
        "startIndex": 0,
        "countPerPage": 20,
        "sortType": 1,
    }
    for i in range(1, count):
        condition = f"searchWord+（{year}）{code}{i}号+1+（{year}）{code}{i}号"
        parameters["conditions"] = condition
        url = base_url + urlencode(parameters)
        r.sadd("conditions:case", url)

def case_number_to_url():
    parameters = {
        "startIndex": 0,
        "countPerPage": 20,
        "sortType": 1,
    }
    case_numbers = r.smembers("panjueshu:casenumber1")
    for each in case_numbers:
        case_number = str(each, encoding="utf-8")
        condition = f"searchWord+{case_number}+1+{case_number}"
        parameters["conditions"] = condition
        url = base_url + urlencode(parameters)
        r.sadd("conditions:case", url)


if __name__ == "__main__":
    case_number_to_url()
