from django.conf import settings
import logging

log = logging.getLogger('community.sources')

try:
    import xml.etree.cElementTree as element_tree
except ImportError:
    try:
        import elementtree.ElementTree as element_tree
    except ImportError:
        try:
            import cElementTree as element_tree
        except ImportError:
            raise ImportError("No ElementTree found")
log.debug("Using specified etree module: %s" % element_tree)

def import_source_modules(source_list=settings.AGRO_SETTINGS['source_list'], class_name=''):
    sources = []
    for source in source_list:
        log.debug('trying to load %s' % source)
        try:
            sources.append(__import__("gazjango.community.sources.%s" % source, 
                                      fromlist=['%s%s' % (source, class_name)]))
        except ImportError, e:
            log.error('unable to load %s: %s', source, e)
    return sources
