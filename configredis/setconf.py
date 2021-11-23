from configredis.setredis import SetRedis
from json import dumps, loads
from datetime import datetime
import sys
import logging
import os
import socket
import re


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
redis = SetRedis()


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
        return redis.getconf(proj_name)

    @classmethod
    def lookup_proj_config(cls, env=None, replace_domain=''):
        """
        lookup current project config.
        """
        return SetConfig.with_domain(SetConfig.conf_mapping_, replace_domain, env)


class ConfigUpdate:
    project_name_ = Tools.project_name()
    local_mapping_ = {}
    redis_mapping_ = Tools.lookup_redis_proj_config()
    conf_mapping_ = local_mapping_ or redis_mapping_

    @classmethod
    def defaultconfig(cls, **mapping):
        """
        set default env args.
        need import this func to your config document.
        :param mapping: dict
        """
        cls.envconfig('default', **mapping)

    @classmethod
    def devconfig(cls, **mapping):
        """
        set development env args.
        need import this func to your config document.
        :param mapping: dict
        """
        cls.envconfig('dev', **mapping)

    @classmethod
    def proconfig(cls, **mapping):
        """
        Set production env args.
        need import this func to your config document.
        :param mapping: dict
        """
        cls.envconfig('pro', **mapping)

    @classmethod
    def envconfig(cls, env: str, **mapping):
        """
        Set production env args.
        need import this func to your config document.
        :param env: env name
        :param mapping: dict
        """
        cls.local_mapping_[env] = mapping

    @classmethod
    def with_domain(cls, configs, replace_domain='', env=None):
        configs = dumps(configs)
        conf = loads(cls.__change_host(configs, replace_domain) if replace_domain else configs)
        return {**conf.get('default', {}), **conf.get(env)} if env else conf

    @classmethod
    def __change_host(cls, conf, domain: str):
        pattern = r'[\w\.]+' + domain.replace('.', r'\.')
        conf, pattern = conf, re.compile(r'' + pattern)
        n_d = {i: Tools.host_ip(i) for i in pattern.findall(conf)}
        for k, v in n_d.items():
            conf = conf.replace(k, v)
        return conf

    class ConfigArgs:
        """
        get config args value from redis.
        """

        def __getitem__(self, env):
            """
            sample:
            :param env: name is 'dev'
            :return: dict e.g: {'disk_name': 'TenTBc'}
            """
            item = redis.getconf(Tools.project_name())
            return item.get(env, '')


class SetConfig(ConfigUpdate):

    @classmethod
    def upsert_config_to_redis(cls, mapping=None, notify=True):
        """
        insert or update current config to redis.
        """
        redis.set_conf(cls.project_name_, mapping=mapping or cls.local_mapping_, notify=False)
        logger.info(f" {cls.project_name_}'s config has been written to redis.") if notify else None

    @classmethod
    def upsert_field_to_redis(cls, env='default', notify=True, **kwargs):
        cls.conf_mapping_[env] = {**cls.conf_mapping_[env], **kwargs}
        redis.set_conf(cls.project_name_, mapping=cls.conf_mapping_, notify=False)
        logger.info(f" {cls.project_name_}'s {env} config fileds has been written to redis.") if notify else None

    @classmethod
    def configs(cls, replace_domain: str = None):
        """
        get config info according env args. [defult/dev/pro]
        need import this func to your END of config document.
        :return: env config info as dict.
        """
        env = sys.argv[-1].lower()
        cls.upsert_config_to_redis(cls.local_mapping_, notify=False)
        if not cls.local_mapping_:
            logger.warning(' Not catch local env args, will use redis env args.')
        if env not in cls.conf_mapping_:
            logger.warning(' Not catch env args or defultconfig not setup. e.g: python sample.py dev|pro')
            logger.warning(' Will start under dev env? exit: ctrl+c')
            logger.info(f' Current env is dev\n')
            env = 'dev'
        else:
            logger.info(f' Current env is {env}\n')
        return cls.with_domain(cls.conf_mapping_, replace_domain, env)

    @classmethod
    def delconfs(cls, name=None):
        """
        delete concent from name or key.
        :param name: proj_name
        """
        confs, res = cls.getconfs(name, score_cast_func=int), 0
        sore_keys = list(confs.keys())
        sore_keys.sort()
        p_conf = "\n".join(["0: All", *[f"{k+1}: {cls.__f_score(v)} ({v}) -> {confs[v]}"
                                        for k, v in enumerate(sore_keys)]])
        print(p_conf)
        choose = input('Enter index num which config choosed (split with ","):').replace(' ', '').split(',')
        del_items = [confs[sore_keys[i]] for i in range(len(sore_keys)) if str(i+1) in choose]
        if '0' in choose:
            res = redis.redis.delete(name)
        elif del_items:
            res = redis.redis.zrem(name, *del_items)
        print(res)
        if res:
            logger.info('Redis configs has been deleted.')

    @classmethod
    def getconfs(cls, name=None, score_cast_func=None):
        name = name or cls.project_name_
        f_score = score_cast_func or cls.__f_score
        return {str(i[1]): i[0] for i in redis.redis.zscan_iter(name, score_cast_func=f_score)}

    @classmethod
    def __f_score(cls, stamp):
        return datetime.fromtimestamp(int(stamp))
