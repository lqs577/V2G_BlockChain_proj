import xlrd


def calculate_p_req():
    workbook1 = xlrd.open_workbook('./sc1std19.xlsx')
    sheet1 = workbook1.sheet_by_index(0)
    data = []
    for i in range(1, 366):
        row_data = []
        for j in range(1, 25):
            row_data.append(sheet1.cell_value(i, j) * 983.99e8)
        data.append(row_data)
    p_low = 1.05e7
    p_high = 1.15e7
    p_req_list = []
    for item in data[300]:
        if item > p_high:
            p_req_list.append(item - p_high)
        elif item < p_low:
            p_req_list.append(item - p_low)
        else:
            p_req_list.append(0)
    print("p_req_list= " + str(p_req_list))
    print("complete calculating p_req")
    return p_req_list
