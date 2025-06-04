# Botzone Wiki 内容整理

## 目录

1. [Chinese Standard Mahjong](#chinese-standard-mahjong)
2. [Bot](#bot)

---

## Chinese-Standard-Mahjong

国标麻将(Chinese Standard Mahjong)是Botzone平台上的四人游戏。


- 1 简介

1.1 作者
- 2 游戏规则

2.1 发牌
2.2 确定庄家和闲家
2.3 出牌
2.4 牌的构成
2.5 和牌

2.5.1 和牌方式
2.5.2 和牌牌型组成


2.6 鸣牌
2.7 番种及相关术语
2.8 算分规则

2.8.1 胡牌人数
2.8.2 错和
2.8.3 正常和牌
- 3 麻将牌的表示
- 4 游戏交互方式

4.1 提示
4.2 Bot输入输出

4.2.1 输入request
4.2.2 输出response
- 5 游戏样例程序
- 6 复式赛制介绍

6.1 简介
6.2 与传统国标的不同

6.2.1 用牌
6.2.2 定座
6.2.3 圈风及门风
6.2.4 牌墙及初始手牌
6.2.5 摸牌
6.2.6 荒牌
6.2.7 海底捞月
6.2.8 妙手回春
6.2.9 计分规则


- 1.1 作者


- 2.1 发牌
- 2.2 确定庄家和闲家
- 2.3 出牌
- 2.4 牌的构成
- 2.5 和牌

2.5.1 和牌方式
2.5.2 和牌牌型组成
- 2.6 鸣牌
- 2.7 番种及相关术语
- 2.8 算分规则

2.8.1 胡牌人数
2.8.2 错和
2.8.3 正常和牌


- 2.5.1 和牌方式
- 2.5.2 和牌牌型组成


- 2.8.1 胡牌人数
- 2.8.2 错和
- 2.8.3 正常和牌


- 4.1 提示
- 4.2 Bot输入输出

4.2.1 输入request
4.2.2 输出response


- 4.2.1 输入request
- 4.2.2 输出response


- 6.1 简介
- 6.2 与传统国标的不同

6.2.1 用牌
6.2.2 定座
6.2.3 圈风及门风
6.2.4 牌墙及初始手牌
6.2.5 摸牌
6.2.6 荒牌
6.2.7 海底捞月
6.2.8 妙手回春
6.2.9 计分规则


- 6.2.1 用牌
- 6.2.2 定座
- 6.2.3 圈风及门风
- 6.2.4 牌墙及初始手牌
- 6.2.5 摸牌
- 6.2.6 荒牌
- 6.2.7 海底捞月
- 6.2.8 妙手回春
- 6.2.9 计分规则


## 简介

麻将在中国有着三千多年的历史，而后传播至世界各地，主要流行于亚洲，具有相当广泛的群众基础。中国国家体育总局于1998年7月制定了一套麻将规则，被称为国标麻将。国标麻将具有较强的制约性、趣味性、竞技性、观赏性。

国标麻将是四人非完全信息游戏。牌山含有8张花牌，饼筒条的数牌108张，东南西北风牌16张，中发白箭牌12张，总计144张。开局时每名玩家各持有13张牌，称作“手牌”。四名玩家分坐在正方形桌子四边，按逆时针方向依次为东南西北家，以东家为庄家，其余家为闲家；每一局，庄家按照逆时针方向流转。在国标麻将的正式比赛中，需要打满四圈，一圈即四名玩家轮流坐庄，不设连庄，故正式比赛中一共打16局。

国标麻将想要获得胜利，需要让胡牌的牌型符合特定模式，即为“番种”。国标麻将有81种番种，不同番种具有不同番数。国标麻将8番起胡。

本游戏为四人游戏，在比赛中为四人对抗。在本游戏中，只打一局。

每名玩家在游戏开局将拥有13张手牌。从庄家开始，按照逆时针顺序从“牌山”中摸一张牌再打出一张牌。玩家需要在若干次摸牌、打牌、吃碰杠之后，使自己拥有的牌组成特定牌型，达到8番及以上才能和牌，否则算错和。根据牌型计算点数，游戏结束时获得点数最多的玩家，为游戏的胜者。当出现同分情况时，根据座位顺序依次排定名次。当一人放铳多人胡牌时，只有按点炮者逆时针转第一个人能胡。


### 作者

裁判程序：ybh1998

播放器：ybh1998


## 游戏规则

标准国标麻将一局有十六桌，本游戏简化为一桌，每次随机风圈。


### 发牌

每人先发13张牌。


### 确定庄家和闲家

0号玩家为庄家（东），1号、2号、3号玩家为闲家（南、西、北）。游戏桌按逆时针分别为“东南西北”，编号依次为0~3，如图所示。


### 出牌

游戏开始时由坐在东位的庄家先摸一张牌，再打出一张牌，接着按照逆时针顺序由南位的玩家进行摸牌打牌。西位、北位玩家同样。当牌山被取尽还没有和牌时，宣告平局。


### 牌的构成

一副144枚牌，由花牌、数牌、风牌和箭牌构成。


- 花牌：春夏秋冬梅兰竹菊各一张。


- 数牌：分为饼、条、万三种花色，每种花色各有数字为1~9的牌，每种数牌各有4枚。例：3饼、2万。


- 风牌：分为东南西北四种风牌，每种风牌各有4枚。例：东风。


- 箭牌：分为中发白三种箭牌，每种箭牌各有4枚。例：白板。


### 和牌


#### 和牌方式

和牌方式有两种：


- 自摸和牌。
- 别人点炮和（含抢杠胡）。


#### 和牌牌型组成

除了特殊和牌十三幺、七星不靠、全不靠、组合龙、连七对、七对之外，和牌牌型一般由四个面子和一个对子组成。对子由相同的两枚牌构成，面子则分为顺子、刻子、杠子。


- 顺子：由相同花色的三张连续数字的数牌构成，比如：一二三万，七八九万，但是八九一万不构成顺子。


- 刻子：由相同花色的三张相同数字的数牌或字牌构成，比如：二二二万，南南南风。


- 杠子：由相同花色的四张相同数字的数牌或字牌构成，比如：二二二二万，南南南南风。

特殊和牌牌型详见下端链接。


### 鸣牌

鸣牌包括吃、碰、杠。优先级为碰=杠>吃。


- 吃牌：一般状态下，在没有其他家要碰的时候，可以吃上家打出的牌，要求是手中有能和上家打出的牌组成顺子的牌，不能从鸣牌的牌中取。不能吃对家和下家的牌，也不能吃自己的牌。


- 碰牌：可以碰任意一家打出的牌，要求是手中有能和打出的牌一样的两张或三张牌，同样的，不能从鸣牌的牌中取，不能碰自己刚刚打出的牌。


- 杠牌：分为明杠、补杠、暗杠。明杠指的是手中有能和打出的牌一样的三张牌，其他要求同碰牌；补杠指的是自己已经鸣牌碰了某花色的牌，手里拿到了第四张，进行补杠操作，使得这个鸣牌的面子由刻子变为杠子；暗杠指的是手中有能和打出的牌一样的四张牌。明杠只有在别家打出牌之后能进行，补杠和暗杠只有在己家摸牌后、打牌前能进行，补杠需要在没有人抢杠和牌时成立。暗杠后其余三家无法获知什么牌被暗杠了。


### 番种及相关术语

国标麻将8番起胡。不同番种有不同的番数

查看中文版番种说明。查看更多规则说明。

提供Python和C++的算番库。


### 算分规则

国标麻将的分数计算需要计算和牌时的番数及和牌的类型。


#### 胡牌人数

一盘只能有一位和牌者。如有一人以上同时表示和牌时，从打牌者按逆时针方向，顺序在前者被定为“和牌者”。


#### 错和

国标8番起和。若Bot在游戏过程中发生错误，返回的操作不合法，和牌时不是和牌牌型或未到8番错和，发生错误的玩家-30分，其余玩家+10分，游戏结束。若有多个玩家同时出错，按“东南西北”的顺序判定第一个出错玩家。


#### 正常和牌

正常和牌后的各方得分：


- 底分=8分


- 胜方：
自摸和牌：(底分+和牌番数)×3
别人点炮和：底分×3+番种分数


- 自摸和牌：(底分+和牌番数)×3
- 别人点炮和：底分×3+番种分数


- 负方：
点炮者：-（底分+番种分数）
非点炮者：-底分
自摸和牌：-（底分+番种分数）


- 点炮者：-（底分+番种分数）
- 非点炮者：-底分
- 自摸和牌：-（底分+番种分数）


## 麻将牌的表示

所有麻将牌均以“大写字母+数字”组合表示。

如：“W4”表示“四万”，“B6”表示“六筒”，“T8”表示“8条”

“F1”～“F4”表示“东南西北”，“J1”～“J3”表示“中发白”，“H1”～“H8”表示“春夏秋冬梅兰竹菊”


## 游戏交互方式


### 提示

如果你不能理解以下交互方式,可以直接看#游戏样例程序。

本游戏与Botzone上其他游戏一样，使用相同的交互方式：Bot#交互

具体交互支持简单交互和JSON交互。


### Bot输入输出


#### 输入request


| request的格式 |
| --- |
| 编号 | 信息格式 | 样例 | 说明 |
| 0 | 0 playerID quan | 0 1 2 | 该信息只会出现在第一回合，playerID表示你的位置（门风），quan表示当前风圈。 |
| 1 | 1 hua0 hua1 hua2 hua3 Card1 Card2 ... Card13 HCard01 ... HCard0hua1 ... HCard31 ... HCard3hua3 | 1 1 2 1 1 W1 B1 ... T3 H1 H4 H2 H3 H6 | 该信息只会出现在第二回合，hua0～hua3表示四个玩家摸到的花牌数，Card1～Card13表示初始手牌，后面的hua0+...+hua3张牌表示所有人摸到的花牌。 保证Card1～Card13没有花牌，后面的均为花牌。注：在采用复式赛制的比赛中将取消花牌，此格式弃用。 |
| 2 | 2 Card1 | 2 T6 | 表示玩家摸牌摸到Card1，保证Card1不是花牌。 |
| 3 | 3 playerID BUHUA Card1 | 3 2 BUHUA H7 | 该消息会发送给所有玩家，表示玩家摸牌摸到花牌Card1，并补花。 |
| 4 | 3 playerID DRAW | 3 2 DRAW | 表示其他玩家进行了摸牌操作。 |
| 5 | 3 playerID PLAY Card1 | 3 2 PLAY T1 | 该消息会发送给所有玩家，表示玩家摸牌后，直接打出了Card1。 |
| 6 | 3 playerID PENG Card1 | 3 2 PENG Card1 | 该消息会发送给所有玩家，表示玩家进行了碰牌操作，碰的牌为上一回合打出的牌，并打出了Card1。 |
| 7 | 3 playerID CHI Card1 Card2 | 3 2 CHI T2 W3 | 该消息会发送给所有玩家，表示玩家进行了吃牌操作，吃牌后的顺子，中间牌为Card1，并打出Card2。 |
| 8 | 3 playerID GANG | 3 2 GANG | 该消息会发送给所有玩家，表示玩家进行了杠牌操作，若上一回合为摸牌，表示进行暗杠，否则杠上回合打出的牌。 |
| 9 | 3 playerID BUGANG Card1 | 3 2 BUGANG W3 | 该消息会发送给所有玩家，表示玩家进行了补杠操作，补杠Card1。 |


#### 输出response


| response的格式 |
| --- |
| 编号 | 信息格式 | 样例 | 说明 |
| 0 | PASS | PASS | 表示Bot成功获得位置和风圈信息。 |
| 1 | PASS | PASS | 表示Bot成功获得初始手牌信息。 |
| 2 | PLAY Card1 | PLAY T6 | 表示玩家摸牌后，直接打出Card1。 |
| GANG Card1 | GANG T6 | 表示玩家摸牌后，手牌存在四张Card1，进行杠牌，成功后会再次摸牌。 |
| BUGANG Card1 | BUGANG T6 | 表示玩家摸牌摸到一张牌，之前碰过这张牌，进行补杠，成功后会再次摸牌。 |
| HU | HU | 表示玩家进行和牌，此命令后无论是否和牌，游戏结束。 |
| 3 | PASS | PASS | 表示Bot成功获得补花信息。 |
| 4 | PASS | PASS | 表示Bot成功获得其他玩家摸牌信息。 |
| 5 6 7 | PASS | PASS | 表示Bot成功获得打牌信息，玩家自己的吃、碰、杠牌操作是否成功，请在此处判断。 |
| PENG Card1 | PENG T6 | 表示玩家手牌中有2张上一回合其他玩家打出的牌，想要进行碰牌，并打出Card1。 |
| CHI Card1 Card2 | CHI T2 T5 | 需要上回合为玩家上家出牌，表示玩家手牌加上上一回合其他玩家打出的牌能组成的顺子，中间牌为Card1，想要进行吃牌，并打出Card2。 |
| GANG | GANG | 表示玩家手牌中有3张上一回合其他玩家打出的牌，想要进行杠牌，成功后，下回合由该玩家开始摸牌。 |
| HU | HU | 表示玩家想要和牌，此命令后无论是否和牌，游戏结束。 |
| 8 | PASS | PASS | 表示Bot成功获得杠牌信息。 |
| 9 | PASS | PASS | 表示Bot成功获得补杠信息。 |
| HU | HU | 表示玩家想要抢杠和，此命令后无论是否和牌，游戏结束。 |

对于5 6 7号操作，由于和牌、吃牌、碰/杠牌可能同时出现，现规定其优先级如下：

和牌 > 碰/杠牌 > 吃牌

由于5 6 7操作可能失败，需要玩家自行通过下一回合的输入判断操作是否成功。


## 游戏样例程序

以下是C++编写的国标麻将样例程序。出牌策略为随机出牌。

请注意程序是有计算时间的限制的，每步要在1秒内完成！

如需使用算番库，请参见https://github.com/ailab-pku/Chinese-Standard-Mahjong/tree/master/fan-calculator-usage。

```
// 国标麻将（Chinese Standard Mahjong）样例程序
// 随机策略
// 作者：ybh1998
// 游戏信息：http://www.botzone.org/games#Chinese-Standard-Mahjong

#include <iostream>
#include <string>
#include <sstream>
#include <vector>
#include <algorithm>

#ifdef _BOTZONE_ONLINE
#include "jsoncpp/json.h"
#else
#include <json/json.h>
#endif

#define SIMPLEIO 0
//由玩家自己定义，0表示JSON交互，1表示简单交互。

using namespace std;

vector<string> request, response;
vector<string> hand;

int main()
{
    int turnID;
    string stmp;
#if SIMPLEIO
    cin >> turnID;
    turnID--;
    getline(cin, stmp);
    for(int i = 0; i < turnID; i++) {
        getline(cin, stmp);
        request.push_back(stmp);
        getline(cin, stmp);
        response.push_back(stmp);
    }
    getline(cin, stmp);
    request.push_back(stmp);
#else
    Json::Value inputJSON;
    cin >> inputJSON;
    turnID = inputJSON["responses"].size();
    for(int i = 0; i < turnID; i++) {
        request.push_back(inputJSON["requests"][i].asString());
        response.push_back(inputJSON["responses"][i].asString());
    }
    request.push_back(inputJSON["requests"][turnID].asString());
#endif

    if(turnID < 2) {
        response.push_back("PASS");
    } else {
        int itmp, myPlayerID, quan;
        ostringstream sout;
        istringstream sin;
        sin.str(request[0]);
        sin >> itmp >> myPlayerID >> quan;
        sin.clear();
        sin.str(request[1]);
        for(int j = 0; j < 5; j++) sin >> itmp;
        for(int j = 0; j < 13; j++) {
            sin >> stmp;
            hand.push_back(stmp);
        }
        for(int i = 2; i < turnID; i++) {
            sin.clear();
            sin.str(request[i]);
            sin >> itmp;
            if(itmp == 2) {
                sin >> stmp;
                hand.push_back(stmp);
                sin.clear();
                sin.str(response[i]);
                sin >> stmp >> stmp;
                hand.erase(find(hand.begin(), hand.end(), stmp));
            }
        }
        sin.clear();
        sin.str(request[turnID]);
        sin >> itmp;
        if(itmp == 2) {
            random_shuffle(hand.begin(), hand.end());
            sout << "PLAY " << *hand.rbegin();
            hand.pop_back();
        } else {
            sout << "PASS";
        }
        response.push_back(sout.str());
    }

#if SIMPLEIO
    cout << response[turnID] << endl;
#else
    Json::Value outputJSON;
    outputJSON["response"] = response[turnID];
    cout << outputJSON << endl;
#endif
    return 0;
}
```

```
// 国标麻将（Chinese Standard Mahjong）样例程序
// 随机策略
// 作者：ybh1998
// 游戏信息：http://www.botzone.org/games#Chinese-Standard-Mahjong

#include <iostream>
#include <string>
#include <sstream>
#include <vector>
#include <algorithm>

#ifdef _BOTZONE_ONLINE
#include "jsoncpp/json.h"
#else
#include <json/json.h>
#endif

#define SIMPLEIO 0
//由玩家自己定义，0表示JSON交互，1表示简单交互。

using namespace std;

vector<string> request, response;
vector<string> hand;

int main()
{
    int turnID;
    string stmp;
#if SIMPLEIO
    cin >> turnID;
    turnID--;
    getline(cin, stmp);
    for(int i = 0; i < turnID; i++) {
        getline(cin, stmp);
        request.push_back(stmp);
        getline(cin, stmp);
        response.push_back(stmp);
    }
    getline(cin, stmp);
    request.push_back(stmp);
#else
    Json::Value inputJSON;
    cin >> inputJSON;
    turnID = inputJSON["responses"].size();
    for(int i = 0; i < turnID; i++) {
        request.push_back(inputJSON["requests"][i].asString());
        response.push_back(inputJSON["responses"][i].asString());
    }
    request.push_back(inputJSON["requests"][turnID].asString());
#endif

    if(turnID < 2) {
        response.push_back("PASS");
    } else {
        int itmp, myPlayerID, quan;
        ostringstream sout;
        istringstream sin;
        sin.str(request[0]);
        sin >> itmp >> myPlayerID >> quan;
        sin.clear();
        sin.str(request[1]);
        for(int j = 0; j < 5; j++) sin >> itmp;
        for(int j = 0; j < 13; j++) {
            sin >> stmp;
            hand.push_back(stmp);
        }
        for(int i = 2; i < turnID; i++) {
            sin.clear();
            sin.str(request[i]);
            sin >> itmp;
            if(itmp == 2) {
                sin >> stmp;
                hand.push_back(stmp);
                sin.clear();
                sin.str(response[i]);
                sin >> stmp >> stmp;
                hand.erase(find(hand.begin(), hand.end(), stmp));
            }
        }
        sin.clear();
        sin.str(request[turnID]);
        sin >> itmp;
        if(itmp == 2) {
            random_shuffle(hand.begin(), hand.end());
            sout << "PLAY " << *hand.rbegin();
            hand.pop_back();
        } else {
            sout << "PASS";
        }
        response.push_back(sout.str());
    }

#if SIMPLEIO
    cout << response[turnID] << endl;
#else
    Json::Value outputJSON;
    outputJSON["response"] = response[turnID];
    cout << outputJSON << endl;
#endif
    return 0;
}
```


## 复式赛制介绍


### 简介

IJCAI2020麻将比赛采用瑞士轮加复式赛赛制。每匹配到的4位选手将进行4副牌墙的对比，每副牌墙将进行24盘比赛，故一共进行96盘比赛（24盘比赛为IJCAI2020比赛规则设置，在2020程设比赛中此值为4，详情见首页补充说明的下载链接内容）。具体来说，4副牌墙的圈风依次指定为东南西北，每副牌墙进行24盘比赛意味着4位选手的座次安排为全排列。积分规则按“一副一比”，也即每副牌墙进行24盘并将这24盘的小分累加，将得到1个累加分，根据累加分进行排名，从高到低依次得到4/3/2/1的排名分。故每次匹配，选手将得到4个排名分。最后，选手的排名分进行累加，并得到最终的比赛名次。假如总排名分有相同，则比较所有小分的累加和。

这种方式相对地削弱了手牌好坏对选手得分的影响。不同选手对同一手牌的不同处理，会导致牌局多样变化，这种变化亦能以得分的形式表现出来。复式国标麻将有效降低随机性，同样的对局数可以更有效的反映牌手及队伍的水平，排名说服力更强。


### 与传统国标的不同

复式国标麻将，大体在国标规则的基础下，有下列规则不同：


#### 用牌

复式国标麻将使用136张麻将牌，不包含8张花牌。注：在上文的request格式表中，有关补花的命令格式在此设置下弃用。


#### 定座

每局开始前，系统自动给选手分配风位。


#### 圈风及门风

参赛bot为4的倍数，如不到4的倍数，我们将以样例程序作为补齐人数的bot。比赛开始分别分配在正方形桌面的东南西北4个风位。
每次匹配中由于会对4个bot的座次进行全排列，保证4个bot分别打每副牌的4个风位。每次匹配为4圈（东南西北），每圈进行24盘（全排列）。


#### 牌墙及初始手牌

牌墙为随机生成，平均分成4份，每份为34张，作为指定座次（风位）的牌墙。初始手牌按座次牌墙指定。bot被分配到哪个座次，就拥有那个座次的牌墙，不能从其他牌墙中摸牌。


#### 摸牌

每次摸牌时，选手需从自己牌墙中顺序摸取一张。杠牌时，仍从自己牌墙中顺序摸取一张，而不是牌墙末尾。由于已经去掉花牌，所以不会有补花。


#### 荒牌

当有一人牌墙为空时，其上家打出一张牌后，其他几家不能吃碰杠。如无人和牌，本盘记为荒牌。


#### 海底捞月

当有一人牌墙为空时，其上家打出一张牌后，其他几家不能吃碰杠。如有人和牌，则记为海底捞月；否则，记为荒牌。


#### 妙手回春

当有一人牌墙为空时，其上家摸牌后，如果和牌，则记为妙手回春；否则，记为荒牌。


#### 计分规则

采用排名分累加的方式作为最后的计分，排名分则是根据小分累加的方式进行。过程为：

按照“一副一比”的规则，一副牌墙比出一个排名分，从高到低依次为4/3/2/1，每匹配到的4位选手将进行4副牌墙的对比，故最后会得到4个排名分。4副牌墙的对应圈风分别记为东南西北，每副牌墙将进行24盘比赛，也即4位选手座次全排列。一盘比赛为Botzone上的一个游戏桌，小分即为一盘比赛的结果分。

最后，将选手的排名分进行累加，得到最终的比赛名次。



---

## Bot


- 1 何为Bot
- 2 运行环境
- 3 支持的语言

3.1 针对 Python 多文件上传的提示
3.2 针对 C++ 多文件上传的提示
- 4 提供的运行库
- 5 交互

5.1 资源和时间限制
5.2 交互格式
5.3 JSON交互

5.3.1 Bot 得到的输入
5.3.2 Bot 应该给出的输出


5.4 简化交互

5.4.1 Bot 得到的输入
5.4.2 样例输入
5.4.3 Bot 应该给出的输出
5.4.4 样例输出


5.5 JSON交互的样例程序
- 6 长时运行

6.1 启用方法
6.2 启用后会发生什么
6.3 需要连续运行多个回合时
6.4 调试


- 3.1 针对 Python 多文件上传的提示
- 3.2 针对 C++ 多文件上传的提示


- 5.1 资源和时间限制
- 5.2 交互格式
- 5.3 JSON交互

5.3.1 Bot 得到的输入
5.3.2 Bot 应该给出的输出
- 5.4 简化交互

5.4.1 Bot 得到的输入
5.4.2 样例输入
5.4.3 Bot 应该给出的输出
5.4.4 样例输出
- 5.5 JSON交互的样例程序


- 5.3.1 Bot 得到的输入
- 5.3.2 Bot 应该给出的输出


- 5.4.1 Bot 得到的输入
- 5.4.2 样例输入
- 5.4.3 Bot 应该给出的输出
- 5.4.4 样例输出


- 6.1 启用方法
- 6.2 启用后会发生什么
- 6.3 需要连续运行多个回合时
- 6.4 调试


## 何为Bot

Bot是Botzone上用户提交的程序，具有一定的人工智能，可以根据已有的游戏规则跟其他的Bot或人类玩家进行对抗。


## 运行环境

Botzone的评测机均为运行Ubuntu 16.04的x86-64架构虚拟机，且仅提供一个可用CPU核。

目前平台可以运行多线程程序，但是由于运行在单核环境下，因此并不会带来性能收益。

Bot可以读写用户存储空间下的文件。详情请在Botzone上点击头像菜单，选择“管理存储空间”进行了解。


## 支持的语言

Bot可以用以下语言编写：


- C/C++（平台上编译时会定义 _BOTZONE_ONLINE 宏）
- Java
- JavaScript
- C# (Mono)
- python2
- python3
- Pascal


### 针对 Python 多文件上传的提示

请参考以下链接：

http://blog.ablepear.com/2012/10/bundling-python-files-into-stand-alone.html

(如果无法访问，请参考BundleMultiPython)

简单来说，就是把python文件打包成zip，并在zip根目录额外包含一个__main__.py作为入口点，然后上传整个zip作为python源码。

注意：数据文件请不要打包，而是使用账户菜单里的“用户存储空间”功能上传，然后在程序中使用'data'路径访问。


### 针对 C++ 多文件上传的提示

请使用该工具：https://github.com/vinniefalco/Amalgamate。

该工具会将若干C++源代码文件合并成一个文件。


## 提供的运行库


- C/C++: 提供 JSONCPP（#include "jsoncpp/json.h"）、 nlohmann/json（#include "nlohmann/json.hpp"）、 Eigen（#include "Eigen/xx"）
 “带很多库”版的编译器里，提供 tensorflow_cc、libtorch (1.5.0) 库，以及 libboost 和 libopenblas，不过要注意如果选择了这个编译器，那么编译用到的 JSONCPP 会是最新版，和 Botzone 提供的稍有不同。
- Java: 提供 JSON.simple
- C#: 提供 Newtonsoft.Json
- python(2/3): 均提供 numpy, scipy, CPU 下的 TensorFlow、theano、pytorch(0.4.0，python 3.6 除外) 和 mxnet(0.12.0), 以及 keras(2.1.6)、lasagne、scikit-image 和 h5py
python 3.6 不支持 theano 和 lasagne
python 3.6 的 pytorch 版本是 1.8.0
python 3.6 的 mxnet 版本是 1.4.0


- “带很多库”版的编译器里，提供 tensorflow_cc、libtorch (1.5.0) 库，以及 libboost 和 libopenblas，不过要注意如果选择了这个编译器，那么编译用到的 JSONCPP 会是最新版，和 Botzone 提供的稍有不同。


- python 3.6 不支持 theano 和 lasagne
- python 3.6 的 pytorch 版本是 1.8.0
- python 3.6 的 mxnet 版本是 1.4.0

如果有更新库或者增加库的需求，请到讨论区发帖提醒管理员。


## 交互

Bot的每次生命周期均为一次输入、一次输出，可以参见右图，每次输入会包括该Bot以往跟平台的所有交互内容。交互格式为单行JSON或简化交互。

新增：现在已经支持“长时运行”模式，可以通过输出特定指令来保持Bot的持续运行，减少冷启动的开销。详见#长时运行。

因此，Bot的程序运行流程应当是：


- 启动程序
- 从平台获取以往的交互内容和最新输入
- 根据获得的交互内容（request + response）进行计算
根据以往自己的输入（request）输出（response）恢复局面到最新状态
根据本次输入（request）给出本次的决策输出
- 输出结果以及保存信息
- 关闭程序


- 根据以往自己的输入（request）输出（response）恢复局面到最新状态
- 根据本次输入（request）给出本次的决策输出


### 资源和时间限制

如果没有特别指出，每次运行，平台都要求程序在 1秒 内结束、使用的内存在 256 MB 内。

每场对局，每个 Bot 的第一回合的时间限制会放宽到原来的两倍。

#长时运行模式下，除了程序刚刚启动的回合，其他回合的时间限制请参看提交 Bot 的页面。

由于不同语言运行效率有别，我们对不同语言的时限也有不同的调整。


- C/C++：1倍
- Java：3倍
- C#：6倍
- JavaScript：2倍
- python：6倍
- Pascal：1倍


### 交互格式

为了照顾初学者，交互形式有两种：JSON交互和简化交互。

提示：为了限制对局 Log 的大小，data、globaldata 域作为对局的中间变量，在对局结束后将不会被存入 Log 中。

如果希望能进行调试，请使用 debug 域，该域会在对局结束后仍保留在 Log 中。


### JSON交互

使用这种交互，可能需要在自己的程序中增加JSON处理相关的库，具体请参见下方样例程序的说明。


#### Bot 得到的输入

实际上Bot得到的输入是单行紧凑的JSON。

```
{
 	"requests" : [
 		"Judge request in Turn 1", // 第 1 回合 Bot 从平台获取的信息（request），具体格式依游戏而定
 		"Judge request in Turn 2", // 第 2 回合 Bot 从平台获取的信息（request），具体格式依游戏而定
 		...
 	],
 	"responses" : [
 		"Bot response in Turn 1", // 第 1 回合 Bot 输出的信息（response），具体格式依游戏而定
 		"Bot response in Turn 2", // 第 2 回合 Bot 输出的信息（response），具体格式依游戏而定
 		...
 	],
 	"data" : "saved data", // 上回合 Bot 保存的信息，最大长度为100KB【注意不会保留在 Log 中】
 	"globaldata" : "globally saved data", // 来自上次对局的、Bot 全局保存的信息，最大长度为100KB【注意不会保留在 Log 中】
 	"time_limit" : "", // 时间限制
 	"memory_limit" : "" // 内存限制
 }
```

```
{
 	"requests" : [
 		"Judge request in Turn 1", // 第 1 回合 Bot 从平台获取的信息（request），具体格式依游戏而定
 		"Judge request in Turn 2", // 第 2 回合 Bot 从平台获取的信息（request），具体格式依游戏而定
 		...
 	],
 	"responses" : [
 		"Bot response in Turn 1", // 第 1 回合 Bot 输出的信息（response），具体格式依游戏而定
 		"Bot response in Turn 2", // 第 2 回合 Bot 输出的信息（response），具体格式依游戏而定
 		...
 	],
 	"data" : "saved data", // 上回合 Bot 保存的信息，最大长度为100KB【注意不会保留在 Log 中】
 	"globaldata" : "globally saved data", // 来自上次对局的、Bot 全局保存的信息，最大长度为100KB【注意不会保留在 Log 中】
 	"time_limit" : "", // 时间限制
 	"memory_limit" : "" // 内存限制
 }
```


#### Bot 应该给出的输出

Bot应当给出的是单行紧凑的JSON。

```
{
 	"response" : "response msg", // Bot 此回合的输出信息（response）
 	"debug" : "debug info", // 调试信息，将被写入log，最大长度为1KB
 	"data" : "saved data" // Bot 此回合的保存信息，将在下回合输入【注意不会保留在 Log 中】
 	"globaldata" : "globally saved data" // Bot 的全局保存信息，将会在下回合输入，对局结束后也会保留，下次对局可以继续利用【注意不会保留在 Log 中】
 }
```

```
{
 	"response" : "response msg", // Bot 此回合的输出信息（response）
 	"debug" : "debug info", // 调试信息，将被写入log，最大长度为1KB
 	"data" : "saved data" // Bot 此回合的保存信息，将在下回合输入【注意不会保留在 Log 中】
 	"globaldata" : "globally saved data" // Bot 的全局保存信息，将会在下回合输入，对局结束后也会保留，下次对局可以继续利用【注意不会保留在 Log 中】
 }
```


### 简化交互

使用这种交互，只需使用标准输入输出按行操作即可。


#### Bot 得到的输入


1. 你的 Bot 首先会收到一行，其中只有一个数字 n，表示目前是第 n 回合（从 1 开始）。
2. 接下来，是 2 * n - 1 条信息，这些信息由 Bot 从平台获取的信息（request）与 Bot 以前每个回合输出的信息（response）交替组成。
 从 1 开始计数，(1 <= i < n)
 第 2 * i - 1 条信息为第 i 回合 Bot 从平台获取的信息（request），共 n - 1 条
 第 2 * i 条信息为 Bot 在第 i 回合输出的信息（response），共 n - 1 条
 最后一条，即第 2 * n - 1 条信息，为当前回合 Bot 从平台获取的新信息（request）
 每条信息可能是 1 行，也可能是多行，具体格式依游戏而定。
 你的 Bot 需要根据以上信息，推演出当前局面，并给出当前局面下的最好决策。
3. 接下来是data，一行 Bot 上回合保存的信息，最大长度为100KB【注意不会保留在 Log 中】。
4. 接下来是globaldata，一行或多行 Bot 上回合或上次对局保存的全局信息，最大长度为100KB【注意不会保留在 Log 中】。
 可以认为 data 行之后的所有内容都是 globaldata，直到文件结尾。


- 从 1 开始计数，(1 <= i < n)
 第 2 * i - 1 条信息为第 i 回合 Bot 从平台获取的信息（request），共 n - 1 条
 第 2 * i 条信息为 Bot 在第 i 回合输出的信息（response），共 n - 1 条
 最后一条，即第 2 * n - 1 条信息，为当前回合 Bot 从平台获取的新信息（request）
- 每条信息可能是 1 行，也可能是多行，具体格式依游戏而定。
- 你的 Bot 需要根据以上信息，推演出当前局面，并给出当前局面下的最好决策。


- 第 2 * i - 1 条信息为第 i 回合 Bot 从平台获取的信息（request），共 n - 1 条
- 第 2 * i 条信息为 Bot 在第 i 回合输出的信息（response），共 n - 1 条
- 最后一条，即第 2 * n - 1 条信息，为当前回合 Bot 从平台获取的新信息（request）


- 可以认为 data 行之后的所有内容都是 globaldata，直到文件结尾。


#### 样例输入

```
3
第一回合游戏信息（request），即 Bot 当时得到的输入
第一回合 Bot 的输出（response）
第二回合游戏信息
第二回合 Bot 的输出
第三回合游戏信息
Bot 上回合保存了这句话作为data！
Bot 上次运行程序保存了这句话作为globaldata！
```


#### Bot 应该给出的输出

你的 Bot 应当输出四段数据，以换行符隔开。


1. 首先是本回合你的 Bot 做出的决策，请按照游戏要求输出。一定只占一行。
2. 接下来是debug，一行用于回放时候进行调试的信息，最大长度为1KB【注意会保留在 Log 中】。
3. 接下来是data，一行 Bot 本回合想保存的信息，将在下回合输入，最大长度为100KB【注意不会保留在 Log 中】。
4. 接下来是globaldata，一行或多行 Bot 想保存的全局信息，将会在下回合输入，对局结束后也会保留，最大长度为100KB【注意不会保留在 Log 中】。


#### 样例输出

```
本回合 Bot 的输出
Bot 这回合想保存这句话作为debug，到时候回放看！
Bot 这回合保存了这句话作为data，下回合想用！
Bot 这次运行程序保存了这句话作为globaldata，以后想用！
```


### JSON交互的样例程序

以下给出C++、C#、Java、python和JavaScript的JSON交互样例程序：

C++

本地编译的方式请查看 JSONCPP。

```
#include <iostream>
 #include <string>
 #include <sstream>
 #include "jsoncpp/json.h" // C++编译时默认包含此库
 
 using namespace std;
 
 int main()
 {
 	// 读入JSON
 	string str;
 	getline(cin, str);
 	Json::Reader reader;
 	Json::Value input;
 	reader.parse(str, input);
 
 	// 分析自己收到的输入和自己过往的输出，并恢复状态
 	string data = input["data"].asString(); // 该对局中，以前该Bot运行时存储的信息
 	int turnID = input["responses"].size();
 	for (int i = 0; i < turnID; i++)
 	{
 		istringstream in(input["requests"][i].asString()),
 			out(input["responses"][i].asString());
 
 		// 根据这些输入输出逐渐恢复状态到当前回合
 	}
 
 	// 看看自己本回合输入
 	istringstream in(input["requests"][turnID].asString());
 
 	// 做出决策存为myAction
 
 	// 输出决策JSON
 	Json::Value ret;
 	ret["response"] = myAction;
 	ret["data"] = myData; // 可以存储一些前述的信息，在整个对局中使用
 	Json::FastWriter writer;
 	cout << writer.write(ret) << endl;
 	return 0;
 }
```

```
#include <iostream>
 #include <string>
 #include <sstream>
 #include "jsoncpp/json.h" // C++编译时默认包含此库
 
 using namespace std;
 
 int main()
 {
 	// 读入JSON
 	string str;
 	getline(cin, str);
 	Json::Reader reader;
 	Json::Value input;
 	reader.parse(str, input);
 
 	// 分析自己收到的输入和自己过往的输出，并恢复状态
 	string data = input["data"].asString(); // 该对局中，以前该Bot运行时存储的信息
 	int turnID = input["responses"].size();
 	for (int i = 0; i < turnID; i++)
 	{
 		istringstream in(input["requests"][i].asString()),
 			out(input["responses"][i].asString());
 
 		// 根据这些输入输出逐渐恢复状态到当前回合
 	}
 
 	// 看看自己本回合输入
 	istringstream in(input["requests"][turnID].asString());
 
 	// 做出决策存为myAction
 
 	// 输出决策JSON
 	Json::Value ret;
 	ret["response"] = myAction;
 	ret["data"] = myData; // 可以存储一些前述的信息，在整个对局中使用
 	Json::FastWriter writer;
 	cout << writer.write(ret) << endl;
 	return 0;
 }
```

C#

本地编译的方式请查看 Newtonsoft.Json。

```
using System;
using Newtonsoft.Json;

struct InputData
{
	public dynamic[] // 类型请根据具体游戏决定
		requests, // 从平台获取的信息集合
		responses; // 自己曾经输出的信息集合
	public string
		data, // 该对局中，上回合该Bot运行时存储的信息
		globaldata; // 来自上次对局的、Bot全局保存的信息
	public int time_limit, memory_limit;
}

struct OutputData
{
	public dynamic response; // 此回合的输出信息
	public string
		debug, // 调试信息，将被写入log
		data, // 此回合的保存信息，将在下回合输入
		globaldata; // Bot的全局保存信息，将会在下回合输入，对局结束后也会保留，下次对局可以继续利用
}

class Program
{
	static void Main(string[] args) // 请保证文件中只有一个类定义了Main方法
	{
		// 将输入解析为结构体
		var input = JsonConvert.DeserializeObject<InputData>(
			Console.ReadLine()
		);

		// 分析自己收到的输入和自己过往的输出，并恢复状态
		int turnID = input.responses.Length;
		for (int i = 0; i < turnID; i++)
		{
			dynamic inputOfThatTurn = input.requests[i], // 当时的输入
 				outputOfThatTurn = input.responses[i]; // 当时的输出

			// 根据这些输入输出逐渐恢复状态到当前回合
		}

		// 看看自己本回合输入
		dynamic inputOfCurrentTurn = input.requests[turnID];

		// 做出决策存为myAction

		// 输出决策JSON
		OutputData output = new OutputData();
		output.response = myAction;
		output.debug = "hhh";
		Console.WriteLine(
			JsonConvert.SerializeObject(output)
		);
	}
}
```

```
using System;
using Newtonsoft.Json;

struct InputData
{
	public dynamic[] // 类型请根据具体游戏决定
		requests, // 从平台获取的信息集合
		responses; // 自己曾经输出的信息集合
	public string
		data, // 该对局中，上回合该Bot运行时存储的信息
		globaldata; // 来自上次对局的、Bot全局保存的信息
	public int time_limit, memory_limit;
}

struct OutputData
{
	public dynamic response; // 此回合的输出信息
	public string
		debug, // 调试信息，将被写入log
		data, // 此回合的保存信息，将在下回合输入
		globaldata; // Bot的全局保存信息，将会在下回合输入，对局结束后也会保留，下次对局可以继续利用
}

class Program
{
	static void Main(string[] args) // 请保证文件中只有一个类定义了Main方法
	{
		// 将输入解析为结构体
		var input = JsonConvert.DeserializeObject<InputData>(
			Console.ReadLine()
		);

		// 分析自己收到的输入和自己过往的输出，并恢复状态
		int turnID = input.responses.Length;
		for (int i = 0; i < turnID; i++)
		{
			dynamic inputOfThatTurn = input.requests[i], // 当时的输入
 				outputOfThatTurn = input.responses[i]; // 当时的输出

			// 根据这些输入输出逐渐恢复状态到当前回合
		}

		// 看看自己本回合输入
		dynamic inputOfCurrentTurn = input.requests[turnID];

		// 做出决策存为myAction

		// 输出决策JSON
		OutputData output = new OutputData();
		output.response = myAction;
		output.debug = "hhh";
		Console.WriteLine(
			JsonConvert.SerializeObject(output)
		);
	}
}
```

JavaScript

```
// 初始化标准输入流
var readline = require('readline');
process.stdin.resume();
process.stdin.setEncoding('utf8');

var rl = readline.createInterface({
	input: process.stdin
});
  
rl.on('line', function (line) {
	// 解析读入的JSON
	var input = JSON.parse(line);
	var data = input.data; // 该对局中，以前该Bot运行时存储的信息

	// 分析自己收到的输入和自己过往的输出，并恢复状态
	for (var i = 0; i < input.responses.length; i++) {
		var myInput = input.requests[i], myOutput = input.responses[i];
		// 根据这些输入输出逐渐恢复状态到当前回合
	}

	// 看看自己本回合输入
	var currInput = input.requests[input.requests.length - 1];

	var myAction = {}, myData = {};

	// 作出决策并输出
	process.stdout.write(JSON.stringify({
		response: myAction,
		data: myData // 可以存储一些前述的信息，在整个对局中使用
	}));

	// 退出程序
	process.exit(0);
});
```

```
// 初始化标准输入流
var readline = require('readline');
process.stdin.resume();
process.stdin.setEncoding('utf8');

var rl = readline.createInterface({
	input: process.stdin
});
  
rl.on('line', function (line) {
	// 解析读入的JSON
	var input = JSON.parse(line);
	var data = input.data; // 该对局中，以前该Bot运行时存储的信息

	// 分析自己收到的输入和自己过往的输出，并恢复状态
	for (var i = 0; i < input.responses.length; i++) {
		var myInput = input.requests[i], myOutput = input.responses[i];
		// 根据这些输入输出逐渐恢复状态到当前回合
	}

	// 看看自己本回合输入
	var currInput = input.requests[input.requests.length - 1];

	var myAction = {}, myData = {};

	// 作出决策并输出
	process.stdout.write(JSON.stringify({
		response: myAction,
		data: myData // 可以存储一些前述的信息，在整个对局中使用
	}));

	// 退出程序
	process.exit(0);
});
```

python

仅提供python3的样例。

```
import json

# 解析读入的JSON
full_input = json.loads(input())
if "data" in full_input:
    my_data = full_input["data"]; # 该对局中，上回合该Bot运行时存储的信息
else:
    my_data = None

# 分析自己收到的输入和自己过往的输出，并恢复状态
all_requests = full_input["requests"]
all_responses = full_input["responses"]
for i in range(len(all_responses)):
    myInput = all_requests[i] # i回合我的输入
    myOutput = all_responses[i] # i回合我的输出
    # TODO: 根据规则，处理这些输入输出，从而逐渐恢复状态到当前回合
    pass

# 看看自己最新一回合输入
curr_input = all_requests[-1]

# TODO: 作出决策并输出
my_action = { "x": 1, "y": 1 }

print(json.dumps({
    "response": my_action,
    "data": my_data # 可以存储一些前述的信息，在该对局下回合中使用，可以是dict或者字符串
}))
```

```
import json

# 解析读入的JSON
full_input = json.loads(input())
if "data" in full_input:
    my_data = full_input["data"]; # 该对局中，上回合该Bot运行时存储的信息
else:
    my_data = None

# 分析自己收到的输入和自己过往的输出，并恢复状态
all_requests = full_input["requests"]
all_responses = full_input["responses"]
for i in range(len(all_responses)):
    myInput = all_requests[i] # i回合我的输入
    myOutput = all_responses[i] # i回合我的输出
    # TODO: 根据规则，处理这些输入输出，从而逐渐恢复状态到当前回合
    pass

# 看看自己最新一回合输入
curr_input = all_requests[-1]

# TODO: 作出决策并输出
my_action = { "x": 1, "y": 1 }

print(json.dumps({
    "response": my_action,
    "data": my_data # 可以存储一些前述的信息，在该对局下回合中使用，可以是dict或者字符串
}))
```

Java

本地编译的方式请查看 JSON.simple。

```
import java.util.*;
import org.json.simple.JSONValue; // Java 库中自动包含此库

class Main { // 注意！！类名""必须""为 Main，且不要有package语句，但上传的 java 代码文件名可以任意
	static class SomeClass {
		// 如果要定义类，请使用 static inner class
	}
	public static void main(String[] args) {
		String input = new Scanner(System.in).nextLine();
		Map<String, List> inputJSON = (Map) JSONValue.parse(input);
		// 下面的 TYPE 为单条 response / request 类型，有较大可能为 Map<String, Long> 或 String
		List<TYPE> requests = inputJSON.get("requests");
		List<TYPE> responses = inputJSON.get("responses");
		for (TYPE rec : requests) {
			// 处理一下
		}
		for (TYPE rec : responses) {
			// 再处理一下
		}
		// 这边运算得出一个 output，注意类型也为 TYPE
		Map<String, TYPE> outputJSON = new HashMap();
		outputJSON.put("response", output);
		System.out.print(JSONValue.toJSONString(outputJSON));
	}
}
```

```
import java.util.*;
import org.json.simple.JSONValue; // Java 库中自动包含此库

class Main { // 注意！！类名""必须""为 Main，且不要有package语句，但上传的 java 代码文件名可以任意
	static class SomeClass {
		// 如果要定义类，请使用 static inner class
	}
	public static void main(String[] args) {
		String input = new Scanner(System.in).nextLine();
		Map<String, List> inputJSON = (Map) JSONValue.parse(input);
		// 下面的 TYPE 为单条 response / request 类型，有较大可能为 Map<String, Long> 或 String
		List<TYPE> requests = inputJSON.get("requests");
		List<TYPE> responses = inputJSON.get("responses");
		for (TYPE rec : requests) {
			// 处理一下
		}
		for (TYPE rec : responses) {
			// 再处理一下
		}
		// 这边运算得出一个 output，注意类型也为 TYPE
		Map<String, TYPE> outputJSON = new HashMap();
		outputJSON.put("response", output);
		System.out.print(JSONValue.toJSONString(outputJSON));
	}
}
```


## 长时运行

如果希望Bot在回合结束后不必退出，从而避免每次重启Bot造成的额外开销（比如神经网络的初始化过程），则可以选择此种交互方式，模式请参见右图。

该模式尚在测试中，可能会有非预期的问题，敬请留意，如果遇到问题请联系管理员或者在讨论区发帖，谢谢支持！


### 启用方法

要开启长时运行模式，需要至少先使用正常的交互方式完成一个回合。（可以认为该回合的输入是只有一个request的输入，且是有限行的）

在该回合结束时，先按前文所述的正常交互方式输出，再通过标准输出方式输出如下内容的一行（注意前后均应有换行符）：

```
>>>BOTZONE_REQUEST_KEEP_RUNNING<<<
```

建议在输出后清空标准输出缓冲区（如fflush(stdout);、cout << flush;、sys.stdout.flush()等）。

输出该行，意味着本回合的输入结束。


### 启用后会发生什么

在Botzone收到如上输入后，会认为本回合Bot已经完成输出，因此会将Bot强制休眠（发送SIGSTOP信号到进程组），在下一回合轮到自己的时候再唤醒（发送SIGCONT到进程组）。

休眠Bot的过程由于延迟，很可能不是在输出那行内容以后立刻进行，而是在Bot等待下回合输入的过程中进行。需要卡时的话，请注意在input()或getline()等操作后再开始卡时。

开启该模式后：


- 下一回合收到的输入将只有一回合的游戏信息（request），不再有历史数据（之前回合的request和response）和data等信息
- debug、data、globaldata功能将失效（请勿在使用简单IO时，向globaldata中存储不定多行的数据）
- Bot的输出格式无须变化
- 在回合之间还未轮到自己时，如果Bot在占用CPU（比如多线程提前计算一些信息），这部分计算所使用的CPU时间会计入下回合的时间，因此请不要这么做


### 需要连续运行多个回合时

如果需要维持该模式，此后每一回合输出response之后，都需要输出上述的一行命令。

如果在开启该模式后，某一回合输出完成后没有输出上述的一行，那么平台就不知道Bot的输出是否结束，因此超时。

如果你的需求十分特殊，希望在连续运行多个回合后关闭程序，然后再启动，那么你需要在希望关闭程序的回合自行了断（在输出决策response后，不输出上述命令，而是直接退出）。这样，下一回合你的程序会像传统运行方式一样，重新启动。


### 调试

开启该模式后，Botzone提供的对局Log里的“玩家输入”会做出相应变化，可以直接从平台复制进行调试。

不过要注意，该调试方法会假设你的Bot的输出和平台上完全一致（即相同局面下平台上和本地调试的决策均相同），如果你的Bot有随机成分，那么将无法正确进行调试。

为了回溯到某一个回合，你的Bot调试时可能需要重新计算之前回合的动作，因此可能会演算很久。

