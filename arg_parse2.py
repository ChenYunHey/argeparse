import argparse
import yaml_fill
import os
def parse_arguments():
    parser = argparse.ArgumentParser(description='Flink command line parser')
    # 添加必填参数
    parser.add_argument('flinkDeploymentState', help='flinkDeployment state,support run/suspended/restart/delete')
    # 添加 -D 开头的参数
    parser.add_argument('-D', action='append', help='Define a property (e.g., -Dkey=value)')
    # 添加 -c 参数后的所有参数
    parser.add_argument('-c', nargs=argparse.REMAINDER, help='Class and JAR file and jar parameters')
    args = parser.parse_args()
    job_state = args.flinkDeploymentState
    user_params = args.c
    class_params = {}
    class_params[0] = user_params[0]
    class_params[1] = user_params[1]
    user_params = user_params[2:]
    define_params = {}
    basemessage = {}
    if args.D:
        for item in args.D:
            key, value = item.split('=', 1)
            if key == "kubernetes.cluster-id":
                basemessage[key] = value
            elif key == "kubernetes.namespace":
                basemessage[key] = value
            define_params[key] = value
    check_key_exists(define_params, "high-availability.storageDir")
    check_key_exists(define_params, "state.savepoints.dir")
    check_key_exists(define_params, "state.checkpoints.dir")
    return {
        "base_massage":basemessage,
        "job_state": job_state,
        "user_params": user_params,
        "class_params": class_params,
        "define_params": define_params
    }

def check_key_exists(data, key):
    if key not in data:
        raise KeyError(f"Key '{key}' is missing from the dictionary.")
    return True


if __name__ == "__main__":
    parsed_args = parse_arguments()
    basemessage = parsed_args.get("base_massage")
    # 打印最终字典
    job_state = parsed_args.get("job_state")
    if job_state == "run":
        user_params, class_params, define_params = parsed_args.get("user_params"), parsed_args.get(
            "class_params"), parsed_args.get("define_params")
        yaml_fill.fill_D_parameters(define_params)
        yaml_fill.fill_user_parameters(user_params)
        yaml_fill.fill_class_parameters(class_params)
        os.system("kubectl create -f base.yaml")
    elif job_state == "suspended":
        command = (
            "kubectl -n "+basemessage.get("kubernetes.namespace")+" patch flinkdeployments.flink.apache.org  "+basemessage.get("kubernetes.cluster-id")+
            " --type='json' -p='[{\"op\": \"replace\", \"path\": \"/spec/job/state\", \"value\":\"suspended\"}]'"
        )
        os.system(command)
    elif job_state == "restart":
        command = (
            "kubectl -n " + basemessage.get("kubernetes.namespace") + " patch flinkdeployments.flink.apache.org  " + basemessage.get(
            "kubernetes.cluster-id") + " --type='json' -p='[{\"op\": \"replace\", \"path\": \"/spec/job/state\", \"value\":\"running\"}]'"
        )
        os.system(command)
    elif job_state == "delete":
        os.system("kubectl delete -f base.yaml")
        print("job has been deleted")
    else:
        raise KeyError(f"Parameter '{job_state}' is invalid,support run/suspended/restart/delete.")
