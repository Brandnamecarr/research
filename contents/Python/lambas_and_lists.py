stuff = ["apple", "orange", "supercalifragilisticexpialidocious", "dog", "boat"]

sorted_stuff = sorted(stuff, key=lambda x: len(x))

print(sorted_stuff)

'''
    Sample interview question from Omaha Mutual:
    You have a list of jobs to do, each with a time estimate and a priority level.
    Given a maximum time you can work, which jobs should you do to maximize the priority level?
'''

class Job():
    def __init__(self, jobTime, jobPriority):
        self.jobTime = jobTime
        self.jobPriority = jobPriority


jobs = [
    Job(25, 3),
    Job(5, 1),
    Job(15, 2),
    Job(30, 4),
    Job(10, 5)
]

def calculate_time(jobs, time_in_seconds) -> int:
    totalTime = 0
    sorted_jobs = sorted(jobs, key=lambda j: j.jobPriority)
    for job in sorted_jobs:
        # print(f"{job.jobPriority}")
        if job.jobTime + totalTime <= time_in_seconds:
            totalTime += job.jobTime
            print(f"Doing job with priority {job.jobPriority} and time {job.jobTime}")
            print(f"Total time worked so far: {totalTime} seconds")
        else:
            print(f"Skipping job with priority {job.jobPriority} and time {job.jobTime}")
            continue
    
    print(f"Total time worked: {totalTime} seconds")


calculate_time(jobs, 40)