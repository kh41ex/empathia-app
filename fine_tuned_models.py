from openai import OpenAI
client = OpenAI()

jobs = client.fine_tuning.jobs.list()
for job in jobs.data:
    print(job.id, job.fine_tuned_model)
