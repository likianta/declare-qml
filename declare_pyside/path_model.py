from os.path import dirname

curr_dir = dirname(__file__).replace('\\', '/')
pkg_dir = curr_dir
proj_dir = dirname(pkg_dir)

qmlside_dir = f'{pkg_dir}/qmlside'
theme_dir = f'{pkg_dir}/theme'

light_clean_theme_dir = f'{theme_dir}/LightClean'

lk_qml_size_dir = f'{qmlside_dir}/LKQmlSide'
