## =======================================================
## Program: Marmoset SQL (marm2)
## Author: Le Zhang
## Email: l652zhan@uwaterloo.ca
## Created Time: 2024-03-20
## Modified by:
##   [2024-03-20] - Le Zhang - CS136 (Winter 2024)
## Company: University of Waterloo
## Department: School of Computer Science
## =======================================================

import csv
import os
import getpass
import subprocess
from datetime import datetime, timedelta
import sys
import pymysql
from pymysql.cursors import Cursor
import re

# ====================================================================
# FOLLOWING IS ASSIGNMENT SETUP
# ====================================================================
# Grace Period in minutes
GRACE_PERIOD = 1  # MINUTES

# ====================================================================
# FOLLOWING IS ENV VARIABLES
# ====================================================================
# Get home path
HOME = os.getenv("HOME")

# Course this script is running as
# ex. CS136
COURSENAME = getpass.getuser().upper()

CURR_TERMCODE_CMD = "/u/isg/bin/termcode"
CURR_TERMCODE = subprocess.check_output(CURR_TERMCODE_CMD, shell=True).decode('utf-8').strip()

CURRTERM_CMD = "/u/isg/bin/termcode -l"
CURRTERM = subprocess.check_output(CURRTERM_CMD, shell=True).decode('utf-8').strip()

CURR_SESSION_CMD = "/u/isg/bin/termcode -l | awk '{print tolower(substr($0, 1, 1))}'"
CURR_SESSION = subprocess.check_output(CURR_SESSION_CMD, shell=True).decode('utf-8').strip()


CURR_YEAR_CMD = "/u/isg/bin/termcode -l | awk '{print substr($0, length($0)-1, length($0))}'"
CURR_YEAR = subprocess.check_output(CURR_YEAR_CMD, shell=True).decode('utf-8').strip()

# Path of database infromation
PATH_DB_INFO = f"{HOME}/.my.cnf"

# ====================================================================
# Helper Functions
# ====================================================================

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


def load_db_info(db_info: str):
    """
    Loads database connection information from a file.

    Parameters:
    - db_info (str): The file path to the database information file.

    Returns:
    - tuple: A tuple containing the database host, database name, user, and password.

    The database information file should contain lines in the format of 'key=value',
    where keys are 'host', 'database', 'user', and 'password'. Each of these details
    are extracted and returned.

    Example:
    db_details = load_db_info("path/to/db_info.txt")
    """
    with open(db_info, mode='r') as infile:
        for line in infile:
            line = line.strip()
            if 'host' in line:
                host = line.split('=')[1]
            if 'database' in line:
                database = line.split('=')[1]
            if 'user' in line:
                user = line.split('=')[1]
            if 'password' in line:
                password = line.split('=')[1]
    return host, database, user, password


def sql_execute(cursor: Cursor, cmd: str):
    """
    Executes an SQL command using the given cursor and returns the results.

    Parameters:
    - cursor (Cursor): The database cursor.
    - cmd (str): The SQL command to execute.

    Returns:
    - The result of the SQL command. The return type can vary: it might be a list, a single value, or an empty list,
      depending on the command's results.

    The function first attempts to execute the provided SQL command. If the command
    returns no rows, an empty list is returned. If the command returns rows, and if
    there's only one row with one column, the single value is returned. Otherwise,
    the full result set is returned.

    Example:
    results = sql_execute(cursor, "SELECT * FROM students")
    """
    result = cursor.execute(cmd)
    result = cursor.fetchall()
    if result == ():
        result = []
    else:
        result_keys = list(result[0].keys())
        if len(result) == 1:
            if len(result_keys) == 1:
                result = result[0][result_keys[0]]              
    return result


def db_init(assn: str):
    """
    Initializes the database connection and retrieves specific project information.

    Parameters:
    - assn (str): The assignment identifier.

    Returns:
    - tuple: A tuple containing the database connection, cursor, project information, and student registration information.

    This function reads the database connection info, establishes a connection, and executes
    queries to retrieve specific information about courses, projects, and student registrations
    based on the provided assignment identifier. The function returns the database connection
    and cursor along with the retrieved project and student registration information.

    If the course, project, or student registration information cannot be found, the function
    will close the database connection and exit.

    Example:
    db, cursor, projects, student_reg = db_init("a")
    """
    now = datetime.today().strftime('%Y-%m-%d %H:%M:%S')

    host_name, db_name, user_name, user_password = load_db_info(PATH_DB_INFO)
    db = pymysql.connect(host=host_name,
                        user=user_name,
                        password=user_password,
                        database=db_name,
                        cursorclass=pymysql.cursors.DictCursor)
    cursor = db.cursor()

    course_pk_query = f"select course_pk from courses where semester ='{CURRTERM}' and coursename='{COURSENAME}'"
    course_pk = sql_execute(cursor, course_pk_query)
    
    if assn == 'a':
        project_pk_query = f"""select project_pk, project_number, ontime from projects where 
                           course_pk ='{course_pk}' and ontime < '{now}'"""
    elif assn == 'c':
        project_pk_query = f"""select project_pk, project_number, ontime 
                                    from projects 
                                    where course_pk = '{course_pk}'
                                    and ontime = (
                                        select MAX(ontime) 
                                        from projects 
                                        where course_pk = '{course_pk}' and ontime < '{now}'
                                    )"""
    else:
        assn = assn.upper()
        if re.search('^[0-9]+$', assn):
            project_pk_query = f"select project_pk, project_number, ontime from projects where course_pk = '{course_pk}' and project_number regexp '^(A|LAB){assn}[PBQ].*';"
        elif re.search('^((A|LAB)[0-9]+)$', assn):
            project_pk_query = f"select project_pk, project_number, ontime from projects where course_pk = '{course_pk}' and project_number regexp '^{assn}[PBQ].*';"
        else:
            project_pk_query = f"select project_pk, project_number, ontime from projects where course_pk = '{course_pk}' and project_number regexp '{assn}';"

    projects = sql_execute(cursor, project_pk_query)

    student_reg_pk_query = f"""select cvs_account, student_registration_pk from student_registration where course_pk='{course_pk}'"""
    student_reg_pk = sql_execute(cursor, student_reg_pk_query)

    if course_pk == [] or projects == [] or student_reg_pk == []:
        db.close()
        exit(1)
    else:
        return db, cursor, projects, student_reg_pk

# ====================================================================
# Functions
# ====================================================================

def marks(assn: str, file: str, dest: str, verbose: bool):
    """
    Processes student submissions for a given assignment and writes their grades into a CSV file.

    Parameters:
    - assn (str): The assignment identifier (e.g., "a1" for Assignment 1).
    - file (str): Path to the file containing the list of student IDs.
    - dest (str): Destination directory path where the output CSV file will be saved.
    - verbose (bool): If True, the function prints detailed progress information.

    This function performs the following steps:
    1. Initializes database connection and retrieves projects and student registration information.
    2. For each project related to the assignment, it fetches submission data from the database.
    3. Calculates the highest mark for each student and writes these to a CSV file named after the project.
    
    Note:
    - The function assumes the presence of a grace period (GRACE_PERIOD) for submissions.
    - It handles different project types by analyzing the project name prefix.
    - The verbose option enables real-time progress tracking on the console.
    """
    verbose = int(verbose)
    student_list = get_student_list(file)
    db, cursor, projects, student_reg_pk = db_init(assn)
    student_reg_pk_dict = {item['cvs_account']: item['student_registration_pk'] for item in student_reg_pk}

    assn_num = -1

    if not os.path.exists(dest):
        os.makedirs(dest)

    for project in projects:
        proj_pk = project['project_pk']
        project_name = project['project_number']
        ontime_date = project['ontime']
        deadline = ontime_date + timedelta(minutes=GRACE_PERIOD)
        project_type = re.split(r'\d+', project_name)[0].upper()
        current_assn_num = int(project_name[len(project_type)])

        if current_assn_num != assn_num:
            assn_num = current_assn_num
            print(f"[Downloading {project_type}{assn_num}] to: {dest}")

        submissions_query = f"""select student_registration_pk, submission_timestamp, num_passed_overall from submissions where project_pk='{proj_pk}'"""
        submissions = sql_execute(cursor, submissions_query)
        submissions_dict = {}
        for item in submissions:
            student_registration_pk = item['student_registration_pk']
            if student_registration_pk in submissions_dict:
                submissions_dict[student_registration_pk].append({'submission_timestamp': item['submission_timestamp'],
                                                                  'num_passed_overall': item['num_passed_overall']})
            else:
                submissions_dict[student_registration_pk] = [{'submission_timestamp': item['submission_timestamp'],
                                                              'num_passed_overall': item['num_passed_overall']}]
        
        with open(f"{dest}/project-{project_name}-grades.csv", mode="w") as outfile:
            writer = csv.writer(outfile)
            total_students_num = len(student_list)
            current_students_num = 0
            for uw_id in student_list:
                student_registration_pk = student_reg_pk_dict[uw_id]

                if student_registration_pk in submissions_dict:
                    student_submission = submissions_dict[student_registration_pk]
                    if assn_num == 0:
                        highest_mark = max(student_submission, key=lambda x: x['num_passed_overall'])['num_passed_overall']
                    else:
                        on_time_submission = list(filter(lambda x: x['submission_timestamp'] <= deadline, student_submission))
                        if on_time_submission != []:
                            highest_mark = max(on_time_submission, key=lambda x: x['num_passed_overall'])['num_passed_overall']
                        else:
                            highest_mark = 0
                else:
                    highest_mark = 0
                writer.writerow([uw_id, highest_mark])

                if verbose:
                    current_students_num += 1
                    print(f">> {current_students_num}/{total_students_num}: {project_name}", end='\r' , flush=True)
            if verbose:
                print(f">> {current_students_num}/{total_students_num}: {project_name}")
            else:
                print(f">> {project_name}")
        
    db.close()


def download(assn: str, file: str, dest: str, verbose: bool):
    """
    Downloads the best submission archives for a given assignment for all students listed in the specified file.

    Parameters:
    - assn (str): The assignment identifier.
    - file (str): The file path that contains a list of student IDs.
    - dest (str): The destination directory where the submission archives will be saved.
    - verbose (bool): If True, prints detailed progress information during execution.

    This function:
    1. Sets up a database connection and fetches project and student registration data.
    2. For each project related to the assignment, it fetches student submissions.
    3. Identifies the best submission for each student based on the highest number of passed tests or submission timestamp.
    4. Downloads and saves the best submission archive for each student in the specified destination.
    
    Note:
    - Assumes the presence of a grace period for submissions.
    - Uses project type and assignment number to organize downloads.
    - Provides real-time progress updates if verbose is true.
    """
    verbose = int(verbose)
    student_list = get_student_list(file)
    db, cursor, projects, student_reg_pk = db_init(assn)
    student_reg_pk_dict = {item['cvs_account']: item['student_registration_pk'] for item in student_reg_pk}

    assn_num = -1
    
    for project in projects:
        proj_pk = project['project_pk']
        project_name = project['project_number']
        ontime_date = project['ontime']
        deadline = ontime_date + timedelta(minutes=GRACE_PERIOD)
        project_type = re.split(r'\d+', project_name)[0].upper()
        current_assn_num = int(project_name[len(project_type)])

        if current_assn_num != assn_num:
            assn_num = current_assn_num
            print(f"[Downloading {project_type}{assn_num}] to: {dest}")

        submissions_query = f"""select student_registration_pk, submission_timestamp, archive_pk, num_passed_overall from submissions where project_pk='{proj_pk}'"""
        submissions = sql_execute(cursor, submissions_query)
        submissions_dict = {}
        for item in submissions:
            student_registration_pk = item['student_registration_pk']
            if student_registration_pk in submissions_dict:
                submissions_dict[student_registration_pk].append({'submission_timestamp': item['submission_timestamp'],
                                                                  'num_passed_overall': item['num_passed_overall'],
                                                                  'archive_pk': item['archive_pk']})
            else:
                submissions_dict[student_registration_pk] = [{'submission_timestamp': item['submission_timestamp'],
                                                              'num_passed_overall': item['num_passed_overall'],
                                                              'archive_pk': item['archive_pk']}]
        
        assignment_folder = f"{dest}/a{assn_num}/{project_name}"
        
        if not os.path.exists(assignment_folder):
            os.makedirs(assignment_folder)

        total_students_num = len(student_list)
        current_students_num = 0
        for uw_id in student_list:
            student_registration_pk = student_reg_pk_dict[uw_id]

            if student_registration_pk in submissions_dict:
                student_submission = submissions_dict[student_registration_pk]
                if assn_num == 0:
                    best_archive_pk = max(student_submission, key=lambda x: x['num_passed_overall'])['archive_pk']
                else:
                    on_time_submission = list(filter(lambda x: x['submission_timestamp'] <= deadline, student_submission))
                    if on_time_submission != []:
                        best_archive_pk = max(on_time_submission, key=lambda x: x['num_passed_overall'])['archive_pk']
                    else:
                        best_archive_pk = 0
            else:
                best_archive_pk = 0
            
            if best_archive_pk:
                zip_file_query = f"""select archive from submission_archives where submission_archives.archive_pk='{best_archive_pk}';"""
                binary_zip = sql_execute(cursor, zip_file_query)
                with open(f"{assignment_folder}/{uw_id}.zip", "wb") as file:
                    file.write(binary_zip)

            if verbose:
                    current_students_num += 1
                    print(f">> {current_students_num}/{total_students_num}: {project_name}", end='\r' , flush=True)
        if verbose:
            print(f">> {current_students_num}/{total_students_num}: {project_name}")
        else:
            print(f">> {project_name}")
    
    db.close()     


def outof(assn: str):
    """
    Retrieves and prints the total points available for each project associated with a given assignment.

    Parameters:
    - assn (str): The assignment identifier.

    This function:
    1. Initializes the database connection and retrieves project information.
    2. For each project, it fetches the total points available excluding 'build' test types.
    3. Prints the available points for each project, grouped by assignment.

    The output format includes a header with the assignment number followed by project names and their respective points.
    
    Note:
    - Sorts the projects by their names before printing.
    - Outputs directly to the console.
    """
    db, cursor, projects, student_reg_pk = db_init(assn)

    result = {}
    for project in projects:
        proj_pk = project['project_pk']
        project_name = project['project_number'].split('-')[0]

        test_run_pk_query = f"""select test_run_pk from project_jarfiles where project_pk = '{proj_pk}' and jarfile_status='active';"""
        test_run_pk = sql_execute(cursor, test_run_pk_query)

        outof_query = f"""select sum(point_value) from test_outcomes where test_type <> 'build' and test_run_pk = '{test_run_pk}';"""
        outof = sql_execute(cursor, outof_query)
        result[project_name] = outof
    db.close() 
    result = dict(sorted(result.items(), key=lambda item: item[0]))
    
    if result != {}:
        print("project,fullMarks")
        current_num = -1
        for project in result:
            assignment_num = int(project[1])
            if assignment_num > current_num:
                current_num = assignment_num
                print(f"# Assignment {current_num}")
            print(f"{project},{result[project]}")
    else:
        print("INVALID NUMBER")

# ====================================================================
# Start of main program
# ====================================================================

def main():
    func = sys.argv[1]
    if func == 'marks':
        if len(sys.argv) == 6:
            assn = sys.argv[2]
            file = sys.argv[3]
            dest = sys.argv[4]
            verb = sys.argv[5]
            marks(assn, file, dest, verb)
        else:
            print("Usage: ASSIGNMENT_NUM, CLASSLIST_PATH, DESTINATION")
            sys.exit(1)
    elif func == 'download':
        if len(sys.argv) == 6:
            assn = sys.argv[2]
            file = sys.argv[3]
            dest = sys.argv[4]
            verb = sys.argv[5]
            download(assn, file, dest, verb)
        else:
            print("Usage: ASSIGNMENT_NUM, CLASSLIST_PATH, DESTINATION")
            sys.exit(1)
    elif func == 'outof':
        if len(sys.argv) == 3:
            assn = sys.argv[2]
            outof(assn)
        else:
            print("Usage: ASSIGNMENT_NUM")
            sys.exit(1)
    else:
        print("Invalid function call")
        sys.exit(1)


main()
