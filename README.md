# config-redis

config-redis is a python library for get project config from redis and don't show your config details in the project.

## Installation

1.Use the package manager [pip](https://pypi.org/project/config-redis/) to install Proj_config.

```bash
pip install config-redis
```

2.Install redis-server.

3.Set environment variables from command line.

```bash
export CONF_FOR_REDISCONF="{'host': '172.0.0.1', 'port': 6379, 'db': 0, 'password': 'your_password', 'decode_responses': True}" :$CONF_FOR_REDISCONF
```



## Usage

#### 1.setup your config
##### your_proj/setting.py
```python
from configredis.setconf import devconfig, proconfig, configs, ConfigArgs

con = ConfigArgs()

devconfig(
    disk_name="Ten",
    sentry=False,
    celery_broker="amqp://user:password@0.0.0.0:5672//",
)

proconfig(
    sentry=True,
    celery_broker="amqp://user:password@172.0.0.1:5672//",
)

config = configs()
```

#### 2.Use upsert_config_to_redis func update or insert current config to redis.  lookup_proj_config func to check the config in redis.
##### your_proj/setting.py
```python
from configredis.setconf import ConfigUpdate, lookup_proj_config

ConfigUpdate.upsert_config_to_redis()  # update or insert current config to redis.

print(lookup_proj_config())  # show current project config

```

#### 3.After write the project config to redis then your can chenge setting.py as below.
##### your_proj/setting.py
```python
from configredis.setconf import devconfig, proconfig, configs, ConfigArgs

con = ConfigArgs()

devconfig(
    disk_name=con['dev']['disk_name'],
    sentry=con['dev']['sentry'],
    celery_broker=con['dev']['celery_broker'],
)

proconfig(
    sentry=con['pro']['sentry'],
    celery_broker=con['pro']['celery_broker'],
)

config = configs()

if __name__ == '__main__':
    print(config)
``` 

#### 4.Run your project as config from command line.
```bash
python sample.py pro/dev
```


## Contributing
Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

Please make sure to update the tests as appropriate.

## License
[MIT](https://choosealicense.com/licenses/mit/)
