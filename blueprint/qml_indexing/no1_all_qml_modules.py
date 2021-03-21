"""
Requirements:
    如需运行本模块, 请先安装 Qt 5.0+ (推荐 5.15) 完整版.
    本模块所用到的离线文件读取自:
        "{YourQtProgram}/Docs/Qt-{version}/qtdoc/modules-qml.html".
"""
from bs4 import BeautifulSoup
from lk_utils import read_and_write


def main(qtdoc_file: str):
    """
    Args:
        qtdoc_file: "{YourQtProgram}/Docs/Qt-{version}/qtdoc/modules-qml.html"
    
    Input:
        `qtdoc_file`
    Output:
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
            1. `module_group` 的键是没有空格或连接符的, 只有纯小写字母和尾部数字
               1 组成 (例如 'qtquickcontrols1')
            2. `module` 的键是由纯小写字母和连接符组成 (例如 'qtquick-windows')
            3. `name` 是由首字母大写的单词和点号组成 (例如 'QtGraphicalEffects')
                1. 但是有一个特例: 'QtQuick.labs.xxx' 从 'lab' 开始全部都是小写
                   (例如 'Qt.labs.folderlistmodel')
            4. 该生成文件可被直接用于 `all_qml_types.py
               :_correct_module_lettercase`
    """
    qtdoc_file = qtdoc_file.replace('\\', '/')
    soup = BeautifulSoup(read_and_write.read_file(qtdoc_file), 'html.parser')
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

        """ 备忘
        
        1. 'Qt NFC' 的 'NFC' 应变成 'Nfc', 'Qt QML' 的 'QML' 应变成 'Qml', 我在
           给 _name 变量赋值时修正了它们
        2. module_group = 'qtwinextras' 的 name = 'Qt Windows Extras', 我使用
           `extra_words` 变量用于解决这个问题, 见相关用法
        3. name = 'Qt 3D Qt3DAnimation' 这个貌似是官方的写法有点问题 (我觉得正确
           写法应该是 'Qt 3D Animation'), 所以我在 name 变量赋值时加了一个
           replace 用于修复它
        4.
        
        总之各种小问题挺多的, 我已经逐行审查了生成结果 (格式化后有 100 多行, 不
        算多, 所以都看了一半), 现在的生成结果已经没问题了
        """
        
        module_group = link[1]  # type: str
        # -> 'qtquickcontrols1'
        module = link[2].replace('-qmlmodule.html', '')  # type: str
        # -> 'qtquick-controls'
        name = e.a.text.replace(' QML Types', '').rstrip(' 12') \
            .replace('Qt Quick', 'QtQuick') \
            .replace('Qt3DAnimation', 'Animation') \
            .replace('Web', 'Web ') \
            .title()  # type: str
        """ name 为 module_group 和 module 提供一个小型词典, 该词典可用于替换后
            二者的字符串中出现的单词, 比如:
                module_group = 'qtquickcontrols1'
                module = 'qtquick-controls'
                name = 'QtQuick Controls'
            则利用 name 提供的小词典, 我们可以快速转换 module_group 和 module 中
            的单词为正确的大小写:
                _module_group = 'QtQuickControls1'
                _module = 'QtQuick-Controls'
                
            但在实际情况中, 并没有这么简单, 因为遇到了很多小问题. 比如:
                module_group = 'qtnfc'
                module = 'qtnfc'
                name = 'Qt NFC'
            我们想要的是 'QtNfc', 但 name 提供的词典的大小写存在错误. 于是我们用
            `str.title()` 方法解决了 (这也是为什么 name 变量赋值表达式中有一个
            `.title()` 的原因).
            但也产生了另外一个问题:
                module_group = 'qtwebengine'
                module = 'qtwebengine'
                name = 'Qt WebEngine'.title() -> 'Qt Webengine'
            这就会导致生成: 'QtWebengine'.
            为了修复这个问题, 我们在 name 的赋值表达式中在 `.title()` 之前加了一
            步 `.replace('Web', 'Web ')`.
            现在所有问题都通过这些观察和反馈进行了修正, 这也是为什么 name 看起来
            有点复杂的原因.
            
            此外还需要说一点, 关于 QtQuick.Controls 是分为 v1 和 v2 的, 我是这样
            处理的:
                module_group = 'qtquickcontrols1' -> 'QtQuickControls'
                    module = 'qtquick-controls' -> 'QtQuickControls'
                module_group = 'qtquickcontrols' -> 'QtQuickControls'
                    module = 'qtquick-controls2' -> 'QtQuickControls'
            (Qt 的命名关系有点乱, 模组尾号 1 对应模块无尾号; 模组无尾号对应模块
            尾号 2, 我把它们最终的名字都统一成一个了, 不用再分 1 和 2.)
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
    
    read_and_write.dumps(writer, '../../resources/all_qml_modules.json')


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
    main(r'D:/programs/qt/qt_5.14.2/Docs/Qt-5.14.2/qtdoc/modules-qml.html')
