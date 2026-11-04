#  MIT License
#
#  Copyright (c) 2019-present Dan <https://github.com/delivrance>
#
#  Permission is hereby granted, free of charge, to any person obtaining a copy
#  of this software and associated documentation files (the "Software"), to deal
#  in the Software without restriction, including without limitation the rights
#  to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
#  copies of the Software, and to permit persons to whom the Software is
#  furnished to do so, subject to the following conditions:
#
#  The above copyright notice and this permission notice shall be included in all
#  copies or substantial portions of the Software.
#
#  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#  IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#  FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#  AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#  LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
#  OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
#  SOFTWARE
#  Code edited By Cryptostark
import urllib
import urllib.parse
import requests
import json
import subprocess
from pyrogram.types.messages_and_media import message
import helper
from pyromod import listen
from pyrogram.types import Message
import tgcrypto
import pyrogram
from pyrogram import Client, filters
from pyrogram.types.messages_and_media import message
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from pyrogram.errors import FloodWait
import time
from pyrogram import Client as bot
from pyrogram.types import User, Message
from p_bar import progress_bar
from subprocess import getstatusoutput
import logging
import os
import sys
import re
import cloudscraper
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad
from base64 import b64encode, b64decode

@bot.on_message(filters.command(["cp"]) & ~filters.edited)
async def account_login(bot: Client, m: Message):
    global cancel
    cancel = False
    s = requests.Session()
    
    # --- Start OTP Login Flow ---
    editable = await m.reply_text("**Send Org Code (e.g., SPCC):**")
    input_org: Message = await bot.listen(editable.chat.id)
    org_code = input_org.text.strip().lower()
    await input_org.delete(True)
    
    await editable.edit("**Send Phone Number (10 digits):**")
    input_phone: Message = await bot.listen(editable.chat.id)
    phone_number = input_phone.text.strip()
    await input_phone.delete(True)
    
    login_headers = {
        'authority': 'api.classplusapp.com',
        'accept': 'application/json, text/plain, */*',
        'api-version': '28',
        'device-id': '516',
        'origin': 'https://web.classplusapp.com',
        'referer': 'https://web.classplusapp.com/',
        'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36'
    }
    
    await editable.edit("**Requesting OTP...**")
    otp_payload = {
        "orgCode": org_code,
        "mobileNumber": phone_number
    }
    
    try:
        otp_res = s.post('https://api.classplusapp.com/v2/otp/generate', headers=login_headers, json=otp_payload)
        otp_res_data = otp_res.json()
        
        if otp_res.status_code != 200 or otp_res_data.get('status') == 'error':
            return await editable.edit(f"**Failed to Generate OTP!**\nResponse: {otp_res.text}")
            
        session_id = otp_res_data['data']['sessionId']
    except Exception as e:
        return await editable.edit(f"**Error generating OTP:** {str(e)}")

    await editable.edit("**OTP sent successfully! Please enter the OTP:**")
    input_otp: Message = await bot.listen(editable.chat.id)
    otp_code = input_otp.text.strip()
    await input_otp.delete(True)
    
    await editable.edit("**Verifying OTP...**")
    verify_payload = {
        "otp": otp_code,
        "orgCode": org_code,
        "mobileNumber": phone_number,
        "sessionId": session_id
    }
    
    try:
        verify_res = s.post('https://api.classplusapp.com/v2/users/verify', headers=login_headers, json=verify_payload)
        verify_res_data = verify_res.json()
        
        if verify_res.status_code != 200 or verify_res_data.get('status') == 'error':
            return await editable.edit(f"**Failed to Verify OTP!**\nResponse: {verify_res.text}")
            
        raw_text0 = verify_res_data['data']['token']
    except Exception as e:
        return await editable.edit(f"**Error verifying OTP:** {str(e)}")
    
    await editable.edit("**Login Successful! Fetching batches...**")
    # --- End OTP Login Flow ---

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
    'x-access-token':f'{raw_text0}'
    }
    
    resp = s.get('https://api.classplusapp.com/v2/batches/details?limit=20&offset=0&sortBy=createdAt', headers=headers)
    if resp.status_code==200:
        pass
    else:
        editable = await m.reply_text("Login Failed Check Response")
    b_data = resp.json()["data"]["totalBatches"]
    print(b_data)
    cool = ""
    for data in b_data:
        t_name =data['batchName']
        t_id =data['batchId']
        FFF = "**BATCH-ID - BATCH NAME**"
        aa = f" ```{t_id}```  - **{t_name}**\n\n"
        if len(f'{cool}{aa}') > 4096:
            print(aa)
            cool = ""
        cool += aa
    await editable.edit(f'{"**You have these batches :-**"}\n\n{FFF}\n\n{cool}')
    editable1 = await m.reply_text("**Now send the Batch ID to Download**")
    input2 = message = await bot.listen(editable.chat.id)
    cr = input2.text
    resp = s.get(f'https://api.classplusapp.com/v2/course/content/get?courseId={cr}', headers=headers)
    print(resp.content)
    b_data = resp.json()['data']['courseContent']
    cool = ""
    for data in b_data:
        id1 = data['id']
        nam2 =  data["name"]
        content =  data["contentType"]
        FFF = "**FOLDER-ID - FOLDER NAME**"
        aa = f" ```{id1}```      - **{nam2}**\n\n"
        if len(f'{cool}{aa}') > 4096:
            print(aa)
            cool = ""
        cool += aa
    await editable.edit(f'{"**You have these Folders :-**"}\n\n{FFF}\n\n{cool}')
    editable1 = await m.reply_text("**Now send the Folder ID to Download**")
    input2 = message = await bot.listen(editable.chat.id)
    raw_text2 = input2.text
    await editable1.delete(True)
    resp = s.get(f'https://api.classplusapp.com/v2/course/content/get?courseId={cr}&folderId={raw_text2}', headers=headers)
    bdata = resp.json()['data']['courseContent']
    cool = ""
    for data in bdata:
        id1 = data['id']
        nam2 =  data["name"]
        vid =  data["resources"]["videos"]
        fid =  data["resources"]["files"]
        content =  data["contentType"]
        FFF = "**FOLDER-ID -FOLDER NAME -TOTAL VIDEOS/PDFS**"
        aa = f" ```{id1}``` - **{nam2}  -{vid} -{fid}**\n\n"
        if len(f'{cool}{aa}') > 4096:
            cool = ""
        cool += aa
    await editable.edit(f'{"**You have these Folders :-**"}\n\n{FFF}\n\n{cool}')
    await input2.delete(True)
    editable1 = await m.reply_text("**Now send the Folder ID to Download**")
    input3 = message = await bot.listen(editable.chat.id)
    raw_text3 = input3.text
    await editable1.delete(True)
    respc = s.get(f'https://api.classplusapp.com/v2/course/content/get?courseId={cr}&folderId={raw_text3}', headers=headers).json()
    ddata = respc['data']['courseContent']
    
    if (respc["data"]["courseContent"][0]["contentType"]) ==1:
        bdata = resp.json()['data']['courseContent']
        cool = ""
        for datas in ddata:
            id2 = datas['id']
            nam2 =  datas["name"]
            vid2 =  datas["resources"]["videos"]
            fid =  datas["resources"]["files"]
            content =  datas["contentType"]
            print(id2,nam2,vid)
            FFF = "**FOLDER-ID -FOLDER NAME -TOTAL VIDEOS/PDFS**"
            aa = f" ```{id2}``` - **{nam2} -{vid2}**\n\n"
            if len(f'{cool}{aa}') > 4096:
                cool = ""
            cool += aa
        await editable.edit(f'{"**You have these Folders :-**"}\n\n{FFF}\n\n{cool}')
        await input2.delete(True)
        editable1 = await m.reply_text("**Now send the Folder ID to Download**")
        input4 = message = await bot.listen(editable.chat.id)
        raw_text4 = input4.text
        await editable1.delete(True)
        resp = s.get(f'https://api.classplusapp.com/v2/course/content/get?courseId={cr}&folderId={raw_text4}', headers=headers)
        bdat = resp.json()['data']['courseContent']
        bdat.reverse()
        cool = ""
        vj1 = ""
        for data in bdat:
            id1 = data['id']
            nam2 =  data["name"]
            dis2 = data["description"]
            url2 = data["url"]
            content =  data["contentType"]
            FFF = "**Topic-ID -Topic NAME **"
            aa = f" ```{id2}``` - **{nam2}  -{dis2}**\n\n"
            if len(f'{vj1}{aa}') > 4096:
                cool = ""
            cool += aa
            mm = "careerplus1"
            with open(f'{mm}.txt', 'a') as f:
                    f.write(f"{nam2}-{dis2}:{url2}\n")
        await m.reply_document(f"{mm}.txt")
        await input4.delete(True)
        await editable.edit(f'{"**You have these Videos :-**"}\n\n{FFF}\n\n{cool}')
    else:
        ddata.reverse()
        cool = ""
        vj = ""
        
        for data in ddata:
            id2 = str(data['id'])
            nam2 =  data["name"]
            url2=  data["url"]
            des2=  data["description"]
            
            FFF = "**Topic-ID -Topic NAME **"
            aa = f" ```{id2}``` - **{nam2}  -{des2}**\n\n"
            if len(f'{vj}{aa}') > 4096:
                cool = ""
            cool += aa
            
            mm = "classplus"
            with open(f'{mm}.txt', 'a') as f:
                    f.write(f"{nam2}-{des2}:{url2}\n")
        await m.reply_document(f"{mm}.txt")           
        await editable.edit(f'{"**You have these Videos :-**"}\n\n{FFF}\n\n{cool}')
        await input3.delete(True)
        await m.reply_text("**Now Press /cpd to Download **")
