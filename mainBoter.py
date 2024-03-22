#coding=utf-8
from const import *
import websocket, ssl, requests, re, threading, traceback, sys, os, random

# 名字提纯
def namePure(name: str) -> str: return name.replace("@", "").replace(" ", "")
# 内容转换
def textPure(text: str) -> str: return text.replace("\\~", "~").replace("~", " ")
# Markdown人名
def nameMd(name: str) -> str: return name.replace("_", "\\_")
# 获取沙雕小设计
def randomDesign(num: int=1) -> str:
    full = []
    if num > 10:
        return "最多一次性获取10个(〃｀ 3′〃)"
    elif num < 1:
        return "最少获取一个(〃｀ 3′〃)"
    for i in range(num):
        item = random.choice(designs["items"])
        const = random.choice(designs["constraints"])
        prepend = random.choice(designs["prepend"])
        if const[-1] == "的":
            full.append(f"{prepend}{const}{item}")
            continue
        full.append( f"{const}{prepend}{item}")
    return "，\n".join(full)
# 分解质因数！这是我的数学极限了，呜呜……
def getPrime(i, factors) -> list:
    if i == 1: return ["没法分解啊啊啊啊(+﹏+)"]
    for x in range(2, int(i**0.5 + 1)):
        if i % x == 0:
            factors.append(str(x))
            getPrime(int(i / x), factors)
            return factors
    factors.append(str(i))
    return factors
# r来r去
def rollTo1(maxNum: int=1000) -> str:
    road =  []
    while True:
        ran=random.randint(1, maxNum)
        road.append(str(ran))
        if ran != 1: maxNum = ran
        else: break
    return f"{'，'.join(road)}：{len(road)}"
def hashByCode(code: str) -> str:
    try: return "，".join(data[code]).replace("_", "\\_")
    except: return "不存在这个hash码(◐_◑)"
def hashByName(name: str, now: bool=False) -> str:
    if now:
        try: return hashByCode(userHash[name])
        except: return "此人当前不在线( ⊙ o ⊙ )"
    else:
        l = []
        for i in data.values():
            if name in i:
                text = "，".join(i)
                l.append(text.replace("_", "\\_"))
        l = list(set(l))
        for i, v in enumerate(l):
            l[i] = f"{i+1}\\. "+l[i]
        result = "\n".join(l) or "没有这个名字！"
        return result if len(result) < 2048 else "太长了几把"
def seenAt(text: str, type_: str) -> str:
    if type_ in ["nick", "trip"]:
        user = lastSaw[type_].get(text)
        if user:
            ltime = user["time"]
            result = f"最后一次见到{type_}为{text}的用户是在{ftime(ltime)}（距现在{timeDiff(intTime() - ltime)}）\n"
            msg = user["msg"]
            if msg is not None:
                result += f"他说了：{msg}"
            else:
                result += "他加入了。"
            return result
        else:
            return "此人还没有光顾此处的样子(◐_◑)"
    else:
        return "格式错误(+﹏+)"
# 一天不涩涩，癫痫发作作
def colorPic(params = None) -> str:
    url = "https://api.lolicon.app/setu/v2"
    if params: url += "?" + params
    setu = requests.get(url).json()
    if setu.get("data"): setu = setu["data"][0]
    else: return "出错啦，请检查参数或紫砂"
    # 过滤离谱关键词
    tags = [i for i in setu["tags"] if not re.search("[乳魅内尻屁胸]", i)]
    url = setu["urls"]["original"]
    title = setu["title"]
    author = setu["author"]
    return f"![]({url})\n标题：{title}\n标签：{', '.join(tags)}\n作者：{author}"
# 随便搞搞
def getLetter() -> str:
    response = requests.get("https://www.thiswebsitewillselfdestruct.com/api/get_letter").json()
    if response["code"] == "200": return response["body"]
    else: return "出错啦，请稍后再试(◐_◑)"
# 结束
def endBomb():
    bombs[5], bombs[2], bombs[1] = False, 0, []
    bombs[6], bombs[7] = bombs[3], bombs[4]
# 判断数字与更新
def bombRule(context, num=None):
    old = bombs[1][bombs[2]]
    if old == nick:
        num = random.randint(bombs[6], bombs[7])
    if bombs[6] > num or bombs[7] < num:
        context.appText(f"不符合规则，数字必须在{bombs[6]}到{bombs[7]}之间！（含两边）")
    else:
        if bombs[0] > num:
            bombs[6] = num + 1
        elif bombs[0] < num:
            bombs[7] = num - 1
        else:
            endBomb()
            context.appText(f"炸弹炸到{old}了！")
            return
        bombs[2] = (bombs[2] + 1) % len(bombs[1])
        player = bombs[1][bombs[2]]
        context.appText(f"{old}没有踩中！\n现在炸弹范围为{bombs[6]}到{bombs[7]}，轮到@{player} 了！")
        if player == nick:
            bombRule(context)
# 扑克有关
def landonwer(context, sender: str): 
    pokers[5] = sender
    pokers[6] = False
    pokers[10] = pokers[2]
    pokers[2] = pokers[7].index(pokers[5])
    pokers[1][sender] += pokers[4]
    pokers[1][sender].sort(key=lambda x: SORT[x])
    cards = " ".join(pokers[1][sender])
    context.appText(f"{' '.join(pokers[4])}是底牌，{sender}是地主。\n游戏开始，地主@{sender} 先出，发送==@{nick} 扑克规则==可以查看出牌规则哦；")
    context.appText(f"/w {sender} 以下是您的牌：{cards}")
def passLand(context, sender: str):
    pokers[2] = (pokers[2]+1)%3
    if pokers[2] == pokers[10]:
        landonwer(context, pokers[7][pokers[2]])
def sameLen(seq) -> bool:
    try:
        length = len(seq[0])
        for i in seq[1:]:
            if len(i) != length or len(set(i)) != 1 or not seq[0] in SORT: return False
        return True
    except: return False
def endPoker():
    pokers[0], pokers[1], pokers[2] = False, {}, 0
    pokers[4], pokers[9], pokers[11] = [], {}, None
def pkReply(context, msg: str, sender: str):
    msg = msg.upper()
    # 叫牌阶段
    if pokers[6]:
        if msg[:2] == "1 ":
            try:
                point = int(msg[2])
                if not point in [1, 2, 3]: raise Exception
                elif point == 3:
                    landonwer(chat, sender)
                else:
                    for i in pokers[9].values():
                        if i >= point:
                            context.appText("叫的数字必须比前面的大！")
                            break
                    else:
                        pokers[9][sender] = point
                        pokers[10] = pokers[2]
                        passLand(chat, sender)
                        context.appText(f"{sender}叫出了{point}点，轮到@{pokers[7][pokers[2]]} ")
            except: context.appText("命令错误，请重新确认后再试;")
        elif msg[:1] == "0":
            passLand(chat, sender)
            context.appText(f"{sender}不叫，轮到@{pokers[7][pokers[2]]} ")
        else: context.appText("命令错误，啊啊啊")
    # 出牌阶段
    else:
        # 跳过
        if msg == ".":
            pokers[2] = (pokers[2]+1)%3
            if pokers[2] == pokers[10]:
                pokers[11] = None
                context.appText(f"所有玩家都要不起，@{pokers[7][pokers[2]]} 继续出牌。")
            else:
                context.appText(f"{sender}跳过，轮到@{pokers[7][pokers[2]]} 。")
        elif msg == "CHECK":
            context.appText(f"/w {sender} 上家出的牌是：{pokers[11]}\n以下是您的牌：{' '.join(pokers[1][sender])}")
        else:
            senderCards = pokers[1][sender]
            # 本轮第一发
            if pokers[11] is None:
                # 单张
                if msg in SORT and msg in senderCards:
                    senderCards.remove(msg)
                # 对子或三张或四张
                elif re.match(r"^[2-9AHJQK]\*[234]$", msg):
                    if senderCards.count(msg[0])>=int(msg[-1]):
                        for _ in range(int(msg[-1])): senderCards.remove(msg[0])
                    else: context.appText("牌数不足！")
                # 顺子
                elif re.match(r"^[3-9AHJQK]-[3-9AHJQK]$", msg):
                    start, end = CARDS.index(msg[0]), CARDS.index(msg[-1])
                    if (end-start) >= 4:
                        for i in CARDS[start:end+1]:
                            if not i in senderCards:
                                context.appText("拥有的牌不够！")
                        for i in CARDS[start:end+1]:
                            senderCards.remove(i)
                    else: context.appText("顺子最少五个！")
                # 三带一、三带二
                elif re.match(r"^[2-9AHJQK]\*3 [2-9AHJQK大小]{1,2}$", msg):
                    mult = len(msg.split()[1])
                    if msg[-1] != msg[0]:
                        condition = senderCards.count(msg[0])>=int(msg[2]) and senderCards.count(msg[-1])>=mult
                    # 不会真有人出6*3 6这种的吧
                    else:
                        condition = senderCards.count(msg[0])>=(int(msg[2])+mult)
                    if condition:
                        for i in range(int(msg[2])): senderCards.remove(msg[0])
                        for i in range(mult): senderCards.remove(msg[-1])
                    else: context.appText("牌数不足！")
                # 双顺、三顺
                elif re.match(r"^[3-9AHJQK]-[3-9AHJQK]\*[23]$", msg):
                    start, end, mult = CARDS.index(msg[0]), CARDS.index(msg[2]), int(msg[-1])
                    if (end-start) >= (4-mult):
                        for i in CARDS[start:end+1]:
                            if senderCards.count(i) < mult:
                                context.appText("拥有的牌不够！")
                        for i in CARDS[start:end+1]:
                            for _ in range(mult): senderCards.remove(i)
                    else: context.appText("牌数不够，三顺最少两个，双顺最少三个;")
                # 四带二
                elif re.match(r"([2-9AHJQK])\*4 (?!.*?\1)(?:([2-9AHJQK])\2 ([2-9AHJQK])\3|[2-9AHJQK大小] [2-9AHJQK大小])$", msg):
                    array = msg.split()[1:]
                    if senderCards.count(msg[0])==4 and senderCards.count(array[0])>=len(array[0]) and senderCards.count(array[1])>=len(array[1]):
                        for _ in range(4): senderCards.remove(msg[0])
                        for i in "".join(array): senderCards.remove(i)
                    else: context.appText("牌不够，;;;")
                # 飞机
                elif re.match(r"^[3-9AHJQK]-[3-9AHJQK]\*3 $", msg[:6]):
                    start, end = CARDS.index(msg[0]), CARDS.index(msg[2])
                    if (end-start) < 1: context.appText("牌数不够;")
                    else:
                        array = msg[6:].split(" ")
                        if sameLen(array) and len(array) == (end-start+1):
                            for i in CARDS[start:end+1]:
                                if senderCards.count(i) < 3: context.appText("牌数不足;;;;")
                                if i in array or i+i in array: context.appText("别搞")
                            for i in array:
                                if senderCards.count(i) < len(i): context.appText("牌数不足;;;;")
                            for i in CARDS[start:end+1]:
                                for _ in range(3): senderCards.remove(i)
                            for i in array: senderCards.remove(i)
                        else: context.appText("不符合规则！")
                # 6
                elif msg == "王炸":
                    if not ("大" in senderCards and "小" in senderCards): context.appText("牌数不足！")
                    else:
                        senderCards.remove("大")
                        senderCards.remove("小")
                else: context.appText("命令不正确或牌数不足，请查看规则后重试;")
            else:
                last = pokers[11]
                # 单张
                if last in SORT and msg in SORT and msg in senderCards:
                    if SORT[msg] <= SORT[last]: context.appText(f"你的牌没有{last}大！")
                    senderCards.remove(msg)
                # 对子或三张或四张
                elif re.match(r"^.\*.$", last) and re.match(rf"^[2-9AHJQK]\*{last[-1]}$", msg):
                    if senderCards.count(msg[0])>=int(msg[-1]):
                        if SORT[msg[0]] <= SORT[last[0]]: context.appText(f"你的牌没有{last}大！")
                        for _ in range(int(msg[-1])): senderCards.remove(msg[0])
                    else: context.appText("牌数不足！")
                # 顺子
                elif re.match(r"^.-.$", last) and re.match(r"^[3-9AHJQK]-[3-9AHJQK]$", msg):
                    start, end = CARDS.index(msg[0]), CARDS.index(msg[-1])
                    lstart, lend = CARDS.index(last[0]), CARDS.index(last[-1])
                    if (end-start) != (lend-lstart): context.appText("牌数不符！")
                    elif lstart >= start: context.appText(f"你的牌没有{last}大！")
                    for i in CARDS[start:end+1]:
                        if not i in senderCards:
                            context.appText("拥有的牌不够！")
                    for i in CARDS[start:end+1]:
                        senderCards.remove(i)
                # 三带一、三带二
                elif re.match(r"^.\*3 .{1,2}$", last) and re.match(r"^[2-9AHJQK]\*3 [2-9AHJQK大小]{1,2}$", msg):
                    mult = len(msg.split()[1])
                    if msg[-1] != msg[0]:
                        condition = senderCards.count(msg[0])>=int(msg[2]) and senderCards.count(msg[-1])>=mult
                    # 不会真有人出6*3 6这种的吧
                    else:
                        condition = senderCards.count(msg[0])>=(int(msg[2])+mult)
                    if not condition: context.appText("牌数不足！")
                    elif SORT[last[0]] >= SORT[msg[0]]: context.appText(f"你的牌没有{last}大！")
                    elif len(msg.split()[1]) != len(last.split()[1]) or SORT[msg[0]] <= SORT[last[0]]: context.appText("牌型不符合！")
                    for i in range(int(msg[2])): senderCards.remove(msg[0])
                    for i in range(mult): senderCards.remove(msg[-1])
                # 双顺、三顺
                elif re.match(r".-.\*.$", last) and re.match(rf"^[3-9AHJQK]-[3-9AHJQK]\*{last[-1]}$", msg):
                    start, end, mult = CARDS.index(msg[0]), CARDS.index(msg[2]), int(msg[-1])
                    lstart, lend = CARDS.index(last[0]), CARDS.index(last[2])
                    if (end-start) != (lend-lstart): context.appText("牌数不符！")
                    elif lstart >= start: context.appText(f"你的牌没有{last}大！")
                    for i in CARDS[start:end+1]:
                        if senderCards.count(i) < mult:
                            context.appText("拥有的牌不够！")
                    for i in CARDS[start:end+1]:
                        for _ in range(mult): senderCards.remove(i)
                # 四带二
                elif re.match(r".\*4 .*", last) and re.match(r"([2-9AHJQK])\*4 (?!.*?\1)(?:([2-9AHJQK])\2 ([2-9AHJQK])\3|[2-9AHJQK大小] [2-9AHJQK大小])$", msg):
                    array = msg.split()[1:]
                    larray = last.split()[1:]
                    if senderCards.count(msg[0])==4 and senderCards.count(array[0])>=len(array[0]) and senderCards.count(array[1])>=len(array[1]):
                        if len(larray[-1]) != len(array[-1]): context.appText("牌型不符！")
                        elif SORT[last[0]] >= SORT[msg[0]]: context.appText(f"你的牌没有{last}大！")
                        for _ in range(4): senderCards.remove(msg[0])
                        for i in "".join(array): senderCards.remove(i)
                    else: context.appText("牌不够，;;;")
                # 飞机
                elif re.match(r"^.-.\*3 $", last[:6]) and re.match(r"^[3-9AHJQK]-[3-9AHJQK]\*3 $", msg[:6]):
                    start, end = CARDS.index(msg[0]), CARDS.index(msg[2])
                    lstart, lend = CARDS.index(last[0]), CARDS.index(last[2])
                    if (end-start) != (lend-lstart): context.appText("牌数不符！")
                    elif SORT[last[0]] >= SORT[msg[0]]: context.appText(f"你的牌没有{last}大！")
                    else:
                        array = msg[6:].split(" ")
                        if sameLen(array) and len(array) == (end-start+1):
                            for i in CARDS[start:end+1]:
                                if senderCards.count(i) < 3: context.appText("牌数不足;;;;")
                                if i in array or i+i in array: context.appText("别搞")
                            for i in array:
                                if senderCards.count(i) < len(i): context.appText("牌数不足;;;;")
                            for i in CARDS[start:end+1]:
                                for _ in range(3): senderCards.remove(i)
                            for i in "".join(array): senderCards.remove(i)
                        else: context.appText("不符合规则！")
                # 炸弹
                elif re.match(r"^[2-9AHJQK]\*4$", msg) and last != "王炸":
                    if senderCards.count(msg[0])<int(msg[-1]): context.appText("牌数不足！")
                    for _ in range(int(msg[-1])): senderCards.remove(msg[0])
                # 6
                elif msg == "王炸":
                    if not ("大" in senderCards and "小" in senderCards): context.appText("牌数不足！")
                    else:
                        senderCards.remove("大")
                        senderCards.remove("小")
                else: context.appText("牌型不符或牌数不足，请查看规则后重试;")
            if not context.text:
                pokers[11] = msg
                pokers[10] = pokers[2]
                pokers[2] = (pokers[2]+1)%3
                context.appText(f"{sender}出了{msg}，轮到@{pokers[7][pokers[2]]} 。")
                if not senderCards:
                    if sender == pokers[5]: context.appText("地主获胜！")
                    else: context.appText("农民获胜！")
                    endPoker()
                elif len(senderCards) < 4: context.appText(f"{sender}只剩{len(senderCards)}张牌了！")
# UNO
def initialize_card():
    unos[3] = []
    for j in "红黄蓝绿":
        for i in range(1, 10):
            unos[3].append(j + str(i))
            unos[3].append(j + str(i))
        for i in ["+2", "禁", "转向"]:
            unos[3].append(j + i)
            unos[3].append(j + i)
        unos[3].append(j + "0")
    for i in range(4):
        unos[3].append("+4")
        unos[3].append("变色")
    return unos[3]
def endUno():
    unos[0] = False
    unos[1] = []
    unos[2] = []
def no_card(context, num):
    if len(unos[3]) < num:
        initialize_card()
        for i in unos[2]:
            for j in i:
                unos[3].remove(j)
        context.appText("牌没了，已重新洗牌。")
def log(text):
    with open(f"logs/{sysList[3]}.txt", "a+", encoding="utf8") as f:
        f.write(text+"\n")
def getrans() -> int:
    return random.randint(1, 134)
def chess(context, sender: str, msg: str):
    res = re.search(r"^([ABCDEFGHIJ])([123456789]) ([ABCDEFGHIJ])([123456789])$", msg.upper())
    if CCList[3][1] and sender == CCList[1] and res:
        res = res.groups()
        old, new = [ord(res[0])-65, int(res[1])-1], [ord(res[2])-65, int(res[3])-1]
        goingChess, moveChess = CCList[4][new[0], new[1]], CCList[4][old[0], old[1]]
        if moveChess != "&ensp;":
            use = CCList[4][min(old[0], new[0])+1:max(old[0], new[0]), old[1]]
            use2 = CCList[4][old[0], min(old[1], new[1])+1:max(old[1], new[1])]
            if (not CCList[3].index(sender) and not goingChess in RED and moveChess in RED) or (CCList[3].index(sender) and not goingChess in BLACK and moveChess in BLACK):                    
                if moveChess == RED[5] and (old[0] > 4 and abs(old[1] - new[1]) == 1 and old[0] == new[0] or new == [old[0]+1, old[1]]):
                        move(old, new, RED[5])
                elif moveChess == BLACK[5] and (old[0] < 5 and abs(old[1] - new[1]) == 1 and old[0] == new[0] or new == [old[0]-1, old[1]]):
                        move(old, new, BLACK[5])
                elif moveChess in [RED[6], BLACK[6]]:
                    if goingChess != "&ensp;":
                        if (new[0] == old[0] and len(use2[use2!="&ensp;"]) == 1) or (new[1] == old[1] and len(use[use!="&ensp;"]) == 1):
                            move(old, new, moveChess)
                        else: context.appText("不符合行棋规则")
                    elif (new[0] == old[0] and not len(use2[use2!="&ensp;"])) or (new[1] == old[1] and not len(use[use!="&ensp;"])):
                        move(old, new, moveChess)
                    else: context.appText("不符合行棋规则")
                elif (moveChess in [RED[0], BLACK[0]]) and ((new[0] == old[0] and not len(use2[use2!="&ensp;"])) or ((new[1] == old[1]) and not len(use[use!="&ensp;"]))):
                        move(old, new, moveChess)
                elif (moveChess in [RED[1], BLACK[1]]) and ((abs(old[0]-new[0]) == 2 and abs(old[1]-new[1]) == 1 and CCList[4][int(old[0]-(old[0]-new[0])/2), old[1]] == "&ensp;") or (abs(old[1]-new[1]) == 2 and abs(old[0]-new[0]) == 1 and CCList[4][old[0], int(old[1]-(old[1]-new[1])/2)] == "&ensp;")):
                        move(old, new, moveChess)
                elif moveChess == RED[2] and (abs(old[0]-new[0]) == 2 and abs(old[1]-new[1]) == 2 and CCList[4][int(old[0]-(old[0]-new[0])/2), int(old[1]+(old[1]-new[1])/2)] == "&ensp;" and new[0] < 5) :
                        move(old, new, RED[2])
                elif moveChess == BLACK[2] and (abs(old[0]-new[0]) == 2 and abs(old[1]-new[1]) == 2 and CCList[4][int(old[0]-(old[0]-new[0])/2), int(old[1]+(old[1]-new[1])/2)] == "&ensp;" and new[0] > 4) :
                        move(old, new, BLACK[2])
                elif moveChess == RED[4] and (new[0] in [0, 1, 2]) and (new[1] in [3, 4, 5]) and ((old[0]==new[0] and abs(old[1]-new[1])==1) or (old[1]==new[1] and abs(old[0]-new[0])==1)):
                        move(old, new, RED[4])
                elif moveChess == BLACK[4] and (new[0] in [7, 8, 9]) and (new[1] in [3, 4, 5]) and ((old[0]==new[0] and abs(old[1]-new[1])==1) or (old[1]==new[1] and abs(old[0]-new[0])==1)):
                        move(old, new, BLACK[4])
                elif moveChess == RED[3] and (new[0] in [0, 1, 2]) and (new[1] in [3, 4, 5]) and abs(old[0]-new[0])==1 and abs(old[1]-new[1])==1:
                        move(old, new, RED[3])
                elif moveChess == BLACK[3] and (new[0] in [7, 8, 9]) and (new[1] in [3, 4, 5]) and abs(old[0]-new[0])==1 and abs(old[1]-new[1])==1:
                        move(old, new, BLACK[3])
                else: context.appText(f"不符合{moveChess}的行棋规则")
            else: context.appText("不能吃自己也不能用别人的棋子！")
        else: context.appText("不能挪动空气！")
    elif msg == "加入游戏":
        if not CCList[3][0]:
            CCList[3][0] = sender
            CCList[4] = CINIT.copy()
            context.appText("游戏创建好了，快找人来加入吧！")
        elif sender == CCList[3][0]:
            context.appText("你已经，加入过了哦~")
        elif CCList[3][1]:
            context.appText("游戏已经开始了，等到下局吧~")
        else:
            CCList[0] = True
            CCList[3][1] = sender
            _sendBoard()
            context.appText(RULE)
            CCList[1] = CCList[3][0]
            context.appText(f"@{CCList[3][0]} 先手执红（绿？）（上方，简体），@{CCList[3][1]} 后手执黑（下方，繁体）。开始了哦~")
    elif msg == "结束游戏" and sender in CCList[3]:
        if not CCList[2]:
            CCList[2] = sender
            context.appText("结束游戏需要双方都发送。")
        elif CCList[2] != sender:
            _endGame()
            context.appText(f"啊，虽然有点儿遗憾不过，既然{sender}说结束了的话就结束吧……发送开始游戏可以再次开始哦~")
            CCList[2] = None
        else: context.appText("结束游戏需要双方都发送。")
    elif msg == "象棋":
        context.appText(CCMENU.replace("sender", sender))
    elif msg == "提问":
        context.appText(random.choice(RANDLIS[5]).replace("sender", sender))
    elif msg == "数字炸弹":
        context.appText(BOMBMENU.replace("sender", sender))
    elif msg == "斗地主":
        context.appText(POKERMENU.replace("sender", sender))
    elif msg == "扑克规则":
        context.appText(POKERRULE.replace("sender", sender))
    elif msg == "结束p" and sender in pokers[7]:
        endPoker()
        context.appText("唔，结束了;;;;")
def move(context, old, new, chess):
    if CCList[4][new[0], new[1]] in [RED[4], BLACK[4]]:
        context.appText(f"@{CCList[1]} 获胜！恭喜！")
        _endGame()
    else:
        now = CCList[1]
        CCList[1] = CCList[3][0] if CCList[1] == CCList[3][1] else CCList[3][1]
        for i in CCList[4][:,3:6]:
            if (BLACK[4] in i) and (RED[4] in i) and set(i[list(i).index(RED[4])+1:list(i).index(BLACK[4])]) == {"&ensp;"}:
                context.appText(f"@{CCList[1]} 获胜！恭喜！")
                _endGame()
                break
        else:
            CCList[4][old[0], old[1]] = "&ensp;"
            CCList[4][new[0], new[1]] = chess
            _sendBoard()
            context.appText(f"{now}挪动了{chr(old[0]+65)}{old[1]+1}的{chess}，轮到@{CCList[1]}")
def _endGame():
    CCList[1] = None
    CCList[3] = [None, None]
    CCList[0] = False
    CCList[4] = CINIT.copy()
def _sendBoard(context):
    mae = CLOLUMN+[f"|{n}|"+ "|".join(i) +"|" for i, n in zip(CCList[4], LETTERS)]
    context.appText("\n".join(mae))

class Context:
    def __init__(self, returns: bool=False) -> dict:
        """type: whisper, chat, same"""
        self.returns = returns
        self.text = []
    def appText(self, text: str, type_: str="same", **kwargs):
        self.text.append(dict({type_: text}, **kwargs))
    def returns(self):
        self.returns = True
def whisback(chat, sender):
    def init(msg):
        chat.whisper(sender, msg)
    return init
def premade(msg, sender, trip, type_):
    context = Context()
    log(f"{sender}：{msg}")
    nowSaw[sender]["words"] += 1
    nowSaw[sender]["msg"] = msg

    lastSaw["nick"][sender]["time"] = intTime()
    lastSaw["nick"][sender]["msg"] = msg
    if trip:
        lastSaw["trip"][trip]["time"] = intTime()
        lastSaw["trip"][trip]["msg"] = msg
    writeJson("userData.json", userData)

    if sender == nick: context.returns = True
    else:
        if 1 < len(msg) < 1024:
            meaningful.append(msg)
        if not trip in whiteList:
            hash_ = userHash[sender]
            frisked = frisk(hash_, 0.9+len(msg)/256)
            if frisked == "warn":
                context.appText(f"@{sender} Warning!!!")
            elif frisked == "limit":
                records[hash_]["score"] = threshold/2
                records[hash_]["warned"] = False
                context.appText(f"~kick {sender}", "chat")
        if not sender in ignored:
            mined = msg[:1024]
            cache = re.sub(r"(?:\n|^) *(~~~|```)[\s\S]*?\n *\1 *(?=\n|$)", "", mined)
            matched = re.search(r"(~~~|```)", cache)
            if matched:
                mined = "\n" + mined + "\n" + matched.group()
            allMsg.append(f"{nameMd(sender)}：{mined}")
            if len(allMsg) > 377: del allMsg[0]
        if userHash[sender] in blackList or sender in blackName: context.returns = True
    return context

def mainfunc(msg, sender, trip, type_):
    context = Context()
    command = msg[:6]
    rans = getrans()

    if msg[0] == PREFIX:
        command = msg[1:5]
        if command == "hash":
            context.appText(hashByName(namePure(msg[6:])))
        elif command == "hasn":
            context.appText(hashByName(namePure(msg[6:]), True))
        elif command == "code":
            context.appText(hashByCode(msg[6:]))
        elif command == "colo":
            color = userColor.get(namePure(msg[6:]))
            if color is None: context.appText("没有这个用户(╰_╯)#")
            else:
                if color: context.appText(color)
                else: context.appText("该用户还没有设置颜色(￢_￢)")
        elif command == "left":
            lis = msg.split()
            length = len(lis)
            if length < 3:
                context.appText("命令不正确！")
            elif lis[1] == "*trip":
                trip = lis[2]
                text = " ".join(lis[3:])
                if trip in userTrip.values():
                    context.appText(f"{trip}在线着呢，为什么还要留言啊喂~")
                elif not re.search(r"^[a-zA-Z+-/]{6}$", lis[2]):
                    context.appText("识别码不合法！")
                elif not text:
                    context.appText("信息不能为空哦uwu")
                else:
                    leftMsg[ftime(time.time())] = [sender, trip, text, "trip"]
                    context.appText(f"@{sender}, #{trip}将会在加入时收到你的留言！~~如果那时我还在的话~~")
            else:
                name = namePure(lis[1])
                text = " ".join(lis[2:])
                if name in onlineUsers:
                    context.appText(f"{name}在线着呢，为什么还要留言啊喂~")
                elif not re.search(r"^@?\w{1,24}$", lis[1]):
                    context.appText("昵称不合法！")
                elif not text:
                    context.appText("信息不能为空哦uwu")
                else:
                    leftMsg[ftime(time.time())] = [sender, name, text, "nick"]
                    context.appText(f"@{sender}, {nameMd(name)}将会在加入时收到你的留言！~~如果那时我还在的话~~")
            writeJson("userData.json", userData)
        elif command == "peep":
            try:
                array = msg.split(" ")
                want_peep = int(array[1])
                if want_peep == 0: raise ValueError
                elif len(array)==2: 
                    if want_peep < 0: res = "\n\n".join(allMsg[:-want_peep])
                    else: res = "\n\n".join(allMsg[-want_peep:])
                    if len(res) >= 2048: context.appText(f"/w {sender} 一次查看的消息太多了，请把数字改小一点再试！")
                    else: context.appText(f"/w {sender} 懒得写提示语了：\n"+ res)
                elif len(array)>2: context.appText(f"/w {sender} 懒得写提示语了：\n"+ "\n\n".join(allMsg[int(array[1]):int(array[2])]))
                else: raise ValueError
            except ValueError: context.appText(f"/w {sender} 然而peep后面需要一个非零整数")
        elif command == "welc":
            if not msg[4:]:
                if not trip in userData["welText"]: context.appText("你还没有设置欢迎语！")
                else:
                    del userData["welText"][trip]
                    writeJson("userData.json", userData)
                    context.appText(f"为识别码{trip}清除欢迎语成功了！")
            elif not trip: context.appText("您当前还没有识别码，请重进并在昵称输入界面使用==昵称#密码==设置一个！")
            else:
                userData["welText"][trip] = msg[6:]
                writeJson("userData.json", userData)
                context.appText(f"为识别码{trip}设置欢迎语成功了！")
        elif command == "last":
            if sender in userData["lastText"] and userData["lastText"][sender][0] != trip:
                context.appText(f"已经有人为{sender}设置过留言了，请换一个名字！")
            elif trip:
                userData["lastText"][sender] = [trip, msg[6:]]
                writeJson("userData.json", userData)
                context.appText(f"为{sender}({trip})设置留言成功了！记得及时清除哦！")
            else: context.appText("您当前还没有识别码，请重启并在昵称输入界面使用==昵称#密码==设置一个！")
        elif command == "lost":
            name, dic = namePure(msg[6:]), userData["lastText"]
            if name in dic:
                context.appText(f"以下是{name}({dic[name][0]})的留言：\n{dic[name][1]}")
            else: context.appText("该用户还没有设置留言~")
        elif command == "unlo":
            name, dic = namePure(msg[6:]), userData["lastText"]
            if name in dic:
                if trip == dic[name][0] or trip in whiteList:
                    del dic[name]
                    writeJson("userData.json", userData)
                    context.appText("留言已删除，感谢您的使用！")
                else: context.appText(f"您的识别码与被清除者不同！正确识别码应为{dic[name][0]}！")
            else: context.appText("此用户还没有设置留言~")
        elif command == "prim":
            try:
                digit = msg[6:19]
                eq = "\\*".join(getPrime(int(digit), []))
                context.appText(f"{digit}={eq}")
            except ValueError: context.appText("请输入一个***正整数***啊啊啊啊(￢_￢)")
        elif command == "rand":
            try:
                digit = int(msg[6:])
                context.appText(randomDesign(digit))
            except ValueError: context.appText("参数必须是1到10之间的正整数(￣_,￣ )")
        elif command == "repl":
            if type_ == "whisper": return
            array = msg.split(" ")
            if len(array) < 3: context.appText(f"命令错误，请使用`{PREFIX}repl 提问 回答`的格式(‾◡◝)")
            else:
                ans = " ".join(array[2:])
                quest = textPure(array[1])
                if not quest in answer: answer[quest] = [ans]
                else: answer[quest].append(ans)
                context.appText(f"添加成功(☆▽☆)")
                writeJson("answer.json", answer)
        elif command == "seen":
            arr = msg.split(" ")
            length = len(arr)
            if length < 2: context.appText("参数呢！！！")
            elif length == 2:
                context.appText(seenAt(namePure(arr[1]), "nick"))
            elif arr[1] == "*trip":
                context.appText(seenAt(namePure(arr[2]), "trip"))
        elif command == "look":
            name = msg[6:]
            if name in nowSaw:
                saw = nowSaw[name]
                result = seenAt(namePure(name), "nick") + "\n"
                joined = intTime() - saw["joined"]
                if saw["words"]:
                    times = joined / 60 / saw["words"]
                    freq = f"每{times:.1f}分钟一次"
                else:
                    freq = "无发言记录"
                result += f"他于{timeDiff(joined)}前加入。\n发言频率：{freq}"
            else:
                result = "查无此人ლ(´ڡ`ლ)"
            context.appText(result)
        elif command == "fuck":
            if type_ == "whisper": return
            poorer = namePure(msg[6:])
            if not poorer: poorer = random.choice(onlineUsers)
            if poorer == sender: context.appText(f"喜欢自卫吗，{sender}？")
            else: context.appText(random.choice(FUCKS).replace("fucker", sender).replace(
                "poor", poorer).replace("passer", random.choice(onlineUsers)))
        elif command == "setu":
            if not sysList[0]: context.appText("你说得对，但是不可以涩涩。")
            else: context.appText(colorPic(msg[6:]))
        elif command == "help":
            cmd = msg[6:]
            if not msg[4:]: context.appText("叫我的话发==菜单==哦~")
            elif not cmd in COMMANDS:
                context.appText("暂时没有此功能或懒得写了¯\\\\\\_(ツ)_/¯", "whisper")
            else:
                context.appText("我是占位符awa\n" + COMMANDS[cmd], "whisper")
    elif msg.strip() == f"@{nick}":
        if rans > 129: context.appText(random.choice(RANDLIS[1]).replace("sender", sender))
        else: context.appText(random.choice(RANDLIS[0]).replace("sender", sender))
    elif msg.startswith(f"@{nick} "):
        chess(context, sender, msg[len(nick)+2:])
    elif msg[0] == "r":
        if type_ == "whisper": return context
        if command == "rprime":
            digit = msg[7:20]
            try:
                dig=random.randint(1, int(digit))
                if dig > 0:
                    eq = "\\*".join(getPrime(dig, []))
                    context.appText(f"{dig}={eq}")
                else: raise ValueError
            except ValueError as e:
                digit = str(random.randint(1, 1000))
                eq = "\\*".join(getPrime(int(digit), []))
                context.appText(f"{digit}={eq}")
        elif msg == "rcolor" and trip in whiteList:
            context.appText(f"/color {hex(random.randint(0, 0xffffff))[2:]:0>6}")
            context.appText("自动变色ヽ(*。>Д<)o゜")
        elif msg == "russia":
            russian[0].append(sender)
            length = len(russian[0])
            times = russian[0].count(sender)
            if length > 3:
                if times >= length / 6 * 5:
                    context.appText("而你，…………6。")
                elif times >= length / 5 * 4:
                    context.appText("而你……故人，你会看见盛大的仪式为你准备的陵墓。")
                elif times >= length / 4 * 3:
                    context.appText("而你，我……你是真正的狂战士。")
                elif times >= length / 3 * 2:
                    context.appText("而你，我的英雄，你是真正的莽夫！")
                elif times >= length / 2:
                    context.appText("而你，我的朋友，你是真正的赌徒。")
            else:
                context.appText("而你，我的朋友，你是真正的勇士。")
    elif msg[:2] == "b " and bombs[5] and sender == bombs[1][bombs[2]]:
        if type_ == "whisper": return context
        try: num = int(msg[2:])
        except: context.appText("请输入一个整数ヾ|≧_≦|〃")
        else: bombRule(context, num)
    elif msg[:2] == "p " and pokers[0] and sender == pokers[7][pokers[2]]:
        if type_ == "whisper": return context
        pkReply(context, msg[2:], sender)
    elif msg[:6] == "bomber":
        if type_ == "whisper": return context
        if bombs[5]: context.appText("这局已经开始了，等下局吧(￣▽￣)")
        elif sender in bombs[1]:
            if msg[-1] == "t":
                bombs[1].remove(sender)
                context.appText("已成功退出(‾◡◝)")
            else: context.appText("您已经加入过了(￣▽￣)")
        else:
            bombs[1].append(sender)
            context.appText("您已成功加入游戏・▽・)ノ ")
    elif msg[:5] == "poker":
        if type_ == "whisper": return context
        if pokers[0]: context.appText("这局已经开始了，等下局吧(￣▽￣)")
        elif sender in pokers[1]:
            if msg[-1] == "t":
                del pokers[1][sender]
                context.appText("已成功退出(‾◡◝)")
            else: context.appText("你已经加入过了(‾◡◝)")
        else:
            pokers[1][sender] = []
            if len(pokers[1]) == 3:
                # 开始
                pokers[0] = True
                pokers[7] = list(pokers[1].keys())
                pokers[3] = PINIT[:]
                # 选底牌
                for i in range(3):
                    index = random.randrange(0, len(pokers[3]))
                    pokers[4].append(pokers[3].pop(index))
                # 洗牌
                random.shuffle(pokers[3])
                # 发牌
                for i, v in enumerate(pokers[3]):
                    pokers[1][pokers[7][i%3]].append(v)
                # 整理牌、告诉牌
                for k, v in pokers[1].items():
                    v.sort(key=lambda x: SORT[x])
                    cards = " ".join(v)
                    context.appText(f"/w {k} 以下是您的牌：{cards}")
                pokers[8] = random.choice(pokers[7])
                pokers[2] = pokers[7].index(pokers[8])
                pokers[10] = pokers[2]
                context.appText(f"好的，发牌完成，随机到@{pokers[8]} 拥有地主牌{random.choice(pokers[1][pokers[8]])}，请发送`p 1 叫分`叫地主或`p 0`选择不叫。")
                pokers[6] = True
            else: context.appText("加入成功，快再找些人吧(☆▽☆)")
    elif msg == "uno":
        if unos[0]:
            context.appText("游戏已经开始了，等下一轮吧。")
        elif sender in unos[1]:
            context.appText("你已经加入了！")
        elif type_ == "whisper": return context
        else:
            unos[1].append(sender)
            context.appText(f"加入成功，现在有{len(unos[1])}人。")   
    elif msg == "开始u" and not unos[0]:
        if type_ == "whisper": return context
        if len(unos[1]) >= 2:
            unos[0] = True
            unos[3] = initialize_card()
            for i in range(len(unos[1])):
                playerCard = []
                for j in range(7):
                    addCard = random.choice(unos[3])
                    playerCard.append(addCard)
                    unos[3].remove(addCard)
                playerCard.sort()
                unos[2].append(playerCard)
                context.appText(f"这是你的牌：{playerCard}", "whisper", to=unos[1][i])
            unos[4] = random.choice(unos[1])
            while unos[5] == "+4":
                unos[5] = random.choice(unos[3])
            unos[3].remove(unos[5])
            context.appText(f"牌发完啦，{UNORULE}\n初始牌是=={unos[5]}==，请`{unos[4]}`先出！")
        else:
            context.appText("人数不够！")
    elif msg == "结束u" and sender in unos[1] and unos[0]:
        if type_ == "whisper": return context
        endUno()
        context.appText("结束了...")
    elif msg[:2] == "u " and sender == unos[4]:
        if type_ == "whisper": return context
        msgList = msg.split(" ")
        card = msgList[1]
        id_ = unos[1].index(sender)
        nextid = (id_ + 1) % len(unos[1])
        next2id_ = (id_ + 2) % len(unos[1])
        if card == "check":
            context.appText(f"现在牌面上的牌是=={unos[5]}==，这是你的牌：{'，'.join(unos[2][id_])}", "whisper")
        else:
            if card == ".":
                addCard = random.choice(unos[3])
                unos[3].remove(addCard)
                if addCard[0] == unos[5][0] or addCard[1:] == unos[5][1:] or unos[5] == "变色":
                    unos[5] = addCard
                    if addCard[1:] == "禁":
                        unos[4] = unos[1][next2id_]
                        context.appText(f"`{sender}`补到了{addCard}并将其打出，`{unos[1][nextid]}`跳过1轮，轮到`{unos[4]}`！")
                    elif addCard[1:] == "+2":
                        unos[4] = unos[1][next2id_]
                        no_card(context, 2)
                        for i in range(2):
                            addCard_ = random.choice(unos[3])
                            unos[2][nextid].append(addCard_)
                            unos[3].remove(addCard_)
                        context.appText(f"`{sender}`补到了=={addCard}==并将其打出，`{unos[1][nextid]}`加2张，轮到`{unos[4]}`！")
                        context.appText(f"你新增了2张牌，这是你现在的牌：{'，'.join(unos[2][nextid])}。", "whisper", to=unos[1][nextid])
                    elif addCard[1:] == "转向":
                        unos[1].reverse()
                        unos[2].reverse()
                        unos[4] = unos[1][(-id_)%len(unos[1])]
                        id_ = (-id_-1)%len(unos[1])
                        context.appText(f"`{sender}`补到了{addCard}并将其打出，==顺序转换==，轮到`{unos[4]}`！")
                    else:
                        unos[4] = unos[1][nextid]
                        context.appText(f"`{sender}`补到了=={addCard}==并将其打出，轮到`{unos[4]}`！")
                else:
                    unos[4] = unos[1][nextid]
                    unos[2][id_].append(addCard)
                    context.appText(f"`{sender}`补了一张牌，轮到`{unos[4]}`！")
                    context.appText(f"你新增了1张牌，这是你现在的牌： {'，'.join(unos[2][id_])}。", "whisper")
            elif not card in unos[2][id_]:
                context.appText("你没有那张牌！")
                return context
            elif card == "+4":
                for i in unos[2][id_]:
                    if i[0] == unos[5][0]:
                        context.appText("不符合规则！")
                        break
                else:
                    if len(msgList) < 3:
                        context.appText("缺少参数！")
                    elif not msgList[2] in "红黄蓝绿":
                        context.appText("参数错误！")
                    else:
                        unos[5] = msgList[2] + "?"
                        unos[4] = unos[1][next2id_]
                        no_card(context, 4)
                        for i in range(4):
                            addCard = random.choice(unos[3])
                            unos[2][nextid].append(addCard)
                            unos[3].remove(addCard)
                        context.appText(f"`{sender}`出了+4（王牌），`{unos[1][nextid]}`加四张，颜色变为=={msgList[2]}==，轮到`{unos[4]}`！")
                        context.appText(f"你新增了4张牌，这是你现在的牌：{'，'.join(unos[2][nextid])}。", "whisper", to=unos[1][nextid])
            elif card == "变色":
                if len(msgList) < 3:
                    context.appText("缺少参数！")
                elif msgList[2] not in "红黄蓝绿":
                    context.appText("参数错误！")
                else:
                    unos[4] = unos[1][nextid]
                    unos[5] = msgList[2] + "?"
                    context.appText(f"`{sender}`出了变色牌，颜色变为=={msgList[2]}==，轮到`{unos[4]}`！")
            elif card[0] == unos[5][0] or card[1:] == unos[5][1:] or unos[5] == "变色":
                unos[5] = card
                if card[1:] == "禁":
                    unos[4] = unos[1][next2id_]
                    context.appText(f"`{sender}`出了{card}，`{unos[1][nextid]}`跳过1轮，轮到`{unos[4]}`！")
                elif card[1:] == "+2":
                    unos[4] = unos[1][next2id_]
                    no_card(context, 2)
                    for i in range(2):
                        addCard = random.choice(unos[3])
                        unos[2][nextid].append(addCard)
                        unos[3].remove(addCard)
                    context.appText(f"`{sender}`出了=={card}==，`{unos[1][nextid]}`加2张，轮到`{unos[4]}`！")
                    context.appText(f"你新增了2张牌，这是你现在的牌：{'，'.join(unos[2][nextid])}。", "whisper", to=unos[1][nextid])
                elif card[1:] == "转向":
                    unos[1].reverse()
                    unos[2].reverse()
                    unos[4] = unos[1][(-id_)%len(unos[1])]
                    id_ = (-id_-1)%len(unos[1])
                    context.appText(f"`{sender}`出了{card}，==顺序转换==，轮到`{unos[4]}`！")
                else:
                    unos[4] = unos[1][nextid]
                    context.appText(f"`{sender}`出了=={card}==，轮到`{unos[4]}`！")
            if card not in ["+4", "变色"]:
                context.appText("不符合规则！")
            else:
                unos[2][id_].remove(card)
                if len(unos[2][id_]) == 1:
                    context.appText(f"`{sender}`==UNO==了！！！")
                if len(unos[2][id_]) != 0:
                    no_card(context, 1)
                else:
                    endUno()
                    context.appText(f"`{sender}`获胜，游戏结束。")
    elif msg == "开始b" and not bombs[5]:
        if type_ == "whisper": return context
        if len(bombs[1]) > 1:
            bombs[5], bombs[6], bombs[7] = True, bombs[3], bombs[4]
            bombs[0] = random.randint(bombs[3], bombs[4])
            context.appText(f"炸弹已经设置好了，范围在{bombs[3]}到{bombs[4]}（包含两数）之间！\n由@{bombs[1][0]} 开始，发送==b 数字==游玩！")
            if bombs[1][0] == nick: bombRule(context)
        else: context.appText("至少需要两个人才能开始(⊙﹏⊙)")
    elif msg == "结束b" and bombs[5]:
        if type_ == "whisper": return context
        endBomb()
        context.appText("好吧好吧，结束咯_(:зゝ∠)\\_")
    elif msg == "开枪" and russian[0] and sender in russian[0]:
        if type_ == "whisper": return context
        length = len(russian[0])
        hero = random.choice(russian[0])
        if length > 7:
            context.appText("英雄们载歌载舞，歌颂着故去者的传奇。")
        elif length > 5:
            context.appText("这难得一见的盛会，将成为谁的葬礼呢。")
        elif length > 3:
            context.appText("今晚的篝火旁，将会多几分冷清呢……")
        else:
            context.appText("群星注视着英雄的陨落，大地不会忘怀。")
        context.appText("~kick " + hero)
        russian[2] = True
        russian[1] = userHash[hero]
        russian[3] = hero
    elif msg[:3] == "=菜单" or msg[:5] == "=menu":
        if msg == "=菜单":
            context.appText(f"/w {sender} {MENUMIN}")
        elif msg == "=菜单w" and trip in whiteList:
            men = "\n".join(ADMMENU)
            context.appText(f"/w {sender} {men}")
        elif msg == "=菜单~" and trip == OWNER:
            context.appText(f"/w {sender} {OWNMENU}")
        elif msg == "=menu":
            if trip == OWNER: men = "\n".join(ENGMENU+ENGMENUSSP)
            elif trip in whiteList: men = "\n".join(ENGMENU+ENGMENUSP)
            else: men = "\n".join(ENGMENU+ENGMENUFT)
        elif msg == "=menuw" and trip in whiteList:
            men = "\n".join(ENGADMMENU)
            context.appText(f"/w {sender} {men}")
        elif msg == "=menu~" and trip == OWNER:
            context.appText(f"/w {sender} {ENGOWNMENU}")
    elif msg.lower() in LINE:
        call = LINE[msg.lower()]
        if hasattr(call, "__call__"): context.appText(call())
        else: context.appText(random.choice(call).replace("sender", sender))
    # 白名单功能，阿瓦娅的VIP用户捏~
    elif msg[0] == "+" and trip in whiteList:
        # 涩涩，没有涩涩我要死了！！！
        if command == "+setu ":
            try:
                sysList[0] = int(msg[6:])
                context.appText("涩涩涩涩涩——")
            except ValueError: context.appText("你是1还是0？")
        # 小黑屋是不值得学习的！
        elif command == "+addb ":
            name = namePure(msg[6:])
            try: hash_ = userHash[name]
            except: context.appText("此人当前不在线(+﹏+)")
            else:
                if hash_ in blackList: context.appText("可惜他/她已经在咯~")
                else:
                    blackList.append(hash_)
                    writeJson("userData.json", userData)
                    context.appText("好好好，又进去了一个。")
        elif command == "+delb ":
            try: banned.remove(msg[6:])
            except: context.appText("命令错误或此人不在小黑屋~")
            else:
                writeJson("userData.json", userData)
                context.appText("删除成功！")
        elif command == "+addn ":
            try:
                name=namePure(msg[6:])
                if not name in blackName:
                    blackName.append(name)
                    writeJson("userData.json", userData)
                    context.appText("好好好，又进去了一个。")
                else: context.appText("可惜他/她已经在咯~")
            except KeyError: context.appText("可惜这人现在不在呢…(⊙＿⊙；)…")
        elif command == "+deln ":
            try:
                name=namePure(msg[6:])
                if name in blackName:
                    blackName.remove(name)
                    writeJson("userData.json", userData)
                    context.appText("删除黑名单用户成功！")
                else: context.appText("这人不在小黑屋里哦？")
            except KeyError: context.appText("可惜这人现在不在呢…(⊙＿⊙；)…")
        elif command == "+time ":
            try:
                sysList[1] = int(msg[6:])
                context.appText("好好好，如你所愿~")
            except ValueError:
                context.appText("1或者0，明白了吗~")
        elif command == "+bcol ":
            context.appText(f"/color {msg[6:]}")
            context.appText("自动变色ヽ(*。>Д<)o゜")
        elif command == "+kill ":
            arr = msg.split(" ")
            name = namePure(arr[1])
            if not name in onlineUsers: context.appText("此人当前不在线！")
            elif name == nick or userTrip[name] == OWNER: context.appText("6")
            elif arr[-1] == "-hash":
                kicked = userHash[name]
                for name, hash_ in userHash.items():
                    if hash_ == kicked:
                        context.appText(f"/w {name} "+"$\\begin{pmatrix}qaq\\\\[999999999em]\\end{pmatrix}$")
                        context.appText(f"~kick {name}")
            else:
                context.appText(f"/w {name} "+"$\\begin{pmatrix}qaq\\\\[999999999em]\\end{pmatrix}$")
                context.appText(f"~kick {name}")
        elif command == "+bans ":
            name = namePure(msg[6:])
            try: hash_ = userHash[name]
            except: context.appText("此人当前不在线(+﹏+)")
            else:
                if not hash_ in banned:
                    if name == nick or userTrip[name] == OWNER: context.appText("6")
                    else:
                        banned.append(hash_)
                        writeJson("userData.json", userData)
                        context.appText(f"/w {name} "+"$\\begin{pmatrix}qaq\\\\[999999999em]\\end{pmatrix}$")
                        context.appText(f"~kick {name}")
                else:
                    context.appText("他/她已经被封了！")
        elif command == "+uban ":
            try: banned.remove(msg[6:])
            except: context.appText("命令错误或此人不在小黑屋~")
            else:
                writeJson("userData.json", userData)
                context.appText("删除成功！")
        elif command == "+setb ":
            sp = msg.split()
            try: mini, maxi = int(sp[1]), int(sp[2])
            except: context.appText("输入格式有误，请在0setb 后面用空格隔开，输入最小值和最大值两个整数！")
            else:
                if (maxi-mini)<1: context.appText("两数的差别过小，请重新设置！")
                else:
                    bombs[3], bombs[4] = mini, maxi
                    context.appText("设置成功！")
        elif trip == OWNER:
            if command == "+addw ":
                name = msg[6:12]
                if not name in whiteList:
                    whiteList.append(name)
                    writeJson("userData.json", userData)
                    context.appText("添加特殊服务的家伙咯╰(￣▽￣)╮")
                else: context.appText("你要找的人并不在这里面(๑°ㅁ°๑)‼")
            elif command == "+delw ":
                name = msg[6:12]
                if name in whiteList:
                    whiteList.remove(name)
                    writeJson("userData.json", userData)
                    context.appText("删除白名单用户成功๑乛◡乛๑")
                else: context.appText("你要找的人并不在这里面( ˃᷄˶˶̫˶˂᷅ )")
            elif command == "+igno ":
                name = namePure(msg[6:])
                if not name in ignored:
                    ignored.append(name)
                    writeJson("userData.json", userData)
                    context.appText(f"忽略{name}的消息咯~")
                else: context.appText("已经在了~")
            elif command == "+unig ":
                name = namePure(msg[6:])
                if name in ignored:
                    ignored.remove(name)
                    writeJson("userData.json", userData)
                    context.appText(f"恢复记录{name}的消息成功了~")
                else: context.appText("好消息是他/她的信息本来就被记录着~")
            elif command == "+chkr ":
                array = msg.split()
                if len(array) >= 2:
                    ans = answer.get(textPure(array[1]))
                    if ans:
                        if len(array) == 2:
                            arr = []
                            for i, v in enumerate(ans): arr.append(f"{i}：{v[:50]}")
                            col = "\n".join(arr)
                            context.appText(f"/w {sender} 此问题的回答有：\n{col}")
                        else:
                            try: context.appText(f"/w {sender} {ans[int(array[2])]}")
                            except: context.appText(f"/w {sender} 当前问题还没有此序号，请重新确认后查询！")
                    else: context.appText(f"/w {sender} 当前问题还没有设置回答，请重新确认后查询（用`~`代表空格，`\\~`代表\\~）！")
                else: context.appText("\n".join(answer.keys()))
            elif command == "+delr ":
                array = msg.split()
                if len(array) > 3: context.appText(f"/w {sender} 命令错误，请使用`0delr 问题 序号`的格式（序号可选，用`~`代表空格，`\\~`代表\\~）！")
                else: 
                    array[1] = textPure(array[1])
                    if len(array) == 2:
                        try: del answer[array[1]]
                        except: context.appText(f"/w {sender} 此问题还未设置答案，请重新确认后再次再试！")
                        else: context.appText(f"/w {sender} 已成功删除“{array[1]}”的所有回答！")
                    else:
                        try: ans = answer[array[1]].pop(int(array[2]))
                        except: context.appText(f"/w {sender} 此问题还未设置答案或序号错误，请重新确认后再次再试！")
                        else: context.appText(f"/w {sender} 已成功删除回答：“{ans}”！")
                    writeJson("answer.json", answer)
            elif command == "+relo ":
                ind = msg[6:]
                if ind == "0":
                    with open(FILENAME, encoding="utf8") as f:
                        global data
                        data = json.load(f)
                        context.appText("开盒数据重读成功咯~")
                elif ind == "1":
                    with open("design.json", encoding="utf8") as f:
                        global designs
                        designs = json.load(f)
                        context.appText("脑瘫设计数据重读成功咯~")
                else:
                    with open("reply.json", encoding="utf8") as f:
                        rpy = json.load(f)
                        RANDLIS[6] = rpy[0]
                        RANDLIS[19] = rpy[1]
                        context.appText(f"{called}回复信息重读成功咯~")
            elif command == "+stfu ":
                try: sysList[2] = int(msg[6:])
                except: pass
            elif msg == "+remake":
                p = sys.executable
                ws.close()
                os.execl(p, p, *sys.argv)
    # 防踢
    elif command == "~kick " and namePure(msg[6:]).startswith(nick):
        context.appText(f"/w {nick} aaaa")

    return context
funclist = [premade, mainfunc]
def msgGot(chat, msg: str, sender: str, trip: str, type_: str):
    if type_ == "whisper":
        type_ = whisback(chat, sender)
    else:
        type_ = chat.sendMsg
    for func in funclist:
        context = func(msg, sender, trip, type_)
        for i in context.text:
            for ctype, text in i.items():
                if ctype == "same":
                    send = type_
                elif ctype == "whisper":
                    to = i.get("to") or sender
                    send = whisback(chat, to)
                else:
                    send = chat.sendMsg
                send(text)
        if context.returns: return

def join(chat, joiner: str, color: str, result: dict):
    '''{'cmd': 'onlineAdd', 'nick': str, 'trip': str, 
        'uType': 'user', 'hash': str, 'level': 100, 
        'userid': iny, 'isBot': False, 'color': False or str, 
        'channel': str, 'time': int}'''
    log(f"{joiner} 加入")
    onlineUsers.append(joiner)
    trip, hash_ = result.get("trip"), result["hash"]
    addSaw(joiner, trip)

    userColor[joiner], userHash[joiner], userTrip[joiner] = color, hash_, trip
    names = data.get(hash_)
    if names:
        if not joiner in names:
            print(f"此hash曾用名：{'，'.join(names)}")
            data[hash_].append(joiner)
            writeJson(FILENAME, data)
    else:
        data[hash_] = [joiner]
        writeJson(FILENAME, data)
    for k, v in leftMsg.copy().items():
        if (joiner == v[1] and v[3] == "nick") or (trip == v[1] and v[3] == "trip"):
            del leftMsg[k]
            chat.sendMsg(f"/w {joiner} {nameMd(v[0])}曾在（{k}）通过{v[3]}给您留言：\n{v[2]}")
            writeJson("userData.json", userData)
    if hash_ in banned:
        chat.sendMsg(f"/w {joiner} "+"$\\begin{pmatrix}qaq\\\\[999999999em]\\end{pmatrix}$")
        chat.sendMsg(f"~kick {joiner}")
    elif hash_ == russian[1] and russian[2]:
        chat.sendMsg("而你，我的朋友，你是真正的投机取巧。")
        chat.sendMsg("~kick " + joiner)
        russian[3] = joiner
    elif not hash_ in blackList and not joiner in blackName:
        pass
def onSet(chat, result: dict):
    '''{'cmd': 'onlineSet', 'nicks': list, 'users': 
        [{'channel': str, 'isme': bool,  'nick': str,  'trip': str, 
            'uType': 'user', 'hash': str,  'level': 100, 'userid': int, 
            'isBot': False, 'color': str or False}*x],
        'channel': str, 'time': int}'''
    global onlineUsers
    onlineUsers = result["nicks"]
    for i in result["users"]:
        nick_ = i["nick"]
        addSaw(nick_, i["trip"])

        userHash[nick_] = i["hash"]
        userColor[nick_] = i["color"]
        userTrip[nick_] = i["trip"]
        names = data.get(i["hash"])
        if names:
            if not nick_ in names:
                data[i["hash"]].append(nick_)
        else:
            data[i["hash"]] = [nick_]
    writeJson(FILENAME, data)
    for i in info["prologue"]: chat.sendMsg(i)
def changeColor(chat, result:dict):
    '''{'nick': str, 'trip': str, 'uType': 'user', 
        'hash': str, 'level': 100, 'userid': int, 
        'isBot': False, 'color': str, 'cmd': 'updateUser', 
        'channel': str, 'time': int}'''
    userColor[result["nick"]] = result["color"]
def leave(chat, leaver: str):
    log(f"{leaver} 离开")
    onlineUsers.remove(leaver)
    while leaver in russian[0]:
        russian[0].remove(leaver)
    del userColor[leaver]
    del userHash[leaver]
    del userTrip[leaver]
    del nowSaw[leaver]
def whispered(chat, sender: str, msg: str, result: dict):
    """{"cmd": "info", "channel": str, "from": str or int, "to": int,
        "text": str, "type": "whisper", "trip": str,
        "level": int, "uType": str, "time": int}"""
    msg = msg[1:]
    print(f"{sender}对你悄悄说：{msg}")
    if result["channel"] != channel:
        p = sys.executable
        chat.ws.close()
        os.execl(p, p, *sys.argv)
    elif sender == nick: return
    else: msgGot(chat, msg, sender, result.get("trip"), "whisper")
def emote(chat, sender: str, msg: str):
    full = f"\\*：{msg}"
    allMsg.append(full)
    log(full)
    if not userTrip[sender] in whiteList:
        hash_ = userHash[sender]
        frisked = frisk(hash_, 0.9+len(msg)/256)
        if frisked == "warn":
            chat.sendMsg(f"@{sender} Warning!!!")
        elif frisked == "limit":
            chat.sendMsg(f"~kick {sender}")
            records[hash_]["score"] = threshold/2
            records[hash_]["warned"] = False
def infoed(chat, text: str):
    arr = text.split(" ")
    if arr[0] == "Kicked":
        if russian[2] and arr[1] == russian[3]:
            russian[3], russian[2] = None, False
            russian[1], russian[0] = None, []
class HackChat:
    def __init__(self, channel: str, nick: str, passwd: str="", color: str=""):
        self.nick = nick
        self.channel = channel
        global ws
        ws = websocket.create_connection(
            "wss://hack.chat/chat-ws", 
            sslopt={"cert_reqs": ssl.CERT_NONE}
        )
        # 人工操作功能，可以让阿瓦娅和主人结合，@w@
        # threading.Thread(target=self._person_control).start()
        self._sendPacket({"cmd": "join", "channel": channel, 
            "nick": f"{nick}#{passwd}"})
        if color: self.sendMsg(f"/color {color}")
    def sendMsg(self, msg: str):
        self._sendPacket({"cmd": "chat", "text": msg})
    def whisper(self, to: str, msg: str):
        self._sendPacket({"cmd": "whisper", "nick": to, "text": msg})
    def _sendPacket(self, packet:dict):
        encoded = json.dumps(packet)
        ws.send(encoded)
    def _person_control(self):
        while True:
            inputs = input()
            # 更新记忆，就算对我洗脑也没关系的……
            if inputs == "-reread":
                with open(FILENAME, encoding="utf8") as f:
                    global data
                    data = json.load(f)
                print("已重新读取数据")
            # 让我康康都有那些小可爱在线~
            elif inputs == "-users":
                print(",".join(onlineUsers))
            elif inputs[:4] == "-st ":
                sysList[0] = eval(inputs[3:])
            else: self.sendMsg(inputs)
    def run(self):
        """开始营业咯，好兴奋好兴奋"""
        try:
            while True:
                result = json.loads(ws.recv())
                cmd = result["cmd"]
                rnick = result.get("nick")
                if (not sysList[2]) or (sysList[2] and result.get("trip") in whiteList): 
                    # 接收到消息！
                    if cmd == "chat":
                        msgGot(self, result["text"], rnick, result.get("trip"), "chat")
                    # 有新人来！
                    elif cmd == "onlineAdd": join(self, rnick, result.get("color", ""), result)
                    # 有人离开……
                    elif cmd == "onlineRemove": leave(self, rnick)
                    # 收到私信！
                    elif result.get("type") == "whisper":
                        froms = result["from"]
                        if isinstance(froms, int): continue
                        whispered(self, result["from"], "".join(result["text"].split(":")[1:]), result)
                    # 更换颜色（色色达咩）
                    elif cmd == "updateUser": changeColor(self, result)
                    elif cmd == "emote": emote(self, result["nick"], result["text"])
                    # 话痨过头被服务器娘教训啦——
                    elif cmd == "warn":
                        if not "blocked" in result["text"]: print(result["text"])
                        else: time.sleep(2)
                    elif cmd == "info":
                        infoed(self, result["text"])
                    # 当然要用最好的状态迎接开始啦！
                    elif cmd == "onlineSet": onSet(self, result)
                else:
                    # 有新人来！
                    if cmd == "onlineAdd":
                        onlineUsers.append(rnick)
                        userColor[rnick], userHash[rnick], userTrip[rnick] = \
                        result.get("color"), result["hash"], result.get("trip")
                    # 有人离开……
                    elif cmd == "onlineRemove": leave(self, rnick)
                    elif cmd == "updateUser": changeColor(self, result)

        # 坏心眼……
        except BaseException as e:
            with open(f"traceback/{time.time()}.txt", "w", encoding="utf8") as f:
                f.write(traceback.format_exc())
            self.sendMsg(f"被玩坏了，呜呜呜……\n```\n{e}\n```")
            self.run()

if __name__ == '__main__':
    chat = HackChat(channel, nick, passwd, color)
    chat.run()