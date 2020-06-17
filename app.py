import json
from cmdb.types import get_instance


# jsonstr = """
# {
#     "type":"cmdb.types.IP",
#     "value":"192.168.0.1",
#     "option":{
#         "prefix":"192.2"
#     }
# }
# """
#
#
# jsonstr = """
# {
#     "type":"cmdb.types.Int",
#     "value":100,
#     "option":{
#         "max":100,
#         "min":1
#     }
# }
# """
#
# obj = json.loads(jsonstr)
#
# print(get_instance(obj['type'], obj['option']).stringify(obj['value']))
#
#
# jsonstr2 = """
# {
#     "type":"cmdb.types.Int",
#     "value":2,
#     "option":{
#         "min":1,
#         "max":100
#     }
# }
# """
#
# obj2 = json.loads(jsonstr2)
# print(get_instance(obj2['type'], obj2['option']).stringify(obj2['value']))



