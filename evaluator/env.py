
import random
from collections import defaultdict

try:
    from MahjongGB import MahjongFanCalculator
except:
    print('MahjongGB library required! Please visit https://github.com/ailab-pku/PyMahjongGB for more information.')
    raise

class Error(Exception):
    pass

class MahjongGBEnv():


    def __init__(self):
        # Environment setup for evaluation
        # Initialize all attributes that are used in other methods to avoid AttributeError
        self.r = random.Random()
        self.reward = None
        self.done = False
        self.obs = {}
        self.prevalentWind = -1
        self.tileWall = []
        self.originalTileWall = ""
        self.duplicate = True  # Default, can be configured if evaluator needs it
        self.variety = -1      # Default
        self.shownTiles = defaultdict(int)
        self.hands = [[] for _ in range(4)] # Ensure it's a list of lists
        self.packs = [[] for _ in range(4)] # Ensure it's a list of lists
        self.curPlayer = 0
        self.curTile = ""
        # state: 0: after Chi/Peng, 1: after Draw, 2: after Play, 3: after BuGang
        self.state = 0
        self.myWallLast = False
        self.wallLast = False
        self.isAboutKong = False
        self.drawAboutKong = False
        # print("MahjongGBEnv initialized for evaluation") # Optional: for debugging

    def reset(self, prevalentWind = -1, tileWall = ''): # Removed backslash
        self.reward = None
        self.done = False
        if self.variety > 0:
            random.seed(self.r.randint(0, self.variety - 1))
        self.prevalentWind = random.randint(0, 3) if prevalentWind < 0 else prevalentWind
        if tileWall:
            self.tileWall = tileWall.split()
        else:
            self.tileWall = []
            for _ in range(4): # Corrected loop for tiles
                for i in range(1, 10):
                    self.tileWall.extend([f'W{i}', f'B{i}', f'T{i}'])
                for i in range(1, 5): self.tileWall.append(f'F{i}')
                for i in range(1, 4): self.tileWall.append(f'J{i}')
            random.shuffle(self.tileWall)
        self.originalTileWall = ' '.join(self.tileWall)
        if self.duplicate:
            # This tile distribution might need adjustment if tileWall isn't 136 tiles
            # For now, assuming it's a standard wall being duplicated
            if len(self.tileWall) == 136: # Standard full wall
                 self.tileWall = [self.tileWall[i * 34 : (i + 1) * 34] for i in range(4)]
            elif not self.tileWall: # if tileWall was empty, duplicate won't work as expected
                pass # or handle error/warning
            # else: don't try to split if not a standard wall for duplication

        self.shownTiles = defaultdict(int)
        self.hands = [[] for _ in range(4)] # Initialize for reset
        self.packs = [[] for _ in range(4)] # Initialize for reset
        self._deal()
        return self.obs

    def step(self, action_dict):
        try:
            if self.state == 0: # After Chi/Peng, current player needs to play a tile
                action_str = action_dict.get(self.curPlayer)
                if not action_str:
                    raise Error(f"Missing action for player {self.curPlayer} in state 0")

                action_parts = action_str.split()
                action_type = action_parts[0]

                if action_type == 'PLAY':
                    if len(action_parts) < 2:
                        raise Error(f"Invalid PLAY action for player {self.curPlayer}: Missing tile")
                    tile_to_discard = action_parts[1]
                    self._discard(self.curPlayer, tile_to_discard)
                else:
                    raise Error(f"Invalid action type {action_type} for player {self.curPlayer} in state 0. Expected PLAY.")
                self.isAboutKong = False
                self.obs = {}

            elif self.state == 1: # After Draw, current player needs to Hu/Play/Gang/BuGang
                action_str = action_dict.get(self.curPlayer)
                if not action_str:
                    raise Error(f"Missing action for player {self.curPlayer} in state 1")

                action_parts = action_str.split()
                action_type = action_parts[0]

                if action_type == 'HU':
                    self.shownTiles[self.curTile] += 1 # Assuming curTile is the winning tile
                    self._checkMahjong(self.curPlayer, isSelfDrawn=True, isAboutKong=self.isAboutKong)
                elif action_type == 'PLAY':
                    if len(action_parts) < 2:
                        raise Error(f"Invalid PLAY action for player {self.curPlayer}: Missing tile")
                    tile_to_discard = action_parts[1]
                    # Player has already drawn, so curTile is in their hand conceptually before PLAY
                    # self.hands[self.curPlayer].append(self.curTile) # This is done in _draw, hand is updated before player makes decision
                    self._discard(self.curPlayer, tile_to_discard)
                elif action_type == 'GANG':
                    if len(action_parts) < 2:
                        raise Error(f"Invalid GANG action for player {self.curPlayer}: Missing tile")
                    tile_to_gang = action_parts[1]
                    if not self.myWallLast and not self.wallLast:
                        self._concealedKong(self.curPlayer, tile_to_gang)
                    else:
                        raise Error(f"Cannot GANG for player {self.curPlayer}: Wall last condition.")
                elif action_type == 'BUGANG':
                    if len(action_parts) < 2:
                        raise Error(f"Invalid BUGANG action for player {self.curPlayer}: Missing tile")
                    tile_to_bugang = action_parts[1]
                    if not self.myWallLast and not self.wallLast:
                        self._promoteKong(self.curPlayer, tile_to_bugang)
                    else:
                        raise Error(f"Cannot BUGANG for player {self.curPlayer}: Wall last condition.")
                else:
                    raise Error(f"Invalid action type {action_type} for player {self.curPlayer} in state 1.")
                self.obs = {}

            elif self.state == 2: # After Play, other players can Chi/Peng/Gang/Hu/Pass
                # Priority: HU > GANG/PENG > CHI
                # Order of checking players: next player, player across, previous player

                action_processed = False
                hu_action = None
                gang_peng_action = None
                chi_action = None

                player_actions = {}
                for j in range(1, 4):
                    p_idx = (self.curPlayer + j) % 4
                    action_str = action_dict.get(p_idx)
                    if not action_str:
                        # Assuming PASS if no action is provided for a player who can act
                        player_actions[p_idx] = "PASS"
                    else:
                        player_actions[p_idx] = action_str.split()

                # Check for HU actions first
                for j in range(1, 4):
                    p_idx = (self.curPlayer + j) % 4
                    action_parts = player_actions.get(p_idx, ["PASS"])
                    if action_parts[0] == 'HU':
                        self._checkMahjong(p_idx, isAboutKong=self.isAboutKong) # isAboutKong might be relevant if prev action was GANG
                        action_processed = True
                        break

                if not action_processed:
                    # Check for GANG/PENG actions
                    for j in range(1, 4):
                        p_idx = (self.curPlayer + j) % 4
                        action_parts = player_actions.get(p_idx, ["PASS"])
                        action_type = action_parts[0]

                        if action_type == 'GANG':
                            if self._canDrawTile(p_idx) and not self.wallLast:
                                self._kong(p_idx, self.curTile) # curTile is the tile just played by self.curPlayer
                                action_processed = True
                                break
                            # else: Cannot GANG (e.g. no tiles left for this player, or wall last)
                        elif action_type == 'PENG':
                            if not self.wallLast:
                                self._pung(p_idx, self.curTile)
                                action_processed = True
                                break
                            # else: Cannot PENG

                if not action_processed:
                    # Check for CHI action (only for the next player)
                    next_player_idx = (self.curPlayer + 1) % 4
                    action_parts = player_actions.get(next_player_idx, ["PASS"])
                    action_type = action_parts[0]

                    if action_type == 'CHI':
                        if not self.wallLast:
                            if len(action_parts) < 2:
                                raise Error(f"Invalid CHI action for player {next_player_idx}: Missing tile for Chi")
                            tile_for_chi = action_parts[1] # This is the middle tile of the Chi sequence
                            self._chow(next_player_idx, tile_for_chi)
                            action_processed = True
                        # else: Cannot CHI (wall last)

                if not action_processed:
                    # All other players PASS or could not perform their desired action due to game rules
                    # Check if all players (who could act) indeed passed or had invalid non-PASS actions handled by prior checks
                    all_passed = True
                    for j in range(1, 4):
                        p_idx = (self.curPlayer + j) % 4
                        action_parts = player_actions.get(p_idx, ["PASS"])
                        if action_parts[0] != 'PASS':
                            # This case should ideally be caught by more specific error handling if an action was invalid
                            # but possible if e.g. a GANG was attempted on wallLast.
                            # For now, treat as a pass if action couldn't be processed.
                            pass

                    if self.wallLast: # No one acted, and it's wall last
                        self.obs = {}
                        self.reward = [0, 0, 0, 0]
                        self.done = True
                    else: # No one acted, not wall last, next player draws
                        self.curPlayer = (self.curPlayer + 1) % 4
                        self._draw(self.curPlayer)
                self.obs = {}

            elif self.state == 3: # After BuGang, other players can Hu/Pass (Qiang Gang)
                action_processed = False
                for j in range(1, 4): # Iterate through other players
                    p_idx = (self.curPlayer + j) % 4
                    action_str = action_dict.get(p_idx)

                    if not action_str: # Assume PASS if no action provided
                        action_type = "PASS"
                    else:
                        action_parts = action_str.split()
                        action_type = action_parts[0]

                    if action_type == 'HU':
                        # Qiang Gang Hu. self.curTile is the tile that was BuGanged.
                        self._checkMahjong(p_idx, isAboutKong=True)
                        action_processed = True
                        break

                if not action_processed:
                    # All other players PASS
                    # The current player (who BuGanged) draws a new tile
                    self._draw(self.curPlayer) # drawAboutKong should be true from _promoteKong
                self.obs = {}

        except Error as e:
            # Log the error message for debugging
            error_msg = e.args[0]
            print(f"MahjongGBEnv Error: {error_msg}") # It's good to print the actual error

            # Determine player index from error message if it's a string like "Missing action for player X"
            # This is a bit fragile; ideally Error would always store player index if relevant.
            player_in_error = -1
            if isinstance(error_msg, int): # Original way of Error(player_idx)
                player_in_error = error_msg
            else: # Try to parse from string
                import re
                match = re.search(r"player (\d+)", str(error_msg))
                if match:
                    player_in_error = int(match.group(1))

            self.obs = {}
            self.reward = [10] * 4 # Default penalty for all
            if 0 <= player_in_error < 4:
                 self.reward[player_in_error] = -30 # Specific penalty for the player causing error
            else: # If player couldn't be identified, apply general penalty or handle as a system error
                 # For now, stick to the original penalty logic if player is not identified.
                 # Consider a more general penalty if player_in_error is -1.
                 pass
            self.done = True
        return self.obs, self.reward, self.done

    def _drawTile(self, player):
        if self.duplicate:
            return self.tileWall[player].pop()
        return self.tileWall.pop()

    def _canDrawTile(self, player):
        if self.duplicate:
            return bool(self.tileWall[player])
        return bool(self.tileWall)

    def _deal(self):
        self.hands = []
        self.packs = []
        for i in range(4):
            hand = []
            while len(hand) < 13:
                tile = self._drawTile(i)
                hand.append(tile)
            self.hands.append(hand)
            self.packs.append([])
            # self.agents[i].request2obs(' '.join(['Deal', *hand]) # Replaced)
        self.curPlayer = 0
        self.drawAboutKong = False
        self._draw(self.curPlayer)

    def _draw(self, player):
        tile = self._drawTile(player)
        self.myWallLast = not self._canDrawTile(player)
        self.wallLast = not self._canDrawTile((player + 1) % 4)
        self.isAboutKong = self.drawAboutKong
        self.drawAboutKong = False
        self.state = 1
        self.curTile = tile
        self.hands[player].append(tile) # Add drawn tile to hand
        for i in range(4):
            if i != player:
                # self.agents[i].request2obs('Player %d Draw' % player) # Replaced
                pass # Added pass for syntactical correctness
        self.obs = {} # Placeholder: obs updated by game logic directly

    def _discard(self, player, tile):
        if tile not in self.hands[player]: 
            print(f"Error: Player {player} does not have tile {tile} in hand.")
            raise Error(player)
        self.hands[player].remove(tile)
        self.shownTiles[tile] += 1
        self.wallLast = not self._canDrawTile((player + 1) % 4)
        self.curTile = tile
        self.state = 2
        # self.agents[player].request2obs('Player %d Play %s' % (player, tile) # Replaced)
        self.obs = {} # Placeholder: obs updated by game logic directly

    def _kong(self, player, tile):
        self.hands[player].append(self.curTile)
        if self.hands[player].count(tile) < 4: 
            print(f"Error: Player {player} does not have enough tiles {tile} for a Kong.")
            raise Error(player)
        for i in range(4): self.hands[player].remove(tile)
        # offer: 0 for self, 123 for up/oppo/down
        self.packs[player].append(('GANG', tile, (player + 4 - self.curPlayer) % 4))
        self.shownTiles[tile] = 4
        self.curPlayer = player
        self.drawAboutKong = True
        self.isAboutKong = False
                # Calls to agent.request2obs removed in _kong
        self._draw(player)

    def _pung(self, player, tile):
        self.hands[player].append(self.curTile)
        if self.hands[player].count(tile) < 3: 
            print(f"Error: Player {player} does not have enough tiles {tile} for a Pung.")
            raise Error(player)
        for i in range(3): self.hands[player].remove(tile)
        # offer: 0 for self, 123 for up/oppo/down
        self.packs[player].append(('PENG', tile, (player + 4 - self.curPlayer) % 4))
        self.shownTiles[tile] += 2
        self.state = 0
        self.curPlayer = player
        for i in range(4):
            if i != player:
                # self.agents[i].request2obs('Player %d Peng' % player) # Replaced
                pass # Added pass for syntactical correctness
        self.obs = {} # Placeholder: obs updated by game logic directly

    def _chow(self, player, tile):
        self.hands[player].append(self.curTile)
        self.shownTiles[self.curTile] -= 1
        color = tile[0]
        num = int(tile[1])
        for i in range(-1, 2):
            t = color + str(num + i)
            if t not in self.hands[player]: 
                print(f"Error: Player {player} does not have tile {t} in hand.")
                raise Error(player)
            self.hands[player].remove(t)
            self.shownTiles[t] += 1
        # offer: 123 for which tile is offered
        self.packs[player].append(('CHI', tile, int(self.curTile[1]) - num + 2))
        self.state = 0
        self.curPlayer = player
        for i in range(4):
            if i != player:
                # self.agents[i].request2obs('Player %d Chi %s' % (player, tile) # Replaced)
                pass # Added pass for syntactical correctness
        self.obs = {} # Placeholder: obs updated by game logic directly

    def _concealedKong(self, player, tile):
        self.hands[player].append(self.curTile)
        if self.hands[player].count(tile) < 4: 
            print(f"Error: Player {player} does not have enough tiles {tile} for a Kong.")
            raise Error(player)
        for i in range(4): self.hands[player].remove(tile)
        # offer: 0 for self, 123 for up/oppo/down
        self.packs[player].append(('GANG', tile, (player + 4 - self.curPlayer) % 4))
        self.shownTiles[tile] = 4
        self.curPlayer = player
        self.drawAboutKong = True
        self.isAboutKong = False
        for i in range(4):
            if i != player:
                # self.agents[i].request2obs('Player %d AnGang' % player) # Replaced
                pass # Added pass for syntactical correctness
        # self.agents[player].request2obs('Player %d AnGang %s' % (player, tile) # Replaced)
        self._draw(player)

    def _promoteKong(self, player, tile):
        self.hands[player].append(self.curTile)
        idx = -1
        for i in range(len(self.packs[player])):
            if self.packs[player][i][0] == 'PENG' and self.packs[player][i][1] == tile:
                idx = i
        if idx < 0: 
            print(f"Error: Player {player} does not have a PENG {tile} to promote.")
            raise Error(player)
        self.hands[player].remove(tile)
        offer = self.packs[player][idx][2]
        self.packs[player][idx] = ('GANG', tile, offer)
        self.shownTiles[tile] = 4
        self.state = 3
        self.curPlayer = player
        self.curTile = tile
        self.drawAboutKong = True
        self.isAboutKong = False
        # self.agents[player].request2obs('Player %d BuGang %s' % (player, tile) # Replaced)
        self.obs = {} # Placeholder: obs updated by game logic directly

    def _checkMahjong(self, player, isSelfDrawn = False, isAboutKong = False):
        try:
            fans = MahjongFanCalculator(
                pack = tuple(self.packs[player]),
                hand = tuple(self.hands[player]),
                winTile = self.curTile,
                flowerCount = 0,
                isSelfDrawn = isSelfDrawn,
                is4thTile = (self.shownTiles[self.curTile] + isSelfDrawn) == 4,
                isAboutKong = isAboutKong,
                isWallLast = self.wallLast,
                seatWind = player,
                prevalentWind = self.prevalentWind,
                verbose = True
            )
            fanCnt = 0
            for fanPoint, cnt, fanName, fanNameEn in fans:
                fanCnt += fanPoint * cnt
            if fanCnt < 8: 
                print(f"Error: Not Enough Fans")
                raise Error('Not Enough Fans')
            self.obs = {} # Placeholder: obs updated by game logic directly
            if isSelfDrawn:
                self.reward = [-(8 + fanCnt)] * 4
                self.reward[player] = (8 + fanCnt) * 3
            else:
                self.reward = [-8] * 4
                self.reward[player] = 8 * 3 + fanCnt
                self.reward[self.curPlayer] -= fanCnt
            self.done = True
        except Exception as e:
            raise Error(player)