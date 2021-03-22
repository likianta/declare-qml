import re
from collections import defaultdict

from lk_utils import read_and_write


def main(file_i, file_o):
    """
    Args:
        file_i: '~/resources/no4_all_qml_props.json'. see `no3_all_qml_props.py`
        file_o: '~/resources/no5_pyml_namespaces.json'
    """
    reader = read_and_write.loads(file_i)  # type: dict
    writer = defaultdict(lambda: defaultdict(dict))
    #   {module: {component: dict x, ...}, ...}
    #       x: {'import': ..., 'inherits': ..., 'props': ...}
    
    for qml_module, node1 in reader.items():
        for qml_type, node2 in node1.items():
            pyml_module = f'pyml.{qml_module.lower()}'
            component = qml_type
            
            writer[pyml_module][component] = {
                'import'  : 'pyml.{}'.format(node2['import'].lower()),
                'inherits': node2['inherits'],
                'props'   : tuple(map(hump_2_underline_case, node2['props'])),
            }
    
    read_and_write.dumps(writer, file_o)


def hump_2_underline_case(name: str):
    """ 驼峰转下划线式命名.
    
    References:
        https://www.yuque.com/tianyunperfect/ygzsw4/av4s8q
    """
    p = re.compile(r'([A-Z]+)')
    name = p.sub(r'_\1', name).lower().lstrip('_')
    return name


if __name__ == '__main__':
    main(
        '../resources/no5_all_qml_props.json',
        '../resources/no6_pyml_namespaces.json'
    )
