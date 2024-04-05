import csv
import sys

def get_student_list(classlist_file: str):
    """
    Reads a class list file and extracts the student names.

    Parameters:
    - classlist_file (str): The file path to the class list.

    Returns:
    - List[str]: A list of student names extracted from the class list.

    The class list file is expected to have multiple lines, where each line represents
    a student entry. Lines starting with '#' or empty lines are ignored. Student names
    are assumed to be in the second column of each line, separated by commas.

    Example:
    student_names = get_student_list("path/to/classlist.csv")
    """
    studentList = []
    with open(classlist_file, mode="r") as classlist:
        for line in classlist:
            if line.strip().startswith('#') or line.strip() == "":
                continue
            else:
                studentList.append(line.split(',')[1])
    return studentList

def diff(old_result, new_result, classlist):
    student_list = get_student_list(classlist)
    old_scores = {}
    new_scores = {}
    with open(old_result, mode='r') as file1:
        data1 = csv.reader(file1)
        for row in data1:
            old_scores[row[0]] = row[1:]
    
    with open(new_result, mode='r') as file2:
        data2 = csv.reader(file2)
        for row in data2:
            new_scores[row[0]] = row[1:]

    old_more = False
    new_more = False
    assements_old = old_scores['']
    assements_new = new_scores['']
    len_old = len(assements_old)
    len_new = len(assements_new)
    midterm_old = 'Midterm' in assements_old
    midterm_new = 'Midterm' in assements_new

    if len_old != len_new:
        if len_old < len_new:
            new_more = True
            assements = assements_old
        else:
            old_more = True
            assements = assements_new
    else:
        assements = assements_old
    
    for uw_id in student_list:
        if uw_id in old_scores and uw_id in new_scores:
            old_data = old_scores[uw_id]
            new_data = new_scores[uw_id]

            if len_old < len_new:
                if midterm_new:
                    new_data = new_data[:len_old - 1] + new_data[-1:]
                else:
                    new_data = new_data[:len_old]
            else:
                if midterm_old:
                    old_data = old_data[:len_new - 1] + old_data[-1:]
                else:
                    old_data = old_data[:len_new]
            for i in range(len_old - 1):
                if new_data[i] != old_data[i]:
                    same = False
                    print(f"[{uw_id} - {assements[i]}]: {old_data[i]} -> {new_data[i]}")
        elif uw_id in old_scores and uw_id not in new_scores:
            print(f"{uw_id} Not in new edx_marks.csv")
        elif uw_id not in old_scores and uw_id in new_scores:
            print(f"{uw_id} Not in old edx_marks.csv")
    
    if new_more:
        print(f"New edx_marks.csv has more Assements")
    if old_more:
        print(f"Old edx_marks.csv has more Assements")


def main():
    if len(sys.argv) == 4:
        old_result = sys.argv[1]
        new_result = sys.argv[2]
        classlist = sys.argv[3]
        diff(old_result, new_result, classlist)

main()
