def classFactory(iface):
    # load qtest class from file qtest
    from layerdefs import LayerDefinitions
    return LayerDefinitions(iface)