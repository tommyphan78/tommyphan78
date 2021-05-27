#/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function
import os.path
import json
import pprint
import pandas as pd
import logging
from telegram.forcereply import ForceReply
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
from telegram.bot import Bot
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google.oauth2 import service_account

pp = pprint.PrettyPrinter()

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']

# The ID and range of a sample spreadsheet.
privateKey = 'key-stock.json'
spreadsheetID_NPS = '1lPR124WV8iSyDYJUEm6_JSUHuZx2LR-gHWjuYhElClk'
range_NPS = 'tồn kho!A:G'

spreadsheetID_Hapu = '1XgqlLv9aQYxWgmfiOHMbcIJbagxBh4mNB5eE9HSCdtY'
range_Hapu = 'BC-XNT!A10:J'

spreadsheetID_NTL = '1lTqMNU01XaU4ZEIGBHduWQskj32Tc-qXm3RLOS9JPjE'
range_NTL = 'Tổng hợp!A:G'

creds = None
creds = service_account.Credentials.from_service_account_file(
        privateKey, scopes=SCOPES)

service = build('sheets', 'v4', credentials=creds)

# https://api.telegram.org/bot1819849729:AAHzHMtMVrJZXGl51A9rrOdioC1G-cP4EtY/getUpdates

# Call the Sheets API
sheet = service.spreadsheets()

result_NPS = sheet.values().get(
    spreadsheetId=spreadsheetID_NPS,
    range=range_NPS
).execute()

result_Hapu = sheet.values().get(
    spreadsheetId=spreadsheetID_Hapu,
    range=range_Hapu
).execute()

result_NTL = sheet.values().get(
    spreadsheetId=spreadsheetID_NTL,
    range=range_NTL
).execute()

database_NPS = result_NPS['values'][1:]
database_Hapu = result_Hapu['values'][1:]
database_NTL = result_NTL['values'][1:]

gif_link='https://media.giphy.com/media/xTiN0pFaCoAxpASv3q/giphy.gif'

def warehouse_find_type(warehouse, item, value):

    print_NPS = []
    print_Hapu = []
    print_NTL = []

    count_NPS = 0
    count_Hapu = 0
    count_NTL = 0

    for k in database_NPS:
        if item in k[0].lower():
            if value in k[1].lower() and int(k[6]) >= 1:
                count_NPS += int(k[6])
                print_NPS.append("{} {} {} ({})".format(k[1],k[2],k[3],k[6]).upper())
            elif value is None and int(k[6]) >= 1:
                count_NPS += int(k[6])
                print_NPS.append("{} {} {} ({})".format(k[1],k[2],k[3],k[6]).upper())

    for k in database_Hapu:
        if item in k[1].lower():
            if value in k[3].lower() and int(k[9]) >= 1:
                count_Hapu += int(k[9])
                print_Hapu.append("{} {} ({})".format(k[3],k[2],k[9]).upper())
            elif value is None and int(k[9]) >= 1:
                count_Hapu += int(k[9])
                print_Hapu.append("{} {} ({})".format(k[3],k[2],k[9]).upper())

    for k in database_NTL:
        if item in k[0].lower():
            if value in k[1].lower() and int(k[6]) >= 1:
                count_NTL += int(k[6])
                print_NTL.append("{} {} {} ({})".format(k[1],k[2],k[3],k[6]).upper())
            elif value is None and int(k[6]) >= 1:
                count_NTL += int(k[6])
                print_NTL.append("{} {} {} ({})".format(k[1],k[2],k[3],k[6]).upper())

    sumStock = count_Hapu + count_NTL + count_NPS
    title_Sum = "*Tổng số {} {} đang tồn tại các kho: {} thiết bị* \n".format(item.upper(),value.upper(),sumStock)
    title_NPS = "\n_Số {} {} đang tồn tại kho NPS: {} thiết b_\n\n".format(item.upper(),value.upper(),count_NPS)
    title_NTL = "\n\n_Số {} {} đang tồn tại kho NTL: {} thiết bị_\n\n".format(item.upper(),value.upper(),count_NTL)
    title_Hapu = "\n\n_Số {} {} đang tồn tại kho Hapu: {} thiết bị_\n\n".format(item.upper(),value.upper(),count_Hapu)

    result =  title_Sum + title_NPS + "\n".join(print_NPS) + title_Hapu + "\n".join(print_Hapu) + title_NTL + "\n".join(print_NTL)

    return result

def warehouse_find_model(warehouse, model):

    count_NPS = 0
    count_Hapu = 0
    count_NTL = 0
    stockOut = 0

    notFound = 0

    typeDevice = ""
    modelDevice = ""
    detailDevice = ""
    colTitle = ""
    
    model = model.upper()

    for k in database_NPS:
        if model in k[2].upper() and int(k[6]) > 0:
            print(k[2])
            count_NPS += int(k[6])

        elif model in k[2].upper() and int(k[6]) == 0:
            print("NPS" ,k[2], k[6])
            stockOut += 1

        elif model not in k[2].upper():
            print(k[2])
            print("NPS Không còn thiết bị")
            notFound += 1

    for k in database_Hapu:
        if model in k[2].upper() and int(k[9]) >= 1:
            count_Hapu += int(k[9])
            colTitle = k[1]
            typeDevice = "*Chủng Loại:* {}\n\n".format(k[1])
            modelDevice = "*Model:* {}\n\n".format(k[2])
            detailDevice = "*Thông số:* {}\n\n".format(k[3])
            print("Hapu" ,k[2], k[9])

        elif model in k[2].upper() and int(k[9]) == 0:
            print("Hapu" ,k[2], k[9])
            stockOut += 1

        elif model not in k[2].upper():
            print("Hapu Không còn thiết bị")
            notFound += 1
        

    for k in database_NTL:
        if model in k[2].upper() and int(k[6]) >= 1:
            count_NTL += int(k[6])
            print("NTL" ,k[2], k[6])

        elif model in k[2].upper() and int(k[6]) == 0:
            print("NTL" ,k[2], k[6])
            stockOut += 1

        elif model not in k[2].upper():
            print("NTL Không còn thiết bị")
            notFound += 1

    sumStock = count_Hapu + count_NTL + count_NPS

    infoDevice = typeDevice + modelDevice + detailDevice

    title_Sum = "*Tổng {} {} đang tồn tại các kho: {} thiết bị* \n \n".format(colTitle.upper(), model.upper(), sumStock)

    title_NPS = "_Số {} {} đang tồn tại kho NPS: {}_\n\n".format(colTitle.upper(), model.upper(),count_NPS)
    title_NTL = "_Số {} {} đang tồn tại kho NTL: {}_\n\n".format(colTitle.upper(), model.upper(),count_NTL)
    title_Hapu = "_Số {} {} đang tồn tại kho Hapu: {}_\n\n".format(colTitle.upper(), model.upper(),count_Hapu)

    result = infoDevice + title_Sum + title_NPS + title_NTL + title_Hapu

    if sumStock == 0 and stockOut ==0 and notFound > 0:
        return "Model không khớp rồi. Nhập lại đi. Ahihi Đồ Ngốc :D"
    else:
        return result

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

def help(update, context):
    startSend = """

*1. Tra cứu các thiết bị tồn theo chủng loại:*

_/<Chủng Loại> <Tham Số>_

VD : /RAM 2933
        /HDD 12TB
        /SSD  480GB
        /RAM Samsung
        /RAM DDR4
        /CPU  all

Các chủng loại đang có bao gồm: _[CPU, RAM, HDD, SSD, MODULE]_

Tham số có thể là các thông tin mô tả chung về loại thiết bị cần tìm
_VD : Samsung, 16GB, 8TB, 2666, 2933,..._

Tham số "all" để tra cứu các loại TB tồn của chủng loại tìm kiếm.
_VD Cú Pháp : /Module all_

*2. Tra cứu các thiết bị tồn theo Model:*

_/Model <Model Thiết BỊ>_

VD : /Model 9271-8i
        /Model GSS-MPO250-SRC
        /Model E5-2620V3

"""
    update.message.reply_animation(
        animation=gif_link )
    update.message.reply_text(text=startSend, parse_mode='Markdown')

def error(update, context):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, context.error)

def ram(update, context):
    """Log Errors caused by Updates."""
    command = context.args[0].lower()
    if "all" in command.lower():
        request = warehouse_find_type("NPS", "ram", '')
        update.message.reply_text(text=request, parse_mode='Markdown')

    else:
        request = warehouse_find_type("NPS", "ram", str(command))
        update.message.reply_text(text=request, parse_mode='Markdown')

def hdd(update, context):
    command = context.args[0].lower()
    if "all" in command.lower():
        request = warehouse_find_type("NPS", "hdd", '')
        update.message.reply_text(text=request, parse_mode='Markdown')

    else:
        request = warehouse_find_type("NPS", "hdd", str(command))
        update.message.reply_text(text=request, parse_mode='Markdown')

def ssd(update, context):
    command = context.args[0].lower()
    if "all" in command.lower():
        request = warehouse_find_type("NPS", "ssd", '')
        update.message.reply_text(text=request, parse_mode='Markdown')

    else:
        request = warehouse_find_type("NPS", "ssd", str(command))
        update.message.reply_text(text=request, parse_mode='Markdown')

def cpu(update, context):
    command = context.args[0].lower()
    if "all" in command.lower():
        request = warehouse_find_type("NPS", "cpu", '')
        update.message.reply_text(text=request, parse_mode='Markdown')

    else:
        request = warehouse_find_type("NPS", "cpu", str(command))
        update.message.reply_text(text=request, parse_mode='Markdown')

def module(update, context):
    command = context.args[0].lower()
    if "all" in command.lower():
        request = warehouse_find_type("NPS", "module", '')
        update.message.reply_text(text=request, parse_mode='Markdown')

    else:
        request = warehouse_find_type("NPS", "module", str(command))
        update.message.reply_text(text=request, parse_mode='Markdown')

def model(update, context):
    command = context.args[0].lower()
    request = warehouse_find_model("NPS", str(command))
    update.message.reply_text(text=request, parse_mode='Markdown')

def main():
    """Start the bot."""
    # Create the Updater and pass it your bot's token.
    # Make sure to set use_context=True to use the new context based callbacks
    # Post version 12 this will no longer be necessary
    updater = Updater("1819849729:AAHzHMtMVrJZXGl51A9rrOdioC1G-cP4EtY", use_context=True)

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # on different commands - answer in Telegram
    teleCommand = ["help", "ram", "cpu", "hdd", "ssd", "module", "model"]
    commandFunc = [help, ram, cpu, hdd, ssd, module, model]

    for k, v in zip(teleCommand, commandFunc):
        dp.add_handler(CommandHandler(k, v))
        
    # if("on" == command):
    #     context.user_data[echo] = True
    #     update.message.reply_text("Repeater Started")
    # elif("off" == command):
    #     context.user_data[echo] = False
    #     update.message.reply_text("Repeater Stopped")

    # on noncommand i.e message - echo the message on Telegram
    # dp.add_handler(MessageHandler(Filters.text, echo))
    # dp.add_handler(MessageHandler(Filters.text, hdd))

    # log all errors
    dp.add_error_handler(error)

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()

if __name__ == '__main__':
    main()