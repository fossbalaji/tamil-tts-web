from __future__ import absolute_import, unicode_literals
from celery import shared_task
from ttsapp.models import Uploads
from datetime import datetime
from ttsapp.utils import task_finished
from django.contrib.auth.models import User
import subprocess


def cleanup_file(filepath):
    try:
        # Read in the file
        with open(filepath, 'r') as file:
            filedata = file.read()

        # Replace the target string
        replace_chars = ["`", "``", "‘", "“", "‘'", "“”", "—", "-", ";", ":", "|"]
        for re_ch in replace_chars:
            filedata = filedata.replace(re_ch, '')

        # Write the file out again
        with open(filepath, 'w') as file:
            file.write(filedata)
        return True, None
    except Exception as e:
        return False, str(e)


@shared_task
def convert_file_to_mp3(upload_id):
    try:
        upfileobj = Uploads.objects.get(id=upload_id)
        file_path = upfileobj.file_path
        clean_check, err = cleanup_file(file_path)
        if not clean_check:
            upfileobj.reason = err
        mycommand = "./tamil-tts.sh --run --gen-mp3 --source %s" % file_path
        # os.system(mycommand)
        # print("command ran")

        # call my command
        p = subprocess.Popen(mycommand, stdout=subprocess.PIPE, shell=True)
        (output, err) = p.communicate()

        # Wait for command to terminate. Get return return code
        p_status = p.wait()
        if p_status == 0:
            # store result path
            upfileobj.modified_on = datetime.now()
            upfileobj.is_processed = True
            output_path = '/%s.mp3' % file_path.replace('.txt', '')
            upfileobj.output_file = output_path

            # call email func and update the flag
            user = User.objects.get(id=upfileobj.user_id)
            file_data = {"id": upfileobj.id, "file_name": upfileobj.file_name, "output_file": output_path,
                         "user": {"email": user.email, "first_name": user.first_name}}
            flag = task_finished(filedata=file_data)
            upfileobj.is_email_sent = flag
            upfileobj.save()

    except Exception as e:
        print(str(e))

