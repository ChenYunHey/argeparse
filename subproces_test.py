import json
import subprocess

a = subprocess.run(["ls","-l"])
print(a)

res = subprocess.run("cat exceptions.json",shell=True,capture_output=True,text=True,check=True).stdout.strip()
root_exception = json.loads(res)
exception = root_exception.get('root-exception',{})
print(exception)

job_status = subprocess.run(
    ["echo","FAILD"],
    capture_output=True,
    text=True,
    check=True
).stdout.strip()
print(job_status)