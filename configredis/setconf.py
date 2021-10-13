from configredis.setredis import SetRedis
from json import dumps, loads
import sys
import logging
import os
import json
import socket
import re


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Tools:
    @classmethod
    def host_ip(cls, hostname: str):
        return socket.gethostbyname(hostname)

    @classmethod
    def project_name(cls, path=os.getcwd(), dirs=(".git",), default=None):
        """
        get current project name.
        :param path: scripts path
        :param dirs: save rule e.g: catch git
        :param default: if set default then save to the default absolute path
        :return: project root directory name
        """
        prev, path = None, os.path.abspath(path)
        while prev != path:
            if any(os.path.isdir(os.path.join(path, d)) for d in dirs):
                return path.split('/')[-1]
            prev, path = path, os.path.abspath(os.path.join(path, os.pardir))
        return default

    @classmethod
    def lookup_redis_proj_config(cls, proj_name=None):
        """
        lookup project config on redis.
        :param proj_name: project name which lookup from redis.
        """
        proj_name = proj_name or cls.project_name()
        return {k: json.loads(v) for k, v in SetRedis().getfiels(proj_name).items()}

    @classmethod
    def lookup_proj_config(cls, env=None):
        """
        lookup current project config.
        """
        return SetConfig.mapping_[env] if env else SetConfig.mapping_


class SetConfig:
    project_name_ = Tools.project_name()
    mapping_ = {**{'default': {}, 'dev': {}, 'pro': {}}, **Tools.lookup_redis_proj_config()}

    @classmethod
    def defaultconfig(cls, **mapping):
        """
        set default env args.
        need import this func to your config document.
        :param mapping: dict
        """
        cls.mapping_['default'] = mapping

    @classmethod
    def devconfig(cls, **mapping):
        """
        set development env args.
        need import this func to your config document.
        :param mapping: dict
        """
        cls.mapping_['dev'] = mapping

    @classmethod
    def proconfig(cls, **mapping):
        """
        Set production env args.
        need import this func to your config document.
        :param mapping: dict
        """
        cls.mapping_['pro'] = mapping

    @classmethod
    def configs(cls, replace_domain: str = None):
        """
        get config info according env args. [defult/dev/pro]
        need import this func to your END of config document.
        :return: env config info as dict.
        """
        env = sys.argv[-1].lower()
        if env not in cls.mapping_:
            logger.warning(' Not catch env args or defultconfig not setup. e.g: python sample.py dev|pro')
            logger.warning(' Will start under dev env? exit: ctrl+c')
            logger.info(f' Current env is dev')
            return cls.__with_domain(replace_domain)
        else:
            logger.info(f' Current env is {env}')
            return cls.__with_domain(replace_domain, env)

    @classmethod
    def __with_domain(cls, replace_domain='', env='dev'):
        return cls.__change_host(
            {**cls.mapping_[env], **cls.mapping_['default']}, replace_domain
        ) if replace_domain else {**cls.mapping_[env], **cls.mapping_['default']}

    @classmethod
    def __change_host(cls, conf, domain: str):
        pattern = r'[\w\.]+' + domain.replace('.', r'\.')
        conf, pattern = dumps(conf), re.compile(r'' + pattern)
        n_d = {i: Tools.host_ip(i) for i in pattern.findall(conf)}
        for k, v in n_d.items():
            conf = conf.replace(k, v)
        return loads(conf)


class ConfigArgs:
    """
    get config args value from redis.
    """

    def __getitem__(self, key):
        """
        sample:
        con = SetRedis()
        print(con['dev'])
        :param key: name is 'dev'
        :return: SetRedis().getfiels(name) -> dict e.g: {'disk_name': 'TenTBc'}
        """
        ConfigUpdate.upsert_config_to_redis(notify=True)
        item = SetRedis().getfiels(Tools.project_name())
        return json.loads(item.get(key)) if item.get(key) else ''


class ConfigUpdate(SetConfig):

    @classmethod
    def upsert_config_to_redis(cls, mapping=None, notify=True):
        """
        insert or update current config to redis.
        """
        SetRedis().upsert(cls.project_name_, mapping=mapping or cls.mapping_, notify=False)
        logger.info(f"Project: {cls.project_name_}'s config has been written to redis.") if notify else None

    @classmethod
    def upsert_field_to_redis(cls, env='default', notify=True, **kwargs):
        cls.mapping_[env] = {**cls.mapping_[env], **kwargs}
        SetRedis().upsert(cls.project_name_, mapping=cls.mapping_, notify=False)
        logger.info(
            f"Project: {cls.project_name_}'s {env} config fileds has been written to redis.") if notify else None
