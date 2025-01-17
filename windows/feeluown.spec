def Entrypoint(dist, group, name, **kwargs):
    import pkg_resources

    # get toplevel packages of distribution from metadata
    def get_toplevel(dist):
        distribution = pkg_resources.get_distribution(dist)
        if distribution.has_metadata('top_level.txt'):
            return list(distribution.get_metadata('top_level.txt').split())
        else:
            return []

    kwargs.setdefault('hiddenimports', [])
    packages = []
    for distribution in kwargs['hiddenimports']:
        packages += get_toplevel(distribution)

    kwargs.setdefault('pathex', [])
    # get the entry point
    ep = pkg_resources.get_entry_info(dist, group, name)
    # insert path of the egg at the verify front of the search path
    kwargs['pathex'] = [ep.dist.location] + kwargs['pathex']
    # script name must not be a valid module name to avoid name clashes on import
    script_path = os.path.join(workpath, name + '-script.py')
    print("creating script for entry point", dist, group, name)
    with open(script_path, 'w') as fh:
        print("import", ep.module_name, file=fh)
        print("%s.%s()" % (ep.module_name, '.'.join(ep.attrs)), file=fh)
        for package in packages:
            print("import", package, file=fh)

        # pydantic dependes on dataclasses and dataclasses is a
        # hidden import. 
        # HELP: However, if we put dataclasses in the hiddenimports,
        # pyinstaller raise an error that "distribution dataclasses is not found"
        print("import dataclasses", file=fh)

    return Analysis(
        [script_path] + kwargs.get('scripts', []),
        **kwargs
    )


block_cipher = None
a = Entrypoint('feeluown', 'console_scripts', 'feeluown',
               datas=[('../source/FeelUOwn/feeluown/themes', 'feeluown/themes'),
                      ('../source/FeelUOwn/feeluown/icons/', 'feeluown/icons/'),
                      ('mpv-1.dll', '.')],
               hiddenimports=['PyQt5', 'fuo_local', 'fuo_netease',
                              'fuo_qqmusic', 'fuo_kuwo', 'fuo_dl'],
               cipher=block_cipher,
               noarchive=False
               )
pyz = PYZ(a.pure, a.zipped_data,
          cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          [],
          name='feeluown',
          exclude_binaries=True,
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=False,
          runtime_tmpdir=None,
          console=False,
          icon='feeluown.ico')
coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=False,
               name='feeluown')
