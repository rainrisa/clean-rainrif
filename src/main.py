from typing import Dict
from pyrogram import Client, filters, idle
from pyrogram.types import Message, BotCommand
from pyrogram.enums import ChatType
from dotenv import load_dotenv
from asyncio import get_event_loop
from os import getenv
from astaroth_game import AstarothGame
from graveyard_config import graveyard_config
from time import time
import re
import math

load_dotenv()

api_id = int(getenv('API_ID') or "")
api_hash = getenv('API_HASH')
string_session = getenv('STRING_SESSION')
bot_token = getenv('BOT_TOKEN')
user_account = Client("graveyard_user", api_id=api_id, api_hash=api_hash, session_string=string_session)
bot_account = Client("graveyard_bot", api_id=api_id, api_hash=api_hash, bot_token=bot_token)
loop = get_event_loop()
astaroth_id = int(getenv('ASTAROTH_ID') or "")
live_channel_id = int(getenv('LIVE_CHANNEL_ID') or "")
discussion_id = int(getenv('DISCUSSION_ID') or "")
astaroth_game: Dict[int, AstarothGame] = {}
graveyard_config.sudo_users = list(map(int, (getenv('SUDO_USERS') or "").split()))
start_time = time()

@user_account.on_message(filters.text & filters.bot)
async def regular_message_handler(_, message: Message):
  chat_id = message.chat.id
  user_id = message.from_user.id

  if user_id == astaroth_id:
    if not graveyard_config.live_cards: return

    if message.text.find("Permainan dimulai!") != -1:
      astaroth_game[chat_id] = AstarothGame(bot_account, live_channel_id, discussion_id, chat_id)
      numbers = re.findall(r'\d+', message.text)
      min_number = int(numbers[0])
      max_number = int(numbers[1])
      unplayed_numbers = list(range(min_number, max_number + 1))

      astaroth_game[chat_id].unplayed_numbers = unplayed_numbers
      await astaroth_game[chat_id].send_live_message()

    elif chat_id not in astaroth_game: return

    elif message.text.find("[Ronde 1]") != -1:
      astaroth_game[chat_id].set_players(message)
      await astaroth_game[chat_id].update_live_message()

    elif message.text.find("[Ronde") != -1:
      number = re.findall(r'\d+', message.text)[0]
      astaroth_game[chat_id].update_round(number)
      await astaroth_game[chat_id].update_live_message()

    elif message.text.find("menyimpan row") != -1:
      astaroth_game[chat_id].update_total_bulls(message)
      await astaroth_game[chat_id].send_live_rank_message()

    elif message.text.find("Kartu ini adalah kartu ke-6") != -1:
      astaroth_game[chat_id].update_total_bulls(message)
      await astaroth_game[chat_id].send_live_rank_message()

    elif message.text.find("+-+-+-+-") != -1:
      if astaroth_game[chat_id].init_numbers_played: return

      astaroth_game[chat_id].init_numbers_played = True
      numbers = re.findall(r'\d+', message.text)
      astaroth_game[chat_id].update_init_numbers(numbers)
      await astaroth_game[chat_id].update_live_message()

    elif message.text.find("Ini adalah kartu yang dimainkan") != -1:
      numbers = re.findall(r'\d+', message.text)
      astaroth_game[chat_id].update_numbers(numbers)
      await astaroth_game[chat_id].update_live_message()
      
    elif message.text.find("Semua kartu telah digunakan!") != -1:
      await astaroth_game[chat_id].update_live_message(finish = True)

    elif message.text.find("Permainan berakhir!") != -1:
      await astaroth_game[chat_id].delete_live_message()
      del astaroth_game[chat_id]

    elif message.text.find("Permainan sudah diberhentikan!") != -1:
      await astaroth_game[chat_id].delete_live_message()
      del astaroth_game[chat_id]

    return

@bot_account.on_message(filters.private & filters.command("enablelive"))
async def enable_live_handler(_, message: Message):
  await graveyard_config.enable_live(message)

@bot_account.on_message(filters.private & filters.command("disablelive"))
async def disable_live_handler(_, message: Message):
  await graveyard_config.disable_live(message)

@bot_account.on_message(filters.private & filters.command("enablerank"))
async def enable_rank_handler(_, message: Message):
  await graveyard_config.enable_rank(message)

@bot_account.on_message(filters.private & filters.command("disablerank"))
async def disable_rank_handler(_, message: Message):
  await graveyard_config.disable_rank(message)

@bot_account.on_message(filters.private & filters.command("changetitle"))
async def change_title_handler(_, message: Message):
  await graveyard_config.change_title(message)

@bot_account.on_message(filters.command("uptime"))
async def uptime(client, message: Message):
    uptime_total = round(time() - start_time)
    uptime_hours = math.floor(uptime_total / 3600)
    uptime_total -= uptime_hours * 3600
    uptime_minutes = math.floor(uptime_total / 60)
    uptime_total -= uptime_minutes * 60
    uptime_seconds = uptime_total

    if uptime_hours != 0 and uptime_minutes != 0:
        await message.reply(f"{uptime_hours}h {uptime_minutes}m {uptime_seconds}s")
    elif uptime_hours == 0 and uptime_minutes != 0:
        await message.reply(f"{uptime_minutes}m {uptime_seconds}s")
    else:
        await message.reply(f"{uptime_seconds}s")

@bot_account.on_message(filters.group & filters.text)
async def bot_regular_message_handler(_, message: Message):
  if message.chat.id == discussion_id and message.sender_chat:
    if message.sender_chat.type == ChatType.CHANNEL:
      if message.text.find(graveyard_config.astaroth_live_title) != -1:
        chat_id = int(re.findall(r'-\d+', message.text)[0])
        astaroth_game[chat_id].discussion_message_id = message.id
        astaroth_game[chat_id].display_chat_id = False

  return

async def init():
  await user_account.start()
  user = await user_account.get_me()
  await bot_account.start()
  bot = await bot_account.get_me()
  print(f"App started as {user.first_name}")
  print(f"App started as {bot.username}")

  await bot_account.set_bot_commands([
    BotCommand("enablelive", "aktifkan live"),
    BotCommand("disablelive", "nonaktifkan live"),
    BotCommand("enablerank", "aktifkan podium"),
    BotCommand("disablerank", "nonaktifkan podium"),
    BotCommand("changetitle", "mengganti live title"),
    BotCommand("uptime", "lihat sudah berapa lama botnya jalan"),
  ])
  await idle()

loop.run_until_complete(init())
