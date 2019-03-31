def split():
    with open("../docs/005.year_round_type_court_reason.txt", mode="r", encoding="utf-8") as f:
        for line in f:
            if not line.strip():
                break
            count, url = line.strip().split()
            with open(f"{count}.txt", mode="a", encoding="utf-8") as t:
                t.write(line)

def merge():
    with open("0.merged.txt", mode="a", encoding="utf-8") as t:
        for i in range(21, 401):
            with open(f"{i}.txt", mode="r", encoding="utf-8") as f:
                for line in f:
                    t.write(line)

if __name__ == "__main__":
    merge()