import json

import re

import sys

import os
from asyncio import exceptions

from telethon import events, Button

# from .login import user
from .. import user, jdbot, chat_id, logger, cache


def press_event(user_id):
    return events.CallbackQuery(func=lambda e: e.sender_id == user_id)



@user.on(events.NewMessage(pattern=r'^停签$', outgoing=True))
async def stop_sevenday_sign(event):
    try:
        # SENDER = event.sender_id
        message = await event.get_reply_message()
        if message:
            msg_content = message.text
            act_ids = re.findall(r'\((.{32})\)', msg_content, re.M)
            if act_ids and len(act_ids) == 1:
                act_id = act_ids[0]
                # btns = [Button.inline("是", data='yes'), Button.inline("否", data='cancel')]
                # async with jdbot.conversation(SENDER, timeout=60) as conv:
                #     msg = await conv.send_message(f"确认停止 {act_id} 的签到吗？", buttons=btns)
                #     convdata = await conv.wait_event(press_event(SENDER))
                #     res = bytes.decode(convdata.data)
                #     if res == 'cancel':
                #         await jdbot.edit_message(msg, '已取消')
                #         conv.cancel()
                #         return
                #     else:
                #         msg = await jdbot.edit_message(msg, f"好的，开始停止 {act_id} 的签到")
                #     conv.cancel()
                cache.set(f'sevenday_stop_{act_id}', '手动停止')
                await event.respond(f'签到 {act_id} 已成功停止')
            else:
                await event.respond(f'没有找到签到ID')
    # except exceptions.TimeoutError:
        # await jdbot.edit_message(msg, '选择已超时，对话已停止，感谢你的使用')
    except Exception as e:
        title = "【💥错误💥】"
        name = "文件名：" + os.path.split(__file__)[-1].split(".")[0]
        function = "函数名：" + sys._getframe().f_code.co_name
        tip = '建议百度/谷歌进行查询'
        await jdbot.send_message(chat_id, f"{title}\n\n{name}\n{function}\n错误原因：{str(e)}\n\n{tip}")
        logger.error(f"错误--->{str(e)}")

@user.on(events.NewMessage(pattern=r'^规则$', outgoing=True))
async def sevenday_sign_info(event):
    try:
        # SENDER = event.sender_id
        message = await event.get_reply_message()
        if message:
            msg_content = message.text
            act_ids = re.findall(r'\((.{32})\)', msg_content, re.M)
            if act_ids and len(act_ids) == 1:
                act_id = act_ids[0]
                data = json.loads(cache.get(f'sevenday_info_{act_id}_org'))
                act = data['actRule'] if 'actRule' in data else data['act']['actRule']
                await event.respond(f'签到 {act_id} :\n{act}')
            else:
                await event.respond(f'没有找到签到ID')
    # except exceptions.TimeoutError:
        # await jdbot.edit_message(msg, '选择已超时，对话已停止，感谢你的使用')
    except Exception as e:
        title = "【💥错误💥】"
        name = "文件名：" + os.path.split(__file__)[-1].split(".")[0]
        function = "函数名：" + sys._getframe().f_code.co_name
        tip = '建议百度/谷歌进行查询'
        await jdbot.send_message(chat_id, f"{title}\n\n{name}\n{function}\n错误原因：{str(e)}\n\n{tip}")
        logger.error(f"错误--->{str(e)}")
