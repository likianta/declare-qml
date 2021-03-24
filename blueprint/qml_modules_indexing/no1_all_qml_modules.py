"""
Requirements:
    如需运行本模块, 请先安装 Qt 5.0+ (推荐 5.15) 完整版.
    本模块所用到的离线文件读取自:
        "{YourQtProgram}/Docs/Qt-{version}/qtdoc/modules-qml.html".
"""
from bs4 import BeautifulSoup
from lk_utils import read_and_write


def main(file_i: str, file_o):
    """
    Args:
        file_i: "~/blueprint/resources/no1_all_qml_modules.html". 该文件被我事先
            从 "{YourQtProgram}/Docs/Qt-{version}/qtdoc/modules-qml.html" 拷贝过
            来.
        file_o: '~/blueprint/resources/no2_all_qml_modules.json'
            "~/resources/all_qml_modules.json"
                格式: {
                    'module_group': {module_group: name, ...},
                        module_group: see `Notes:no1`
                        name: see `Notes:no3`
                    'module': {module: name, ...}
                        module: see `Notes:no2`
                }
                示例: {
                    'module_group': {
                        'qtquick': 'QtQuick',
                        'qtquickcontrols1': 'QtQuickControls1',
                        ...
                    },
                    'module': {
                        'qtquick-windows': 'QtQuick.Windows',
                        ...
                    },
                }
            Notes:
                1. `module_group` 的键是没有空格或连接符的, 只有纯小写字母和尾部
                    数字 1 组成 (例如 'qtquickcontrols1')
                2. `module` 的键是由纯小写字母和连接符组成 (例如 'qtquick
                    -windows')
                3. `name` 是由首字母大写的单词和点号组成 (例如
                    'QtGraphicalEffects')
                    1. 但是有一个特例: 'QtQuick.labs.xxx' 从 'lab' 开始全部都是
                        小写(例如 'Qt.labs.folderlistmodel')
                4. 该生成文件可被直接用于 `all_qml_types.py:_correct_module
                    _lettercase`
    """
    file_i = file_i.replace('\\', '/')
    soup = BeautifulSoup(read_and_write.read_file(file_i), 'html.parser')
    container = soup.find('table', 'annotated')
    
    writer = {
        'module_group': {},  # value: {module_group: name, ...}
        'module'      : {},  # value: {module: name, ...}
    }
    
    extra_words = ['Qt', 'Quick', 'Qml', 'Win', 'Labs']
    
    for e in container.find_all('td', 'tblName'):
        """ <td class="tblName">
                <p>
                    <a href="../qtquickcontrols1/qtquick-controls-qmlmodule
                            .html">
                        Qt Quick Controls 1 QML Types
                    </a>
                </p>
            </td>
        """
        link = e.a['href'].split('/')
        # -> ['..', 'qtquickcontrols1', 'qtquick-controls-qmlmodule.html']
        
        module_group = link[1]  # type: str
        # -> 'qtquickcontrols1'
        module = link[2].replace('-qmlmodule.html', '')  # type: str
        # -> 'qtquick-controls'
        name = (e.a.text
                .replace(' QML Types', '')
                .rstrip(' 12')
                .replace('Qt Quick', 'QtQuick')
                .replace('Qt3DAnimation', 'Animation')
                .replace('Web', 'Web ')
                .title())  # type: str
        
        """ 解释一下上面的 name 的处理逻辑.
            
            name 为 module_group 和 module 提供一个小型词典, 该词典可用于替换后
            二者的字符串中出现的单词的大小写形式, 比如:
                已知:
                    name = 'QtQuick Controls'
                待处理:
                    module_group = 'qtquickcontrols1'
                    module = 'qtquick-controls'
            则利用 name 提供的小词典, 我们可以快速转换 module_group 和 module 中
            的单词为想要的大小写:
                处理后:
                    module_group = 'QtQuickControls1'
                    module = 'QtQuick-Controls'
                
            在实际情况中, 不能直接用 `e.a.text` 的值, 因为有很多小问题需要修正,
            所以我们才进行了一系列处理:
                1. `replace(' QML Types', '')`: 把不必要的词尾去掉
                2. `rstrip(' 12')`: 为了解决 Qt 对 QtQuick.Controls 比较混乱的命
                    名, 我决定不再区分 v1 和 v2, 即去掉尾部的 '1' 和 '2'
                    背景: Qt 对 QtQuick.Controls 的命名关系有点乱, 如下所示:
                        QtQuick.Controls v1:
                            module_group = 'qtquickcontrols1'
                            module = 'qtquick-controls'
                        QtQuick.Controls v2:
                            module_group = 'qtquickcontrols'
                            module = 'qtquick-controls2'
                    经过处理后, v1 和 v2 统一变成了 'QtQuickControls', 不再作区
                    分.
                3. `replace('Qt Quick', 'QtQuick')`: 遵循模块的写法规范
                4. `replace('Qt3DAnimation', 'Animation')`: 针对 'Qt 3D
                    Qt3DAnimation' 的处理. 这个貌似是官方的写法有点问题, 所以我
                    把 'Qt3DAnimation' 改成了 'Animation'
                5. `replace('Web', 'Web ')`: 为了将 'Webengine' 拆分成 'Web' 和
                    'engine' (下一步会把 'engine' 改成 'Engine')
                6. `title()`: 将首字母大写, 非首字母小写. 例如:
                    1. 'Qt NFS' -> 'Qt Nfc'
                    2. 'Web engine' -> 'Web Engine'
                    3. 'Qt QML' -> 'Qt Qml'
                    
            此外还有一些其他问题:
                1. module_group = 'qtwinextras' 的 name = 'Qt Windows Extras',
                    我使用 `extra_words` 变量解决这个问题, 见相关用法
            
            很多都是由于 html 中书写格式比较自由导致的, 这里做了很多格式化工作.
            我已经逐行审查了早期的生成结果 (格式化后有 100 多行, 不算多, 所以都
            看了一遍), 经过上述的处理后, 已经可以看到新的输出结果都符合预期了.
        """
        
        _name = [x.title() for x in name.split(' ') if len(x) > 1]
        # -> ['QtQuick', 'Controls']
        _module_group = correct_module_lettercase(
            module_group, extra_words + _name
        )
        _module = correct_module_lettercase(
            module, extra_words + _name
        )
        
        writer['module_group'][module_group] = _module_group
        writer['module'][module] = _module
    
    read_and_write.dumps(writer, file_o)


def correct_module_lettercase(module: str, words: list):
    module = module.replace('-', '.').rstrip(' 12')
    #   'qtquick-controls2' -> 'qtquick.controls'
    for w in words:
        module = module.replace(w.lower(), w)
    #   'qtquick.controls' -> 'QtQuick.Controls'
    
    if '.Labs.' in module:
        a, b = module.split('.', 1)
        module = a + '.' + b.lower()
        # -> 'QtQuick.labs.calendar'
    
    return module


if __name__ == '__main__':
    main('resources/no1_all_qml_modules.html',
         'resources/no2_all_qml_modules.json')
