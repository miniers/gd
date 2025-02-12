from telethon import events
from .. import jdbot, chat_id
from ..bot.utils import V4


@jdbot.on(events.NewMessage(from_users=chat_id, pattern='^/help'))
async def bot_help(event):
    """接收/help命令后执行程序"""
    msg_text = event.raw_text.split(' ')
    if len(msg_text) == 2:
        text = msg_text[-1]
    else:
        text = 'mhelp'
    if V4:
        mhelp = '''
pkc-检测状态
mx-查看监控明细
a-自定义快捷按钮
bean-获取收支
blockcookie-屏蔽账号
chart-统计收支变化
check-测试user连接
checkcookie-检测过期
clearboard-删除快捷输入按钮
cmd-执行cmd命令
edit-编辑文件
export-管理环境变量
help-获取帮助
getfile-获取jd目录下文件
log-选择日志
list-列出已拓展功能
node-执行js脚本文件，绝对路径
restart-重启本程序
redial-路由重新拨号
repo-仓库管理
set-BOT设置
setname-设置命令别名
setshort-设置自定义按钮
snode-选择脚本后台运行
start-开始使用本程序
upbot-升级机器人
ver-版本
cx-查询当前运行的进程
upgd-更新gd监控代码
clean-清理缓存日志'''
        bean = '/bean 加数字，获取该账户近期收支情况\n/bean in\\out获取所有账户近期收或支情况\n/bean 获取账户总豆数量'
        cmd = '/cmd用于执行shell命令，如果命令持续10分钟仍未结束，将强行终止，以保障机器人响应'
        edit = '/edit 进入/jd目录选择文件进行编辑，仅限简易编辑\n/edit /jd/config进入config目录选择文件编辑\n/edit /jd/config/config.sh 直接编辑config.sh文件'
        node = '/node 用于执行js脚本 用法：\n/node /jd/own/abc/def.js'
        getfile = '/getfile 进入/jd目录选择文件进行获取\n/getfile /jd/config进入config目录选择文件获取\n/getfile /jd/config/config.sh 直接获取config.sh文件'
        setshort = '/setshort 用于设置快捷方式，格式如下：\n更新-->jup\nAAA-->BBB这种格式使用/a选择\n/bean 1\n/edit /jd/config/config.sh\n以“/”开头的为机器人命令快捷，使用/b选择'
    else:
        mhelp = '''
pkc-检测状态
mx-查看监控明细
a-自定义快捷按钮
bean-获取收支
blockcookie-屏蔽账号
chart-统计收支变化
check-测试user连接
checkcookie-检测过期
clearboard-删除快捷输入按钮
cmd-执行cmd命令
edit-编辑文件
export-管理环境变量
help-获取帮助
getfile-获取jd目录下文件
log-选择日志
list-列出已拓展功能
node-执行js脚本文件，绝对路径
restart-重启本程序
redial-路由重新拨号
repo-仓库管理
set-BOT设置
setname-设置命令别名
setshort-设置自定义按钮
snode-选择脚本后台运行
start-开始使用本程序
upbot-升级机器人
ver-版本
cx-查询当前运行的进程
upgd-更新gd监控代码
clean-清理缓存日志'''
        bean = '/bean 加数字，获取该账户近期收支情况'
        cmd = '/cmd用于执行shell命令，如果命令持续10分钟仍未结束，将强行终止，以保障机器人响应'
        edit = '/edit 进入/ql目录选择文件进行编辑，仅限简易编辑\n/edit /ql/config进入config目录选择文件编辑\n/edit /ql/config/config.sh 直接编辑config.sh文件'
        node = '/node 用于执行js脚本 用法：\n/node /ql/own/abc/def.js'
        getfile = '/getfile 进入/jd目录选择文件进行获取\n/getfile /ql/config进入config目录选择文件获取\n/getfile /ql/config/config.sh 直接获取config.sh文件'
        setshort = '/setshort 用于设置快捷方式，格式如下：\nAAA-->BBB这种格式使用/a选择\n/bean 1\n/edit /ql/config/config.sh\n以“/”开头的为机器人命令快捷，使用/b选择'
    snode = '/snode 选择脚本并运行'
    chart = '/chart 加数字，统计该账户近期收支情况'
    botset = '''    /set
    - snode时中英文切换
    - 每列几个按钮
    - 是否开启机器人转发
    - 机器人聊天黑名单
        - 使用，或者空格等符号进行用户id区隔
    - 机器人黑名单垃圾话
        - 加入机器人黑名单后，使用 | 区隔设置垃圾话，会随机挑选垃圾话回复该用户'''
    cron = '''    - /cron 命令
    - /cron 加关键字 可进行cron管理'''
    help_me = {
        'bean': bean, 'cmd': cmd,
        'edit': edit, 'node': node,
        'getfile': getfile,
        'setshort': setshort,
        'snode': snode,
        'chart': chart,
        'mhelp': mhelp,
        'set': botset,
        'cron': cron
    }
    await jdbot.send_message(chat_id, help_me[text])
