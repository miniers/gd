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
        if len(configs) < 3:
            await msg.edit("ROS_CONFIG格式错误")
            return
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
            if len(e.message) > 0:
                ips = e.message.split(',')
                if len(ips) > 0:
                    old_ip = ips[0]
                    new_ip = ips[1]
                    await jdbot.edit_message(msg, f"重新拨号成功，旧IP为：{old_ip},新IP为:{new_ip}")
    except Exception as e:
        title = "【💥错误💥】"
        name = "文件名：" + os.path.split(__file__)[-1].split(".")[0]
        function = "函数名：" + sys._getframe().f_code.co_name
        tip = '建议百度/谷歌进行查询'
        await jdbot.send_message(chat_id, f"{title}\n\n{name}\n{function}\n错误原因：{str(e)}\n\n{tip}")
        logger.error(f"错误--->{str(e)}")


if ch_name:
    jdbot.add_event_handler(myredial, events.NewMessage(from_users=chat_id, pattern=BOT_SET['命令别名']['redial']))
