import json, time, numpy as np

# 莫名其妙的编码问题，很让我头疼啊~
def dec(cont: str) -> str:
    if cont.startswith(u"\ufeff"):
        return cont.encode("utf8")[3:].decode("utf8")
    else:
        return cont
# 返回日期
def nowDay() -> str:
    now = time.localtime()
    return f"{now.tm_year}{now.tm_mon:0>2}{now.tm_mday:0>2}"
# 整数秒
def intTime() -> int:
    return int(time.time())
# 日期差
def timeDiff(seconds) -> str:
    if seconds >= 86400:
        diff = f"{seconds // 86400}日"
        return diff + timeDiff(seconds % 86400)
    elif seconds >= 3600:
        diff = f"{seconds // 3600}时"
        return diff + timeDiff(seconds % 3600)
    elif seconds >= 60:
        diff = f"{seconds // 60}分"
        return diff + timeDiff(seconds % 60)
    else:
        return f"{seconds}秒"
# 格式化时间
def ftime(seconds) -> str:
    struct = time.localtime(seconds)
    result = time.strftime("%Y/%m/%d %H:%M:%S", struct)
    if seconds % 1: result += f":{seconds:.2f}"[-2:]
    return result
# 初始化saw
def addSaw(nick, trip):
    now = intTime()
    lastSaw["nick"][nick] = {"time": now, "msg": None}
    if trip: lastSaw["trip"][trip] = {"time": now, "msg": None}
    writeJson("userData.json", userData)
    nowSaw[nick] = {"joined": now, "words": 0}
# 存入记忆中！
def writeJson(filename, datas):
    with open(filename, "w", encoding="utf8") as f:
        json.dump(datas, fp=f, ensure_ascii=False, indent=2)

# 读取文件们
FILENAME = "hash.json"
with open("info.json", encoding="utf8") as f:
    info = json.loads(dec(f.read()))
with open("design.json", encoding="utf8") as f:
    designs = json.loads(dec(f.read()))
with open(FILENAME, encoding="utf8") as f:
    data = json.loads(dec(f.read()))
with open("userData.json", encoding="utf8") as f:
    userData = json.loads(dec(f.read()))
with open("reply.json", encoding="utf8") as f:
    replys = json.loads(dec(f.read()))
with open("answer.json", encoding="utf8") as f:
    answer = json.loads(dec(f.read()))

#命令前缀
PREFIX = "-"

# [0涩图开关, 1报时开关, 2休眠开关, 3当前日期]
sysList = [False, True, False, nowDay()]
# [0[参加的], 1要踢的hash, 2是否有要踢的, 3要踢的名字]
russian = [[], None, False, None]
# [0象棋开关, 1轮到谁, 2结束游戏的人, 3[红方, 黑方], 4当前棋盘]
CCList = [False, None, None, [None, None], []]
# [0真心话开关, 1{昵称：摇出的数字}, 2[玩游戏中的hash]]
truthList = [False, {}, []]
# [0炸弹数字, 1[在玩的人], 2轮到序号, 3初始最小值, 4初始最大值, 5是否在玩, 6本轮最小值, 7本轮最大值]
bombs = [0, [], 0, 1, 1000, False, 1, 1000]
# [0扑克开关, 1{在玩的人:[拥有的牌]}, 2轮到序号, 3当前牌堆, 4底牌, 5地主, 6是否在叫牌阶段, 7[玩家名称], 8谁拿地主牌, 9{叫牌人:叫几分}, 10本轮第一出牌的序号, 11上家的牌]
pokers = [False, {}, 0, [], [], None, False, [], None, {}, None, None]
# [0uno开关, 1玩家列表, 2玩家的牌, 3牌堆, 4轮到玩家, 5当前的牌]
unos = [False, [], [], [], "", "+4"]
# 在这的变量和在sysList里的区别是，在这里的变量都不需要直接改变，只在原来基础上增删；
# 在sysList中的则需要，例如游戏中的hash和摇出的数字都会在结算中清空，储存在一个列表中就避免了各种莫名其妙的作用域问题
allMsg, afk, leftMsg, ignored, banned = [], {}, userData["leftMsg"], userData["ignored"], userData["banned"]
userHash, userTrip, userColor, engUsers, nowSaw = {}, {}, {}, userData["engUsers"], {}
blackList, blackName, whiteList = userData["blackList"], userData["blackName"], userData["whiteList"]
lastSaw = userData["lastSaw"]
# 复读万岁
meaningful = []
#常量
channel, nick, passwd, color = info["channel"], info["nick"], info["passwd"], info["color"],
owner, called = info["owner"], info["called"]
# 主人：我无所不能的卡密哒！
OWNER = info["ownerTrip"]

CLOLUMN, LETTERS = ["| \\ |1|2|3|4|5|6|7|8|9|", "|-|-|-|-|-|-|-|-|-|-|"], list("ABCDEFGHIJ")
RED, BLACK = ["==车==", "==马==", "==相==", "==士==", "==帥==", "==兵==", "==炮=="], ["車", "馬", "象", "仕", "將", "卒", "砲"]
# WHITE, GRAY = "O", "X"
CARDS = ['3', '4', '5', '6', '7', '8', '9', 'H', 'J', 'Q', 'K', 'A', '2']
JOKERS = ["小", "大"]
SORT = dict(zip(CARDS+JOKERS, range(15)))
PINIT = CARDS*4 + JOKERS
# 自定义回复，包含了主人对我的满满心意，诶嘿嘿~
RANDLIS = [
    [f"找{owner}去吧。", "早上好！", "干什么?", "想下象棋吗？发送菜单看看？", "好好好~", "有什么吩咐~", "sender寂寞了吧",
    "发送菜单了解我的功能~", "怎么了？", "阿巴阿巴", "干啥的", "/hax", "没中奖，感谢惠顾！", "没中奖，恭喜！", "中……紫砂吧。",
    "嗨，看起来很好\n你对一切都感到失望吗？\n不用担心！跟随勇士的战争与我们同在！它会顺利漂浮！", "落入他人之手的你会变得不幸",
    "![](https://i.gyazo.com/eab45f465ed035c58c8595159eb9f6e2.gif)", "在这在这~", "@sender", "Hello", "Yep", " ~kick sender",
    "接下来我要说一个f开头的单词", "#"], #0
    replys[0], #1
    ["sender最可爱了", "sender棒棒", "sender是小天使", "/shrug", "是这样的", "你说得对", "违法内容，请终止当前话题。", "？", "/hax", 
    "@sender", " ~kick sender"], #2
    ["hi, joiner", "hello, joiner", "joiner!", "Sup", "joiner! Hows ur day?", "出现了，joiner!", "这不是joiner吗~", "hihih",
    "你好诶，joiner，新的一天也要加油哦！", "Welcome, joiner!", "好久不见啊，joiner~", "早上好，joiner!", "下午好，joiner~",
    "@joiner 您好，您看上去挺面善的~\n最近您会因为诸事不如意而感到沮丧吗？\n别担心！和我们一起追随勇士战神吧！这样定能一帆风顺！"], #3
    replys[1], #5
    ["hello~", "hi", "欢迎", "今天过得怎么样", "还好吗", "你好", "whats up", "Good morning", "早上好！", "sender啊，好好", "sender~",
    "您好，您看上去挺面善的~", "？", "感觉怎么样？"], #6
]
FUCKS = [
    "fucker尝试草poor，成功了，死也可以瞑目了。",
    "fucker尝试草poor，被poor反草了，可喜可贺可喜可贺。",
    "fucker尝试草poor，poor看起来很开心，恭喜大家成人。",
    "fucker尝试草poor，被passer*不小心*看到了，在差一点成功的时候警察将fucker绳之以法了，残念，下次记得找空旷的地方。",
    "fucker强行草poor，在去的一瞬间发现原来是一场梦，……再做一次吧。",
    "fucker通过*自身魅力*让poor迷上了他，整个过程十分顺畅，孩子已经两个月了。",
    "fucker把poor灌醉了，但是安全措施做得很好，没有后患。",
    "fucker不想草poor，poor说：“不要让意志击垮你的欲望！”，然后手把手把fucker引上了极乐殿堂，啊啊啊啊。",
    "fucker想草poor，十分真诚地说：“poor，可以让我草草吗”，poor说“不可以涩涩！”。然后没了，乖孩子。",
    "fucker发情了，想要草poor，但是发现poor其实并不存在，只能意淫了，残念。",
    "fucker认为草是一种十分不好的行为，poor也如此认为。没人受到伤害，大家都开心极了。"
]
del replys
RULE = "\n".join([
    "好、的，听清楚规则了哦~",
    "如你所见，棋盘一共有10行，从上到下依次为ABCDEFGHIJ；又有9列，从左到右依次为123456789。",
    "用这个方法可以表示出棋盘上的任何位置，例如左上角的马，其坐标应为A2。",
    "发送`@bot名 旧位置 新位置`移动棋子，例如`@awaBot C2 C3`可以将左上角的炮向右挪动一格。",
    "明白了吗？开始吧~",
    "温馨提示：使用暗色主题棋盘显示效果更佳~"
])
CCMENU = "\n".join([
    f"/w sender 使·用·说·明\\~\n哟，这不是sender吗，我是来自阿瓦国的狂热象棋Bot{called}哦，很高兴认识你\\~",
    "以下是我能做的事情，如果能帮上你的忙的话我会很高兴的！~~请随意使用我吧~~",
    "`@Bot名 加入游戏`：加入游戏或者创建一个游戏\\~",
    "`@Bot名 结束游戏`：结束游戏，如果你执意要这么做的话……",
    "`@Bot名 帮助`：显示这一段话~~，也就是套娃啦！~~",
    "芜湖，就这么多了，虽然我也知道我很棒不过毕竟人的能力是有限的嘛~但放心，我每天都在努力学习，也许明天，下个小时或者下一分钟，\
    在你不注意的时候，我就有新功能啦，ᕕ( ᐛ )ᕗ\\~"
])
BOMBMENU = "\n".join([
    "/w sender 数字炸弹——",
    "规则很简单，在一个给定的范围中设某个数字为「炸弹」，玩家轮流猜数缩小范围，直到某人猜到炸弹。以下是关于数字炸弹的命令：",
    "`bomber` : 加入数字炸弹游戏！",
    "`bomber t`: 在开始之前退出游戏~",
    "`*bom` : 让机器人加入！",
    "`开始b` : 开始数字炸弹，至少需要两个人。",
    "`结束b` : 结束数字炸弹……",
    "`b 数字` : 猜数。",
    "就是这么多了，祝你好运，ᕕ( ᐛ )ᕗ\\~"
])
POKERMENU = "\n".join([
    "/w sender 斗地主...",
    "poker: 创建或加入一场斗地主，满三人后自动开始。",
    "poker t: 在开始之前退出对局。",
    "p 牌: 出牌，具体规则请查看出牌规则。",
    f"@{nick} 结束p: 在对局中结束游戏。",
    f"@{nick} 扑克规则: 获取扑克的出牌规则。",
])
POKERRULE = "\n".join([
    "/w sender 游戏规则请自行参考[此处](https://baike.baidu.com/item/%E4%B8%89%E4%BA%BA%E6%96%97%E5%9C%B0%E4%B8%BB/9429860)，要注意的是这里用==H==代表==10==，==小==代表小王，==大==代表大王。以下是出牌规则：",
    "使用==p 牌==出牌，例如==p 1==, ==p J==，大小写均可；",
    "使用==p .==跳过回合、==p check==查看自己目前的牌；",
    "多张相同面值的牌间使用==牌*张数==，例如==p 3*2==，==p 4*3==；",
    "顺子使用==最小牌-最大牌==，例如==p 4-8==，==p 6-A==；",
    "双顺或三顺使用==最小-最大*张数==，例如==p 3-5*2==，==p 4-5*3==；",
    "三带二、飞机等带的对子中不使用==*==，例如==p K*3 77==，==p 8-9*3 33 44==",
    "王炸直接发送==p 王炸==即可；",
    "剩余的就将这两种组合，不同组别用空格隔开即可，例如==p 4-5*3 7 9== ==p 7*4 99 HH==……",
    "玩得开心~"
])
UNORULE = "\n".join([
    "简而言之就是出与上家的牌颜色或数字相同的牌。更细节的玩法请自行百度。",
    "程序由@Blaze (geGDVS)提供。"
])
CINIT=np.array([
    [RED[0], RED[1], RED[2], RED[3], RED[4], RED[3],RED[2], RED[1], RED[0]],
    ["&ensp;"]*9,
    ["&ensp;", RED[6], "&ensp;", "&ensp;", "&ensp;", "&ensp;", "&ensp;", RED[6], "&ensp;"],
    [RED[5], "&ensp;", RED[5], "&ensp;", RED[5], "&ensp;", RED[5], "&ensp;", RED[5]],
    ["&ensp;"]*9,

    ["&ensp;"]*9,
    [BLACK[5], "&ensp;", BLACK[5], "&ensp;", BLACK[5], "&ensp;", BLACK[5], "&ensp;", BLACK[5]],
    ["&ensp;", BLACK[6], "&ensp;", "&ensp;", "&ensp;", "&ensp;", "&ensp;", BLACK[6], "&ensp;"],
    ["&ensp;"]*9,
    [BLACK[0], BLACK[1], BLACK[2], BLACK[3], BLACK[4], BLACK[3], BLACK[2], BLACK[1], BLACK[0]],
])

MENUMIN = "\n".join([
    "菜单：",
    "普通用户：",
    f">{PREFIX}hasn, {PREFIX}hash, {PREFIX}code, {PREFIX}colo, {PREFIX}left, {PREFIX}peep, {PREFIX}welc, {PREFIX}last, " +
    f"{PREFIX}lost, {PREFIX}unlo, {PREFIX}prim, {PREFIX}rand, {PREFIX}repl, {PREFIX}seen, {PREFIX}seen, {PREFIX}setu, {PREFIX}fuck, " +
    f"{PREFIX}tran, r, rprime, russia, letter, uno, 真心话, @{nick} 象棋, @{nick} 数字炸弹, @{nick} 斗地主",
    ">",
    "白名单用户：",
    ">+setu, +time, +addb, +delb, +kill, +bans, +uban, +addn, +deln, +bcol, +setb",
    ">",
    f"发送=={PREFIX}help 命令==可获得该指令详细用法，如=={PREFIX}help hash==, =={PREFIX}help 真心话==, =={PREFIX}help 斗地主== 等等...",
])
COMMANDS = {
    "help": "\n".join([
        "# Help Of Commands:",
        "||",
        "|:-:|",
        "|权限要求: 无|",
        "|所需参数: <命令>|",
        "|描述: 查询<命令>的使用方法。|",
        f"|例: {PREFIX}help help|",
        "|返回格式: 如你所见。|",
        "|注: <所需参数>中==?参数==表示可选参数，<返回格式>所描述的为==参数合法==情况下的理想返回格式|"
    ]),
    "hasn": "\n".join([
        "# Hash Now Online User:",
        "||",
        "|:-:|",
        "|权限要求: 无|",
        "|所需参数: <昵称>|",
        "|描述: 查询==当前在线==名为<昵称>用户的Hash的历史昵称|",
        f"|例: {PREFIX}hasn @{nick}|",
        "|返回格式: 昵称, 昵称, 昵称..|",
        "|注: 别翻路人的身份证，即使它是公开的:)|"
    ]),
    "hash": "\n".join([
        "# History Nickname For Hash Of Nick:",
        "||",
        "|:-:|",
        "|权限要求: 无|",
        "|所需参数: <昵称>|",
        "|描述: 查询使用过所有<昵称>的用户的Hash的历史昵称|",
        f"|例: {PREFIX}hash @{nick}|",
        "|返回格式: 1. 昵称, 昵称, 昵称.. 2. 昵称, 昵称, 昵称.. ...|",
        "|注: 谨慎使用，当心后果。|"
    ]),
    "code": "\n".join([
        "# History Nickname For Hash Code:",
        "||",
        "|:-:|",
        "|权限要求: 无|",
        "|所需参数: <Hash码>|",
        "|描述: 查询使用过所有<昵称>的用户的Hash的历史昵称|",
        f"|例: {PREFIX}hash abcdefg|",
        "|返回格式: 昵称, 昵称, 昵称.. |",
        "|注: `/myhash`可快捷查看自己的Hash。谨慎使用，当心后果。|"
    ]),
    "colo": "\n".join([
        "# Color Of Nickname:",
        "||",
        "|:-:|",
        "|权限要求: 无|",
        "|所需参数: <昵称>|",
        "|描述: 查询当前名为<昵称>的用户的颜色|",
        f"|例: {PREFIX}hash abcdefg|",
        "|返回格式: 十六进制颜色值|"
    ]),
    "left": "\n".join([
        "# Leave Message For Someone:",
        "||",
        "|:-:|",
        "|权限要求: 无|",
        "|所需参数: ?*trip <昵称或识别码> <消息>|",
        "|描述: 为<昵称>或<识别码>（当使用*trip时）留言，会在用户上线时私信。|",
        f"|例: {PREFIX}left *trip coBad2 Hi there! 或 {PREFIX}left {nick} Are you a bot?|",
        "|返回格式: 留言成功|",
        "|注: 支持私信，用户上线时通知格式：<昵称>曾在（<时间>）给您留言：<消息>|",
    ]),
    "peep": "\n".join([
        "# View History Messages:",
        "||",
        "|:-:|",
        "|权限要求: 无|",
        "|所需参数: <整数> ?<整数>|",
        "|描述: 浏览最近的<整数>条消息，参数长度为二时则会选择最近377条消息中第<整数>至第<整数>条。|",
        f"|例: {PREFIX}peep 23|",
        "|返回格式: 私信, 昵称：消息, 昵称：消息..|",
        "|注: 最多存储377条消息，查看消息过长时无法显示。|",
    ]),
    "welc": "\n".join([
        "# Set Welcome Message:",
        "||",
        "|:-:|",
        "|权限要求: 无|",
        "|所需参数: ?<欢迎语>|",
        "|描述: 为当前识别码设置欢迎语，参数为空时清除欢迎语。|",
        f"|例: {PREFIX}welc Oh, here's {nick}!|",
        "|返回格式: 设置成功。|",
        "|注: 不是什么都行的哦(*￣ω￣)。|",
    ]),
    "last": "\n".join([
        "# Leave Message:",
        "||",
        "|:-:|",
        "|权限要求: 无|",
        "|所需参数: <消息>|",
        f"|描述: 为当前昵称设置一条留言，可被他人使用=={PREFIX}lost==查看。|",
        f"|例: {PREFIX}last I'll come back next Thursday!|",
        "|返回格式: 设置成功。|",
        "|注: 接灰的功能(￣_,￣ )。|",
    ]),
    "lost": "\n".join([
        "# Check Someone's Last Message:",
        "||",
        "|:-:|",
        "|权限要求: 无|",
        "|所需参数: <昵称>|",
        "|描述: 查看<昵称>设置的留言。|",
        f"|例: {PREFIX}lost {nick}|",
        "|返回格式: 消息|",
    ]),
    "unlo": "\n".join([
        "# Clear Last Message:",
        "||",
        "|:-:|",
        "|权限要求: 无|",
        "|所需参数: <昵称>|",
        "|描述: 清除<昵称>设置的留言，识别码须与<昵称>一致。|",
        f"|例: {PREFIX}unlo {nick}|",
        "|返回格式: 清除成功。|",
    ]),
    "prim": "\n".join([
        "# Prime Factorization:",
        "||",
        "|:-:|",
        "|权限要求: 无|",
        "|所需参数: <自然数>|",
        "|描述: 对<自然数>进行分解质因数。|",
        f"|例: {PREFIX}prim 42|",
        "|返回格式: <自然数> = 质数\\*质数\\*质数|",
    ]),
    "rand": "\n".join([
        "# Random Wired Designs:",
        "||",
        "|:-:|",
        "|权限要求: 无|",
        "|所需参数: <整数>|",
        "|描述: 返回<整数>（1-10）个随机设计。|",
        f"|例: {PREFIX}rand 6|",
        "|返回格式: 设计, 设计...|",
        "|注: [来自点我](https://protobot.org/#zh)|",
    ]),
    "repl": "\n".join([
        "# Customize Bot Reply:",
        "||",
        "|:-:|",
        "|权限要求: 无|",
        "|所需参数: <问题> <回答>|",
        f"|描述: 为问题设置回答，当==@{nick} <问题>==时有几率使用<回答>回答|",
        f"|例: {PREFIX}repl Who\\~are\\~you I Am You.|",
        "|返回格式: 添加成功。|",
        "|注: <问题>支持正则表达式，使用`~`代替空格，`\\~`代替`~`。|",
    ]),
    "seen": "\n".join([
        "# Last Saw Someone At:",
        "||",
        "|:-:|",
        "|权限要求: 无|",
        "|所需参数: ?*trip <昵称或识别码>|",
        f"|描述: 最后一次看到某昵称或识别码的时间，与他最后一句话的内容。|",
        f"|例: {PREFIX}seen *trip coBad2|",
        "|返回格式: 时间，发言内容。|"
    ]),
    "look": "\n".join([
        "# I Don't Know:",
        "||",
        "|:-:|",
        "|权限要求: 无|",
        "|所需参数: <昵称>|",
        f"|描述: 当前在线昵称的加入时间，发言频率，以及与{PREFIX}seen相同。|",
        f"|例: {PREFIX}look Krs_|",
        "|返回格式: 略。 |"
    ]),
    "setu": "\n".join([
        "# Beautiful Picture:",
        "||",
        "|:-:|",
        "|权限要求: 无|",
        "|所需参数: ?<参数>|",
        "|描述: 注意身体。|",
        f"|例: {PREFIX}setu tag=黑丝|白丝 |",
        "|返回格式: 图片, 图片信息|",
        "|注: [来自点我](https://api.lolicon.app/#/setu)（参数也可以在这看）|",
    ]),
    "fuck": "\n".join([
        "# Virtual Fucking:",
        "||",
        "|:-:|",
        "|权限要求: 无|",
        "|所需参数: ?<昵称>|",
        "|描述: 兰枝发电协会推荐。 |",
        f"|例: {PREFIX}fuck {nick} |",
        "|返回格式: 草。 |",
        "|注: 不加参数则随机草一个人， |",
    ]),
    "tran": "\n".join([
        "# Translate:",
        "||",
        "|:-:|",
        "|权限要求: 无|",
        "|所需参数: <消息>|",
        "|描述: 翻译，由DPG提供。|",
        f"|例: {PREFIX}tran Down North Water|",
        "|返回格式: 翻译结果|"
    ]),
    "gras": "\n".join([
        "# Grass, Grew:",
        "||",
        "|:-:|",
        "|权限要求: 无|",
        "|所需参数: <消息>|",
        "|描述: 谷歌生草，由DPG提供。|",
        f"|例: {PREFIX}gras ‍Colorless green ideas sleep furiously.|",
        "|返回格式: 生草结果。|"
    ]),
    "r": "\n".join([
        "# Random Integer:",
        "||",
        "|:-:|",
        "|权限要求: 无|",
        "|所需参数: ?<整数> ?<整数>|",
        "|描述: 1\\~1000、1\\~<整数>、<整数>\\~1、或<整数>\\~<整数>之间的随机整数。|",
        "|例: r 6 666|",
        "|返回格式: 整数|",
        "|注: 更多用法参见真心话。|",
    ]),
    "rprime": "\n".join([
        "# Random Prime Factorization:",
        "||",
        "|:-:|",
        "|权限要求: 无|",
        "|所需参数: ?<整数>|",
        "|描述: 获取1\\~1000或1\\~<整数>之间的随机数并进行质因数分解。|",
        "|例: rprime 12345|",
        "|返回格式: 随机数 = 质数\\*质数\\*质数..|"
    ]),
    "russia": "\n".join([
        "# Russian Roulette:",
        "||",
        "|:-:|",
        "|权限要求: 无|",
        "|所需参数: 无|",
        "|描述: 加入一场俄罗斯轮盘赌。|",
        "|例: russia |",
        "|返回格式: 加入成功|",
        "|注: 发送==开枪==会随机选择一名参与者踢出:D|",
    ]),
    "letter": "\n".join([
        "# A Letter From A Stranger:",
        "||",
        "|:-:|",
        "|权限要求: 无|",
        "|所需参数: 无|",
        "|描述: 获得一封信。|",
        f"|例: letter|",
        "|返回格式: 信件内容|",
        "|注: [来自点我](https://www.thiswebsitewillselfdestruct.com/)|",
    ]),
    "uno": "\n".join([
        "# UNO Game:",
        "||",
        "|:-:|",
        "|权限要求: 无|",
        "|所需参数: 无|",
        "|描述: 参加一场UNO游戏。|",
        "|例: uno|",
        "|返回格式: 加入成功。|",
        "|注: 玩法请自行百度。|",
    ]),
    "真心话": "\n".join([
        "# Russian Roulette:",
        "||",
        "|:-:|",
        "|权限要求: 无|",
        "|所需参数: 无|",
        "|描述: 加入一场真心话游戏。|",
        "|例: 真心话 |",
        "|返回格式: 游戏规则|"
    ]),
    "象棋": "\n".join([
        "# Chinese Chess:",
        "||",
        "|:-:|",
        "|权限要求: 无|",
        "|所需参数: 无|",
        "|描述: 象棋Bot的使用方法。|",
        f"|例: @{nick} 象棋|",
        "|返回格式: 使用帮助。|"
    ]),
    "数字炸弹": "\n".join([
        "# Number Bomb:",
        "||",
        "|:-:|",
        "|权限要求: 无|",
        "|所需参数: 无|",
        "|描述: 数字炸弹Bot的使用方法。|",
        f"|例: @{nick} 数字炸弹|",
        "|返回格式: 使用帮助。|"
    ]),
    "斗地主": "\n".join([
        "# Poker:",
        "||",
        "|:-:|",
        "|权限要求: 无|",
        "|所需参数: 无|",
        "|描述: 扑克Bot的使用方法。|",
        f"|例: @{nick} 斗地主|",
        "|返回格式: 使用帮助。|"
    ]),
}
MENUFT = [
    "其他命令：[涩图](https://api.lolicon.app/#/setu)、真心话，功能和名字一样所以就没单独列出来（）",
    "Bot源码请查看[这里](https://github.com/Kroos372/awaBot/)。",
    "注： 网络不是法外之地~"
]
MENUSP = [
    "|菜单w|白名单用户的特殊菜单|菜单w| \\ |",
] + MENUFT
MENUSSP = [
    "|菜单\\~|主人的特殊菜单\\~|菜单\\~| 最后的波浪线也是命令的一部分哦 |",
] + MENUSP
ADMMENU = [
    "白名单用户的特殊服务~",
    "|命令|介绍|例|备注|",
    "|:-:|:-:|:-:|:-:|",
    "|0setu 0或1|涩图开关，0关1开|0setu 1| 实际上是int后面的语句 |",
    "|0time 0或1|报时开关，同上|0time 0|同上|",
    "|0kill 昵称| 使用LaTeX对某人进行刷屏并使用ModBot的kick |0kill qaq|需要注意的是这只有在对方开启LaTeX的情况下才有用、|",
    "|0bans 昵称| 封禁某人，和kill一样，但会持续 | 0bans abcd | \\ |",
    "|0uban 序号| 取消封禁某人 | 0uban abcd | \\ |",
    f"|0addb 昵称|添加黑名单用户（输入的是昵称，添加的是hash）|0addb {owner}| ==addb==lacklist user|",
    f"|0delb 昵称|删除黑名单用户|0delb {owner}| \\ |",
    f"|0addn 昵称|添加黑名单昵称|0addn {owner}| 同上 |",
    f"|0deln 昵称|删除黑名单昵称|0deln {owner}| 同上 |",
    "|0bcol 颜色值|修改bot颜色值|0bcol aaaaaa| \\ |",
    "|0setb 最小值 最大值|设置数字炸弹的最小值与最大值|0setb 1 100| \\ |",
]
OWNMENU = "\n".join(["只为主人提供的秘密服务❤~"] + ADMMENU[1:] + [
    f"|0addw 识别码|添加白名单用户（识别码）|0addw {OWNER}| ==addw==hitelist user|",
    f"|0delw 识别码|删除白名单用户|0delw {OWNER}| \\ |",
    f"|0igno 昵称|不记录某人消息|0igno @{owner}| `@`，省略，懂？最好在真心话的时候用。 |",
    f"|0unig 昵称|记录某人信息|0unig @{owner}| 同上 |",
    "|0stfu 0或1| 1为休眠，使bot只回复白名单用户，0为取消休眠 | 0stfu | 刷屏什么的去死好了。 |",
    "|0remake| 重启 |0remake|restart太长了|",
    "|0chkr 问题 序号|查看某个问题的回答或第序号个回答，序号可选。|0chkr 什么鬼| ==ch==ec==k== ==r==eply |",
    "|0delr 问题 序号|删除某个问题的回答或第序号个回答，序号可选。|0delr 什么鬼| \\ |",
    "其他：自己去他妈看源码去！"
])
ENGMENU = [
    "Here are all functions menu:",
    "|Command|Description|e.g.|Note|",
    "|:-:|:-:|:-:|:-:|",
    f"|{PREFIX}peep <integers>|View last <integers> history messages| {PREFIX}peep 10| <integers> up to 377.|",
    f"|{PREFIX}colo <nickname>| Return <nickname>'s hex color value. | {PREFIX}colo @{nick}| `@` can be omitted.|",
    f"|{PREFIX}hash <nickname>| Return history nicknames of <nickname>. | {PREFIX}hash @{nick}| `@` can be omitted. |",
    f"|{PREFIX}code <hashcode>| Return history nicknames of <hashcode>. | {PREFIX}code abcdefg | Use `/myhash` to check your hashcode.|",
    f"|{PREFIX}left <nickname> <message> | Leave a message for <nickname>, <message> will be whispered to him/her when he/she join" +
    f"the channel|{PREFIX}left @{nick} hello world| `@` can be omitted. |",
    f"|{PREFIX}welc <message> | Set welcome text for current trip. | {PREFIX}welc ᕕ( ᐛ )ᕗ | Trip is a must, send `{PREFIX}welc` to cancel. |",
    f"|{PREFIX}last <message> | Leave a message that everyone can check. | {PREFIX}last I'll be back tomorrow. | Trip is a must. |",
    f"|{PREFIX}lost <nickname> | Check the message that <nickname> left. | {PREFIX}lost @{owner} | `@` can be... u know what im going to say :D |",
    f"|{PREFIX}unlo <nickname> | Clear the message that u left by `{PREFIX}last` | {PREFIX}unlt @{owner} | <nickname>'s trip must be as same as yours. |",
    f"|{PREFIX}prim <digit> | Decomposing prime factors for <digit>. | {PREFIX}prim 1234567890123 | Up to 13 digits, more than that will be automatically cut off. |",
    f"|{PREFIX}rand <digit>|Get <digit> kinda random designs|{PREFIX}rand 1|API from [HERE](https://protobot.org/#zh), <digit> up to 10|",

    "|afk| Mark yourself as afk, automatically unmark the next time you say sth. |afk sleeping| AFK(Away From Keyboard) |",
    "|r| Get a random number. |r 100| if r followed by a space and an integer, return a random number between 1 to that integer" +
    "(include) or that integer(include) to 1, else return random number between 1 to 1000. |",
    f"|rprime| Decomposing prime factors for a random number. |rprim 9999| Rules are as same as `r` + `{PREFIX}prim` |",
    "|rollen| Repeatedly generate random numbers until 1. | rollen 9999 | Rules same. |",
    "|listwh| List whitelist trips. | listwh |==list wh==itelist users|",
    "|listbl| List blacklist trips. | listbl | \\ |",
    f"|@<botname> <message> | Chat in Chinese with bot. | @{nick} help | API from [HERE](https://api.qingyunke.com/). |",
    f"|@<botname> 象棋| Help message of Chinese Chess Bot. | @{nick} 帮助| \\ |",
    f"|@<botname> 数字炸弹| Help message of Number Bomb Bot. (A kinda game) | @{nick} 数字炸弹| \\ |",
    "|真心话| Start a Truth ~~or Dare~~ game. | 真心话 | \\ |",
    "|菜单| Return Chinese version of this menu. | 菜单 | \\ |",
    "|涩图| Beatiful pictures XD | 涩图 | API from [Lolicon](https://api.lolicon.app/). |",
    "| engvers | Use english version for current trip (All reply *for you* will be in English)| engvers | Not supported now, to be continue...| ",
]
ENGMENUFT = [
    "This bot is open-sourced, you can view all source code [HERE](https://github.com/Kroos372/awaBot/).",
]
ENGMENUSP = [
    "|menuw| special menu for whitelist users | menuw | \\ |",
] + MENUFT
ENGMENUSSP = [
    "|menu~| special menu for owner\\~| menu\\~| `~` is also a part of command. |",
] + MENUSP
ENGADMMENU = [
    "Special whitelist user~",
    "|Command|Description|e.g.|Note|",
    "|:-:|:-:|:-:|:-:|",
    "| 0setu 0 or 1 | Picture switch | 0setu 1 | `int()` is what program actually done |",
    "| 0time 0或1 | Chime switch | 0time 0 | Ibid |",
    f"| 0addb <nick> | Add blacklist user.(hash) |0addb {owner}| \\ |",
    f"| 0delb <nick> | Delete blacklist user. |0delb {owner}| \\ |",
    f"|0addn <nick> | Add blacklist name.|0addn {owner}| \\ |",
    f"|0deln <nick> |Delete blacklist name.|deln {owner}| \\ |",
    f"| 0bcol <hex color value> | Change bot's color |0bcol aaaaaa| \\ |",
]
ENGOWNMENU = "\n".join(["Only for master❤~"] + ENGADMMENU[1:] + [
    f"|0addw <trip>|Add whitelist user|0addw {OWNER}| \\ |",
    f"|0delw <trip>|Delete whitelist user|0delw {OWNER}| \\ |",
    f"|0igno <nickname> | Stop recording sb.'s message. |0igno @{owner}| `@` can be... |",
    f"|0unig <nickname>| Start to record sb.'s message. |0unig @{owner}| Ibid |",
    "|0stfu 0 or 1 | 1 means sleep, let bot not reply any messages, 0 cancel it. | 0stfu | \\ |",
    "|0bans <nick>| Ban someone by LaTeX. | 0bans abcd | \\ |",
    "|0uban <nick> | Unban someone. | 0uban abcd | \\ |",
    "|0remake| Restart. |0remake| \\ |",
])
GAMEMENU = "\n".join([
    "真心话现在开始啦，发送*r*来获取随机数，*结算*来结算，*结束游戏*来结束游戏~",
    "以下是注意事项：",
    "1\\.愿赌服输，所谓的**真心话**的意思是什么，参与了就不能后悔了，",
    "2\\.不要把游戏当成拷问，提的问题请在能够接受的范围内，",
    "3\\.尺度请自行把握，不用过于勉强自己也不要勉强他人，感到不适可以要求对方更换问题，",
    "4\\.玩得愉快。",
    f"PS: ***实在***没活整了可以发送==@{nick} 提问==获取些离谱小问题，当然你要是把这当成功能的一部分的话我就\\*优美的中国话\\*",
    f"PSS: 获取随机数只能用*r*，而不是*r 数字*，后者在真心话中会被忽略。"
])

def bom()->str:
    if not bombs[5]:
        if not nick in bombs[1]:
            bombs[1].append(nick)
            return "已成功添加机器人进入游戏！"
        else: return "机器人已经加入过了！"
    else: return "这局已经开始了，等下局吧~"
def truth()->str:
    if not truthList[0]:
        truthList[0] = True
        return GAMEMENU
    else: return "已经在玩了哦╮(╯_╰)╭"
def atLast()->str:
    if truthList[0]:
        if len(truthList[2]) < 2: return "有句话叫什么，一个巴掌拍不响(°o°；)"
        else:
            sort = sorted(truthList[1].items(), key=lambda x: x[1])
            loser, winner = sort[0], sort[-1]
            fin = "\n".join([f"本轮参与人数：{len(truthList[1])}。",f"最大：{winner[1]}（{winner[0]}），",
                f"最小：{loser[1]}（{loser[0]}）。", f"@{winner[0]} 向@{loser[0]} 提问，@{loser[0]} 回答。"])
            truthList[1] = {}
            truthList[2] = []
            return fin
    else: return "真心话还没开始你在结算什么啊(▼皿▼#)"
def endTruth()->str:
    if truthList[0]:
        truthList[0] = False
        return "好吧好吧，结束咯(一。一;;）"
    return "真心话还没开始你在结束什么啊(▼皿▼#)"
def afkDict() -> str:
    none = []
    for k, v in afk:
        none.append(f"{k}正在{v};")
    return "正在挂机的……\n" + "\n".join(none) or "大家都在哦"
LINE = {

    "listwh": lambda: f"当前白名单识别码：{'，'.join(whiteList)}",
    "listbn": lambda: f"当前黑名单昵称：{'，'.join(blackName)}",
    "listbl": lambda: f"当前黑名单hash：{'，'.join(blackList)}",
    "listig": lambda: f"当前被忽略的用户：{'，'.join(ignored)}",
    "listba": lambda: f"当前被封禁的hash：{'，'.join(banned)}",
    "listak": afkDict,
    "真心话": truth,
    "结算": atLast,
    "结束游戏": endTruth,
    "*bom": bom,
}

# 仿rate-limiter
records, halflife, threshold = {}, 25, 12

def now()->int:
    return int(time.time())
# 获取信息
def search(name: str)->dict:
    record = records.get(name)
    if not record:
        record = records[name] = {"time": now(), "score": 0, "warned": False}
    return record
# 监测与增加刷屏分（？）
def frisk(name: str, delta: float):
    record = search(name)
    score = record["score"]
    # 使分数随时间衰减，半衰期(与上次发言相差halflife秒时)为0.5
    record["score"] *= 2**(-(now()-record["time"])/halflife)
    # 低于阈值一半时取消警告
    if record["warned"] and score < (threshold/2):
        record["warned"] = False
    # 加分（？）
    record["score"] += delta
    record["time"] = now()
    # 分数达到阈值(threshold)时被rl
    if score >= threshold:
        return "limit"
    # 超过阈值三分之二时警告
    elif score >= (threshold/3*2) and not record["warned"]:
        record["warned"] = True
        return "warn"
    return None