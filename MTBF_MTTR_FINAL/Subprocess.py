import subprocess

# Define the commands for each program
command1 = ["python", "MTBF_MTTR(1).py"]
process1 = subprocess.Popen(command1)
process1.wait()

command2 = ["python", "MTBF_MTTR(2).py"]
process2 = subprocess.Popen(command2)
process2.wait()

command3 = ["python", "MTBF_MTTR(3).py"]
process3 = subprocess.Popen(command3)
process3.wait()

print("All programs have finished.")
