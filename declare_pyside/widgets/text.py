from .base_item import BaseItem

from ..path_model import light_clean_theme_dir


class Text(BaseItem):
    qmlfile = f'{light_clean_theme_dir}/LCText.qml'
