import smtplib
import ssl
import classes

# todo stop calling this config() to fetch credentials again and again. Maybe use a top level module?
conf = classes.Config()


async def send_email(to_email, message):
    smtp_server = conf.get("smtp_server")
    port = conf.get("smtp_port")
    username = conf.get("smtp_username")
    password = conf.get("smtp_password")
    from_email = conf.get("smtp_fromemail")
    context = ssl.create_default_context()
    try:
        server = smtplib.SMTP(smtp_server, port)
        server.starttls(context=context)
        server.login(username, password)
        server.sendmail(from_email, to_email, message)
    except Exception as e:
        print(e)
    finally:
        server.quit()