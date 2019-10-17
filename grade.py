#!/usr/bin/env python3
import os, re, signal, subprocess, sys

TIMEOUT = 300

WORKDIR = "temporary_script_folder"

# handle failure or interrupt by cleaning first
def fail(exit_code=1):
    bash(f"rm -rf {WORKDIR}")
    exit(exit_code)

# returns out, exits on error; throws TimeoutExpired
def bash(cmd, cwd=None, expectErrors=False):
    process = subprocess.Popen(cmd.split(), stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=cwd)
    out, err = process.communicate(timeout=TIMEOUT)
    if err:
        if expectErrors:
            return "ERROR"
        print(err.decode("utf-8"), "Error has occurred, exiting...")
        fail()
    return out.decode("utf-8")

# returns a map of {studentname -> map{original_filename -> path_to_file}}
def getSubmissions(directory):
    files = [f for f in os.listdir(directory) if f.endswith(".py")]
    submissions = {}
    for file in files:
        split = file.split("_")
        student = split[0]
        filename = re.sub(r'-[0-9]+\.', ".", split[-1]) # canvas adds -1 to re-submissions, as in search-1.py
        if student not in submissions:
            submissions[student] = {}
        submissions[student][filename] = directory + "/" + file
    return submissions

# finds the total score and formats it, or exits if multiple or none in correct format
def parseGrade(output):
    matches = re.findall(r'Total: [0-9]+/[0-9]+', output)
    if len(matches) != 1:
        print(output, "Ambiguous or incorrect autograder.py output")
        fail()
    return matches[0].split(" ")[1]

# register SIGINT handler, unzip submissions and project; returns path to unzipped project
def setup(zipfile, projectfile):
    def handler(signal, frame):
        print("Stopping.")
        fail(0)
    signal.signal(signal.SIGINT, handler)

    bash(f"rm -rf {WORKDIR}")
    bash(f"mkdir {WORKDIR}")
    print("Unzipping submissions...")
    bash("unzip " + zipfile + f" -d {WORKDIR}")
    bash(f"mkdir {WORKDIR}/project")
    print("Unzipping project...")
    bash("unzip " + projectfile + f" -d {WORKDIR}/project")
    return WORKDIR + "/project/" + os.listdir(WORKDIR + "/project/")[0]

def main(args):
    if len(args) <= 2:
        print("[Usage] ./grade.py [submissions.zip path] [project.zip path] <file1.py file2.py ... fileN.py>")
        fail()
    zipfile = args[0]
    projectfile = args[1]
    tested_files = args[2:]

    project_path = setup(zipfile, projectfile)
    submissions = getSubmissions(WORKDIR)

    format_width = len(max(submissions.keys(), key=lambda k: len(k)))

    print("")
    print("=" * (format_width + 7))
    for student in sorted(submissions):
        submitted_files = submissions[student]
        grade_string = ""
        if set(submitted_files.keys()) != set(tested_files):
            grade_string = "BAD SUBMISSION: " + ', '.join(submitted_files.keys())
        else:
            for expected_name, file_path in submitted_files.items():
                bash(f"mv {file_path} {project_path}/{expected_name}")
                bash(f"rm -f {project_path}/{expected_name}c") # remove the precompiled file; else old submission is run
            try:
                grader_out = bash(f"python2 autograder.py --no-graphics ", cwd=project_path, expectErrors=True)
                grade_string = "PYTHON ERROR IN SUBMISSION" if grader_out == "ERROR" else parseGrade(grader_out)
            except subprocess.TimeoutExpired:
                grade_string = "TIMED OUT IN " + str(TIMEOUT) + "s"
        print(f"{student.rjust(format_width)}: {grade_string}")


    print("=" * (format_width + 7))
    print()

    bash(f"rm -rf {WORKDIR}")
    print("Done.")


main(sys.argv[1:])
