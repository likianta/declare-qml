from collections import defaultdict
from os.path import exists

from bs4 import BeautifulSoup
from lk_utils import read_and_write
from lk_utils.lk_logger import lk
from lk_utils.read_and_write import loads


def main(file_i, file_o):
    """
    Args:
        file_i: '~/resources/no3_all_qml_types.json'. see `no2_all_qml_types.py`
        file_o: '~/resources/no4_all_qml_props.json'
            {
                module: {
                    qmltype: {
                        'import': module,
                        'inherits': parent_qmltype,
                        'props': [
                            prop, ...
                        ]
                    }, ...
                }, ...
            }
    """
    reader = read_and_write.loads(file_i)  # type: dict
    writer = defaultdict(lambda: defaultdict(lambda: {
        'import'  : '',
        'inherits': '',
        'props'   : []
    }))
    
    for module, qmltype, file_i in _get_files(
            reader['data'], reader['qtdoc_dir']
    ):
        lk.logax(qmltype)
        
        if not exists(file_i):
            lk.logt('[W3924]', 'file not found', qmltype)
            writer[module][qmltype]['import'] = module
            continue
        
        soup = BeautifulSoup(loads(file_i), 'html.parser')
        #   以 '{qt}/Docs/Qt-5.14.2/qtquick/qml-qtquick-rectangle.html' 为例分析
        
        try:  # inherits
            e = soup.find('table', 'alignedsummary')
            e = e.tr.find_next_sibling('tr')
            if e.td.text.strip() == 'Inherits:':
                e = e.find('td', 'memItemRight bottomAlign')
                parent_component = e.text.strip()
            else:
                parent_component = ''
        except AttributeError:
            parent_component = ''
        
        try:  # props
            e = soup.find(id='properties')
            e = e.find_next_sibling('ul')
            props = [li.a.text for li in e.find_all('li')]
        except AttributeError:
            props = []
        
        writer[module][qmltype]['import'] = module
        writer[module][qmltype]['inherits'] = parent_component
        writer[module][qmltype]['props'] = props
        
        del soup
    
    read_and_write.dumps(writer, file_o)


def _get_files(data: dict, idir: str):
    for module_group, node1 in data.items():
        for module, node2 in node1.items():
            for qmltype, relpath in node2.items():
                yield module, qmltype, idir + '/' + relpath


if __name__ == '__main__':
    main('../resources/no4_all_qml_types.json',
         '../resources/no5_all_qml_props.json')
    lk.print_important_msg()
