import json
from cmdb.types import get_instance


jsonstr = """
{
    "type":"cmdb.types.Int",
    "value":300
}
"""

obj = json.loads(jsonstr)

print(get_instance(obj['type']).stringify(obj['value']))



