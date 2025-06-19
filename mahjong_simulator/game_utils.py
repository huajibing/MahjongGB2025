import subprocess
import os
import random
from typing import List, Tuple, Optional, Dict, Any
from MahjongGB import MahjongFanCalculator

# Tile Constants
WAN = "W"; TONG = "B"; TIAO = "T"; FENG = "F"; JIAN = "J"
ALL_TILES: List[str] = []
for suit_val in [WAN, TONG, TIAO]:
    for i in range(1, 10): ALL_TILES.extend([f"{suit_val}{i}"] * 4)
for i in range(1, 5): ALL_TILES.extend([f"{FENG}{i}"] * 4) # Winds E S W N
for i in range(1, 4): ALL_TILES.extend([f"{JIAN}{i}"] * 4) # Dragons R G Wh

class Agent:
    def __init__(self, agent_id: int):
        self.agent_id = agent_id
        agent_command = ["python", "agent_trainer/__main__.py"]
        cwd = os.path.dirname(os.path.abspath(__file__))
        self.process = subprocess.Popen(
            agent_command, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, # Merge stderr to stdout
            universal_newlines=True, bufsize=1, cwd=cwd
        )
    def send_request(self, request_str: str):
        if self.process.stdin: self.process.stdin.write(request_str + "\n"); self.process.stdin.flush()
    def receive_response(self) -> str:
        if not self.process.stdout:
            return ""

        first_line = self.process.stdout.readline().strip()

        # Check if this looks like an error message or if it's an empty line (agent might have crashed)
        # Typical agent responses are "PASS", "PLAY ...", "HU", etc.
        # Tracebacks often start with "Traceback..."
        if not first_line or "Traceback" in first_line or "Error" in first_line or "Exception" in first_line:
            # Potentially an error or crash, try to read more for diagnostics
            error_output = [first_line]
            try:
                # Try to read a few more lines, but don't block indefinitely
                for _ in range(10): # Read up to 10 more lines for the error
                    # Check if stdout is still open and if there's data
                    # This is tricky without select.poll on the file descriptor.
                    # A simple readline might block if nothing more is available.
                    # However, if the process crashed, readline might return empty immediately.
                    if self.process.stdout.closed:
                        break
                    # A very short timeout mechanism is hard to implement here directly with readline.
                    # We rely on the agent process flushing its output upon crash or normal error reporting.
                    next_line = self.process.stdout.readline().strip()
                    if next_line:
                        error_output.append(next_line)
                    elif not first_line: # If first_line was also empty, likely no output / process died quietly
                        break
                    else: # Got some error lines, then an empty one, probably end of error.
                        break

                # For debugging, print the collected error output to the main simulator's console
                if any(line for line in error_output if line): # If any non-empty line was captured
                    print(f"--- Agent {self.agent_id} Diagnostic Output ---", flush=True)
                    for err_line in error_output:
                        print(f"A{self.agent_id} CAPTURED: {err_line}", flush=True)
                    print(f"--- End Agent {self.agent_id} Diagnostic ---", flush=True)

                # Return the first line, as that's what the game logic currently expects for response check
                return first_line

            except Exception as e:
                print(f"Error while trying to read extended output from agent {self.agent_id}: {e}", flush=True)
                return first_line # Return what we got

        return first_line # Normal response

    def close(self):
        if self.process:
            if self.process.stdin: self.process.stdin.close()
            if self.process.stdout: self.process.stdout.close()
            if self.process.stderr: self.process.stderr.close()
            self.process.terminate(); self.process.wait()

class Player:
    def __init__(self, player_id: int, agent_process: Agent, seat_wind: int):
        self.player_id: int = player_id
        self.agent: Agent = agent_process
        self.seat_wind: int = seat_wind # 0:E, 1:S, 2:W, 3:N
        self.hand: List[str] = []
        self.melds: List[Tuple[str, str, Any, Optional[int]]] = []
        self.discarded_tiles: List[str] = []
        self.score: int = 0

class GameState:
    def __init__(self, agents: List[Agent]):
        self.tile_wall: List[str] = list(ALL_TILES); random.shuffle(self.tile_wall)
        self.players: List[Player] = [Player(i, agents[i], i) for i in range(4)]
        self.dealer_player_index: int = 0
        self.current_player_index: int = self.dealer_player_index
        self.prevalent_wind: int = 0
        self.last_discarded_tile: Optional[str] = None
        self.last_discarding_player_index: Optional[int] = None
        self.game_over: bool = False
        self.winner_index: Optional[int] = None
        self.winning_tile: Optional[str] = None
        self.is_self_drawn_win: bool = False
        self.is_robbing_kong_win: bool = False
        self.turn_number: int = 0
        self.kong_declarer_index: Optional[int] = None
        self.kong_tile: Optional[str] = None
        self.just_declared_kong: bool = False
        self.just_discarded: bool = False
        self.about_to_BUGANG_tile: Optional[str] = None
        self.error_message: Optional[str] = None
        self.current_action_responses: Dict[int, str] = {}

        self.win_details: Optional[List[Tuple[int, int, str, str]]] = None
        self.final_scores: Dict[int, int] = {i: 0 for i in range(4)}
        self.drew_kong_replacement_this_action: bool = False
        self.pending_qiangganghu_check: bool = False # New attribute

        self.shuffle_and_deal()

    def shuffle_and_deal(self):
        random.shuffle(self.tile_wall)
        for player in self.players: player.hand = [self.tile_wall.pop() for _ in range(13)]

    def draw_tile(self, player_index: int) -> Optional[str]:
        self.just_discarded = False; self.just_declared_kong = False
        self.about_to_BUGANG_tile = None; self.drew_kong_replacement_this_action = False
        self.pending_qiangganghu_check = False # Reset this flag here
        return self.tile_wall.pop() if self.tile_wall else None

    def _get_relative_offer(self, meld_from_player_abs_idx: Optional[int], winner_abs_idx: int) -> int:
        if meld_from_player_abs_idx is None: return 0
        if meld_from_player_abs_idx == winner_abs_idx: return 0
        diff = (meld_from_player_abs_idx - winner_abs_idx + 4) % 4
        if diff == 1:
            return 3 # Lower player (Downstream) / Shimocha
        elif diff == 2:
            return 2 # Opposite player / Toimen
        elif diff == 3:
            return 1 # Upper player (Upstream) / Kamicha
        return 0 # Should not happen if inputs are correct

    def end_game(self, winner_index: Optional[int] = None, winning_tile: Optional[str] = None,
                 is_self_drawn: bool = False, is_robbing_kong: bool = False,
                 is_draw: bool = False, error_message: Optional[str] = None,
                 was_kong_replacement_draw: bool = False,
                 last_discarding_player_idx_for_payment: Optional[int] = None): # New param for QGH
        self.game_over = True; self.winner_index = winner_index; self.winning_tile = winning_tile
        self.is_self_drawn_win = is_self_drawn; self.is_robbing_kong_win = is_robbing_kong
        self.error_message = error_message

        if is_draw or error_message:
            msg = f"ERROR: {error_message}" if error_message else "DRAW."
            print(f"GAME ENDED ({msg})", flush=True)
            self.final_scores = {p.player_id: p.score for p in self.players}
            return

        if winner_index is not None and winning_tile is not None:
            winner = self.players[winner_index]
            calculator_packs = []
            for meld_tuple in winner.melds:
                meld_type = meld_tuple[0].upper(); tile1 = meld_tuple[1]; data = meld_tuple[2]
                offer_relative = 0; actual_calc_meld_type = meld_type
                if meld_type == "CHI":
                    offer_relative = self._get_relative_offer(meld_tuple[3], winner_index)
                elif meld_type in ["PENG", "GANG", "ANGANG", "BUGANG"]:
                    meld_from_abs_idx = data
                    offer_relative = self._get_relative_offer(meld_from_abs_idx, winner_index)
                    if meld_type == "BUGANG": actual_calc_meld_type = "GANG"
                    if meld_type == "ANGANG": actual_calc_meld_type = "KONG"
                calculator_packs.append((actual_calc_meld_type, tile1, offer_relative))

            is_4th_tile = False
            is_about_kong_for_calc = is_robbing_kong or (is_self_drawn and was_kong_replacement_draw)

            try:
                fans_calculator = MahjongFanCalculator(
                    pack=tuple(calculator_packs), hand=tuple(sorted(winner.hand)), winTile=winning_tile,
                    flowerCount=0, isSelfDrawn=is_self_drawn, is4thTile=is_4th_tile,
                    isAboutKong=is_about_kong_for_calc, isWallLast=(len(self.tile_wall) == 0),
                    seatWind=winner.seat_wind, prevalentWind=self.prevalent_wind, verbose=False
                )
                fan_cnt_total = 0; self.win_details = []
                for fp, cnt, f_zh, f_en in fans_calculator:
                    self.win_details.append((fp, cnt, f_zh, f_en)); fan_cnt_total += fp * cnt

                if fan_cnt_total < 8:
                    print(f"Player {winner_index} HU claim has insufficient fans ({fan_cnt_total} < 8). Treating as Chombo.", flush=True)
                    self.error_message = f"P{winner_index} Chombo - insufficient fans ({fan_cnt_total})."
                    chombo_penalty_winner = -8 * 3
                    self.players[winner_index].score += chombo_penalty_winner
                    for p_idx in range(4):
                        if p_idx != winner_index: self.players[p_idx].score += 8
                    self.final_scores = {p.player_id: p.score for p in self.players}; return

                base_score = 8
                if is_self_drawn:
                    pts_change = base_score + fan_cnt_total
                    self.players[winner_index].score += pts_change * 3
                    for p_idx in range(4):
                        if p_idx != winner_index: self.players[p_idx].score -= pts_change
                else: # Discard win or robbing kong
                    # Determine the actual payer
                    payer_idx = last_discarding_player_idx_for_payment if is_robbing_kong else self.last_discarding_player_index

                    if payer_idx is None:
                        self.error_message = "Payer index not determined for non-self-drawn win."
                        print(f"GAME ENDED (ERROR): {self.error_message}", flush=True)
                        self.final_scores = {p.player_id: p.score for p in self.players}; return

                    if is_robbing_kong:
                        # Robbing kong: Robbed player (payer_idx) pays (base_score + fan_cnt_total). Others pay 0.
                        # This is a common interpretation, though some rules make them pay as if self-drawn by winner.
                        # The prompt said: "Robbed player (bugang_player_idx) pays (base_score + fan_cnt_total). Others pay 0."
                        pts_change = base_score + fan_cnt_total
                        self.players[winner_index].score += pts_change
                        self.players[payer_idx].score -= pts_change
                    else: # Normal discard
                        pts_change = base_score + fan_cnt_total
                        self.players[winner_index].score += pts_change
                        self.players[payer_idx].score -= pts_change

                self.final_scores = {p.player_id: p.score for p in self.players}
                win_type_str = "ROBBING KONG" if is_robbing_kong else ("SELF-DRAWN (After Kong)" if was_kong_replacement_draw and is_self_drawn else ("SELF-DRAWN" if is_self_drawn else "DISCARD"))
                print(f"GAME ENDED (WIN): Player {winner_index} wins with {fan_cnt_total} Fan (+{base_score} Base). Type: {win_type_str}.", flush=True)
                if self.win_details: print(f"  Fan Details: {self.win_details}", flush=True)
            except Exception as e:
                print(f"Error during MahjongFanCalculator for P{winner_index}: {e}", flush=True)
                import traceback; traceback.print_exc()
                self.error_message = f"P{winner_index} score calculation error: {e}"
                self.final_scores = {p.player_id: p.score for p in self.players}
        else:
            self.final_scores = {p.player_id: p.score for p in self.players}

    def can_player_hu_discard(self, player_idx: int, discarded_tile: str, num_wall_tiles_left: int, is_potential_robbing_kong: bool = False) -> bool:
        player = self.players[player_idx]
        temp_hand = list(player.hand); temp_hand.append(discarded_tile); temp_hand.sort()
        calculator_melds = []
        for meld_tuple in player.melds:
            meld_type = meld_tuple[0].upper(); tile1 = meld_tuple[1]; data = meld_tuple[2]
            offer_relative = 0; actual_calc_meld_type = meld_type
            if meld_type == "CHI": offer_relative = self._get_relative_offer(meld_tuple[3], player_idx)
            elif meld_type in ["PENG", "GANG", "ANGANG", "BUGANG"]:
                offer_relative = self._get_relative_offer(data, player_idx)
                if meld_type == "BUGANG": actual_calc_meld_type = "GANG"
                if meld_type == "ANGANG": actual_calc_meld_type = "KONG"
            calculator_melds.append((actual_calc_meld_type, tile1, offer_relative))
        try:
            fan_total = MahjongFanCalculator(
                pack=tuple(calculator_melds), hand=tuple(temp_hand), winTile=discarded_tile, flowerCount=0,
                isSelfDrawn=False, is4thTile=False,
                isAboutKong=is_potential_robbing_kong, # Correctly using the passed flag
                isWallLast=(num_wall_tiles_left == 0),
                seatWind=player.seat_wind, prevalentWind=self.prevalent_wind
            ).calculate_fan()
            return fan_total >= 8
        except Exception: return False

    def can_player_peng(self, player_idx: int, discarded_tile: str) -> bool:
        return self.players[player_idx].hand.count(discarded_tile) >= 2
    def can_player_ming_kong_from_discard(self, player_idx: int, discarded_tile: str) -> bool:
        return self.players[player_idx].hand.count(discarded_tile) >= 3
    def get_chi_hand_tiles_to_remove(self, player_idx: int, discarded_tile_str: str, chi_request_middle_tile_str: str) -> Optional[List[str]]:
        player = self.players[player_idx]
        if not (len(discarded_tile_str) == 2 and len(chi_request_middle_tile_str) == 2): return None
        discarded_suit, middle_suit = discarded_tile_str[0], chi_request_middle_tile_str[0]
        if discarded_suit != middle_suit or discarded_suit not in [WAN, TONG, TIAO]: return None
        try: discarded_num, middle_num = int(discarded_tile_str[1:]), int(chi_request_middle_tile_str[1:])
        except ValueError: return None
        if not (1 < middle_num < 9): return None
        sequence_nums = [middle_num - 1, middle_num, middle_num + 1]
        if discarded_num not in sequence_nums: return None
        expected_sequence_tiles = [f"{discarded_suit}{n}" for n in sequence_nums]
        tiles_player_needs_in_hand = [t for t in expected_sequence_tiles if t != discarded_tile_str]
        if len(tiles_player_needs_in_hand) != 2: return None
        temp_hand = list(player.hand)
        for needed_tile in tiles_player_needs_in_hand:
            if needed_tile in temp_hand: temp_hand.remove(needed_tile)
            else: return None
        return sorted(tiles_player_needs_in_hand)

if __name__ == '__main__': pass
