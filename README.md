# config-redis

config-redis是一个python库，用于从redis获取项目配置，并且可以在项目中隐藏您的配置详细信息，以免配置信息泄露。

## Installation

1.使用python包管理工具 [pip](https://pypi.org/project/config-redis/) 进行安装.

```bash
pip install config-redis
```

2.本项目需要使用redis存储配置

3.从命令行设置环境变量或写入配置文件

```bash
export CONF_FOR_REDISCONF="{'host': '172.0.0.1', 'port': 6379, 'db': 0, 'password': 'your_password', 'decode_responses': True}" :$CONF_FOR_REDISCONF
```

## Usage

#### 1.setup your config, e.g: your_proj/setting.py
```python
from configredis import SetConfig, Tools, SetRedis

con = SetConfig.ConfigArgs()

# env 关键字是default, default是全局配置，可以放置env共用的配置
SetConfig.defaultconfig(
    c_env='default',
    disk_name='TenD'
)

# env 关键字是dev
SetConfig.devconfig(
    c_env='dev',
    celery_broker="amqp://user:password@172.0.0.1:5672//",
    r_flow={'host': Tools.host_ip('httpbin.org'), 'port': 7000, 'db': 0, "cluster": True},
    r_flow1={'host': 'httpbin.org', 'port': 7000, 'db': 0, "cluster": True}
)

# env 关键字是pro
SetConfig.proconfig(
    c_env='pro',
    celery_broker="amqp://user:password@172.0.0.1:5672//",
    disk_name="TenB"
)

# env 关键字是custom_env
SetConfig.envconfig(
    'custom_env',
    c_env='custom_env'
)

config = SetConfig.configs('bin.org')  # 如果明文配置env，会以明文配置优先，如果配置文件删除明文配置，则会查找redis最新配置，SetConfig.configs会自动把明文配置持久化到redis, replace_domain参数可以自动解析相关域名IP，适合局域网静态IP地址，如果是动态IP，请关闭。
if __name__ == '__main__':
    print(config)  # 获得当前env的配置

```

#### 2.运行上一步SetConfig.configs会自动会自动把明文配置持久化到redis，此时删除所有明文配置文件SetConfig.defaultconfig/SetConfig.devconfig/SetConfig.proconfig/SetConfig.envconfig，项目会自动从redis拉取最新的配置。
```python
from configredis import SetConfig, Tools, SetRedis

con = SetConfig.ConfigArgs()
config = SetConfig.configs('bin.org')

if __name__ == '__main__':
    print(config)  # 获得当前env的配置
    # print(SetConfig.getconfs())  # 查看redis中项目目前所有版本配置
    # SetConfig.print_config()  # 罗列项目所有版本的配置信息，并根据index打印相关配置，方便复制到配置文件, 顺序从新到旧
    # print(con['custom_env'])  # 根据env查看redis储存的最新配置
    # SetConfig.upsert_field_to_redis('custom_env', disk_name='TenC')  # 明文配置删除的情况下，给redis中的最新配置增加字段，不要跟明文配置同时使用，会导致redis版本错乱  # noqa
    # print(Tools.lookup_redis_proj_config())  # 显示redis存储的最新配置
    # print(Tools.lookup_proj_config(replace_domain='bin.org'))  # 显示当前所有env配置，明文优先于redis配置
    # print(SetRedis().getkeys())  # 查看redis所有的项目名称
    # SetConfig.delconfs()  # 罗列项目所有版本的配置信息，并根据index删除相关配置, 顺序从旧到新

```

#### 3.在项目中导入config获得对应的配置

```python
from tests.setting import config

def test_env():
    return config['celery_broker']

if __name__ == '__main__':
    print(test_env())
``` 

#### 4.使用命令行根据关键字获得配置运行项目。
```bash
python sample.py pro/dev/custom_env  # default 是全局配置，可以放置env共用的配置
```


## Contributing
使用前请做适当的测试，以确定跟您的项目完全兼容。

## License
[MIT](https://choosealicense.com/licenses/mit/)
