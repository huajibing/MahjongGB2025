
import sys
import time

agent_name = 'D'
stderr_writer = sys.stderr

def eprint(*args, **kwargs):
    print(f"Dummy_{agent_name}:", *args, file=stderr_writer, **kwargs)

eprint("starting")

# Type 0: INIT
line0 = sys.stdin.readline().strip()
# eprint(f"Received for Type 0: {line0}")
print('PASS')
sys.stdout.flush()

# Type 1: HAND
line1 = sys.stdin.readline().strip()
# eprint(f"Received for Type 1: {line1}")
print('PASS')
sys.stdout.flush()

interactions = 0
max_interactions = 20

while interactions < max_interactions:
    request = sys.stdin.readline().strip()
    if not request:
        eprint("EOF received, stopping.")
        break

    eprint(f"R: {request}")
    parts = request.split()
    action = "PASS"

    if parts and parts[0] == '2' and len(parts) > 1:
        action = f'PLAY {parts[1]}'

    print(action)
    sys.stdout.flush()
    eprint(f"S: {action}")
    interactions += 1
    time.sleep(0.005)

eprint("stopping after max_interactions or EOF")
sys.exit(0)
