from ..models import session, Field, Entity, FieldMeta, Value
from .schema import get_schema_by_name
from ..utils import get_logger
from ..config import LOG_HOME

logger = get_logger(__name__, '{}/logs/{}.log'.format(LOG_HOME, __name__))


def get_fields(schema_name: str, deleted=False):
    """
    获取一个表的所有字段信息
    :param schema_name: 表名称
    :param deleted:
    :return:
    """
    schema = get_schema_by_name(schema_name)
    if not schema:
        raise ValueError('Error: schema name {} not exists.'.format(schema_name))
    query = session.query(Field).filter(schema.id == Field.schema_id)
    if not deleted:
        query = query.filter(Field.deleted is False)
    return query.all()


def get_field_info(schema_name: str, field_name: str, deleted=False):
    """
    获取一个表的一个字段信息
    :param schema_name:
    :param field_name:
    :param deleted:
    :return:
    """
    schema = get_schema_by_name(schema_name)
    if not schema:
        raise ValueError('Error: schema name {} not exists.'.format(schema_name))
    query = session.query(Field).filter(Field.schema_id == schema.id).filter(Field.name == field_name)
    if not deleted:
        query = query.filter(Field.deleted is False)
    return query.first()


def table_used(schema_id, deleted=False):
    """
    判断一个逻辑表是否已经在使用
    :param schema_id:
    :param deleted:
    :return:
    """
    query = session.query(Entity).filter(Entity.id == schema_id)
    if not deleted:
        query = query.filter(Entity.deleted is False)
    return query.first()  # None表示表未使用，非None表示该表已有记录


def _add_field(field: Field):
    """
    增加字段
    :param field:
    :return:
    """
    session.add(field)
    try:
        session.commit()
        return field
    except Exception as e:
        session.rollback()
        logger.error('Failed to add a field {}. Error: {}'.format(field.name, e))


def add_field(schema_name, field_name, meta):
    """
    在一个表上增加一个字段需要考虑的因素很多：
    1. 定义的meta格式是否正确，需要对传入的meta进行解析
    2. 增加的字段是否和其他字段有外键约束，即meta中是否有reference
    3. 增加字段的表是否已经有数据记录，即是否已经在使用，没使用直接增加字段
    4. 增加字段的表已经在使用时，meta中要求nullable可为空时，直接增加
    5. 表已经在使用，nullable要求不为空，且要求unique时，直接抛错，违反常理
    6. 表已经在使用，nullable要求不为空，不要求unique，且提供default值时，可以增加
    :param schema_name:
    :param field_name:
    :param meta:
    :return:
    """
    schema = get_schema_by_name(schema_name)
    if not schema:
        raise ValueError('Error: schema name {} not exists.'.format(schema_name))

    # 先解析meta
    meta_data = FieldMeta(meta)  # 能解析成功格式才符合要求
    field = Field()
    field.name = field_name.strip()
    field.meta = meta
    field.schema_id = schema.id

    # ref_id引用
    if meta_data.reference:
        # 获得引用的字段
        ref = get_field_info(meta_data.reference.schema, meta_data.reference.field)
        if not ref:
            raise TypeError('Wrong reference {}.{}.'.format(meta_data.reference.schema, meta_data.reference.field))
        field.ref_id = ref.id  # 数据库实体上绑定ref.id

    # 判断逻辑表是否在使用
    if not table_used(schema.id):  # 逻辑表没有数据时，直接增加字段
        return _add_field(field)

    # 已使用的逻辑表
    if meta_data.nullable:  # 允许为空，直接增加
        return _add_field(field)

    # 已使用逻辑表，且不允许为空
    if meta_data.unique:  # 还要求unique，不合理，做不到
        raise TypeError('This field is required an unique.')

    # 已使用逻辑表，且不允许为空，可以不唯一，那就看是否有default值了
    if not meta_data.default:
        raise TypeError('This field need a default value.')
    else:
        # 为逻辑表所有记录增加字段
        entities = session.query(Entity).filter((Entity.schema_id == schema.id) & (Entity.deleted is False)).all()

        for entity in entities:
            value = Value()
            value.entity_id = entity.id
            value.field = field  # 通过relationship关系去Field表中找相应的id
            value.value = meta_data.default
        return _add_field(field)






