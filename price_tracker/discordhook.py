from time import sleep
from discord_webhook import DiscordWebhook, DiscordEmbed
# from dotenv import load_dotenv
import os
# load_dotenv()

hook = os.getenv("HOOK")
def send_msg(title: str, description: str, url=None):
    """Fancy discord message. The title is clickable and redirects to url """
    webhook = DiscordWebhook(
        url=hook, 
        )
    embed = DiscordEmbed(
        url=url, 
        title=title,
        description=description, 
        rate_limit_retry=True, ## limit retries
        color='fcba03' ## Yellow Color 
        ) 
    webhook.add_embed(embed)
    response = webhook.execute()
    if response.status_code != 200:
        sleep(5) ## if failed, retry again only
        webhook.execute()


def sendmail(subject, msg, myemail, password, sendto):
    """Send email"""
    import smtplib
    mail_text = f"Subject: {subject}\n\n{msg}" 
    server = smtplib.SMTP(host='smtp.gmail.com', port=587)
    server.ehlo()
    server.starttls()
    server.login(myemail, password)
    server.sendmail(sendto, myemail, mail_text) ## to and from email address 
