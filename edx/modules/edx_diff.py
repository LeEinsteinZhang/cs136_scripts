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
    """
    Compares scores between two result sets for assignments by name,
    ensuring alignment in printed output.
    """
    student_list = get_student_list(classlist)
    old_scores = {}
    new_scores = {}

    with open(old_result, mode='r') as file1:
        data1 = csv.reader(file1)
        headers_old = next(data1)
        for row in data1:
            student_scores = {headers_old[i]: row[i] for i in range(1, len(row))}
            old_scores[row[0]] = student_scores

    with open(new_result, mode='r') as file2:
        data2 = csv.reader(file2)
        headers_new = next(data2)
        for row in data2:
            student_scores = {headers_new[i]: row[i] for i in range(1, len(row))}
            new_scores[row[0]] = student_scores

    common_assignments = set(headers_old).intersection(headers_new)
    common_assignments.remove('')

    for uw_id in student_list:
        if uw_id not in old_scores or uw_id not in new_scores:
            continue
        
        for assignment in common_assignments:
            old_score = old_scores[uw_id].get(assignment, "Missing")
            new_score = new_scores[uw_id].get(assignment, "Missing")
            if old_score != new_score:
                 print(f"[{uw_id:<8} - {assignment:<16}] {old_score} -> {new_score}")


def main():
    if len(sys.argv) == 4:
        old_result = sys.argv[1]
        new_result = sys.argv[2]
        classlist = sys.argv[3]
        diff(old_result, new_result, classlist)

main()
