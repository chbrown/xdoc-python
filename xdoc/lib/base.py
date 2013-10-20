class object_ustr(object):
    def __unicode__(self):
        '''This should really be overriden in subclasses'''
        class_name = self.__class__.__name__
        attr_pairs = ('%s=%s' % (key, val) for key, val in self.__dict__.items())
        return u'<%s %s>' % (class_name, ' '.join(attr_pairs))

    def __str__(self):
        '''This won't usually be overridden in subclasses'''
        return unicode(self).encode('utf8')

    def __repr__(self):
        return str(self)
