from pyrogram.types import Message
from functions.get_payload import get_payload
from configparser import ConfigParser

class GraveyardConfig():
  def __init__(self, config: ConfigParser, config_file_path: str):
    self.config_name = 'GraveyardConfig'
    self.graveyard = config[self.config_name]
    self.config_file_path = config_file_path

    self.live_cards = self.graveyard.getboolean('live_cards')
    self.live_rank = self.graveyard.getboolean('live_rank')
    self.enable_rank_sticker = self.graveyard.get('enable_rank_sticker')
    self.disable_rank_sticker = self.graveyard.get('disable_rank_sticker')
    self.success_sticker = self.graveyard.get('success_sticker')
    self.fail_sticker = self.graveyard.get('fail_sticker')
    self.astaroth_live_title = self.graveyard.get('astaroth_live_title')
    self.sudo_users = []

  async def enable_live(self, message: Message):
    if message.from_user.id in self.sudo_users:
      self.modify_config('live_cards', True)
      await message.reply_sticker(self.enable_rank_sticker)
    else:
      await message.reply_sticker(self.fail_sticker)

  async def disable_live(self, message: Message):
    if message.from_user.id in self.sudo_users:
      self.modify_config('live_cards', False)
      await message.reply_sticker(self.enable_rank_sticker)
    else:
      await message.reply_sticker(self.fail_sticker)

  async def enable_rank(self, message: Message):
    if message.from_user.id in self.sudo_users:
      self.modify_config('live_rank', True)
      await message.reply_sticker(self.enable_rank_sticker)
    else:
      await message.reply_sticker(self.fail_sticker)

  async def disable_rank(self, message: Message):
    if message.from_user.id in self.sudo_users:
      self.modify_config('live_rank', False)
      await message.reply_sticker(self.disable_rank_sticker)
    else:
      await message.reply_sticker(self.fail_sticker)
    
  async def change_title(self, message: Message):
    title = get_payload(message.text)

    if not title: await message.reply_sticker(self.fail_sticker)
    elif message.from_user.id not in self.sudo_users:
      await message.reply_sticker(self.fail_sticker)
    else:
      self.modify_config('astaroth_live_title', title)
      await message.reply_sticker(self.success_sticker)

  def modify_config(self, key, new_value):
    setattr(self, key, new_value)
    config.set(self.config_name, key, str(new_value))

    with open(config_file_path, 'w') as config_file:
      config.write(config_file)

config_file_path = 'src/config.ini'
config = ConfigParser()
config.read(config_file_path)

graveyard_config = GraveyardConfig(config, config_file_path)
