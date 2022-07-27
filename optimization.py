import csv
import reliability as R
import latest as L
csv_file = 'review_example.csv'

def main():
    f = open(csv_file, "r")
    rdr = csv.reader(f)
    csv_list = list()

    for line in rdr:
        csv_list.append(line)

    l1, l2 = R.reliability(csv_list)
    average = R.score_correction(l2)
    print(l1)
    print(l2)
    print(average)
    f.close()

if __name__ == '__main__':
    main()