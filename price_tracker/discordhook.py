from time import sleep
from discord_webhook import DiscordWebhook, DiscordEmbed
from dotenv import load_dotenv
import os
load_dotenv()

hook = os.getenv("HOOK")
def send_msg(title: str, description: str, url=None):
    webhook = DiscordWebhook(
        url=hook, 
    #     content='Webhook Message'
        )
    embed = DiscordEmbed(
        url=url, 
        title=title,
        description=description, 
        rate_limit_retry=True,
        color='fcba03')
    webhook.add_embed(embed)
    response = webhook.execute()
    if response.status_code != 200:
        sleep(5)
        webhook.execute()


def sendmail(subject, msg, myemail, password, sendto):
    import smtplib
    mail_text = f"Subject: {subject}\n\n{msg}" 

    server = smtplib.SMTP(host='smtp.gmail.com', port=587)
    server.ehlo()
    server.starttls()
    server.login(myemail, password)
    server.sendmail(sendto, myemail, mail_text) ## to and from email address 
