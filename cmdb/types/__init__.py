import ipaddress


classes_cache = {}  # 缓存类
obj_cache = {}  # 缓存实例对象


def get_class(meta_type: str):
    """
    :param meta_type: 数据库中field表中meta字段中json字符串中的type值
    :return: class
    """
    cls = classes_cache.get(meta_type)
    if cls:
        return cls
    raise TypeError('Wrong Type {}. Not subclass of BaseType.'.format(meta_type))

    # m, _, c = meta_type.rpartition('.')
    # cls = getattr(importlib.import_module(m), c)  # 使用反射动态加载,python中相同的模块多次加载时也只加载一次
    # classes_cache[meta_type] = cls  # 缓存类
    # if not issubclass(cls, BaseType):
    #     raise TypeError('Wrong Type {}. Not subclass of BaseType.'.format(meta_type))
    # return cls


def get_instance(meta_type: str, option: dict):
    """
    :param meta_type: 数据库中field表中meta字段中json字符串中的type值
    :param option: meta中的option
    :return: 通过对type字串的解析处理后返回一个类型转换的实例
    """
    # 为了少创建实例对象，这里对实例对象也存放在加速字典中，选择key是关键，要不要创建一个新的实例由meta_type和option两个参数确定，如果不两个参数不变就是相同的一个实例
    key = ",".join("{}={}".format(k, v) for k, v in sorted(option.items()))
    key = "{}|{}".format(meta_type, key)
    obj = obj_cache.get(key)
    if obj:
        return obj
    cls = get_class(meta_type)
    obj = cls(option)
    obj_cache[key] = obj
    return obj


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


def inject_classes_cache():
    for k, v in globals().items():
        if type(v) == type and k != 'BaseType':
            classes_cache[k] = v      # Int   短名称
            classes_cache["{}.{}".format(__name__, k)] = v  # cmdb.types.Int  长名称
    # print(classes_cache)


# 此模块被导入时注入较验数据类型的class
inject_classes_cache()




