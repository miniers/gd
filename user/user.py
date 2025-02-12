#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from datetime import datetime

import asyncio
import random
import os, time
import re
import sys
import json
from telethon import events, Button
# from .login import user
from .. import chat_id, jdbot, logger, TOKEN, user, jk, CONFIG_DIR, readJKfile, LOG_DIR, cache,spy_decode_url
from ..bot.utils import cmd, V4
from ..diy.utils import rwcon, myzdjr_chatIds, my_chat_id, forward_ids
jk_version = 'v1.2.9'
from ..bot.update import version as jk_version
from urllib import parse
import requests

requests.adapters.DEFAULT_RETRIES = 5
session = requests.session()
session.keep_alive = False

bot_id = int(TOKEN.split(":")[0])
client = user
######  初始化
## 新增配置自定义监控
nameList, envNameList, scriptPathList = [], [], []
jcDict = {}
dlDict = {}
todayEnv_tmp = {}
jk_list = jk["jk"]
cmdName = jk["cmdName"]
cmdParams = jk["cmdParams"] if jk["cmdParams"] else "now"
env_trans = jk["env_trans"]
monitor_converters_whitelist_keywords = jk["monitor_converters_whitelist_keywords"]
monitor_converters = jk["monitor_converters"]
patternStr = ''
v_today = time.strftime('%Y-%m-%d', time.localtime(time.time()))
jk_today_file = f'{LOG_DIR}/bot/jk-{v_today}.txt'
for i in jk_list:
    if i["isOpen"]:
        nameList.append(i["name"])
        envNameList.append(i["envName"])
        scriptPathList.append(i["scriptPath"])
        dlDict[i["name"]] = 0
dlDict["v"] = []
envNum = len(envNameList)
try:
    isNow = jk["isNow"]
except Exception as e:
    isNow = True
# 开启随机延时
if isNow:
    yanshi = ''
else:
    yanshi = 'now'

# 增加jk配置在线修改生效
@readJKfile
async def getJkConfig(jk):
    global cmdName, cmdParams, env_trans, isNow, log_send, log_type, patternStr, nameList, envNameList, scriptPathList, dlDict, yanshi, envNum, jk_list, jcDict, v_today, jk_today_file, todayEnv_tmp
    v_today = time.strftime('%Y-%m-%d', time.localtime(time.time()))
    jk_today_file = f'{LOG_DIR}/bot/jk-{v_today}.txt'
    """Do some math."""
    jk_list = jk["jk"]
    cmdName = jk["cmdName"]
    cmdParams = jk["cmdParams"] if jk["cmdParams"] else "now"
    env_trans = jk["env_trans"]
    dlDict = {}
    jcDict = {}
    todayEnv_tmp = {}
    patternStr = ''
    try:
        isNow = jk["isNow"]
        log_send = jk["log_send"]
        log_type = jk["log_type"]
    except Exception as e:
        isNow = True
        log_send = "1"
        log_type = "1"
    nameList, envNameList, scriptPathList = [], [], []
    for i in jk_list:
        if i["isOpen"]:
            nameList.append(i["name"])
            envNameList.append(i["envName"])
            scriptPathList.append(i["scriptPath"])
            dlDict[i["name"]] = 0
    if isNow:
        yanshi = ''
    else:
        yanshi = 'now'
    envNum = len(envNameList)
    for i in range(envNum):
        if i == envNum - 1:
            trans_env_keys = list(env_trans)
            patternStr += envNameList[i] + "|jd_redrain_url|jd_redrain_half_url|zjdbody"
            if len(trans_env_keys) > 0:
                patternStr += '|' + '|'.join(trans_env_keys)
        else:
            patternStr += envNameList[i] + "|"
    if os.path.exists(jk_today_file):
        with open(jk_today_file, "r", encoding="utf-8") as f1:
            todayEnv_tmp = json.load(f1)
    # else:
    #     with open(jk_today_file, "w+", encoding="utf-8") as f:
    #         f.write('{}')


    # return jk, cmdName, isNow, patternStr, nameList, envNameList, scriptPathList, dlDict, yanshi
    # readDL(True, dlDict)
    return jk


def readDL(write, dl=dlDict):
    if write:
        with open('duilie.json', "w+", encoding="utf-8") as f:
            json.dump(dl, f, ensure_ascii=False)
    else:
        with open('duilie.json', "r", encoding="utf-8") as f:
            dl = json.load(f)
    return dl

# 增加当天变量判断去重
async def isjkEnvToDay(key, value):
    isNewEnv = True
    try:
        if os.path.exists(jk_today_file):
            with open(jk_today_file, "r", encoding="utf-8") as f1:
                todayEnv = json.load(f1)
            for k in todayEnv:
                if k == key and k in envNameList:
                    if "activityId" in value:
                        # 增加去重activityId
                        value = re.findall(r"(?<=activityId=).[0-9A-Za-z]{10,32}", value)[0]
                        # logger.info(f"{value}  in {todayEnv[k]}")
                    if value in todayEnv[k]:
                        # logger.info(f"{value}")
                        # logger.info(f"{todayEnv[k]}")
                        isNewEnv = False
                        break
            if isNewEnv and key in envNameList:
                with open(jk_today_file, "w+", encoding="utf-8") as f:
                    if key in todayEnv.keys():
                        todayEnv[key].append(value)
                    else:
                        todayEnv[key] = []
                        todayEnv[key].append(value)
                    json.dump(todayEnv, f, ensure_ascii=False)
        else:
            with open(jk_today_file, "w+", encoding="utf-8") as f:
                if key in envNameList:
                    todayEnv = {}
                    todayEnv[key] = []
                    todayEnv[key].append(value)
                    json.dump(todayEnv, f, ensure_ascii=False)
                else:
                    f.write('{}')
    except Exception as e:
        logger.error(f"{e}")
    return isNewEnv

readDL(True)
########
# 开启队列
async def funCX(name, scriptPath, msg, group, lable=1):
    try:

        cxjc = f'ps -ef | egrep -v "tail|timeout|grep" | grep {os.path.basename(scriptPath)} | egrep "python|node"'
        result = os.popen(cxjc)
        r = result.readlines()
        if r:
            a = random.randint(60, 180) #队列检测休眠时间
            msg = await jdbot.edit_message(msg, f"【队列】{group} 的 `[{name}]` 变量当前已在跑，已加入队列等待。本次等待`{a}`秒后再次尝试。可发送【`监控明细`】查询队列情况。")
            if lable < 21:
                if lable == 1:
                    dl = readDL(False)
                    try:
                        dl[name] += 1
                    except:
                        dl[name] = 1
                    readDL(True, dl)
                lable += 1
                await asyncio.sleep(a)
                return await funCX(name, scriptPath, msg, group, lable)
        else:
            msg = await jdbot.edit_message(msg, f"【队列】`[{name}]`当前空闲，后台将随机延时执行。")
    except Exception as e:
        logger.error(f"funCX->{e}")
    return msg

# 查询当前已运行
async def funCXDL():
    await getJkConfig(jk)
    dl = readDL(False)
    # logger.info(dl)
    for n, i in zip(nameList, scriptPathList):
        cxjc = f'ps -ef | egrep -v "tail|timeout|grep" | grep {os.path.basename(i)} | egrep "python|node"'
        result = os.popen(cxjc)
        r = result.readlines()
        jcDict[n] = len(r)

    dlmsg = ''
    # logger.info(jcDict)
    n = 1
    count_dtNum = 0
    for i, e in zip(jcDict, envNameList):
        if jcDict[i] > 0:
            jcNum = f'`{jcDict[i]}`'
        else:
            jcNum = jcDict[i]
        try:
            if dl[i] > 0:
                dlNum = f'`{dl[i]}`'
            else:
                dlNum = dl[i]
        except:
            dlNum = 0
        if e in todayEnv_tmp.keys():
            dtNum = len(todayEnv_tmp[e])
        else:
            dtNum = 0
        count_dtNum += dtNum
        dlmsg += f"当前:{jcNum} | 队列:{dlNum} | 今天:{dtNum}\t【{n}.{i}】\n"
        n += 1
    if log_send == "1":
        log_send_msg = "bot发送"
    else:
        log_send_msg = "user发送"
    if log_type == "1":
        log_type_msg = "默认"
    else:
        log_type_msg = "txt文件"
    if isNow:
        dlmsg += f"\n是否队列等待: `已开启`\n"
    else:
        dlmsg += f"\n是否队列等待:`未开启`（如需开启，请配置jk.json的参数isNow=true）\n"
    dlmsg += f"\n日志发送模式: `{log_send_msg}`\n\n日志显示形式: `{log_type_msg}`"
    dlmsg += f"\n\n{v_today}: 监控`{count_dtNum}`次"
    return dlmsg

# 增加再进入队列之前判断重复变量
async def isduilie(kv):
    is_in = False
    dl = readDL(False)
    for i in dl['v']:
        if kv == i:
            is_in = True
            break
    if not is_in:
        dl = readDL(False)
        dl['v'].append(kv)
        readDL(True, dl)
    return is_in

@client.on(events.NewMessage(chats=bot_id, from_users=chat_id, pattern=r"^(/pkc|user|在吗)(\?|\？|)"))
async def users(event):
    try:
        dlmsg = await funCXDL()
        msg = await jdbot.send_message(chat_id, f'靓仔你好，pkc监控`{jk_version}`已正常启动！\n\n配置变量: `{len(jk_list)}` | 当前监控: `{envNum}`')
        await asyncio.sleep(3)
        msg = await jdbot.edit_message(msg, f'\n================\n\t\t\t\t\t\t\t监控明细\n================\n{dlmsg}')
        await asyncio.sleep(30)
        await jdbot.delete_messages(chat_id, msg)
        await client.delete_messages(chat_id, event.message)
    except Exception as e:
        title = "【💥错误💥】"
        name = "文件名：" + os.path.split(__file__)[-1].split(".")[0]
        function = "函数名：" + sys._getframe().f_code.co_name
        tip = '建议百度/谷歌进行查询'
        await jdbot.send_message(chat_id, f"{title}\n\n{name}\n{function}\n错误原因：{str(e)}\n\n{tip}")
        logger.error(f"错误--->{str(e)}")

@client.on(events.NewMessage(chats=bot_id, from_users=chat_id, pattern=r"^(监控明细|/mx)$"))
async def user_mx(event):
    try:
        # await getJkConfig(jk)
        dlmsg = await funCXDL()
        msg = await jdbot.send_message(chat_id, f'\n================\n\t\t\t\t\t\t\t监控明细\n================\n{dlmsg}')
        await asyncio.sleep(30)
        await jdbot.delete_messages(chat_id, msg)
        await client.delete_messages(chat_id, event.message)
    except Exception as e:
        title = "【💥错误💥】"
        name = "文件名：" + os.path.split(__file__)[-1].split(".")[0]
        function = "函数名：" + sys._getframe().f_code.co_name
        tip = '建议百度/谷歌进行查询'
        await jdbot.send_message(chat_id, f"{title}\n\n{name}\n{function}\n错误原因：{str(e)}\n\n{tip}")
        logger.error(f"错误--->{str(e)}")

def get_text(origin):
    spy_text = re.findall(r'^(.*)(SpyEncode_.*?)([\'"])', origin)

    if len(spy_text) > 0 and spy_decode_url:
        try:
            resp = requests.post(spy_decode_url, json={'data':spy_text[0][1]})
            origin = f'{spy_text[0][0]}{resp.text}{spy_text[0][2]}'
            logger.info(f"spy变量: {origin}")
            return origin
        except:
            pass
    text = re.findall(r'https://i.walle.com/api\?data=(.+)?\)', origin)
    if len(text) > 0:
        text = parse.unquote_plus(text[0])
    elif origin.startswith("export "):
        text = origin
    else:
        return origin
    try:
        # logger.info(f"原始数据 {text}")
        # 微定制
        if "WDZactivityId" in text:
            activity_id = re.search(f'WDZactivityId="(.+?)"', text)[1]
            text = f'export jd_wdz_custom="{activity_id}"'
        logger.info(f"walle变量: {text}")
        return text
    except Exception as e:
        logger.error(e)
        return origin

@jdbot.on(events.CallbackQuery(chats=chat_id, pattern=r"^re_run\s.*"))
async def click_callback(event):
    try:
        val_key = re.findall(r"^re_run\s(.*)", event.data.decode())[0]
        data = cache.get(val_key)
        if data:
            data = json.loads(data)
            all_kv = data['all_kv']
            kvs = all_kv.split('\n')
            configs = rwcon("str")
            for ex in kvs:
                if "export " not in ex:
                    continue
                kv = ex.replace("export ", "")
                key = kv.split("=")[0]
                if key in configs:
                    configs = re.sub(f'{key}=("|\').*("|\').*', kv, configs)
                else:
                    configs += f'export {kv}"\n'
            rwcon(configs)
            script_path = data['scriptPath']
            await event.respond('开始重新执行 {}!'.format(val_key))
            await cmd(f'{cmdName} {script_path} {cmdParams}', val_key)
        else:
            await event.respond('读取执行配置失败!')

    except Exception as e:
        logger.error(e)
        await event.respond('重新执行失败!')
async def re_send(name,msg):
    for cid in forward_ids:
        await user.send_message(cid, f'[{name}]\n{msg}')
# @client.on(events.NewMessage(chats=myzdjr_chatIds, pattern=r'%s' % pat))


async def converter_handler(text):
    text = "\n".join(list(filter(lambda x: "export " in x, text.replace("`", "").split("\n"))))
    for c_w_key in monitor_converters_whitelist_keywords:
        result = re.search(c_w_key, text)
        if result is not None:
            logger.info(f"无需转换 {text}")
            return text
    # logger.info(f"转换前数据 {text}")
    try:
        tmp_text = text
        # 转换
        for c_key in monitor_converters:
            result = re.search(c_key, text)
            if result is None:
                # logger.info(f"规则不匹配 {c_key},下一个")
                continue
            rule = monitor_converters.get(c_key)
            target = rule.get("env")
            argv_len = len(re.findall("%s", target))
            values = re.findall(r'"([^"]*)"', text)
            if argv_len == 1:
                target = target % (values[0])
            elif argv_len == 2:
                target = target % (values[0], values[1])
            elif argv_len == 3:
                target = target % (values[0], values[1], values[2])
            else:
                print("不支持更多参数")
            text = target
            break
    except Exception as e:
        logger.info(str(e))
    logger.info(f"转换后数据 {text}")
    return text



@client.on(events.NewMessage(chats=myzdjr_chatIds))
async def activityID(event):
    try:
        await getJkConfig(jk)
        pat = '(.|\\n)*export\s(%s)=(".*"|\'.*\')' % patternStr
        text = get_text(event.message.text)
        text = await converter_handler(text)
        #export M_WX_LUCK_DRAW_URL="https://lzkj-isv.isvjd.com/wxDrawActivity/activity/activity?activityId=106814ae61ac406c8879aed53d044a9a"
        # text = event.message.text
        msg_result = re.findall(pat, text)
        if len(msg_result) > 0:
            pass
        else:
            return
        try:
            group = f'[{event.chat.title}](https://t.me/c/{event.chat.id}/{event.message.id})'
        except Exception as e:
            logger.error(f"错误22--->{str(e)}")
            if event.chat and event.message:
                group = f'[{event.chat.id}](https://t.me/c/{event.chat.id}/{event.message.id})'
            else:
                group = f''
        name = None
        if env_trans is not None:
            for trans_key in list(env_trans):
                if trans_key in text:
                    text = re.sub(r'export\s%s' % trans_key, r'export %s' % env_trans[trans_key], text)
        for i in envNameList:
            if i in text:
                name = nameList[envNameList.index(i)]
                scriptPath = scriptPathList[envNameList.index(i)]
                break
            elif "zjdbody" in text:
                name = "赚喜豆-每天90豆"
                scriptPath = '/ql/data/scripts/pkc_zjd.js'
                break
            elif "jd_redrain_url" in text:
                name = "整点京豆雨"
                scriptPath = 'xxxxxxxxx'
                break
            elif "jd_redrain_half_url" in text:
                name = "半点京豆雨"
                scriptPath = 'xxxxxxxxx'
                break
        if not name:
            return
        msg = await jdbot.send_message(chat_id, f'【监控】{group} 发出的 `[{name}]` 环境变量！', link_preview=False)
        messages = text.split("\n")
        change = ""
        is_exec = ""
        all_kv = ""
        for message in messages:
            force_run = True if "fexport" in message else False
            if "export " not in message:
                continue
            kvs = re.sub(r'.*export ', 'export ', message,0, re.S)
            kv = kvs.replace("export ", "")
            key = kv.split("=")[0]
            valuelist = re.findall(r'[\'|"]([^"]*)[\'|"]', kv)
            # 一些变量没有双引号情况处理
            if len(valuelist) == 0:
                value = kv.split("=")[1]
            else:
                value = valuelist[0]
            configs = rwcon("str")
            # 去掉一些奇怪的符号。
            kv = kv.replace('`', '').replace('*', '')
            key = key.replace('`', '').replace('*', '')
            value = value.replace('`', '').replace('*', '')
            isNewEnv = await isjkEnvToDay(key, value)
            all_kv += f"export {kv}\n"
            if not isNewEnv and not force_run:
                is_exec = f"【重复】{group} 发出的 `[{name}]`当天变量已重复, 本次取消改动。\n`fexport {kv}`\n\n"
                logger.info(is_exec)
                continue
            if value in configs and not force_run:
                is_exec = f"【取消】{group} 发出的 `[{name}]` 配置文件已是该变量，无需改动！\n`fexport {kv}`\n\n"
                continue
            if key in configs:
                if await isduilie(kv):
                    # msg = await jdbot.edit_message(msg, f"变量已在队列【{kv}】, 本次取消改动。")
                    is_exec = f"【队列】{group} 发出的 `[{name}]` 变量已在队列，本次取消改动！\n`fexport {kv}`\n\n"
                    continue
                if isNow:
                    # 进入队列检测前随机休眠，防止并行检测。
                    a = random.randint(1, 10)
                    await asyncio.sleep(a)
                    if scriptPath:
                        msg = await funCX(name, scriptPath, msg, group)
                    else:
                        msg = await jdbot.edit_message(msg, f"【{name}】脚本路径未配置，跳过检测！")
                    configs = rwcon("str")
                    if kv in configs and not force_run:
                        is_exec = f"【取消】{group} 发出的 `[{name}]` 配置文件已是该变量，无需改动！\n`fexport {kv}`\n\n"
                        continue
                if 'VENDER_ID' in key:
                    # 监控开卡随机休眠
                    a = random.randint(3, 10)
                    await asyncio.sleep(a)
                configs = re.sub(f'{key}=("|\').*("|\').*', kv, configs)
                change += f"【{'强制替换' if force_run else '替换' }】{group} 发出的 `[{name}]` 环境变量成功\n`fexport {kv}`\n\n"
                # msg = await jdbot.edit_message(msg, change, buttons=Button.inline("重新执行", data=f"re_run {val_key}"))
                msg = await jdbot.edit_message(msg, change)
            else:
                if V4:
                    end_line = 0
                    configs = rwcon("list")
                    for config in configs:
                        if "第五区域" in config and "↑" in config:
                            end_line = configs.index(config) - 1
                            break
                    configs.insert(end_line, f'export {key}="{value}"\n')
                else:
                    configs = rwcon("str")
                    configs += f'export {key}="{value}"\n'
                change += f"【新增】{group} 发出的 `[{name}]` 环境变量成功\n`fexport {kv}`\n\n"
                msg = await jdbot.edit_message(msg, change)
            rwcon(configs)
        cache_key=""
        if all_kv and change:
            if scriptPath:
                count_key = f"bot_{v_today}_{name}_count"
                cache.incr(count_key)
                index = cache.get(count_key)
                today = datetime.today()
                dt = datetime(year=today.year, month=today.month, day=today.day, hour=23, minute=59, second=59)
                cache.expire(count_key, int(dt.timestamp() - time.time()))
                cache_key = f"bot_{v_today}_{name}_{index}"
                cache.set(cache_key, json.dumps({
                    "scriptPath": scriptPath,
                    "all_kv": all_kv,
                }), ex=7*24*60*60)
                msg = await jdbot.edit_message(msg, change, buttons=Button.inline("重新执行", data=f"re_run {cache_key}"))
            #转发
            if "fexport" not in text:
                await re_send(name, all_kv)
        if len(change) == 0:
            # await jdbot.edit_message(msg, f"【取消】{group} 发出的 `[{name}]` 变量无需改动！")
            if is_exec:
                msg = await jdbot.edit_message(msg, is_exec)
            await asyncio.sleep(5)
            # await jdbot.delete_messages(chat_id, msg)
            return
        try:
            lable = None
            for i in envNameList:
                if i in text:
                    lable = True
                    dl = readDL(False)
                    if dl[name] > 0:
                        dl[name] -= 1
                        readDL(True, dl)
                    try:
                        for v in dl['v']:
                            if kv == v:
                                dl['v'].remove(kv)
                                readDL(True, dl)
                    except:
                        pass
                    if scriptPath:
                        await cmd(f'{cmdName} {scriptPath} {cmdParams}', cache_key)
                    else:
                        await jdbot.edit_message(msg, f"【{name}】脚本路径未配置，跳过执行！")
                    break
                # 赚京豆助力，将获取到的团body发给自己测试频道，仅自己内部助力使用
                # elif "zjdbody" in text:
                #     lable = True
                #     if str(event.chat.id) in str(my_chat_id):
                #         await cmd(f'{cmdName} /ql/data/scripts/pkc_zjd.js {cmdParams}')
                #     break
                # elif "jd_redrain_url" in text:
                #     lable = True
                #     msg = await jdbot.send_message(chat_id, r'`更换整点雨url完毕\n请定时任务0 0 * * * task jd_redrain now')
                #     await asyncio.sleep(1)
                #     await jdbot.delete_messages(chat_id, msg)
                #     break
                # elif "jd_redrain_half_url" in text:
                #     lable = True
                #     msg = await jdbot.send_message(chat_id, r'`更换半点雨url完毕\n请定时任务30 21,22 * * * task jd_redrain_half now')
                #     await asyncio.sleep(1)
                #     await jdbot.delete_messages(chat_id, msg)
                #     break
            if not lable:
                await jdbot.send_message(chat_id, f"看到这行字,是有严重BUG!")
        except ImportError:
            pass
    except Exception as e:
        title = "【💥错误💥】"
        name = "文件名：" + os.path.split(__file__)[-1].split(".")[0]
        function = "函数名：" + sys._getframe().f_code.co_name
        tip = '建议百度/谷歌进行查询'
        await jdbot.send_message(chat_id, f"{title}\n\n{name}\n{function}\n错误原因：{str(e)}\n\n{tip}")
        logger.error(f"错误--->{str(e)}")
