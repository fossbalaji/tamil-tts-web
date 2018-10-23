import smtplib
import email.message
from django.conf import settings


def task_finished(filedata):
    try:
        msg = email.message.Message()
        msg['Subject'] = "Your file has been converted into mp3 Successfully %s" % filedata["file_name"]
        msg['From'] = settings.FROM_EMAIL
        msg['To'] = filedata.get('user').get('email')
        msg.add_header('Content-Type', 'text/html')
        text = """
                Hi $FIRST_NAME, <br/> 
                    Your file has been successfully converted to mp3. Please login to your account and 
                    download the file from your home page'
        """.replace('$FIRST_NAME', filedata.get('user', {}).get('first_name', ''))
        msg.set_payload(text)

        # creates SMTP session
        s = smtplib.SMTP(settings.MAIL_SERVER, 587)
        s.starttls()
        s.login(settings.FROM_EMAIL,
                settings.EMAIL_PASS)
        s.sendmail(msg['From'], [msg['To']], msg.as_string())
        s.quit()
        return True
    except Exception as e:
        print(str(e))
        return False


