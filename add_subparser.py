import argparse
import subprocess

import yaml

import yaml_fill
import os


def parse_arguments():
    parser = argparse.ArgumentParser(description='Flink command line parser')
    subparsers = parser.add_subparsers(help="sub-command help")

    # 启动flink job
    run_command = subparsers.add_parser('run', help='start the job.')
    run_command.add_argument('-D', action='append', help='Define a property (e.g., -Dkey=value)')
    run_command.add_argument('-c', nargs=argparse.REMAINDER, help='Class and JAR file and jar parameters')
    run_command.set_defaults(func=execute_run)

    # 暂停flink job
    suspended_command = subparsers.add_parser('suspended', help='pause the job')
    suspended_command.add_argument("-jobNamespace", required=True)
    suspended_command.add_argument("-jobName", required=True)
    suspended_command.set_defaults(func=execute_suspended)

    # 暂停后恢复flink job
    restart_command = subparsers.add_parser('restart', help='restart the job,use after suspended the job.')
    restart_command.add_argument("-jobNamespace", required=True)
    restart_command.add_argument("-jobName", required=True)
    restart_command.set_defaults(func=execute_restart)

    # 删除flink job
    delete_command = subparsers.add_parser('delete', help="delete the job.")
    delete_command.add_argument("-jobNamespace", required=True)
    delete_command.add_argument("-jobName", required=True)
    delete_command.set_defaults(func=execute_delete)

    # 查询flink job状态
    status_command = subparsers.add_parser('status', help="Query task status")
    status_command.add_argument("-jobNamespace", required=True)
    status_command.add_argument("-jobName", required=True)
    status_command.set_defaults(func=query_status)

    args = parser.parse_args()
    args.func(args)


def execute_run(args):
    user_params = args.c
    class_params = user_params[:2]
    user_params = user_params[2:]
    define_params = {}
    job_info = {}
    # deployment yaml
    job_name_yaml = ""
    if args.D:
        for item in args.D:
            key, value = item.split('=', 1)
            if key == "kubernetes.cluster-id":
                job_info[key] = value
                job_name_yaml = value
            elif key == "kubernetes.namespace":
                job_info[key] = value
                job_name_yaml = job_name_yaml+"_"+value+".yaml"
            elif key == "kubernetes.job.parallelism":
                job_info[key] = value
            define_params[key] = value
    with open("base.yaml","r",encoding="utf-8") as f:
        base_yaml = yaml.safe_load(f.read())
    with open(job_name_yaml,"w",encoding="utf-8") as nf:
        try:
            yaml.dump(base_yaml, nf, default_style=False)
        except yaml.YAMLError as exec:
            print(exec)

    job_yaml = "session-"+job_name_yaml
    yaml_fill.fill_flink_conf_yaml("flink-conf.yaml","base.yaml",job_name_yaml)
    check_key_exists(define_params, "high-availability.storageDir")
    check_key_exists(define_params, "state.savepoints.dir")
    check_key_exists(define_params, "state.checkpoints.dir")
    yaml_fill.fill_D_parameters(define_params,job_name_yaml)
    yaml_fill.fill_user_parameters(user_params,"base_job.yaml",job_yaml)
    yaml_fill.fill_class_parameters(class_params,job_yaml)
    yaml_fill.fill_base_job_yaml(job_info,job_yaml)
    yaml_fill.fill_flink_podTemplate("flink-podTemplate.yaml",job_name_yaml)
    command_start_deploy = "kubectl create -f "+job_name_yaml+" "
    command_start_job = "kubectl create -f "+job_yaml+" "
    os.system(command_start_deploy)
    os.system(command_start_job)


def execute_suspended(args):
    job_name = args.jobName
    job_namespace = args.jobNamespace
    command = (
            "kubectl -n " + job_namespace + " patch flinksessionjobs.flink.apache.org  " + job_name +
            "-session --type='json' -p='[{\"op\": \"replace\", \"path\": \"/spec/job/state\", \"value\":\"suspended\"}]'"
    )
    print(command)
    os.system(command)


def execute_restart(args):
    job_name = args.jobName
    job_namespace = args.jobNamespace
    command = (
            "kubectl -n " + job_namespace + " patch flinksessionjobs.flink.apache.org  " + job_name +
            "-session --type='json' -p='[{\"op\": \"replace\", \"path\": \"/spec/job/state\", \"value\":\"running\"}]'"
    )
    print(command)
    os.system(command)


def execute_delete(args):
    job_name = args.jobName
    job_namespace = args.jobNamespace
    command_delete_deploy = (
            "kubectl -n " + job_namespace + " delete flinkdeployments.flink.apache.org " + job_name
    )
    command_delete_job = (
            "kubectl -n " + job_namespace + " delete  flinksessionjobs.flink.apache.org" + job_name
    )

    print(command_delete_job)
    os.system(command_delete_job)
    print(command_delete_deploy)
    os.system(command_delete_deploy)
    rm_command = "rm "+job_name+"_"+job_namespace+".yaml"
    os.system(rm_command)

def query_status(args) :
    job_name = args.jobName
    job_namespace = args.jobNamespace

    # job_status=subprocess.call(["kubectl","get","flinksessionjobs.flink.apache.org",job_name,"-session","-n",job_namespace,"-o","json","|","jq","-r","'.status.jobStatus.state'"],shell=True)
    job_status = subprocess.run(
        ["kubectl", "get", "flinksessionjobs.flink.apache.org", job_name + "-session", "-n", job_namespace, "-o",
         "json"],
        capture_output=True,
        text=True,
        check=True
    ).stdout.strip()
    job_id = subprocess.run(["kubectl","get","flinksessionjobs.flink.apache.org",job_name,"-session","-n",job_namespace,"-o","|","-jq","-r","'.status.jobStatus.jobId'"],
                            capture_output=True,
                            text=True,
                            check=True,
                            shell=True).stdout.strip()

    if job_status == "":
        error=subprocess.call(["kubectl","-n",job_namespace,"get","flinksessionjobs.flink.apache.org",job_name,"-o","jsonpath='{.status.error}'"],shell=True)
        print(error)
    if job_status == "RUNNING":
        print(job_status)
    # command_id = (
    #     "kubectl get flinksessionjobs.flink.apache.org " + job_name + "-session -n " + job_namespace + " -o json | jq -r '.status.jobStatus.jobId'"
    # )
    if job_status == "FAILED":
        print("有错误")
        app_name = "app=" + job_name
        pod_names = subprocess.run(
            ["kubectl", "get", "pods", "-l", app_name, "-n", job_namespace, "-o", "jsonpath='{.items[*].metadata.name"],
            capture_output=True,
            shell=True,
            text=True,
            check=True).stdout.strip()
        print(pod_names)
        pod_name = str(pod_names).split(" ")[0]
        print(pod_name)
        subprocess.run(["kubectl", "-n", job_namespace, "exec", "-it", pod_name, "-- bash"], check=True)
        exception_uri = f"https://{job_name}-rest.flink-k8s-operator.svc.cluster.local:8081/jobs/{job_id}/exceptions"

        exceptions_output = subprocess.run(
            ["curl", "-s", exception_uri],
            capture_output=True,
            text=True,
            check=True
        ).stdout
        print(exceptions_output)

def check_key_exists(data, key):
    if key not in data:
        raise KeyError(f"Key '{key}' is missing from the dictionary.")
    return True

if __name__ == "__main__":
    parse_arguments()
