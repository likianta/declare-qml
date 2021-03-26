from collections import defaultdict

from lk_logger import lk
from lk_utils.read_and_write import loads, dumps


def static_qml_basic_types(file_i, file_o):
    """ 统计 qml 的基本类型有哪些.
    
    Args:
        file_i: 'blueprint/resources/no5_all_qml_props.json'
            structure: {
                module: {
                    qmltype: {
                        'parent': ...,
                        'props': {prop: type, ...}
                    }, ...              ^--^ 我们统计的是这个.
                }, ...
            }
        file_o: *.txt or empty str. the empty string means 'donot dump to file,
            just print it on the console'.
            structure: [type, ...]. 一个去重后的列表, 按照字母表顺序排列.
            
    Outputs:
        data_w: {type: [(module, qmltype, prop), ...], ...}
    """
    data_r = loads(file_i)
    data_w = defaultdict(set)  # type: dict[str, set[tuple[str, str, str]]]
    
    for k1, v1 in data_r.items():
        for k2, v2 in v1.items():
            for k3, v3 in v2['props'].items():
                # k1: module; k2: qmltype; k3: prop; v3: type
                data_w[v3].add((k1, k2, k3))
                
    if file_o == '':
        lk.logp(sorted(data_w.keys()))
    else:
        data_w = {k: sorted(data_w[k]) for k in sorted(data_w.keys())}
        dumps(data_w, file_o)


if __name__ == '__main__':
    static_qml_basic_types(
        '../resources/no5_all_qml_props.json', '../../tests/test.json'
    )
