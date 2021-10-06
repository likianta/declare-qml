import QtQuick

Item {
    id: root
    objectName: 'QmlSide'

    function connectProp(s_obj, s_prop, t_obj, t_prop) {
        eval(`t_obj.${t_prop} = Qt.binding(() => s.obj.${s_prop})`)
    }

    function connectFunc(s_obj, s_prop, func_id, participants) {
        eval(`
            s_obj.${s_prop} = Qt.binding(
                () => PySide.eval('${func_id}', ${participants})
            )
        `)
    }

    function createComponent(qmlfile) {
        return Qt.createComponent(qmlfile)
    }

    function createObject(component, container) {
        return component.createObject(container)
    }

    function evalJs(code, args) {
        eval(code)
    }

    // Component.onCompleted: {
    //     console.log('register qmlside object')
    //     pyside.call('__register_qmlside_object', root)
    // }
}
