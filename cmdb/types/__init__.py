import importlib
import ipaddress


def get_instance(meta_type: str):
    """
    :param meta_type: 数据库中field表中meta字段中json字符串中的type值
    :return: 通过对type字串的解析处理后返回一个类型转换的实例
    """
    m, _, c = meta_type.rpartition('.')
    cls = getattr(importlib.import_module(m), c)  # 使用反射动态加载
    obj = cls()
    if isinstance(obj, BaseType):
        return obj
    raise TypeError('Wrong Type {}. Not subclass of BaseType.'.format(meta_type))


class BaseType:
    """cmdb字段类型基类"""
    def stringify(self, value):
        # 转换成字符串，基类未实现
        raise NotImplementedError()

    def destringify(self, value):
        #
        raise NotImplementedError()


class Int(BaseType):
    """
    int类型较验
    """
    def stringify(self, value):
        return str(int(value))

    def destringify(self, value):
        return value


class IP(BaseType):
    """
    ip地址类型较验
    """
    def stringify(self, value):
        return str(ipaddress.ip_address(value))

    def destringify(self, value):
        return value



