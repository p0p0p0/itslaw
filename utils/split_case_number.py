with open("casenumber.dat", mode="r", encoding="utf-8") as f:
    for line in f.readlines():
        if not line.strip():
            continue
        case_number = line.strip()
        filename = case_number[1:5] if case_number[1:5].isdigit() else "other"
        with open("case_number/"+filename+".txt", mode="a", encoding="utf-8") as t:
            t.write(case_number+"\n")
