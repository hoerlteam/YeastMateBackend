from PyInstaller.utils.hooks import collect_data_files

datas = collect_data_files('napari')
hiddenimports = ['napari.__main__', 'napari._event_loop']