from pyml_rc.declare_qt import *
from tests.test3 import AddressBar

'''
-------------------------
391 chars, 13 line breaks
-------------------------
'''

with Application() as app:
    with Widget() as win:
        with Label() as label:
            label.setText('Hello World')
        
        with VBoxLayout() as vbox:
            with PushButton('Top') as btn1:
                pass
            
            with PushButton('Bottom') as btn2:
                pass
            
            with AddressBar() as addr_bar:
                pass

''' qml like structure
-------------------------
494 chars, 27 line breaks
-------------------------

Application {
    Widget {
        id: win

        Label {
            id: label
            text: 'Hello World'
        }

        VBoxLayout {
            id: vbox

            PushButton {
                id: btn1
                text: 'Top'
            }

            PushButton {
                id: btn2
                text: 'Bottom'
            }

            AddressBar {
                id: addr_bar
            }
        }
    }
}
'''
