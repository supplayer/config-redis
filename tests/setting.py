from configredis.setconf import SetConfig, ConfigArgs, Tools
# from configredis.setredis import SetRedis


con = ConfigArgs()

SetConfig.defaultconfig(
    disk_name='TenD'
)

SetConfig.devconfig(
    sentry=False,
    celery_broker="amqp://user:password@172.0.0.1:5672//",
    r_flow={'host': Tools.host_ip('pro.cluster_redis.dns.com'), 'port': 7000, 'db': 0, "cluster": True},
    r_flow1={'host': 'pro.cluster_redis.dns.com', 'port': 7000, 'db': 0, "cluster": True}
)

SetConfig.proconfig(
    sentry=True,
    celery_broker="amqp://user:password@172.0.0.1:5672//",
    disk_name="TenB"
)

config = SetConfig.configs('dns.com')  # if use ConfigUpdate.upsert_field_to_redis, need use configs for new fields


if __name__ == '__main__':
    # ConfigUpdate.upsert_field_to_redis(disk_name='TenD')
    print(config)
    # upsert_config_to_redis()  # update or insert current config to redis.
    # print(Tools.lookup_redis_proj_config())  # show current project config
    # print(Tools.lookup_proj_config('dev'))
    # print(SetRedis.getkeys())
    # SetRedis.delfiels('config_redis')
