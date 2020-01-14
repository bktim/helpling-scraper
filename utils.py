import csv


def read_plz(csv_path: str):
    plz = []
    with open(csv_path, 'r') as csvfile:
        plz_reader = csv.reader(csvfile)
        for row in plz_reader:
            plz.append(str(row[0]))

    return plz


if __name__ == "__main__":
    plz = read_plz('plz_berlin.csv')
    print(plz)
