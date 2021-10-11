from configredis.setconf import defaultconfig, devconfig, proconfig, configs, ConfigArgs, ConfigUpdate, lookup_proj_config, host_ip  # noqa
from configredis.setredis import SetRedis


con = ConfigArgs()

defaultconfig(
    disk_name='TenD'
)

devconfig(
    sentry=False,
    celery_broker="amqp://user:password@172.0.0.1:5672//",
    r_flow={'host': host_ip('pro.cluster_redis.mztdns.com'), 'port': 7000, 'db': 0, "cluster": True}
)

proconfig(
    sentry=True,
    celery_broker="amqp://user:password@172.0.0.1:5672//",
    disk_name="TenB"
)

config = configs()  # if use ConfigUpdate.upsert_field_to_redis, need use configs for new fields


if __name__ == '__main__':
    # ConfigUpdate.upsert_field_to_redis(disk_name='TenD')
    print(configs())
    # upsert_config_to_redis()  # update or insert current config to redis.
    # print(lookup_proj_config())  # show current project config
    # print(SetRedis.getkeys())
    # SetRedis.delfiels('config_redis')
