import datetime
import os
import shutil
from export_utils import *
from apscheduler.schedulers.blocking import BlockingScheduler

MAIN_BACKUP_DIRECTORY = 'backup/'
EXTERNAL_DRIVE_DIRECTORY = 'ext_drive/'
sched = BlockingScheduler()

def get_backup_directory(directory):
    date = datetime.datetime.now().strftime('%Y-%m-%d')
    return directory.format(date)

def copy_files(dstdir):
    file_path = "tfescheduler.db"
    if os.path.isfile(file_path):
        shutil.copy(file_path, dstdir)

def perform_backup(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)
    backup_directory = get_backup_directory(directory+"backup_{0}")
    os.makedirs(backup_directory)
    copy_files(backup_directory)
    export_data(backup_directory+"/")
    export_data_excel(backup_directory+"/")

@sched.scheduled_job('cron', day_of_week='mon-sun', hour=3)
def scheduled_job():
    print("!!! perform backup"+str(datetime.datetime.now().strftime('%Y-%m-%d'))+" !!!")
    perform_backup(MAIN_BACKUP_DIRECTORY)
    #perform_backup(EXTERNAL_DRIVE_DIRECTORY)
    print("!!! end backup"+str(datetime.datetime.now().strftime('%Y-%m-%d'))+" !!!")

if __name__ == '__main__':
    sched.start()