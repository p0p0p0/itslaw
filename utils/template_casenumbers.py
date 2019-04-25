from re import compile
from redis import Redis

r = Redis()

templates = [str(each, encoding="utf-8") for each in r.zrange("casenumber:template", 0, -1)]
patten = compile(r"(\d+)号")

with open("201703.txt", mode="r", encoding="utf-8") as f:
    try:
        for line in f:
            number = patten.findall(line.strip())
            if not number:
                continue
            end = line.find(f"{number[0]}号")
            case = line[:end]
            if case in templates:
                score = r.zscore("casenumber:template", case)
                r.zadd("casenumber:template", {case: max(int(number[0]), score)})
                # print(f"[+] scanning {line.strip()}")
    except KeyboardInterrupt:
        print(line.strip())
