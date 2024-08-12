import yaml

# 定义 YAML 文件内容
yaml_content = """
env.java.opts: -Djava.io.tmpdir=/tmp
containerized.master.env.LAKESOUL_PG_DRIVER: com.lakesoul.shaded.org.postgresql.Driver
containerized.master.env.LAKESOUL_PG_USERNAME: postgres
containerized.master.env.LAKESOUL_PG_PASSWORD: zkz9s7m4
containerized.master.env.LAKESOUL_PG_URL: jdbc:postgresql://pgcluster-postgresql.default.svc.cluster.local:5432/postgres?stringtype=unspecified
containerized.taskmanager.env.LAKESOUL_PG_DRIVER: com.lakesoul.shaded.org.postgresql.Driver
containerized.taskmanager.env.LAKESOUL_PG_USERNAME: postgres
containerized.taskmanager.env.LAKESOUL_PG_PASSWORD: zkz9s7m4
containerized.taskmanager.env.LAKESOUL_PG_URL: jdbc:postgresql://pgcluster-postgresql.default.svc.cluster.local:5432/postgres?stringtype=unspecified

metrics.reporter.promgateway.factory.class: org.apache.flink.metrics.prometheus.PrometheusPushGatewayReporterFactory
metrics.reporter.promgateway.host: pushgateway-service.lakesoul-dashboard.svc
metrics.reporter.promgateway.port: 9091

metrics.reporter.promgateway.jobName: flink-metrics
metrics.reporter.promgateway.randomJobNameSuffix: false
metrics.reporter.promgateway.deleteOnShutdown: false
metrics.reporter.promgateway.interval: 10 SECONDS
"""

# 解析 YAML 内容到 Python 字典
config_dict = yaml.safe_load(yaml_content)

# 打印字典内容
for key, value in config_dict.items():
    print(f"Key: {key}, Value: {value}")