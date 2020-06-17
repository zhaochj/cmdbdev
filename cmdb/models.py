from sqlalchemy import Column, String, Integer, Boolean, Text
from sqlalchemy import ForeignKey, UniqueConstraint, create_engine
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.ext.declarative import declarative_base
from . import config
import json
from .types import get_instance


Base = declarative_base()


class Schema(Base):
    """模型表，记录一个个虚拟表的名称"""
    __tablename__ = 'schema'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(48), nullable=False, comment='生成虚拟表的表名称')
    desc = Column(String(128), nullable=True)
    deleted = Column(Boolean, nullable=False, default=False)

    # 描述关系，从schema表想找到一个表对应的字段，需要到field表中找
    fields = relationship('Field')


class reference:
    """虚拟表外键约束解析"""
    def __init__(self, ref: dict):
        self.schema = ref['schema']
        self.field = ref['field']
        self.on_delete = ref.get('on_delete', 'disable')
        self.on_update = ref.get('on_update', 'disable')


class FieldMeta:
    """解析meta字符串"""
    def __init__(self, meta_str:str):
        meta = json.loads(meta_str)
        if isinstance(meta['type'], str):  # 如果是简写的方式
            self.instance = get_instance(meta['type'])
        else:
            option = meta['type'].get('option')  # 有可能option写成了一个数组，如： option:[...]
            if option:
                self.instance = get_instance(meta['type'], option)
            else:
                self.instance = get_instance(meta['type'])
        self.nullable = meta.get('nullable', False)  # 默认不可为空
        self.unique = meta.get('unique', True)   # 默认为唯一
        self.default = meta.get('default')
        self.multi = meta.get('multi', False)  # 默认不可存放多值

        ref = meta.get('reference')
        if ref:
            self.reference = reference(ref)
        else:
            self.reference = None


class Field(Base):
    """字段表，记录虚拟表的对应的字段名称
    meta字段是对字段的属性定义以及各种约束，格式如下：
    {
        "type":{
            "name":"cmdb.types.IP",
            "option":{
                "prefix":"192.168"
            }
        },
        "nullable":true,
        "unique":false,
        "default":"",
        "multi":true,
        "reference":{
            "schema":"ippool",
            "field":"ip",
            "on_delete":"cascade|set_null|disable",   表示取一个值
            "on_update":"cascade|disable"     表示取一个值
        }

    }
    如果没有option，还可以简写为：
    {
        "type":"cmdb.types.IP",
        "unique":true,
        ...
    }
    """
    __tablename__ = 'field'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(48), nullable=False)
    meta = Column(Text, nullable=False, comment='元数据，描述字段的约束，以json方式存放')
    deleted = Column(Boolean, nullable=False, default=False)
    schema_id = Column(Integer, ForeignKey('schema.id'), nullable=False)
    ref_id = Column(Integer, ForeignKey('field.id'), nullable=True, comment='虚拟表中外键关联')

    # 关系描述
    schema = relationship('Schema')
    ref = relationship('Field', uselist=False)  # 一对一

    # 一个表(schema_id)和此表中的一个字段(name)是不可重复的，所以schema_id与name可以联合作为一个unique唯一键，但增加了deleted这个表示逻辑删除的字段后会带来一个问题
    # 当删除一个表中的字段后，再创建一个同名的字段，那同名字段在unique键约束下无法创建。所以如果设置了unique约束，那字段被删除后再创建就得创建一个不同名的字段名。
    # 还有一个处理方法，把schema_id，name， deleted三个字段联合作为unique，那这样一个字段被删除后下一次创建同名字段不会有问题，但再删除一次时因是逻辑删除又会违反unique约束。
    # 这里需要有所取舍
    __table_args__ = (UniqueConstraint('schema_id', 'name'),)

    # 解析meta字段并绑定到meta_data属性上
    @property
    def meta_data(self):
        return FieldMeta(self.meta)


class Entity(Base):
    """实体表，每个虚拟表记录一行数据，此表得增加一行记录"""
    __tablename__ = 'entity'

    id = Column(Integer, primary_key=True, autoincrement=True)
    key = Column(String(128), nullable=False, comment='uuid')
    deleted = Column(Boolean, nullable=False, default=False)
    schema_id = Column(Integer, ForeignKey('schema.id'), nullable=False)

    # 关系描述
    schema = relationship('Schema')


class Value(Base):
    """真实记录字段数据的表"""
    __tablename__ = 'value'

    id = Column(Integer, primary_key=True, autoincrement=True)
    value = Column(Text, nullable=False)
    deleted = Column(Boolean, nullable=False, default=False)
    entity_id = Column(Integer, ForeignKey('entity.id'), nullable=False)
    field_id = Column(Integer, ForeignKey('field.id'), nullable=False)

    # 关系描述
    entity = relationship('Entity')
    field = relationship('Field')

    # 一行数据中，即一个虚拟表的一个字段上的一行数据是唯一的
    __table_args__ = (UniqueConstraint('entity_id', 'field_id'),)


# 创建数据库连接引擎
engine = create_engine(config.URL, echo=config.DATABASE_DEBUG)


# 创建所有表
def create_all():
    Base.metadata.create_all(engine)


# 删除所有表
def drop_all():
    Base.metadata.drop_all(engine)


# 创建连接数据库会话
Session = sessionmaker(engine)
session = Session()


