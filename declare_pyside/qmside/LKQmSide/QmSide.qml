import QtQuick 2.15

Item {
    id: root

    function connect_prop(s_obj, s_prop, t_obj, t_prop) {
        eval(`t_obj.${t_prop} = Qt.binding(() => s.obj.${s_prop})`)
    }

    function connect_func(s_obj, s_prop, func_id, participants) {
        eval(`
            s_obj.${s_prop} = Qt.binding(
                () => PySide.eval('${func_id}', ${participants})
            )
        `)
    }

    function eval_in_js(code, args) {
        eval(code)
    }

    Component.onCompleted: {
        PySide.call('__register_qside_object', root)
    }
}
