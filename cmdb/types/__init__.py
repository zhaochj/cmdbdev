import importlib
import ipaddress


def get_class(meta_type: str):
    """
    :param meta_type: 数据库中field表中meta字段中json字符串中的type值
    :return: class
    """
    m, _, c = meta_type.rpartition('.')
    cls = getattr(importlib.import_module(m), c)  # 使用反射动态加载
    if not issubclass(cls, BaseType):
        raise TypeError('Wrong Type {}. Not subclass of BaseType.'.format(meta_type))
    return cls


def get_instance(meta_type: str, option: dict):
    """
    :param meta_type: 数据库中field表中meta字段中json字符串中的type值
    :param option: meta中的option
    :return: 通过对type字串的解析处理后返回一个类型转换的实例
    """
    cls = get_class(meta_type)
    return cls(option)


class BaseType:
    """cmdb字段类型基类"""
    def __init__(self, option: dict):
        self.option = option  # dict

    def __getattr__(self, item):
        return self.option.get(item)

    def stringify(self, value):
        # 转换成字符串，基类未实现
        raise NotImplementedError()

    def destringify(self, value):
        #
        raise NotImplementedError()


class Int(BaseType):
    """
    int类型及范围较验
    """
    def stringify(self, value):
        val = int(value)
        _min = self.min  # 能够使用self.min，是因为父类BaseType实现了__getattr__方法
        _max = self.max
        if _min and val < _min:
            raise ValueError('too small')
        if _max and val > _max:
            raise ValueError('too big')
        return str(val)

    def destringify(self, value):
        return value


class IP(BaseType):
    """
    ip地址类型及前缀较验
    """
    def stringify(self, value):
        val = ipaddress.ip_address(value)
        if not str(val).startswith(self.prefix):
            raise ValueError('Must startswith {}'.format(self.prefix))
        return str(val)

    def destringify(self, value):
        return value



