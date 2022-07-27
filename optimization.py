import csv
import reliability as R
csv_file1 = 'example.csv'
csv_file2 = 'review_example.csv'

def read(csv_file):
    f = open(csv_file, "r")
    rdr = csv.reader(f)
    csv_list = list()

    for line in rdr:
        csv_list.append(line)
    f.close()
    return csv_list

def make(csv_list1, csv_list2):
    k = 1
    result = list()
    store = csv_list1[0].index('가게이름')
    address = csv_list1[0].index('주소')
    category = csv_list1[0].index('카테고리')

    store_index = csv_list2[0].index('가게이름')
    id_index = csv_list2[0].index('ID')
    score_index = csv_list2[0].index('별점')
    day_index = csv_list2[0].index('날짜')
    review_index = csv_list2[0].index('리뷰')

    for i in range(1, len(csv_list1)):
        introduce = R.Store(csv_list1[i][store], csv_list1[i][address], csv_list1[i][category])
        while k < len(csv_list2) and csv_list1[i][store] == csv_list2[k][store_index]:
            introduce.review_append(csv_list2[k][id_index], csv_list2[k][score_index],
                                    csv_list2[k][day_index], csv_list2[k][review_index])
            k += 1
        introduce.user_overlap()
        introduce.score_correction()
        introduce.latest()
        result.append(introduce)
    return result

def update(class_list):
    f = open('write.csv', 'w', newline='')
    wr = csv.writer(f)
    wr.writerow(['가게이름','평점','ID','별점','날짜','리뷰'])
    for line in class_list:
        result = line.write()
        for i in result:
            wr.writerow(i)
    f.close()

def main():
    csv_list1 = read(csv_file1)
    csv_list2 = read(csv_file2)
    class_list = make(csv_list1, csv_list2)
    update(class_list)

if __name__ == '__main__':
    main()
