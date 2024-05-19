from multiprocessing import Pool
import os


def execute_script(script_filename):
    try:
        with open(script_filename, 'r') as script_file:
            script_code = script_file.read()
            exec(script_code)
    except FileNotFoundError:
        print(f"Script '{script_filename}' not found.")
    except Exception as e:
        print(f"Error running {script_filename}: {e}")


def execute_script2(script_filename):
    return_code = os.system(f'python3 {script_filename}')

    print(f"Child script finished with return code: {return_code}")


with Pool() as pool:
    files = ["united_award_ticket_iah.py", "united_award_ticket_sfo.py"]
    #files = ["test1.py"]
    pool.map(execute_script2, files)

