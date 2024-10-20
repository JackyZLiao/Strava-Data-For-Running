import subprocess
import os

def make_empty_commit():


    # Get the absolute path of the script
    script_path = os.path.abspath(__file__)
    print(f"The path to this script is: {script_path}")

    os.chdir("/Users/jackyliao/Desktop/Uni/Personal Projects/Strava-Data-For-Running")

    try:
        # Run the Git command to create an empty commit
        subprocess.run(['git', 'commit', '--allow-empty', '-m', 'Regular empty commit'], check=True)
        subprocess.run(['git', 'push'], check=True)
        print("Empty commit made successfully.")
    except subprocess.CalledProcessError as e:
        print(f"Error making empty commit: {e}")

if __name__ == "__main__":
    make_empty_commit()
