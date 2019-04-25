# -*- coding: utf-8 -*-
import re

patten = re.compile(r"\d{6}")

with open("2016.txt", mode="r", encoding="utf-8") as f:
    try:
        for line in f:
            if not patten.search(line):
                with open("2016_1.txt", mode="a", encoding="utf-8") as t:
                    t.write(line)
    except KeyboardInterrupt:
        print(line.strip())
