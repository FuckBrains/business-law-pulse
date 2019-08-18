# -*- coding: utf-8 -*-


class BasicException(Exception):
    def __init__(self, err=0, msg='', log=''):
        self.err = err
        self.msg = msg
        self.log = log

    def __str__(self):
        return '%s(err=%s, msg=\'%s\', log=\'%s\')' % (self.__class__.__name__,self.err,self.msg,self.log)

    def __repr__(self):
        return self.__str__()


class BizException(BasicException):
    def __init__(self, msg, err=1, log=''):
        super(BizException,self).__init__(err,msg,log)


class ThriftException(BasicException):
    def __init__(self, result=None, err=-1, msg='', log=''):
        if result:
            err = result.err
            msg = result.msg
            log = result.log

        super(ThriftException,self).__init__(err,msg,log)


class RestException(BasicException):
    def __init__(self, result):
        err = result['err']
        msg = result['msg']
        log = result['log']
        super(RestException,self).__init__(err,msg,log)


class HttpException(BasicException):
    def __init__(self, status, content):
        err = -1
        msg = 'HTTP Status : %s' % status
        log = content
        super(RestException,self).__init__(err,msg,log)



