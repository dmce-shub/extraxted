# MIT License
# Copyright (c) 2019-present Dan <https://github.com/delivrance>

import urllib
import urllib.parse
import requests
import json
import subprocess
import os
import sys
import re
import time
import logging
import cloudscraper

from base64 import b64encode, b64decode
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad

import pyrogram
import tgcrypto
import helper
from pyromod import listen
from pyrogram import Client, filters
from pyrogram import Client as bot
from pyrogram.types import User, Message, InlineKeyboardButton, InlineKeyboardMarkup
from pyrogram.types.messages_and_media import message
from pyrogram.errors import FloodWait
from p_bar import progress_bar
from subprocess import getstatusoutput


@bot.on_message(filters.command(["cp"]))
async def account_login(bot: Client, m: Message):
    global cancel
    cancel = False
    s = requests.Session()
    
    editable = await m.reply_text("**Send Token from ClassPlus App**")
    input1: Message = await bot.listen(editable.chat.id)
    raw_text0 = input1.text.strip()
    
    headers = {
        'authority': 'api.classplusapp.com',
        'accept': 'application/json, text/plain, */*',
        'accept-language': 'en',
        'api-version': '28',
        'cache-control': 'no-cache',
        'device-id': '516',
        'origin': 'https://web.classplusapp.com',
        'pragma': 'no-cache',
        'referer': 'https://web.classplusapp.com/',
        'region': 'IN',
        'sec-ch-ua': '"Chromium";v="107", "Not=A?Brand";v="24"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Linux"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-site',
        'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36',
        'x-access-token': '{raw_text0}'
        'orgCode': 'QNQKBN'
    }
    
    resp = s.get('https://api.classplusapp.com/v2/batches/details?limit=20&offset=0&sortBy=createdAt', headers=headers)
    
    # 1. Ensure execution stops on HTTP error
    if resp.status_code != 200:
        await m.reply_text(f"❌ Login Failed (HTTP {resp.status_code}). Please check your token.")
        return

    res_json = resp.json()
    
    # 2. Safely parse response data structure
    data_field = res_json.get("data", {})
    if isinstance(data_field, list):
        b_data = data_field
    elif isinstance(data_field, dict):
        b_data = data_field.get("totalBatches") or data_field.get("batches") or []
    else:
        b_data = []

    if not b_data:
        await m.reply_text("⚠️ No batches found for this account/token.")
        return

    try:
        await input1.delete(True)
    except Exception:
        pass

    cool = ""
    FFF = "**BATCH-ID - BATCH NAME**"
    for item in b_data:
        t_name = item.get('batchName', 'N/A')
        t_id = item.get('batchId') or item.get('id', 'N/A')
        aa = f" ```{t_id}```  - **{t_name}**\n\n"
        if len(f'{cool}{aa}') > 4096:
            await editable.edit(f'**You have these batches :-**\n\n{FFF}\n\n{cool}')
            cool = ""
        cool += aa

    if cool:
        await editable.edit(f'**You have these batches :-**\n\n{FFF}\n\n{cool}')

    editable1 = await m.reply_text("**Now send the Batch ID to Download**")
    input2: Message = await bot.listen(editable.chat.id)
    cr = input2.text.strip()
    
    try:
        await editable1.delete(True)
        await input2.delete(True)
    except Exception:
        pass

    resp = s.get(f'https://api.classplusapp.com/v2/course/content/get?courseId={cr}', headers=headers)
    if resp.status_code != 200:
        await m.reply_text("❌ Failed to fetch course content. Invalid Batch ID.")
        return

    b_data = resp.json().get('data', {}).get('courseContent', [])
    cool = ""
    FFF = "**FOLDER-ID - FOLDER NAME**"
    for item in b_data:
        id1 = item.get('id', '')
        nam2 = item.get('name', '')
        aa = f" ```{id1}```      - **{nam2}**\n\n"
        if len(f'{cool}{aa}') > 4096:
            await editable.edit(f'**You have these Folders :-**\n\n{FFF}\n\n{cool}')
            cool = ""
        cool += aa

    if cool:
        await editable.edit(f'**You have these Folders :-**\n\n{FFF}\n\n{cool}')

    editable1 = await m.reply_text("**Now send the Folder ID to Download**")
    input3: Message = await bot.listen(editable.chat.id)
    raw_text2 = input3.text.strip()
    
    try:
        await editable1.delete(True)
        await input3.delete(True)
    except Exception:
        pass

    resp = s.get(f'https://api.classplusapp.com/v2/course/content/get?courseId={cr}&folderId={raw_text2}', headers=headers)
    if resp.status_code != 200:
        await m.reply_text("❌ Failed to fetch subfolder content.")
        return

    respc = resp.json()
    ddata = respc.get('data', {}).get('courseContent', [])
    if not ddata:
        await m.reply_text("⚠️ This folder is empty.")
        return

    if ddata[0].get("contentType") == 1:
        cool = ""
        FFF = "**FOLDER-ID - FOLDER NAME - TOTAL VIDEOS/PDFS**"
        for datas in ddata:
            id2 = datas.get('id', '')
            nam2 = datas.get('name', '')
            vid2 = datas.get('resources', {}).get('videos', 0)
            fid = datas.get('resources', {}).get('files', 0)
            aa = f" ```{id2}``` - **{nam2} - {vid2} Videos / {fid} Files**\n\n"
            if len(f'{cool}{aa}') > 4096:
                await editable.edit(f'**You have these Folders :-**\n\n{FFF}\n\n{cool}')
                cool = ""
            cool += aa

        if cool:
            await editable.edit(f'**You have these Folders :-**\n\n{FFF}\n\n{cool}')

        editable1 = await m.reply_text("**Now send the Folder ID to Download**")
        input4: Message = await bot.listen(editable.chat.id)
        raw_text4 = input4.text.strip()
        
        try:
            await editable1.delete(True)
            await input4.delete(True)
        except Exception:
            pass

        resp = s.get(f'https://api.classplusapp.com/v2/course/content/get?courseId={cr}&folderId={raw_text4}', headers=headers)
        bdat = resp.json().get('data', {}).get('courseContent', [])
        bdat.reverse()

        cool = ""
        FFF = "**Topic-ID - Topic NAME**"
        mm = "careerplus1"
        
        if os.path.exists(f"{mm}.txt"):
            os.remove(f"{mm}.txt")

        for item in bdat:
            id1 = item.get('id', '')
            nam2 = item.get('name', '')
            dis2 = item.get('description', '')
            url2 = item.get('url', '')
            aa = f" ```{id1}``` - **{nam2}  -{dis2}**\n\n"
            if len(f'{cool}{aa}') > 4096:
                cool = ""
            cool += aa
            with open(f'{mm}.txt', 'a', encoding='utf-8') as f:
                f.write(f"{nam2}-{dis2}:{url2}\n")

        if os.path.exists(f"{mm}.txt"):
            await m.reply_document(f"{mm}.txt")
        await editable.edit(f'**You have these Videos :-**\n\n{FFF}\n\n{cool}')

    else:
        ddata.reverse()
        cool = ""
        FFF = "**Topic-ID - Topic NAME**"
        mm = "classplus"

        if os.path.exists(f"{mm}.txt"):
            os.remove(f"{mm}.txt")

        for item in ddata:
            id2 = str(item.get('id', ''))
            nam2 = item.get('name', '')
            url2 = item.get('url', '')
            des2 = item.get('description', '')

            aa = f" ```{id2}``` - **{nam2}  -{des2}**\n\n"
            if len(f'{cool}{aa}') > 4096:
                cool = ""
            cool += aa

            with open(f'{mm}.txt', 'a', encoding='utf-8') as f:
                f.write(f"{nam2}-{des2}:{url2}\n")

        if os.path.exists(f"{mm}.txt"):
            await m.reply_document(f"{mm}.txt")
        await editable.edit(f'**You have these Videos :-**\n\n{FFF}\n\n{cool}')
        await m.reply_text("**Now Press /cpd to Download**")
