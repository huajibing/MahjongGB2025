import time
import subprocess
from evaluator.env import MahjongGBEnv
from evaluator.agent import Agent

class GameController:
    def __init__(self, agent_main_paths, game_id="game"):
        if len(agent_main_paths) != 4:
            raise ValueError("Exactly four agent main paths are required.")

        self.game_id = game_id
        self.env = MahjongGBEnv()
        self.agents = []
        self._agent_procs_started = False
        self.game_log = []

        for i in range(4):
            try:
                # Ensure agent_main_paths[i] is a valid path string
                if not isinstance(agent_main_paths[i], str) or not agent_main_paths[i]:
                    raise ValueError(f"Agent main path for agent {i} is invalid: '{agent_main_paths[i]}'")
                agent = Agent(agent_main_path=agent_main_paths[i], agent_id=int(i))
                self.agents.append(agent)
            except Exception as e:
                self._log_error(f"Error initializing agent {i} from {agent_main_paths[i]}: {e}")
                self._cleanup_agents_on_error(is_init_error=True)
                raise
        self._pending_discard_after_meld = {}


    def _log_error(self, message):
        print(message)
        self.game_log.append(f"ERROR: {message}")

    def _cleanup_agents_on_error(self, is_init_error=False):
        log_msg = "Cleaning up agents due to an error"
        if is_init_error:
            log_msg += " during initialization."
        else:
            log_msg += " during gameplay."
        self.game_log.append(log_msg)

        if not hasattr(self, 'agents') or not self.agents:
            self.game_log.append("No agents to clean up.")
            return

        if self._agent_procs_started:
            for agent in self.agents:
                if agent: agent.stop()
        elif is_init_error:
             for agent_obj in self.agents:
                 if agent_obj and agent_obj.process:
                     agent_obj.stop()
        self._agent_procs_started = False


    def _start_agents(self):
        if self._agent_procs_started:
            return
        self.game_log.append(f"Starting all agent subprocesses for game {self.game_id}...")
        for i, agent in enumerate(self.agents):
            try:
                agent.start()
            except Exception as e:
                self._log_error(f"Failed to start agent {i} ({agent.agent_main_path}): {e}")
                # Stop already started agents on failure
                for j in range(i): # Only stop those that were successfully started
                    if self.agents[j] and self.agents[j].process and self.agents[j].process.poll() is None:
                         self.agents[j].stop()
                self._agent_procs_started = False
                raise RuntimeError(f"Could not start all agents for game {self.game_id}.") from e
        self._agent_procs_started = True
        self.game_log.append("All agents started successfully.")


    def _stop_agents(self):
        if not self._agent_procs_started and not any(a.process for a in self.agents if a and a.process):
            self.game_log.append(f"Stop agents called but no agents seem to be running for game {self.game_id}.")
            return

        self.game_log.append(f"Stopping all agent subprocesses for game {self.game_id}...")
        for agent in self.agents:
            if agent: agent.stop()
        self._agent_procs_started = False
        self.game_log.append("All agents stopped.")


    def _send_to_agent(self, player_id, message, log_prefix="SENT"):
        agent = self.agents[player_id]
        full_log_message = f"{log_prefix} to Agent {player_id}: {message}"
        self.game_log.append(full_log_message)

        if agent and agent.process and agent.process.poll() is None:
            try:
                agent.send_request(message)
            except Exception as e:
                self._log_error(f"Exception sending to agent {player_id}: {e}")
                raise Exception(f"Agent {player_id} unavailable for message: {message} (send failed)") from e
        else:
            self._log_error(f"Agent {player_id} not available or process not running to send '{message}'.")
            raise Exception(f"Agent {player_id} unavailable for message: {message} (not running)")


    def _get_player_response(self, player_id, timeout_seconds=10, context=""):
        agent = self.agents[player_id]
        response = None
        log_context_suffix = f" in context '{context}'" if context else ""

        if not (agent and agent.process and agent.process.poll() is None):
            self._log_error(f"Agent {player_id} not available to get response{log_context_suffix}.")
            raise Exception(f"Agent {player_id} unavailable to get response{log_context_suffix}.")

        try:
            response = agent.get_response(timeout_seconds=timeout_seconds)
        except Exception as e:
            self._log_error(f"Exception getting response from agent {player_id}{log_context_suffix}: {e}")
            raise Exception(f"Agent {player_id} failed during get_response{log_context_suffix}.") from e

        if response:
            self.game_log.append(f"RESPONSE from Agent {player_id}: {response}{log_context_suffix}")
        else:
            self._log_error(f"NO RESPONSE (timeout or empty) from Agent {player_id}{log_context_suffix}.")
            # Check for stderr from agent during this period
            error_messages = []
            while not agent.error_queue.empty():
                try: error_messages.append(agent.error_queue.get_nowait())
                except Exception: break # Should be queue.Empty but being safe
            if error_messages:
                self._log_error(f"Agent {player_id} had STDERR messages during failed response: {' | '.join(error_messages)}")
            raise Exception(f"Agent {player_id} failed to provide a valid response{log_context_suffix}.")
        return response

    def _parse_agent_response(self, response_str, player_id_acting):
        """
        Parses agent response. For melds like PENG/CHI that require a subsequent discard,
        it extracts the discard and stores it.
        Example: "PENG W1 W2" (Peng W1, discard W2) -> action="PENG W1", pending_discard="W2"
                 "CHI W1 W2 W3 W4" (Chi W1W2W3, discard W4) -> action="CHI W1 W2 W3", pending_discard="W4"
        Returns: (action_for_env, None) or (action_for_env, pending_discard_tile)
        """
        if not response_str: return "PASS", None
        parts = response_str.split()
        if not parts: return "PASS", None

        action_verb = parts[0].upper() # Normalize to uppercase

        if action_verb == "PENG":
            if len(parts) == 2: # Agent response: "PENG TILE_TO_DISCARD"
                self._pending_discard_after_meld[player_id_acting] = parts[1] # Store TILE_TO_DISCARD
                # The actual tile being PENGed is self.env.curTile (the tile played by the previous player).
                # The game controller will use this when calling env.step().
                # So, the action for env here is just "PENG".
                # The env._pung() method expects the tile that was offered (self.env.curTile).
                # The game_controller's main loop (play_game) needs to handle passing the correct tile to env.step.
                # For _parse_agent_response, we return "PENG" as the primary action.
                # The env.step in env.py for state 2, when it sees a "PENG" action from a player,
                # should use self.curTile (which is the tile just played by the previous player) as the tile being PENGed.
                return action_verb, None # Action for env is "PENG"
            else: # Malformed PENG (not 2 parts)
                self._log_error(f"Agent {player_id_acting} malformed PENG: '{response_str}'. Expected 2 parts (PENG TILE_TO_DISCARD). Assuming PASS.")
                return "PASS", None

        elif action_verb == "CHI":
            # Expected format: "CHI <Card1_middle_tile> <Card2_tile_to_discard>" (3 parts total)
            if len(parts) == 3:
                middle_tile = parts[1]
                tile_to_discard = parts[2]
                self._pending_discard_after_meld[player_id_acting] = tile_to_discard
                # Environment's _chow method expects the middle tile of the sequence
                return f"CHI {middle_tile}", None
            else: # Malformed for CHI
                self._log_error(f"Agent {player_id_acting} malformed CHI response: '{response_str}'. Expected 3 parts (CHI middle_tile discard_tile). Assuming PASS.")
                return "PASS", None

        # For PLAY, HU, GANG, BUGANG, PASS - the response is the action itself
        # e.g., "PLAY W1", "HU", "GANG T3", "BUGANG F1", "PASS"
        return response_str, None


    def play_game(self, prevalent_wind_initial=-1, tile_wall_str_initial=''):
        game_results = {"scores": [0]*4, "winner": None, "log": self.game_log, "error": None, "reason": "Game did not start properly"}
        self._pending_discard_after_meld.clear()

        try:
            self._start_agents()
            game_results["reason"] = "Agents started, game initializing."

            # Send initial newline to satisfy agent's first input()
            self.game_log.append("Sending initial newline to all agents...")
            for i, agent_proc in enumerate(self.agents):
                try:
                    # agent.send_request already adds a newline. Sending an empty string
                    # will effectively just send the newline.
                    agent_proc.send_request("")
                    self.game_log.append(f"Sent initial newline to Agent {i}")
                except Exception as e:
                    self._log_error(f"Failed to send initial newline to agent {i}: {e}")
                    # This could be a critical error, might need to stop the game
                    raise RuntimeError(f"Could not send initial newline to agent {i} for game {self.game_id}.") from e
            self.game_log.append("Initial newlines sent to all agents.")

            # Env reset returns initial obs, reward, done
            # For now, obs from env.reset() is not directly used to message agents, specific messages are crafted
            self.env.reset(prevalentWind=prevalent_wind_initial, tileWall=tile_wall_str_initial)
            self.game_log.append(f"Env reset. Wind: {self.env.prevalentWind}. Initial Player: {self.env.curPlayer}. Initial State: {self.env.state}")

            # Initial Handshake (Type 0 and Type 1)
            for i in range(4):
                # Type 0: INIT "ID QUAN"
                initial_setup_msg = f"0 {i} {self.env.prevalentWind}" # Game sends player_id and prevalent_wind
                self._send_to_agent(i, initial_setup_msg, log_prefix="SEND_INIT")
                response0 = self._get_player_response(i, timeout_seconds=5, context="initial_setup_type_0")
                if response0.upper() != "PASS": raise Exception(f"Agent {i} bad response to Type 0 (INIT): '{response0}', expected PASS.")

                # Type 1: HAND "TILE1 TILE2 ..." (13 tiles)
                hand_str = " ".join(self.env.hands[i])
                initial_hand_msg = f"1 {hand_str}" # Game sends only the hand
                self._send_to_agent(i, initial_hand_msg, log_prefix="SEND_HAND")
                response1 = self._get_player_response(i, timeout_seconds=5, context="initial_hand_type_1")
                if response1.upper() != "PASS": raise Exception(f"Agent {i} bad response to Type 1 (HAND): '{response1}', expected PASS.")

            self.game_log.append("Initial handshakes (Type 0 & 1) completed for all agents.")
            game_results["reason"] = "Handshake OK, starting main game loop."

            turn_count = 0
            max_turns = 250 # Prevent infinite loops

            while not self.env.done and turn_count < max_turns:
                turn_count += 1
                cur_P, cur_S = self.env.curPlayer, self.env.state
                self.game_log.append(f"--- Turn {turn_count}: Player {cur_P}, State {cur_S} ---")

                actions_for_env_step = {}

                if cur_S == 1: # Player current_player Drew a tile, needs to act (Play, Hu, Gang, BuGang)
                    # Message Type 2: DRAW "2 TILENAME"
                    msg_to_agent = f"2 {self.env.curTile}"
                    self._send_to_agent(cur_P, msg_to_agent, log_prefix=f"SEND_DRAW_P{cur_P}")
                    agent_response_str = self._get_player_response(cur_P, timeout_seconds=10, context="draw_action")
                    # For state 1, agent response is directly used for env.step
                    actions_for_env_step[cur_P] = agent_response_str

                elif cur_S == 0: # Player current_player Melded (Chi/Peng), now needs to Play a tile
                    if cur_P in self._pending_discard_after_meld:
                        tile_to_discard = self._pending_discard_after_meld.pop(cur_P)
                        # Action for env.step is "PLAY <tile>"
                        actions_for_env_step[cur_P] = f"PLAY {tile_to_discard}"
                        self.game_log.append(f"Player {cur_P} auto-discarding '{tile_to_discard}' after meld.")
                    else:
                        raise Exception(f"State 0 (pending discard) for P{cur_P}, but no pending discard tile found.")

                elif cur_S == 2: # Player prev_player Played a tile, current_player and others can react (Chi, Peng, Gang, Hu, Pass)
                                 # Note: env.curPlayer is already updated to the player who played the tile.
                                 # The one who played (self.env.curPlayer) does not act now. Others do.
                    played_tile = self.env.curTile
                    player_who_played = self.env.curPlayer # This is the one whose tile is being reacted to.

                    # Message Type 3: OTHER_PLAY "3 PLAYER_ID TILE" (who played, what tile)
                    # This message goes to all other players.
                    msg_to_agents = f"3 {player_who_played} {played_tile}"
                    for i in range(4):
                        if i == player_who_played: continue # The player who just played doesn't act on their own play

                        self._send_to_agent(i, msg_to_agents, log_prefix=f"SEND_OTHER_PLAY_TO_P{i}")
                        agent_response_str = self._get_player_response(i, timeout_seconds=10, context=f"react_to_play_by_P{player_who_played}")
                        action_for_env, pending_discard = self._parse_agent_response(agent_response_str, i)
                        actions_for_env_step[i] = action_for_env
                        if pending_discard:
                             # This state (S2) should not result in a pending discard.
                             # _parse_agent_response should only set pending_discard for PENG/CHI from S2.
                             # And env.step will transition to S0 for that player if they PENG/CHI.
                             # So, this is more of a safeguard or future-proofing if S2 logic changes.
                            self._log_error(f"Warning: Pending discard '{pending_discard}' set for P{i} from S2 response '{agent_response_str}'. This is unusual.")
                            self._pending_discard_after_meld[i] = pending_discard


                elif cur_S == 3: # Player prev_player BuGanged a tile, others can react (Qianggang Hu or Pass)
                                 # env.curPlayer is the one who BuGanged.
                    bugang_tile = self.env.curTile
                    player_who_buganged = self.env.curPlayer

                    # Message Type 3: OTHER_ACTION "3 PLAYER_ID ACTION_TYPE TILE" (who acted, what action, what tile)
                    # For BUGANG, this notifies other players who might Qianggang.
                    msg_to_agents = f"3 {player_who_buganged} BUGANG {bugang_tile}"
                    for i in range(4):
                        if i == player_who_buganged: continue

                        self._send_to_agent(i, msg_to_agents, log_prefix=f"SEND_BUGANG_ACTION_TO_P{i}") # Log prefix updated for clarity
                        agent_response_str = self._get_player_response(i, timeout_seconds=10, context=f"react_to_bugang_by_P{player_who_buganged}")
                        # For Qianggang Hu, response should be "HU" or "PASS"
                        actions_for_env_step[i] = agent_response_str

                else:
                    raise Exception(f"Unhandled environment state: Player {cur_P}, State {cur_S}")

                if not actions_for_env_step and not self.env.done : # If no player could/wanted to act
                    # This can happen if all players PASS in S2 or S3. The env should handle this.
                    # If env doesn't advance, it's an issue.
                    self.game_log.append(f"No agent actions for env.step. Current P{cur_P}, S{cur_S}. Env should handle PASS internally.")
                    # Forcing a pass for current player if it's their turn to act and no action was taken (e.g. S1)
                    # This shouldn't be needed if agent always responds.
                    if cur_S == 1 and cur_P not in actions_for_env_step:
                         self._log_error(f"Critical: P{cur_P} in S1 did not provide an action. Forcing PASS.")
                         actions_for_env_step[cur_P] = "PASS"


                self.game_log.append(f"Actions for env.step: {actions_for_env_step}")
                # Env step is currently simplified in evaluator/env.py, needs to match this logic.
                # It expects a dict like {player_idx: "ACTION_STR"}
                _, self.env.reward, self.env.done = self.env.step(actions_for_env_step) # Obs is not used here.
                self.game_log.append(f"Env step outcome. Reward:{self.env.reward}, Done:{self.env.done}, Next Player:{self.env.curPlayer}, Next State:{self.env.state}")

                if self.env.done:
                    game_results["reason"] = f"Game ended by Mahjong or Draw after {turn_count} turns."
                    # Send HU message (Type 7 or 8) to agents if game ended by HU
                    # This is for post-game notification, not for an action response.
                    # For now, just log it.
                    self.game_log.append(f"Game ended. Final scores: {self.env.reward}")
                    break

            if turn_count >= max_turns and not self.env.done:
                game_results["reason"] = f"Max turns ({max_turns}) reached. Game ended as a draw."
                self.env.done = True
                self.env.reward = [0,0,0,0] # Ensure rewards are neutral for timeout draw

            game_results["scores"] = self.env.reward if self.env.reward and isinstance(self.env.reward, list) and len(self.env.reward)==4 else [0]*4
            if self.env.reward and any(s > 0 for s in self.env.reward): # Simplistic winner check (any positive score)
                max_sc = -float('inf')
                winners = [] # Can be multiple winners in some Mahjong variants, though not typical for final score
                current_max_score = 0
                for i, s_val in enumerate(game_results["scores"]):
                    if s_val > current_max_score:
                        current_max_score = s_val
                        winners = [i]
                    elif s_val == current_max_score and current_max_score > 0 : # check current_max_score > 0 to avoid all players with 0 score as winners
                        winners.append(i)

                if len(winners) == 1: game_results["winner"] = winners[0]
                elif len(winners) > 1: game_results["winner"] = winners # Multiple winners if scores are tied


        except ImportError as e: # Specifically for MahjongGB if not found
            self._log_error(f"Critical Import Error: {e}. This often means MahjongGB library is not installed or not found.")
            game_results["error"] = f"MahjongGB library missing: {e}"
            game_results["reason"] = "Setup error (MahjongGB library not found)."
            # No need to raise here, as we want to return the results object.
        except Exception as e:
            import traceback
            err_msg = f"Game Play Exception: {type(e).__name__}: {e}"
            tb_str = traceback.format_exc()
            self._log_error(f"{err_msg}\nTraceback:\n{tb_str}")
            game_results["error"] = err_msg
            game_results["reason"] = "Runtime error during game execution."
            if not isinstance(game_results.get("scores"), list) or len(game_results.get("scores", [])) != 4:
                 game_results["scores"] = [0]*4 # Ensure scores is always a list of 4
        finally:
            self._stop_agents() # Ensure agents are stopped regardless of how play_game exits
            self.game_log.append(f"Game {self.game_id} finished. Reason: {game_results.get('reason', 'Unknown reason')}")
            if not game_results.get("scores"): game_results["scores"] = [0]*4

        return game_results

def test_parse_agent_response(controller):
    print("\n--- Running test_parse_agent_response ---")
    # Test 1: Correct PENG
    controller._pending_discard_after_meld.clear()
    action, discard = controller._parse_agent_response("PENG W1", 0)
    assert action == "PENG", f"Test 1 PENG Failed: action was {action}"
    assert discard is None, f"Test 1 PENG Failed: discard was {discard}"
    assert controller._pending_discard_after_meld.get(0) == "W1", f"Test 1 PENG Failed: pending was {controller._pending_discard_after_meld.get(0)}"
    print("Test 1 (Correct PENG W1): Passed")

    # Test 2: Malformed PENG (too many parts)
    controller._pending_discard_after_meld.clear()
    action, discard = controller._parse_agent_response("PENG W1 W2", 1)
    assert action == "PASS", f"Test 2 Malformed PENG Failed: action was {action}"
    assert discard is None, f"Test 2 Malformed PENG Failed: discard was {discard}"
    assert 1 not in controller._pending_discard_after_meld, "Test 2 Malformed PENG Failed: pending should be empty for player 1"
    print("Test 2 (Malformed PENG W1 W2): Passed")

    # Test 3: Malformed PENG (too few parts)
    controller._pending_discard_after_meld.clear()
    action, discard = controller._parse_agent_response("PENG", 2)
    assert action == "PASS", f"Test 3 Malformed PENG Failed: action was {action}"
    assert discard is None, f"Test 3 Malformed PENG Failed: discard was {discard}"
    assert 2 not in controller._pending_discard_after_meld, "Test 3 Malformed PENG Failed: pending should be empty for player 2"
    print("Test 3 (Malformed PENG): Passed")

    # Test 4: Correct CHI (ensure no interference)
    controller._pending_discard_after_meld.clear()
    action, discard = controller._parse_agent_response("CHI T1 T2", 0)
    assert action == "CHI T1", f"Test 4 CHI Failed: action was {action}"
    assert discard is None, f"Test 4 CHI Failed: discard was {discard}"
    assert controller._pending_discard_after_meld.get(0) == "T2", f"Test 4 CHI Failed: pending was {controller._pending_discard_after_meld.get(0)}"
    print("Test 4 (Correct CHI T1 T2): Passed")

    print("--- test_parse_agent_response completed successfully ---")

if __name__ == '__main__':
    print("Simplified Test for GameController...")
    # This test assumes dummy_agent_main.py is in evaluator/ as created by agent.py
    dummy_agent_path = 'evaluator/dummy_agent_main.py'

    import os
    if not os.path.exists(dummy_agent_path):
        print(f"CRITICAL: Dummy agent script '{dummy_agent_path}' not found. It should have been created by agent.py's test.")
        # Create a very basic fallback if it's missing, just to allow GC to init
        # This fallback might not behave correctly with the game protocol.
        os.makedirs("evaluator", exist_ok=True)
        with open(dummy_agent_path, 'w') as f:
            f.write("import sys\nprint('Fallback dummy agent started', file=sys.stderr)\n"
                    "sys.stdin.readline(); print('PASS'); sys.stdout.flush()\n" # Type 0
                    "sys.stdin.readline(); print('PASS'); sys.stdout.flush()\n" # Type 1
                    "while True:\n"
                    "  line = sys.stdin.readline().strip()\n"
                    "  if not line: break\n"
                    "  parts = line.split()\n"
                    "  action = 'PASS'\n"
                    "  if parts and parts[0] == '2' and len(parts) > 1: action = f'PLAY {parts[1]}'\n" # Type 2 Draw
                    "  print(action); sys.stdout.flush()\n"
                    "print('Fallback dummy agent stopping', file=sys.stderr)\nsys.exit(0)\n")
        print(f"Created a fallback dummy agent at: {dummy_agent_path}")


    agent_paths = [dummy_agent_path] * 4
    gc_instance = None
    test_run_results = {}

    try:
        gc_instance = GameController(agent_main_paths=agent_paths, game_id="gc_main_test")
        # Run the specific unit test for _parse_agent_response
        test_parse_agent_response(gc_instance)
        print(f"\nGameController initialized with agents: {agent_paths}. Proceeding to play_game...")

        # Proceed with the existing game simulation
        test_run_results = gc_instance.play_game()

        print("\n--- GameController Full Game Simulation Results ---")
        for key, value in test_run_results.items():
            if key != "log": # Don't print the full log to console here
                print(f"  {key}: {value}")

        log_file_path = "gc_test_run.log"
        print(f"  Full game log saved to: {log_file_path}")
        with open(log_file_path, "w") as logfile:
            if test_run_results.get("log"):
                for log_entry in test_run_results["log"]:
                    logfile.write(log_entry + "\n")

        if test_run_results.get("error"):
            print(f"GC TEST RUN ENCOUNTERED AN ERROR: {test_run_results['error']}")
        else:
            print("GC TEST RUN COMPLETED (no error reported by play_game). Review log for details.")

    except ImportError as e: # Catch MahjongGB missing specifically
        print(f"IMPORT ERROR during GameController test: {e}. MahjongGB library might be missing or not in PYTHONPATH.")
        if gc_instance and gc_instance.game_log: gc_instance.game_log.append(f"TEST IMPORT ERROR: {e}")
    except Exception as e:
        print(f"UNHANDLED EXCEPTION in GameController test __main__: {type(e).__name__} - {e}")
        import traceback
        traceback.print_exc()
        if gc_instance and gc_instance.game_log: gc_instance.game_log.append(f"TEST MAIN EXCEPTION: {e}\n{traceback.format_exc()}")
    finally:
        print("GameController __main__ test execution finished.")
        # Note: gc_instance.play_game() has its own finally block to stop agents.
        # If GameController fails to initialize, _cleanup_agents_on_error is called.
