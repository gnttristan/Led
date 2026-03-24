def read_list_csv(i=12):
    with open("./dataframes/pddf.csv", 'r') as f:
        for lineno, line in list(enumerate(f)):
            if lineno == i:
                line = line.strip()
                row = [int(float(x.strip())) for x in line.split(',')[1:]]
                return row

        return None

read_list_csv(12)