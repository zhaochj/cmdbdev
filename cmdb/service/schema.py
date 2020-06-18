from ..models import Schema, session
from ..utils import get_logger, paginate
from ..config import LOG_HOME


logger = get_logger(__name__, '{}/logs/{}.log'.format(LOG_HOME, __name__))


def get_schema_by_name(name: str, deleted=False):
    """
    根据表名称查询接口
    :param name: 表名称，唯一键
    :param deleted: 是否删除
    :return: query对象
    """
    query = session.query(Schema).filter(Schema.name == name.strip())  # 因name是唯一键，只能查出一条数据
    if not deleted:
        query = query.filter(Schema.deleted is False)
    return query.first()


def add_schema(name: str, desc: str = None):
    """
    增加一虚拟表接口
    :param name: 表名称，唯一键
    :param desc: 表描述信息
    :return: 表对象
    """
    schema = Schema()
    schema.name = name
    schema.desc = desc
    session.add(schema)
    try:
        session.commit()
        logger.info('Add a schema. id:{} name:{}'.format(schema.id, schema.name))
        return schema
    except Exception as e:
        session.rollback()
        logger.error('Failed to add schema {}. Error: {}'.format(name, e))


def drop_schema(schema_id: int):
    """
    删除一张虚拟表接口，使用id来删除比使用name要好
    :param schema_id: 表的id
    :return: 表对象
    """
    try:
        schema = session.query(Schema).filter((Schema.id == schema_id) & (Schema.deleted is False))
        if schema:
            schema.deleted = True
            session.add(schema)
            try:
                session.commit()
                logger.info('Delete a schema. id:{} name:{}'.format(schema.id, schema.name))
                return schema
            except Exception as e:
                session.rollback()
                raise e  # 外层有捕获，直接raise
        else:
            raise ValueError('Wrong ID {}'.format(id))  # 不是在try...except中不能直接raise，需要有具体的错误类型
    except Exception as e:
        logger.error('Failed to drop schema {}. Error: {}'.format(schema_id, e))


def list_schema(page: int, size: int, deleted=False):
    """
    列表逻辑表，列表正在使用的，即未删除的表
    :param page: 第几页
    :param size: 一页显示数据量
    :param deleted: 删除状态
    :return:
    """
    query = session.query(Schema)
    if not deleted:
        query.filter(Schema.deleted is False)
    try:
        result = paginate(page, size, query)
        return result
    except Exception as e:
        logger.error('Failed to paginate. Error: {}'.format(e))




