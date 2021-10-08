import QtQuick

Item {
    id: root
    objectName: 'QmlSide'

    function bind(t_obj, t_propName, s_obj, s_propName) {
        console.log('call qmlbind', t_obj, t_propName, s_obj, s_propName)
        eval(`t_obj.${t_propName} = Qt.binding(() => s_obj.${s_propName})`)
    }

    // TEST
    function test_bind(t_prop, s_prop) {
        t_prop = Qt.binding(() => s_prop)
    }

    function connect_func(s_obj, s_prop, func_id, participants) {
        eval(`
            s_obj.${s_prop} = Qt.binding(
                () => PySide.eval('${func_id}', ${participants})
            )
        `)
    }

    function create_component(qmlfile) {
        return Qt.createComponent(qmlfile)
    }

    function create_object(component, container) {
        return component.createObject(container)
    }

    function eval_js(code, args) {
        eval(code)
    }

    // Component.onCompleted: {
    //     console.log('register qmlside object')
    //     pyside.call('__register_qmlside_object', root)
    // }
}
