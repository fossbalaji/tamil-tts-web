from django.conf import settings
from django.core.mail import send_mail


def task_finished(filedata):
    try:
        subject = "Your file has been converted into mp3 Successfully %s" % filedata["file_name"]
        To = filedata.get('user').get('email')
        text = """
                Hi $FIRST_NAME,
                    Your file has been successfully converted to mp3. Please login to your account and 
                    download the file from your home page'
        """.replace('$FIRST_NAME', filedata.get('user', {}).get('first_name', ''))
        send_mail(
            subject,
            text,
            settings.FROM_EMAIL,
            [To],
            fail_silently=False, html_message=True)
        return True
    except Exception as e:
        print(str(e))
        return False


