from game_utils import Agent, GameState
import sys # For flushing stdout
from typing import Optional # Ensure Optional is imported

def run_game():
    print("Starting game...")
    agents = []
    try:
        # 1. Initialize four Agent objects
        print("Initializing agents...")
        for i in range(4):
            agents.append(Agent(agent_id=i))
        print("Agents initialized.")

        # 2. Crucial: Send initial newline to each agent
        print("Sending initial newline to agents...")
        for i, agent_proc in enumerate(agents):
            # The agent_trainer/__main__.py has an input() call before its main loop.
            # Sending an empty string + newline via send_request.
            agent_proc.send_request("")
            print(f"Sent initial newline to agent {i}.")
        print("Initial newlines sent.")

        # 3. Create GameState instance
        print("Creating GameState...")
        gs = GameState(agents)
        print("GameState created.")
        print(f"Prevalent wind (Quan): {gs.prevalent_wind}")
        for i, player in enumerate(gs.players):
            print(f"Player {i} initial hand: {player.hand}")
        sys.stdout.flush()


        # 4. Initial Agent Communication Loop
        for p_idx in range(4):
            player = gs.players[p_idx]
            agent = player.agent # This is agents[p_idx]

            print(f"\nCommunicating with Player {p_idx} (Agent ID: {agent.agent_id}, Seat Wind: {player.seat_wind})...")
            sys.stdout.flush()

            # Request 0: Position and Round Wind
            # Format: "0 <player_id> <prevalent_wind>"
            # player.player_id is their seat, 0-3. gs.prevalent_wind is 0-3.
            req0 = f"0 {player.player_id} {gs.prevalent_wind}"
            print(f"P{p_idx} Sending Req0: '{req0}'")
            sys.stdout.flush()
            agent.send_request(req0)

            resp0 = agent.receive_response()
            print(f"P{p_idx} Received Resp0: '{resp0}'")
            sys.stdout.flush()
            if resp0 != "PASS":
                print(f"Error: P{p_idx} Req0 expected PASS, got {resp0}")
                # Potentially raise an error or handle more gracefully

            # Request 1: Initial Hand
            # Format: "1 0 0 0 0 <hand_tiles_space_separated>" (no flower tiles)
            # Player's hand is already dealt by GameState constructor
            hand_str = " ".join(player.hand)
            req1 = f"1 0 0 0 0 {hand_str}"
            print(f"P{p_idx} Sending Req1: '{req1}'")
            sys.stdout.flush()
            agent.send_request(req1)

            resp1 = agent.receive_response()
            print(f"P{p_idx} Received Resp1: '{resp1}'")
            sys.stdout.flush()
            if resp1 != "PASS":
                print(f"Error: P{p_idx} Req1 expected PASS, got {resp1}")
                # Potentially raise an error or handle more gracefully

        print("\nInitial communication sequence finished for all players.")
        sys.stdout.flush()

        # --- Main Game Loop ---
        print("\n--- Starting Main Game Loop ---", flush=True)
        while not gs.game_over:
            current_player_index = gs.current_player_index
            current_player = gs.players[current_player_index]
            current_agent = current_player.agent
            current_player.hand.sort() # Keep hand sorted for consistent views

            action_context_tile: Optional[str] = None
            response_from_agent: Optional[str] = None

            if gs.pending_qiangganghu_check:
                print(f"--- Evaluating QiangGangHu for P{gs.last_discarding_player_index}'s BUGANG of {gs.about_to_BUGANG_tile} ---", flush=True)
                gs.pending_qiangganghu_check = False # Consume the flag

                bugang_tile_being_robbed = gs.about_to_BUGANG_tile
                bugang_player_idx = gs.last_discarding_player_index # Player who attempted BuGang

                potential_robbers = []
                for p_idx, response_str in gs.current_action_responses.items():
                    if response_str.upper() == "HU":
                        # Validate if this player can actually HU on this tile (as a robbing kong)
                        if gs.can_player_hu_discard(p_idx, bugang_tile_being_robbed, len(gs.tile_wall), is_potential_robbing_kong=True):
                            potential_robbers.append(p_idx)
                            print(f"  Player {p_idx} can QiangGangHu on {bugang_tile_being_robbed}.", flush=True)
                        else:
                            print(f"  Player {p_idx} claimed HU on BUGANG {bugang_tile_being_robbed} but validation failed.", flush=True)

                if potential_robbers:
                    robbing_player_idx = min(potential_robbers) # Simplistic choice: lowest index player
                    print(f"Player {robbing_player_idx} WINS by ROBBING THE KONG (QiangGangHu) of {bugang_tile_being_robbed} from P{bugang_player_idx}!", flush=True)

                    robbed_player = gs.players[bugang_player_idx]
                    # Revert the BuGang meld for the robbed player
                    # Find the BUGANG meld and change it back to PENG, add tile back to hand.
                    for i, meld_tuple in enumerate(robbed_player.melds):
                        # BUGANG meld: ('BUGANG', tile_kong, original_discarder_idx_for_peng, None)
                        if meld_tuple[0] == 'BUGANG' and meld_tuple[1] == bugang_tile_being_robbed:
                            robbed_player.melds[i] = ('PENG', meld_tuple[1], meld_tuple[2], None) # Revert to PENG
                            robbed_player.hand.append(bugang_tile_being_robbed) # Give tile back
                            robbed_player.hand.sort()
                            print(f"  P{bugang_player_idx}'s BUGANG of {bugang_tile_being_robbed} reverted. Hand: {robbed_player.hand}, Melds: {robbed_player.melds}", flush=True)
                            break

                    gs.end_game(winner_index=robbing_player_idx, winning_tile=bugang_tile_being_robbed,
                                is_robbing_kong=True, last_discarding_player_idx_for_payment=bugang_player_idx)

                    for i in range(4): # Notify all agents of the HU
                        gs.players[i].agent.send_request(f"3 {robbing_player_idx} HU")
                    # gs.game_over is now true, loop will terminate. No continue needed.
                else:
                    # No QiangGangHu, BuGang is successful.
                    print(f"No QiangGangHu. P{bugang_player_idx}'s BUGANG of {gs.about_to_BUGANG_tile} is successful.", flush=True)
                    gs.current_player_index = bugang_player_idx # Ensure current player is still the BuGanger
                    gs.just_declared_kong = True # Proceed to draw replacement tile
                    gs.about_to_BUGANG_tile = None # Clear after check
                    gs.last_discarding_player_index = None # Was for QGH context
                    gs.current_action_responses.clear()
                    # Loop will restart, and 'if gs.just_declared_kong:' will handle replacement draw.
                    continue # Explicitly continue to re-evaluate loop conditions like gs.just_declared_kong

            elif gs.just_declared_kong:
                # This player just declared a KONG (AnGang, successful BuGang, or Ming Kong from discard)
                # and needs to draw a replacement tile.
                print(f"--- Turn {gs.turn_number} (Player {current_player_index} KONG REPLACEMENT) ---", flush=True)
                print(f"Player {current_player_index} hand before KONG replacement: {current_player.hand}", flush=True)

                # Reset Kong flags before drawing replacement.
                # Note: gs.about_to_BUGANG_tile is reset in draw_tile if it was a BuGang that didn't get robbed.
                # If it was robbed, game would have ended. If not, player draws.
                # The draw_tile method itself resets just_declared_kong.
                # gs.just_declared_kong = False # This is now done by draw_tile
                # gs.about_to_BUGANG_tile = None # This is also reset by draw_tile
                gs.drew_kong_replacement_this_action = True # Set flag before drawing replacement

                action_context_tile = gs.draw_tile(current_player_index) # This resets relevant flags like just_declared_kong
                if action_context_tile is None:
                    print("Wall is empty during KONG replacement draw. Game is a draw.", flush=True)
                    gs.end_game(is_draw=True, error_message="Wall empty on kong replacement", was_kong_replacement_draw=True) # Pass flag
                    break

                print(f"Player {current_player_index} draws KONG replacement tile: {action_context_tile}", flush=True)
                current_player.hand.append(action_context_tile)
                current_player.hand.sort()
                print(f"Player {current_player_index} hand after KONG replacement (before decision): {current_player.hand}", flush=True)

                # Agent needs to act on this new tile (e.g., PLAY, another GANG, HU)
                request_str = f"2 {action_context_tile}" # Same as normal draw for agent's perspective
                # print(f"Player {current_player_index} hand: {current_player.hand}") # DEBUG
                # print(f"Player {current_player_index} request: {request_str}") # DEBUG
                current_agent.send_request(request_str)
                response_from_agent = current_agent.receive_response()
                # print(f"Player {current_player_index} response: {response_from_agent}") # DEBUG
                print(f"Player {current_player_index} KONG replacement draw req: '{request_str}', Agent response: '{response_from_agent}'", flush=True)

            elif gs.just_discarded:
                # A player has discarded, and we need to process other players' reactions (PENG, CHI, GANG, HU or PASS)
                # This part of the loop is for determining who acts next, or if play passes to next player.
                print(f"--- Evaluating Discard from P{gs.last_discarding_player_index} (Tile: {gs.last_discarded_tile}) ---", flush=True)
                print(f"  Responses from other players: {gs.current_action_responses}", flush=True)

                # TODO: Implement logic to prioritize HU > PENG/GANG > CHI from gs.current_action_responses
                # This includes:
                # 1. Iterating through responses.
                # 2. Validating if the action is legal (e.g., can PENG? can CHI?).
                # 3. Handling multiple players wanting to act (e.g., HU wins over PENG).
                # 4. If an action is taken (e.g., PENG by player X), then gs.current_player_index becomes X.
                #    Player X then needs to discard a tile (which will be handled by the PLAY action_type in the common block).
                #    The agent for player X would be sent a specific request indicating they made a meld and now need to discard.
                #    e.g. "4 PENG W1" -> agent responds "PLAY B2"

                # --- Start of enhanced gs.just_discarded logic ---
                potential_actions = []
                num_wall_tiles = len(gs.tile_wall)
                processed_player_action_on_discard = False # Flag to check if any player (other than discarder) acts

                # Check responses from other players for HU, PENG, KONG, CHI
                for p_idx, response_str in gs.current_action_responses.items():
                    if gs.last_discarding_player_index is None or p_idx == gs.last_discarding_player_index:
                        continue

                    response_parts = response_str.split()
                    if not response_parts: continue
                    action = response_parts[0].upper()
                    player_to_check = gs.players[p_idx]

                    if action == "HU":
                        is_robbing_kong_context = (gs.about_to_BUGANG_tile == gs.last_discarded_tile)
                        if gs.can_player_hu_discard(p_idx, gs.last_discarded_tile, num_wall_tiles, is_potential_robbing_kong=is_robbing_kong_context):
                            potential_actions.append({'type': 'HU', 'player_idx': p_idx, 'tile': gs.last_discarded_tile, 'is_robbing': is_robbing_kong_context})
                            print(f"  Player {p_idx} validated HU on {gs.last_discarded_tile} (Robbing context: {is_robbing_kong_context}).", flush=True)
                        else:
                            print(f"  Player {p_idx} claimed HU on {gs.last_discarded_tile} but validation FAILED. Hand: {player_to_check.hand}, Melds: {player_to_check.melds}", flush=True)
                    elif action == "PENG":
                        if gs.can_player_peng(p_idx, gs.last_discarded_tile):
                            if len(response_parts) < 2:
                                print(f"  Player {p_idx} PENG response invalid (missing tile to play): '{response_str}'", flush=True)
                                continue
                            tile_to_play_after_peng = response_parts[1]
                            potential_actions.append({
                                'type': 'PENG', 'player_idx': p_idx,
                                'tile': gs.last_discarded_tile,
                                'play_after': tile_to_play_after_peng
                            })
                            print(f"  Player {p_idx} validated PENG on {gs.last_discarded_tile}.", flush=True)
                        else:
                            print(f"  Player {p_idx} claimed PENG on {gs.last_discarded_tile} but validation FAILED (Hand: {player_to_check.hand}).", flush=True)
                    elif action == "GANG": # Ming Kong from discard
                        if gs.can_player_ming_kong_from_discard(p_idx, gs.last_discarded_tile):
                            potential_actions.append({'type': 'KONG', 'player_idx': p_idx, 'tile': gs.last_discarded_tile})
                            print(f"  Player {p_idx} validated KONG on {gs.last_discarded_tile}.", flush=True)
                        else:
                            print(f"  Player {p_idx} claimed KONG on {gs.last_discarded_tile} but validation FAILED (Hand: {player_to_check.hand}).", flush=True)
                    elif action == "CHI":
                        if p_idx == (gs.last_discarding_player_index + 1) % 4: # CHI only for next player
                            if len(response_parts) < 3: # "CHI <middle_tile> <tile_to_play>"
                                print(f"  Player {p_idx} CHI response invalid (missing middle tile or tile to play): '{response_str}'", flush=True)
                                continue
                            chi_middle_tile = response_parts[1]
                            tile_to_play_after_chi = response_parts[2]
                            # gs.get_chi_hand_tiles_to_remove will validate if the chi is possible with player's hand
                            required_hand_tiles_for_chi = gs.get_chi_hand_tiles_to_remove(p_idx, gs.last_discarded_tile, chi_middle_tile)
                            if required_hand_tiles_for_chi:
                                potential_actions.append({
                                    'type': 'CHI', 'player_idx': p_idx,
                                    'discarded_tile': gs.last_discarded_tile,
                                    'middle_tile': chi_middle_tile,
                                    'play_after': tile_to_play_after_chi,
                                    'hand_tiles_for_chi': required_hand_tiles_for_chi # Store for removal
                                })
                                print(f"  Player {p_idx} validated CHI on {gs.last_discarded_tile} with middle {chi_middle_tile}.", flush=True)
                            else:
                                print(f"  Player {p_idx} claimed CHI on {gs.last_discarded_tile} with middle {chi_middle_tile} but validation FAILED (Hand: {player_to_check.hand}).", flush=True)
                        else:
                             print(f"  Player {p_idx} attempted CHI out of turn for {gs.last_discarded_tile}.", flush=True)

                # Priority: HU > KONG > PENG > CHI
                hu_action = None
                all_hu_actions = [act for act in potential_actions if act['type'] == 'HU']
                if all_hu_actions:
                    hu_action = min(all_hu_actions, key=lambda x: x['player_idx']) # Simplistic choice
                    if len(all_hu_actions) > 1:
                         print(f"  Multiple valid HU claims. Player {hu_action['player_idx']} selected.", flush=True)

                if hu_action:
                    acting_player_idx = hu_action['player_idx']
                    winning_tile = hu_action['tile']
                    is_robbing = hu_action.get('is_robbing', False) # Get robbing status from action
                    print(f"Player {acting_player_idx} WINS by HU on discard {winning_tile} from P{gs.last_discarding_player_index}! (Robbing: {is_robbing})", flush=True)
                    gs.end_game(winner_index=acting_player_idx, winning_tile=winning_tile, is_self_drawn=False, is_robbing_kong=is_robbing)
                    for i in range(4): gs.players[i].agent.send_request(f"3 {acting_player_idx} HU")
                    processed_player_action_on_discard = True

                else: # No HU, check KONG -> PENG -> CHI
                    kong_action = next((act for act in potential_actions if act['type'] == 'KONG'), None)
                    # Simplified: first valid KONG claim, no complex priority if multiple.

                    if kong_action:
                        acting_player_idx = kong_action['player_idx']
                        acted_tile = kong_action['tile']
                        acting_player = gs.players[acting_player_idx]
                        print(f"Player {acting_player_idx} KONGs (Ming) {acted_tile} from P{gs.last_discarding_player_index}.", flush=True)

                        for _ in range(3): # Remove 3 for Ming Kong
                            if acted_tile in acting_player.hand: acting_player.hand.remove(acted_tile)
                            else:
                                gs.end_game(error_message=f"P{acting_player_idx} KONG validation mismatch for {acted_tile}"); break
                        if gs.game_over: continue

                        acting_player.melds.append(('GANG', acted_tile, gs.last_discarding_player_index))
                        acting_player.hand.sort()
                        print(f"  P{acting_player_idx} hand after KONG: {acting_player.hand}, Melds: {acting_player.melds}", flush=True)

                        kong_broadcast_msg = f"3 {acting_player_idx} GANG" # No tile after GANG for BotIO for Ming Kong on discard
                        for i in range(4):
                            if i == acting_player_idx: continue
                            gs.players[i].agent.send_request(kong_broadcast_msg)
                            gs.players[i].agent.receive_response() # Expect PASS

                        gs.current_player_index = acting_player_idx
                        gs.just_declared_kong = True # Player will draw replacement
                        gs.just_discarded = False
                        gs.last_discarded_tile = None
                        gs.last_discarding_player_index = None
                        gs.current_action_responses.clear()
                        gs.about_to_BUGANG_tile = None
                        processed_player_action_on_discard = True

                    else: # No KONG, check PENG
                        peng_action = next((act for act in potential_actions if act['type'] == 'PENG'), None)
                        if peng_action:
                            acting_player_idx = peng_action['player_idx']
                            acted_tile = peng_action['tile']
                            tile_to_play_after_peng = peng_action['play_after']
                            acting_player = gs.players[acting_player_idx]
                            print(f"Player {acting_player_idx} PENGs {acted_tile} from P{gs.last_discarding_player_index}.", flush=True)

                            for _ in range(2):
                                if acted_tile in acting_player.hand: acting_player.hand.remove(acted_tile)
                                else: gs.end_game(error_message=f"P{acting_player_idx} PENG validation mismatch for {acted_tile}"); break
                            if gs.game_over: continue

                            acting_player.melds.append(('PENG', acted_tile, gs.last_discarding_player_index))
                            acting_player.hand.sort()
                            print(f"  P{acting_player_idx} hand after PENG: {acting_player.hand}, Melds: {acting_player.melds}", flush=True)

                            if tile_to_play_after_peng not in acting_player.hand:
                                gs.end_game(error_message=f"P{acting_player_idx} PENG invalid discard {tile_to_play_after_peng}. Hand: {acting_player.hand}")
                                processed_player_action_on_discard = True # Game ends
                            else:
                                acting_player.hand.remove(tile_to_play_after_peng)
                                acting_player.hand.sort()
                                acting_player.discarded_tiles.append(tile_to_play_after_peng)
                                print(f"  P{acting_player_idx} then discards {tile_to_play_after_peng}. Hand: {acting_player.hand}", flush=True)

                                peng_broadcast_msg = f"3 {acting_player_idx} PENG {tile_to_play_after_peng}"
                                new_responses = {}
                                for i in range(4):
                                    if i == acting_player_idx: continue
                                    gs.players[i].agent.send_request(peng_broadcast_msg)
                                    new_responses[i] = gs.players[i].agent.receive_response()
                                    print(f"    P{i} (Agent {gs.players[i].agent.agent_id}) response to PENG broadcast (P{acting_player_idx} played {tile_to_play_after_peng}): '{new_responses[i]}'", flush=True)

                                gs.last_discarded_tile = tile_to_play_after_peng
                                gs.last_discarding_player_index = acting_player_idx
                                gs.current_player_index = acting_player_idx
                                gs.just_discarded = True
                                gs.current_action_responses = new_responses
                                gs.about_to_BUGANG_tile = None
                                processed_player_action_on_discard = True

                        else: # No PENG, check CHI
                            chi_action = next((act for act in potential_actions if act['type'] == 'CHI'), None)
                            if chi_action:
                                acting_player_idx = chi_action['player_idx']
                                discarded_chi_tile = chi_action['discarded_tile']
                                middle_tile = chi_action['middle_tile']
                                tile_to_play_after_chi = chi_action['play_after']
                                hand_tiles_for_chi = chi_action['hand_tiles_for_chi'] # Already validated by get_chi_hand_tiles_to_remove
                                acting_player = gs.players[acting_player_idx]

                                print(f"Player {acting_player_idx} CHIs {discarded_chi_tile} (using middle {middle_tile}, needs {hand_tiles_for_chi}) from P{gs.last_discarding_player_index}.", flush=True)

                                for tile_to_remove in hand_tiles_for_chi:
                                    if tile_to_remove in acting_player.hand: acting_player.hand.remove(tile_to_remove)
                                    else: gs.end_game(error_message=f"P{acting_player_idx} CHI validation mismatch for {tile_to_remove}"); break
                                if gs.game_over: continue

                                # Determine full sequence string for meld e.g. W1W2W3
                                suit = middle_tile[0]
                                mid_num = int(middle_tile[1:])
                                full_sequence_str = f"{suit}{mid_num-1}{suit}{mid_num}{suit}{mid_num+1}"
                                acting_player.melds.append(('CHI', middle_tile, full_sequence_str, gs.last_discarding_player_index))
                                acting_player.hand.sort()
                                print(f"  P{acting_player_idx} hand after CHI: {acting_player.hand}, Melds: {acting_player.melds}", flush=True)

                                if tile_to_play_after_chi not in acting_player.hand:
                                    gs.end_game(error_message=f"P{acting_player_idx} CHI invalid discard {tile_to_play_after_chi}. Hand: {acting_player.hand}")
                                    processed_player_action_on_discard = True # Game ends
                                else:
                                    acting_player.hand.remove(tile_to_play_after_chi)
                                    acting_player.hand.sort()
                                    acting_player.discarded_tiles.append(tile_to_play_after_chi)
                                    print(f"  P{acting_player_idx} then discards {tile_to_play_after_chi}. Hand: {acting_player.hand}", flush=True)

                                    chi_broadcast_msg = f"3 {acting_player_idx} CHI {middle_tile} {tile_to_play_after_chi}" # BotIO: CHI middle_tile tile_discarded_after
                                    new_responses = {}
                                    for i in range(4):
                                        if i == acting_player_idx: continue
                                        gs.players[i].agent.send_request(chi_broadcast_msg)
                                        new_responses[i] = gs.players[i].agent.receive_response()
                                        print(f"    P{i} (Agent {gs.players[i].agent.agent_id}) response to CHI broadcast (P{acting_player_idx} played {tile_to_play_after_chi}): '{new_responses[i]}'", flush=True)

                                    gs.last_discarded_tile = tile_to_play_after_chi
                                    gs.last_discarding_player_index = acting_player_idx
                                    gs.current_player_index = acting_player_idx
                                    gs.just_discarded = True
                                    gs.current_action_responses = new_responses
                                    gs.about_to_BUGANG_tile = None
                                    processed_player_action_on_discard = True

                if not processed_player_action_on_discard and not gs.game_over: # No HU, KONG, PENG, or CHI was processed
                    print(f"  All other players PASS on discarded tile {gs.last_discarded_tile} from P{gs.last_discarding_player_index}.", flush=True)
                    gs.current_player_index = (gs.last_discarding_player_index + 1) % 4
                    gs.just_discarded = False
                    gs.last_discarded_tile = None # Clear only if no one acted.
                    gs.last_discarding_player_index = None # Clear only if no one acted.
                    gs.current_action_responses.clear()
                    gs.about_to_BUGANG_tile = None
                    continue # Important: proceed to next player's normal turn
                # --- End of enhanced gs.just_discarded logic ---

            else: # Normal player turn: Draw a tile
                gs.turn_number += 1
                print(f"\n--- Turn {gs.turn_number}: Player {current_player_index} (Seat: {current_player.seat_wind}, AgentID: {current_agent.agent_id}) ---", flush=True)
                print(f"Player {current_player_index} hand before normal draw: {current_player.hand}", flush=True)

                action_context_tile = gs.draw_tile(current_player_index) # This resets relevant flags
                if action_context_tile is None:
                    print("Wall is empty during normal draw. Game is a draw.", flush=True)
                    gs.end_game(is_draw=True, error_message="Wall empty on normal draw")
                    break

                print(f"Player {current_player_index} draws normal tile: {action_context_tile}", flush=True)
                current_player.hand.append(action_context_tile)
                current_player.hand.sort()
                print(f"Player {current_player_index} hand after normal draw (before decision): {current_player.hand}", flush=True)

                request_str = f"2 {action_context_tile}"
                # print(f"Player {current_player_index} hand: {current_player.hand}") # DEBUG
                # print(f"Player {current_player_index} request: {request_str}") # DEBUG
                current_agent.send_request(request_str)
                response_from_agent = current_agent.receive_response()
                # print(f"Player {current_player_index} response: {response_from_agent}") # DEBUG
                print(f"Player {current_player_index} normal draw req: '{request_str}', Agent response: '{response_from_agent}'", flush=True)

            # -------- COMMON RESPONSE PROCESSING BLOCK --------
            # This block processes responses from HU, PLAY, GANG, BUGANG that came from either a normal draw or a kong replacement draw

            if gs.game_over: # Game might have ended due to wall empty
                break

            if response_from_agent is None:
                # This should not happen if the logic for KONG/DISCARD/NORMAL states is correct and leads to a response
                err_msg = f"P{current_player_index} missing agent response unexpectedly (not a discard evaluation cycle)."
                print(f"CRITICAL LOGIC ERROR: {err_msg}", flush=True)
                gs.end_game(error_message=err_msg)
                break

            current_player.hand.sort() # Ensure hand is sorted before printing or validation
            print(f"Player {current_player_index} processing response: '{response_from_agent}' for action tile '{action_context_tile}'. Hand: {current_player.hand}", flush=True)

            action_parts = response_from_agent.split()
            action_type = action_parts[0] if action_parts else "NO_ACTION"

            if action_type == "HU":
                # Handles HU from drawn tile (normal or kong replacement)
                print(f"Player {current_player_index} declares SELF-DRAWN HU with {action_context_tile}!", flush=True)
                gs.end_game(
                    winner_index=current_player_index,
                    winning_tile=action_context_tile,
                    is_self_drawn=True,
                    was_kong_replacement_draw=gs.drew_kong_replacement_this_action # Pass the flag
                )
                # Loop will terminate as gs.game_over is True

            elif action_type == "PLAY":
                if len(action_parts) < 2:
                    err_msg = f"P{current_player_index} PLAY action missing tile. Response: '{response_from_agent}'"
                    print(f"CRITICAL ERROR: {err_msg}", flush=True)
                    gs.end_game(error_message=err_msg)
                    break
                tile_played = action_parts[1]

                # print(f"Player {current_player_index} played {tile_played}, hand: {current_player.hand}") # DEBUG
                if tile_played not in current_player.hand:
                    err_msg = f"P{current_player_index} tried to play {tile_played} which is NOT in hand {current_player.hand} (action tile was: {action_context_tile})."
                    print(f"CRITICAL ERROR: {err_msg}", flush=True)
                    gs.end_game(error_message=err_msg)
                    break

                current_player.hand.remove(tile_played)
                current_player.hand.sort()
                current_player.discarded_tiles.append(tile_played)
                gs.last_discarded_tile = tile_played
                gs.last_discarding_player_index = current_player_index
                gs.just_discarded = True # IMPORTANT: Set this flag for the next loop iteration

                print(f"Player {current_player_index} plays tile: {tile_played}. Hand: {current_player.hand}", flush=True)

                # Broadcast discard to other players
                gs.current_action_responses = {}
                for p_idx in range(4):
                    if p_idx == current_player_index:
                        continue
                    other_player = gs.players[p_idx]
                    other_agent = other_player.agent
                    request_play_broadcast = f"3 {current_player_index} PLAY {tile_played}"
                    other_agent.send_request(request_play_broadcast)
                    response_broadcast = other_agent.receive_response()
                    gs.current_action_responses[p_idx] = response_broadcast
                    print(f"  P{p_idx} (Agent {other_agent.agent_id}) saw P{current_player_index} play {tile_played}. Agent response: '{response_broadcast}'", flush=True)

                # Notify the acting agent about its own play so it can update its internal state
                self_play_notification_req = f"3 {current_player_index} PLAY {tile_played}"
                # print(f"Player {current_player_index} (acting agent) Sending self-notification of PLAY: '{self_play_notification_req}'", flush=True) # DEBUG
                # The current_agent is already defined in this scope
                current_agent.send_request(self_play_notification_req)
                self_play_notification_resp = current_agent.receive_response()
                # print(f"Player {current_player_index} (acting agent) Received response to self-notification: '{self_play_notification_resp}'", flush=True) # DEBUG
                if self_play_notification_resp.upper() != "PASS":
                    print(f"WARNING: Player {current_player_index} (acting agent) did not respond with PASS to self-play notification. Got: {self_play_notification_resp}", flush=True)
                    # Decide if this should be a critical error or just a warning.
                    # For now, a warning, as the agent's __main__.py should handle this by printing PASS.
                # The next iteration of the main while loop will handle gs.just_discarded = True

            elif action_type == "GANG": # AnGang from drawn tile (normal or kong replacement)
                if len(action_parts) < 2:
                    err_msg = f"P{current_player_index} GANG action missing tile. Response: '{response_from_agent}'"
                    print(f"CRITICAL ERROR: {err_msg}", flush=True)
                    gs.end_game(error_message=err_msg)
                    break
                tile_kong = action_parts[1]

                if current_player.hand.count(tile_kong) != 4: # Action_context_tile was already added
                    err_msg = f"P{current_player_index} declared GANG {tile_kong} but hand count is {current_player.hand.count(tile_kong)} (requires 4). Hand: {current_player.hand} (action tile was: {action_context_tile})"
                    print(f"CRITICAL ERROR: {err_msg}", flush=True)
                    gs.end_game(error_message=err_msg)
                    break

                for _ in range(4):
                    current_player.hand.remove(tile_kong)
                current_player.hand.sort()
                current_player.melds.append(('ANGANG', tile_kong, current_player_index))
                print(f"Player {current_player_index} declares ANGANG with {tile_kong}. Hand: {current_player.hand}. Melds: {current_player.melds}", flush=True)

                gs.just_declared_kong = True # Player will draw replacement in next iteration
                # current_player_index remains the same.

            elif action_type == "BUGANG":
                if len(action_parts) < 2:
                    err_msg = f"P{current_player_index} BUGANG action missing tile. Response: '{response_from_agent}'"
                    print(f"CRITICAL ERROR: {err_msg}", flush=True)
                    gs.end_game(error_message=err_msg); break
                tile_kong = action_parts[1]

                if tile_kong != action_context_tile: # BuGang must use the drawn tile (or tile just added to hand)
                    err_msg = f"P{current_player_index} BUGANG tile {tile_kong} must be the action context tile {action_context_tile}."
                    print(f"CRITICAL ERROR: {err_msg}", flush=True)
                    gs.end_game(error_message=err_msg); break

                # Find the PENG meld to upgrade
                peng_meld_to_upgrade = None
                peng_meld_idx = -1
                original_peng_from_idx = -1
                # Player.melds stores: ('PENG', tile_str, from_player_abs_idx, None)
                for i, meld in enumerate(current_player.melds):
                    if meld[0] == 'PENG' and meld[1] == tile_kong:
                        peng_meld_to_upgrade = meld
                        peng_meld_idx = i
                        original_peng_from_idx = meld[2] # This is from_player_abs_idx
                        break

                if not peng_meld_to_upgrade:
                    err_msg = f"P{current_player_index} declared BUGANG {tile_kong} but no corresponding PENG found. Melds: {current_player.melds}"
                    print(f"CRITICAL ERROR: {err_msg}", flush=True)
                    gs.end_game(error_message=err_msg); break

                # Temporarily update meld to BUGANG for broadcast and QGH check
                # This might be reverted if robbed.
                current_player.melds[peng_meld_idx] = ('BUGANG', tile_kong, original_peng_from_idx, None)
                current_player.hand.remove(tile_kong) # Tile is now part of the meld
                current_player.hand.sort()
                print(f"Player {current_player_index} declares BUGANG with {tile_kong}. Hand: {current_player.hand}, Melds: {current_player.melds}", flush=True)

                gs.about_to_BUGANG_tile = tile_kong
                gs.last_discarding_player_index = current_player_index # Player attempting BuGang
                gs.current_action_responses.clear()

                bugang_broadcast_msg = f"3 {current_player_index} BUGANG {tile_kong}"
                for p_idx in range(4):
                    if p_idx == current_player_index: continue
                    gs.players[p_idx].agent.send_request(bugang_broadcast_msg)
                    response_qgh = gs.players[p_idx].agent.receive_response()
                    gs.current_action_responses[p_idx] = response_qgh
                    print(f"  P{p_idx} response to P{current_player_index}'s BUGANG of {tile_kong}: '{response_qgh}'", flush=True)

                gs.pending_qiangganghu_check = True
                # current_player_index remains current_player_index to see if QGH happens or if they get to draw replacement.
                # Loop will cycle, new 'elif gs.pending_qiangganghu_check:' will handle it.
                continue # Explicitly continue to trigger the pending_qiangganghu_check block

            else: # Unexpected action
                err_msg = f"P{current_player_index} responded with unexpected action '{response_from_agent}' after action on tile '{action_context_tile}'. Expected PLAY, GANG, BUGANG, or HU."
                print(f"CRITICAL ERROR: {err_msg}", flush=True)
                gs.end_game(error_message=err_msg)
                # Loop will terminate as gs.game_over is True

            if gs.game_over: # If game ended due to HU or error from this block
                break

            # Turn limit condition
            if gs.turn_number >= 80 and not gs.game_over:
                print("Turn limit (80) reached.", flush=True)
                gs.end_game(is_draw=True, error_message="Turn limit reached")
                # Loop will terminate due to gs.game_over

        print("\n--- Main Game Loop Ended ---", flush=True)

        # --- Print Game Over Information ---
        print("\n--- Game Over ---", flush=True)
        if gs.error_message:
            print(f"Game ended due to an error: {gs.error_message}", flush=True)
        elif gs.winner_index is not None:
            print(f"Player {gs.winner_index} is the winner!", flush=True)
            if gs.winning_tile: print(f"Winning Tile: {gs.winning_tile}", flush=True)

            win_type_str = "UNKNOWN"
            if gs.is_self_drawn_win:
                win_type_str = "SELF-DRAWN (Zimo)"
                if gs.drew_kong_replacement_this_action: # Check if this was set for the winning action
                     # Note: drew_kong_replacement_this_action might be reset by a subsequent (failed) draw if game ends by other means.
                     # The was_kong_replacement_draw flag passed to end_game is more reliable for the specific winning moment.
                    win_type_str = "SELF-DRAWN After Kong (Ling Shang Kai Hua)"
            elif gs.is_robbing_kong_win:
                win_type_str = "Robbing the Kong (Qiang Gang Hu)"
            elif gs.last_discarding_player_index is not None: # Check if it's a discard win
                win_type_str = f"Win by Discard from Player {gs.last_discarding_player_index}"
            print(f"Type: {win_type_str}", flush=True)

            if gs.win_details:
                print("Fan Breakdown:", flush=True)
                total_fan_calc = 0
                for points, count, name_zh, name_en in gs.win_details:
                    print(f"  - {name_zh} ({name_en}): {points} Fan x {count}", flush=True)
                    total_fan_calc += points * count
                print(f"Total Fan Points (from calculator): {total_fan_calc}", flush=True)
        else: # No winner_index and no error_message means a draw
            print("Game ended in a draw (e.g., wall empty or turn limit).", flush=True)

        print("\nFinal Scores:", flush=True)
        for i in range(4):
            # Use final_scores if populated by end_game, otherwise current player scores (e.g. if error before scoring)
            player_score = gs.final_scores.get(i, gs.players[i].score)
            print(f"  Player {i}: {player_score} points", flush=True)
        # --- End of Game Over Information ---

    except Exception as e:
        print(f"An error occurred during the game: {e}", flush=True)
        # Print traceback for more details
        import traceback
        traceback.print_exc()
    finally:
        # 5. Agent Cleanup
        print("\nClosing agent processes...")
        sys.stdout.flush()
        for i, agent_proc in enumerate(agents):
            if agent_proc: # Check if agent was successfully created
                print(f"Closing agent {i}...")
                sys.stdout.flush()
                agent_proc.close()
                print(f"Agent {i} closed.")
                sys.stdout.flush()
        print("All agent processes closed.")

if __name__ == "__main__":
    run_game()
