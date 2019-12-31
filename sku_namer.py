"""
Using a csv as an input where the 1st column is the path of a file, and the 2nd a new filename,
renames the file with the new name.
"""

import os
import csv
import argparse
from datetime import datetime

# Set logging variables
log_file_name = f"log_{os.getpid()}.csv"
log_file = open(log_file_name, "w", newline="")
log = csv.writer(log_file)

log.writerow(["datetime", "message", "error"])
success = 0
error = 0


def fix_path(path):
    """Converts a windows path to linux and vise versa"""
    return os.path.abspath(os.path.expanduser(path))


def log_event(msg, err=True, echo=True):
    """Logs event to log and optionally the terminal"""
    if echo:
        e_str = "ERROR: " if err else ""
        print(e_str, msg)
    log.writerow([datetime.now(), msg, err])


# Accept arguments
parser = argparse.ArgumentParser(
    epilog="description: renames files linked in the first column of a csv with the file-names in the 2nd column."
)

parser.add_argument("input_csv", help="path to input csv")
parser.add_argument(
    "-d",
    "--parent_dir",
    help="directory of file location (default=current working dir)",
    default=os.getcwd(),
)
parser.add_argument(
    "-i",
    "--include_header",
    help="include first (header) column (default=True)",
    default=True,
)
args = parser.parse_args()


# Verify inputs
if not os.path.isfile(args.input_csv):
    msg = f"The file 'f{args.input_csv}' is not a valid .csv file"
    log_event(msg)
    quit()
if not os.path.isdir(args.parent_dir):
    msg = f"The parent directory '{args.parent_dir}' is not a valid directory"
    log_event(msg)
    quit()


# Do the work
first_row = args.include_header
with open(args.input_csv) as csvfile:
    reader = csv.reader(csvfile)
    for row in reader:
        if first_row:
            log_event("Skipping header row (use -s to suppress)", err=False)
            first_row = False
            continue
        if row[0] != "":
            file_path = fix_path(os.path.join(args.parent_dir, row[0]))
            file_dir = os.path.dirname(file_path)
            file_info = os.path.splitext(os.path.basename(file_path))
            file_ext = file_info[1]

            new_file_path = os.path.join(file_dir, row[1] + file_ext)

            try:
                os.rename(file_path, new_file_path)
                log_event(f"{file_path} -> {new_file_path}", err=False, echo=False)
                success += 1
            except Exception as e:
                log_event(e, echo=False)
                error += 1

print(f"Operation complete with {success} successes and {error} errors.")
print(f"View log file at '{os.path.join(os.getcwd(), log_file_name)}'")
