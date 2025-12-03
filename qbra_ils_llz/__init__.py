def classFactory(iface):
    from .qbra_plugin import QbraIlsLlzPlugin
    return QbraIlsLlzPlugin(iface)
