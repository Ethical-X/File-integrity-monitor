import hashlib
import json
import os
import argparse

from pathlib import Path
from time import sleep
from datetime import datetime

# Calculates and returns the given file's SHA256 hash.
def calc_hash(filepath):

    sha256 = hashlib.sha256()

    if Path(filepath).exists():

        with open(filepath, "rb") as file:
            while chunk := file.read(4096):
                sha256.update(chunk)

        return sha256.hexdigest()
    else:
        return "Filepath does not exist or is a directory"


# Converts and stores all files and their corresponding hashes into baseline.json.
def create_baseline(files_dictionary):
    with open("baseline.json", "w") as json_file:
        json_file.write(json.dumps(files_dictionary, indent=4))


# Creates log.json to log changes.
def initialize_logs():

    logs = []

    with open("log.json", "w") as log_file:
        log_file.write(json.dumps(logs))


# Creates the dictionary with file names,hashes and total files.
def create_dictionary():
    dir = Path.cwd()
    files = dir.rglob("*")

    files_dict = dict()

    for file in files:
        if "/files/" in str(file):
            file_path = str(file)
            file_name = Path(file_path).name
            hash = calc_hash(file_path)
            files_dict.update({file_name: hash})


    return files_dict


def get_prev_hash(file):

    with open("baseline.json", "r") as baseline_file:
        baseline = json.load(baseline_file)
        prev_hash = baseline[file]

    return prev_hash


# Returns the last modified time of a file, if the file doesnt exist it Returns the current time.
def get_timestamp(file):

    if Path(file).exists():
        unix_time = Path(f"files/{file}").stat().st_mtime
        timestamp = datetime.fromtimestamp(unix_time).strftime("%Y-%m-%d %H:%M:%S")

    else:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    return timestamp


# Updates a confirmed change to baseline.json
def write_change(file, action):

    if action == "Added" or action == "Modified":

        directory = Path("files").resolve()
        filepath = directory / file

        file_hash = calc_hash(filepath)

    with open("baseline.json") as baseline_json:
        json_dictionary = json.load(baseline_json)

    
    if action == "Added":
        json_dictionary.update({file: file_hash})
    elif action == "Modified":
        json_dictionary[file] = file_hash
    elif action == "Deleted":
        del json_dictionary[file]

    create_baseline(json_dictionary)


# Checks changes every set time until stopped by the user.
def monitor():

	while True:
		try:

            
			print("|----------------------------------------------------")
			print("| Select how often a check will run in seconds")
			set_time = int(input("|: "))
			print("|----------------------------------------------------")

			break

		except ValueError:
			print("| Please Enter an intager")
			print("|---------------------------------------------------")

		except KeyboardInterrupt:
			print("\n")
			print("Exiting...")
			return

	while True:

		try:

			changes = check_changes()

			if changes:
            
				for action in changes:

					if action == changes[0]:
	            	    			action_show = "[+] Added:"
					elif action == changes[1]:
						action_show = "[-] Deleted:"
					elif action == changes[2]:
						action_show = "[!] Modified:"
            
					if "Added" in action_show:
						action_name = "Added"
					elif "Modified" in action_show:
						action_name = "Modified"
					elif "Deleted" in action_show:
						action_name = "Deleted"
	
					for file_changed in action:
						timestamp = get_timestamp(file_changed)
	                       	
						if action_name != "Deleted":
								file_hash = calc_hash(f"files/{file_changed}")
						else:
							file_hash = get_prev_hash(file_changed)
	
						if not already_prompted(file_changed, action_name, file_hash):
							confirmed = confirm_changes(action_show, action_name, file_changed, timestamp)
							log_change(action_name, file_changed, confirmed, timestamp)

						else:
							confirmed = False
	
						if confirmed:
							write_change(file_changed, action_name)

				sleep(set_time)
				
		except KeyboardInterrupt:
			print("\n")
			print("Stopping...")
			return 
		except FileNotFoundError as e:
			print(e)
			print("Please run --init first to initialize baseline.json")
			return



def already_prompted(file_name, action, file_hash):

    if Path("log.json").exists() and Path("log.json").stat().st_size != 0:
        with open("log.json", "r") as log_file:
            logs = json.load(log_file)
    
        for log in logs:
            if log["File: "] == file_name and log["Action: "] == action and log["Hash: "] == file_hash and not log["Authorized: "]:
                return True
       	
       	return False

    else:
        initialize_logs()
        return False
        

# Checks for any changes in the monitered directory.
def check_changes():
    changes = [[], [], []]

    added = changes[0]
    deleted = changes[1]
    modified = changes[2]

    with open("baseline.json", "r", encoding="utf-8") as json_file:
        baseline_dictionary = json.load(json_file)
    
    curr_dictionary = create_dictionary()

    for file in baseline_dictionary:
        if file not in curr_dictionary:
            deleted.append(file)
        elif file in curr_dictionary and file in baseline_dictionary and baseline_dictionary[file] != curr_dictionary[file]:
            modified.append(file)

    for file in curr_dictionary:
        if file not in baseline_dictionary:
            added.append(file)

    if added or deleted or modified:
        return changes

    return False
    

# Prints to the screen any changes that have been made since last check.
def report_changes(changes):
    
    print("| Changes since last scan:")


    for action in changes:
        for changed_file in action:

            if action == changes[0] and changed_file:
                print(f"| [+] Added: {changed_file}")
            elif action == changes[1] and changed_file:
                print(f"| [-] Deleted: {changed_file}")
            elif action == changes[2]:
                print(f"| [!] Modified: {changed_file}")

    print("|----------------------------------------------------")

    return True


# Logs time,action,filename and wether the change authorized in log.json (does this for every chage detected).
def log_change(action_performed, file_changed, confirmed, timestamp):

    if "Deleted" in action_performed:
        file_hash = get_prev_hash(file_changed)
    else:
        file_hash = calc_hash(f"files/{file_changed}")

    log_object = {"Time: ": timestamp,
                  "Action: ": action_performed,
                  "File: ": file_changed,
                  "Authorized: ": confirmed,
                  "Hash: ": file_hash
                  }

    if Path("log.json").exists() and Path("log.json").stat().st_size != 0:

        with open("log.json", "r") as log_file:
            logs = json.load(log_file)

    else:
        logs = []


    logs.append(log_object)

    with open("log.json", "w") as log_file:
        log_file.write(json.dumps(logs, indent=4))



# Asks if any changes that are detected was done by the user.
def confirm_changes(action_show, action_name, change, timestamp):

    while True:
        print("| Did you make this change? (yes/no)")

        if action_name == "Added":
            print(f"| Time Added: {timestamp}")
        elif action_name == "Modified":
            print(f"| Time Modified: {timestamp}")
        elif action_name == "Deleted":
            print(f"| Time detected: {timestamp}")

        print(f"| {action_show} {change}")
        user_confirmation = input("| : ")
        print("|----------------------------------------------------")

        if user_confirmation.lower() == "yes":
            return True

        elif user_confirmation.lower() == "no":
            return False

        else:
            print("Please enter (yes/no)")


def main():

    if args.init:
        dictionary = create_dictionary()
        create_baseline(dictionary)
        return

    elif args.check:
        try:

            changes = check_changes()

            if changes:
                report_changes(changes)


        except KeyboardInterrupt:
            print("\n")
            print("Stopping...")
            return 
        except FileNotFoundError as e:
            print(e)
            print("Please run --init first to initialize baseline.json")
            return

        return

    elif args.monitor:
        monitor()
        return


parser = argparse.ArgumentParser()
group = parser.add_mutually_exclusive_group()

group.add_argument("--init", action="store_true", help="Initializes the baseline and stores it in baseline.json.")
group.add_argument("--check", action="store_true", help="Checks for any changes in the monitored directory.")
group.add_argument("--monitor", action="store_true", help="Continuously monitors the monitored directory for changes every set time. (You set the time after running)")

args = parser.parse_args()


if __name__ == "__main__":
    main()


