import subprocess

# Define the commands for each program
command1 = ["python", "MTBF_MTTR_1.py"]
process1 = subprocess.Popen(command1)

command2 = ["streamlit", "run", "Dashboard_2.py"]
process2 = subprocess.Popen(command2)

# Wait for both processes to finish
process1.wait()
process2.wait()

print("All programs have finished.")