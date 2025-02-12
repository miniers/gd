#!/usr/bin/env python3
# -*- coding: utf-8 -*-


import os
import sys
import requests
import re
from telethon import events, Button
from ..bot.utils import press_event, V4
from .. import chat_id, jdbot, logger, BOT_SET
from ..bot.update import version as jk_version
from ..bot.utils import cmd


async def getNewVer():
    url = 'https://raw.githubusercontent.com/curtinlv/gd/main/bot/update.py'
    if '下载代理' in BOT_SET.keys() and str(BOT_SET['下载代理']).lower() != 'false' and 'github' in url:
        url = f'{BOT_SET["下载代理"]}/{url}'
    newversion = None
    r = requests.get(url)
    if r.status_code == 200:
        newver = re.findall(r'^version.*\'(.*?)\'$', r.text, re.M)
        if len(newver) > 0:
            newversion = newver[0]
    return newversion


@jdbot.on(events.NewMessage(from_users=chat_id, pattern=r'^/upgd$'))
async def upgdjk(event):
    try:
        SENDER = event.sender_id
        btns = [Button.inline("Yes, I do.", data='yes'), Button.inline("No~", data='cancel')]
        async with jdbot.conversation(SENDER, timeout=60) as conv:
            msg = await conv.send_message(f"您是否更新gd", buttons=btns, link_preview=False)
            convdata = await conv.wait_event(press_event(SENDER))
            res = bytes.decode(convdata.data)
            if res == 'cancel':
                await jdbot.edit_message(msg, '对话已取消，感谢你的使用')
                await jdbot.delete_messages(chat_id, msg)
                conv.cancel()
                return
            conv.cancel()
        if V4:
            msg = await jdbot.send_message(chat_id, "抱歉！暂不支持v4在线更新监控！")
            await jdbot.delete_messages(chat_id, msg)
        else:
            await cmd('ql bot 2>&1 > /ql/data/log/bot/up.log &')

    except Exception as e:
        title = "【💥错误💥】"
        name = "文件名：" + os.path.split(__file__)[-1].split(".")[0]
        function = "函数名：" + sys._getframe().f_code.co_name
        tip = '建议百度/谷歌进行查询'
        msg = await jdbot.send_message(chat_id, f"你的选择已超时。本次取消。\n{str(e)}")
        # if len(e) > 0:
        #     await jdbot.send_message(chat_id, f"{title}\n\n{name}\n{function}\n错误原因：{str(e)}\n\n{tip}")
        # else:
        #     msg = await jdbot.edit_message(msg, f"已超时")
        #     await jdbot.delete_messages(chat_id, msg)
        logger.error(f"错误--->{str(e)}")
