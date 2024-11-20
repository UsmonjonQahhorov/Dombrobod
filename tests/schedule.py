from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
import time
from apscheduler.triggers.cron import CronTrigger

# Define a simple function to schedule
def my_task():
    print("Task is running...")

# Create a scheduler
scheduler = BackgroundScheduler()

# Start the scheduler
scheduler.start()

# Schedule a task that runs every 5 seconds
scheduler.add_job(my_task, CronTrigger(second=5))
scheduler.add_job(my_task, CronTrigger(second=5))
jobs = scheduler.get_jobs()
for i in jobs:
    print(i.id)

time.sleep(20)


# scheduler.remove_job(job.id)

# Optionally shutdown the scheduler
scheduler.shutdown()
