#!/usr/bin/env python3
# -*- coding: utf-8 -*-


import os
import sys
from librouteros import connect

from telethon import events

from .. import chat_id, jdbot, logger, ch_name, BOT_SET


@jdbot.on(events.NewMessage(from_users=chat_id, pattern=r'^/redial'))
async def myredial(event):
    try:
        msg = await jdbot.send_message(chat_id, "开始重新拨号")
        ros_config = os.environ['ROS_CONFIG']
        configs = ros_config.split('&&')
        api = connect(
            username=configs[1],
            password=configs[2],
            host=configs[0],
            timeout=30
        )
        script = api.path('system', 'script')
        try:
            tuple(script('run', **{'.id': 're_dial'}))
        except Exception as e:
            ips = e.message.split(',')
            await jdbot.edit_message(msg, f"重新拨号成功，旧IP为：{ips[0]},新IP为:{ips[1]}")
    except Exception as e:
        title = "【💥错误💥】"
        name = "文件名：" + os.path.split(__file__)[-1].split(".")[0]
        function = "函数名：" + sys._getframe().f_code.co_name
        tip = '建议百度/谷歌进行查询'
        await jdbot.send_message(chat_id, f"{title}\n\n{name}\n{function}\n错误原因：{str(e)}\n\n{tip}")
        logger.error(f"错误--->{str(e)}")


if ch_name:
    jdbot.add_event_handler(myredial, events.NewMessage(from_users=chat_id, pattern=BOT_SET['命令别名']['redial']))
