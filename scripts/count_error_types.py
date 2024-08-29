def count_occurrences(logfile_path, search_string="same as id:000003"):
    count = 0
    try:
        with open(logfile_path, 'r') as logfile:
            for line in logfile:
                if search_string in line:
                    count += 1
    except FileNotFoundError:
        print(f"File not found: {logfile_path}")
    except Exception as e:
        print(f"An error occurred: {e}")
    return count


if __name__ == "__main__":
    logfile_path = "dump/crashes_documentation.txt"
    occurrences = count_occurrences(logfile_path)
    print(f"The string 'same as id:000003' occurred {occurrences} times in the logfile.")
