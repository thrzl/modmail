from src.bot import ModMail

client = ModMail()

client.load("src.cmds")
client.load("src.modmail")

client.start()
