from __future__ import absolute_import, unicode_literals
from celery import shared_task
from ttsapp.models import Uploads
from datetime import datetime
import os
import subprocess



@shared_task
def convert_file_to_mp3(upload_id):
    try:
        upfileobj = Uploads.objects.get(id=upload_id)
        file_path = upfileobj.file_path
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
            upfileobj.output_file = '/media/%s.mp3' % file_path.replace('.txt', '')
            # call email func and update the flag
            upfileobj.is_email_sent = True
            upfileobj.save()

    except Exception as e:
        print(str(e))

