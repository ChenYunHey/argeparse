import yaml


def change_base_yaml(key, value, yaml_data):
    if key == "kubernetes.namespace":
        yaml_data['metadata']['namespace'] = value
    elif key == "kubernetes.service-account":
        yaml_data['spec']['serviceAccount'] = value
    elif key == "kubernetes.cluster-id":
        yaml_data['metadata']['name'] = value
    else:
        yaml_data['spec']['flinkConfiguration'][key] = value


def fill_D_parameters(equal_params):
    with open("base.yaml", "r", encoding='utf-8') as f:
        yaml_data = yaml.safe_load(f.read())
        for equal_param in equal_params:
            # 是否选择D开头的参数才写进去
            key = str(equal_param)
            value = equal_params.get(equal_param)
            change_base_yaml(key, value, yaml_data, )
            # yaml_data['spec']['flinkConfiguration'][key] = value
    with open("base.yaml", "w", encoding='utf-8') as updated_file:
        try:
            yaml.dump(yaml_data, updated_file, default_style=False)
        except yaml.YAMLError as exec:
            print(exec)


def fill_class_parameters(class_params):
    with open("base.yaml", "r", encoding='utf-8') as f:
        yaml_data = yaml.safe_load(f.read())
        class_entry = class_params[0]
        JAR_URI = class_params[1]
        yaml_data['spec']['job']['jarURI'] = JAR_URI
        yaml_data['spec']['job']['entryClass'] = class_entry

    with open("base.yaml", "w", encoding='utf-8') as updated_file:
        try:
            yaml.dump(yaml_data, updated_file, default_style=False)
        except yaml.YAMLError as exec:
            print(exec)


def fill_other_parameters(space_params):
    with open("base.yaml", "r", encoding='utf-8') as f:
        yaml_data = yaml.safe_load(f.read())
        for space_param in space_params:
            if space_param == "flink.checkpoint":
                value = space_params.get(space_param)
                yaml_data['spec']['flinkConfiguration']['state.checkpoints.dir'] = value
            elif space_param == "s":
                value = space_params.get(space_param)
                yaml_data['spec']['flinkConfiguration']['state.savepoints.dir'] = value
            elif space_param == 'c':
                jarURI = space_params.get(space_param)[1]
                entryClass = space_params.get(space_param)[0]
                yaml_data['spec']['job']['jarURI'] = jarURI
                yaml_data['spec']['job']['entryClass'] = entryClass
    with open("base.yaml", "w", encoding='utf-8') as updated_file:
        try:
            yaml.dump(yaml_data, updated_file, default_style=False)
        except yaml.YAMLError as exec:
            print(exec)


def fill_user_parameters(user_params):
    with open("base.yaml", "r", encoding='utf-8') as f:
        yaml_data = yaml.safe_load(f.read())
        yaml_data['spec']['job']['args'] = user_params

    with open('base.yaml', 'w', encoding='utf-8') as updated_file:
        try:
            yaml.dump(yaml_data, updated_file, default_style=False)
        except yaml.YAMLError as exec:
            print(exec)
