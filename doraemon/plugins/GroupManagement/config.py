from nonebot import get_driver
from pydantic import BaseModel, Extra


class Config(BaseModel):
    """Plugin Config Here"""
    ban_rand_time_min: int = 60  # 随机禁言最短时间(s) default: 1分钟
    ban_rand_time_max: int = 2_591_999  # 随机禁言最长时间(s) default: 30天: 60*60*24*30


driver = get_driver()
global_config = driver.config
plugin_config = Config.parse_obj(global_config.dict())
