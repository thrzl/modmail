from src.bot import ModMail
from ka import keep_alive

keep_alive()

client = ModMail()

client.load("src.cmds")
client.load("src.modmail")

client.start()