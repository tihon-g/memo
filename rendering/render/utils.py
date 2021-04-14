import subprocess
def execute_wait(com):
    proc = subprocess.Popen(com, shell=False, stdout=subprocess.PIPE, universal_newlines=True)
    # windows Warning : Using shell = True can be a security hazard
    # Note Do not use stdout=PIPE or stderr=PIPE with this function as that can deadlock based on the child process output volume. Use Popen with the communicate() method when you need pipes.
    # subprocess.run(["ls", "-l", "/dev/null"], capture_output=True)
    for stdout_line in iter(proc.stdout.readline, ""):
        yield stdout_line
    proc.stdout.close()
    return_code = proc.wait()
    if return_code:
        print(f"proc failed - {subprocess.CalledProcessError(return_code, com)}")