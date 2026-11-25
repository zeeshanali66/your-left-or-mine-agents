"""Temperature watchdog for the overnight run.

Every 30 s: logs GPU temperature, utilisation and CPU load to results/temps.log.
If the GPU reaches 84 C on two readings in a row, it stops the judging run (the pipeline is
resumable, so nothing is lost) and writes an ALERT line. CPU temperature needs admin rights on
Windows, so CPU *load* is logged instead.
Usage: python -I watchdog.py <pid-of-pipeline>
"""
import os, subprocess, sys, time

LIMIT = 84
HERE = os.path.dirname(os.path.abspath(__file__))
LOG = os.path.join(HERE, "results", "temps.log")
os.makedirs(os.path.dirname(LOG), exist_ok=True)
pid = int(sys.argv[1])


def alive(p):
    out = subprocess.run(["tasklist", "/FI", f"PID eq {p}"], capture_output=True, text=True).stdout
    return str(p) in out


hot = 0
while alive(pid):
    g = subprocess.run(["nvidia-smi", "--query-gpu=temperature.gpu,utilization.gpu,memory.used",
                        "--format=csv,noheader,nounits"], capture_output=True, text=True).stdout.strip()
    c = subprocess.run(["powershell", "-NoProfile", "-Command",
                        "(Get-CimInstance Win32_Processor | Measure-Object LoadPercentage -Average).Average"],
                       capture_output=True, text=True).stdout.strip()
    temp = int(g.split(",")[0]) if g else 0
    line = f"{time.strftime('%H:%M:%S')}  GPU {temp}C  util/mem {g}  CPU load {c}%"
    hot = hot + 1 if temp >= LIMIT else 0
    if hot >= 2:
        subprocess.run(["taskkill", "/PID", str(pid), "/T", "/F"], capture_output=True)
        line += f"  ALERT: GPU >= {LIMIT}C twice, run stopped"
    with open(LOG, "a") as f:
        f.write(line + "\n")
    if hot >= 2:
        break
    time.sleep(30)
