
import sys
import time

# This is a very basic agent for testing communication.
player_id = -1 # Default
quan = -1 # Default

def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)

eprint("Dummy agent started")

# Initial handshake for player ID and quan (Type 0)
# Expects "ID QUAN" e.g. "0 0" (player_id, prevalent_wind_for_quan_calc)
try:
    initial_info = sys.stdin.readline().strip()
    eprint(f"Dummy agent received initial info line: '{initial_info}'")
    if initial_info:
        parts = initial_info.split()
        if len(parts) == 2: # Format: "ID QUAN"
            player_id = parts[0]
            quan = parts[1]
            # According to bot_io.md, for type 0 (INIT), agent should output "PASS"
            print("PASS")
            sys.stdout.flush()
            eprint(f"Dummy agent (ID: {player_id}) responded PASS to initial info (ID QUAN)")
        else:
            eprint(f"Dummy agent (ID: {player_id}) received malformed initial info: {initial_info}. Expected 2 parts.")
            # Still need to send a response if game expects one.
            # print("FAIL") # Or some error indicator if protocol allows
            # sys.stdout.flush()
            # For now, let's assume it might try to continue or game handles failure.
    else:
        eprint("Dummy agent received empty initial info line.")

except Exception as e:
    eprint(f"Dummy agent (ID: {player_id}) error during initial info: {e}")


# Second handshake for initial hand (Type 1)
# Expects "TILE1 TILE2 ..." (13 tiles)
try:
    initial_hand_info = sys.stdin.readline().strip()
    eprint(f"Dummy agent received initial hand line: '{initial_hand_info}'")
    if initial_hand_info: # Assuming it's the hand tiles
        # According to bot_io.md, for type 1 (HAND), agent should output "PASS"
        print("PASS")
        sys.stdout.flush()
        eprint(f"Dummy agent (ID: {player_id}) responded PASS to initial hand")
    else:
        eprint("Dummy agent received empty initial hand line.")
except Exception as e:
    eprint(f"Dummy agent (ID: {player_id}) error during initial hand: {e}")


while True:
    try:
        request = sys.stdin.readline().strip()
        eprint(f"Dummy agent (ID: {player_id}) received request: '{request}'")
        if not request: # EOF or empty line
            eprint(f"Dummy agent (ID: {player_id}) received empty request, exiting.")
            break

        parts = request.split()
        request_type = int(parts[0]) # First part is always the type

        response = "PASS" # Default response for most types for this dummy agent

        if request_type == 2: # Draw (e.g., "2 T6")
            if len(parts) > 1:
                drawn_tile = parts[1]
                response = f"PLAY {drawn_tile}" # Always discard the drawn tile
            else:
                eprint(f"Dummy agent (ID: {player_id}) received malformed DRAW request: {request}")
                response = "PLAY W1" # Fallback, should not happen with correct env

        # For other types (3-9) like PLAY, PENG, CHI, GANG, BUGANG, HU, an opponent action,
        # this dummy agent will just PASS.

        print(response)
        sys.stdout.flush()
        eprint(f"Dummy agent (ID: {player_id}) responded: {response}")

    except Exception as e:
        eprint(f"Dummy agent (ID: {player_id}) error in main loop: {e}, exiting.")
        break
eprint(f"Dummy agent (ID: {player_id}) exiting gracefully.")
sys.exit(0)
