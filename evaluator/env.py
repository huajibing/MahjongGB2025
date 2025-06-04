
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
            if self.state == 0:
                # After Chi/Peng, prepare to Play
                response = "PLAY W1".split() # Placeholder action for curPlayer
                if response[0] == 'PLAY':
                    self._discard(self.curPlayer, response[1])
                else:
                    raise Error(self.curPlayer)
                self.isAboutKong = False
            elif self.state == 1:
                # After Draw, prepare to Hu/Play/Gang/BuGang
                response = "PLAY W1".split() # Placeholder action for curPlayer
                if response[0] == 'HU':
                    self.shownTiles[self.curTile] += 1
                    self._checkMahjong(self.curPlayer, isSelfDrawn = True, isAboutKong = self.isAboutKong)
                elif response[0] == 'PLAY':
                    self.hands[self.curPlayer].append(self.curTile)
                    self._discard(self.curPlayer, response[1])
                elif response[0] == 'GANG' and not self.myWallLast and not self.wallLast:
                    self._concealedKong(self.curPlayer, response[1])
                elif response[0] == 'BUGANG' and not self.myWallLast and not self.wallLast:
                    self._promoteKong(self.curPlayer, response[1])
                else:
                    raise Error(self.curPlayer)
            elif self.state == 2:
                # After Play, prepare to Chi/Peng/Gang/Hu/Pass
                responses = {i : "PASS" for i in range(4) if i != self.curPlayer} # Placeholder actions for others
                t = {i : responses[i].split() for i in responses}
                # Priority: Hu > Peng/Gang > Chi
                for j in range(1, 4):
                    i = (self.curPlayer + j) % 4
                    if t[i][0] == 'HU':
                        self._checkMahjong(i)
                        break
                else:
                    for j in range(1, 4):
                        i = (self.curPlayer + j) % 4
                        if t[i][0] == 'GANG' and self._canDrawTile(i) and not self.wallLast:
                            self._kong(i, self.curTile)
                            break
                        elif t[i][0] == 'PENG' and not self.wallLast:
                            self._pung(i, self.curTile)
                            break
                    else:
                        i = (self.curPlayer + 1) % 4
                        if t[i][0] == 'CHI' and not self.wallLast:
                            self._chow(i, t[i][1])
                        else:
                            for j in range(1, 4):
                                i = (self.curPlayer + j) % 4
                                if t[i][0] != 'PASS': raise Error(i)
                            if self.wallLast:
                                # A draw
                                self.obs = {} # Placeholder: obs updated by game logic directly
                                self.reward = [0, 0, 0, 0]
                                self.done = True
                            else:
                                # Next player
                                self.curPlayer = (self.curPlayer + 1) % 4
                                self._draw(self.curPlayer)
            elif self.state == 3:
                # After BuGang, prepare to Hu/Pass
                responses = {i : "PASS" for i in range(4) if i != self.curPlayer} # Placeholder actions for others
                for j in range(1, 4):
                    i = (self.curPlayer + j) % 4
                    if responses[i] == 'HU':
                        self._checkMahjong(i, isAboutKong = True)
                        break
                else:
                    for j in range(1, 4):
                        i = (self.curPlayer + j) % 4
                        if responses[i] != 'PASS': raise Error(i)
                    self._draw(self.curPlayer)
        except Error as e:
            player = e.args[0]
            self.obs = {} # Placeholder: obs updated by game logic directly
            self.reward = [10] * 4
            self.reward[player] = -30
            self.done = True
        return self.obs, self.reward, self.done # Adjusted

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