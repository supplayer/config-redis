from configredis.setconf import devconfig, proconfig, configs, ConfigArgs, upsert_config_to_redis


con = ConfigArgs()

devconfig(
    disk_name="Ten",
    sentry=False,
    celery_broker="amqp://user:password@172.0.0.1:5672//",
)

proconfig(
    sentry=True,
    celery_broker="amqp://user:password@172.0.0.1:5672//",
)

config = configs()


if __name__ == '__main__':
    print(config)
    upsert_config_to_redis()  # update or insert current config to redis.
    print(lookup_proj_config())  # show current project config
