# -*- coding: utf-8 -*-

from core.utils.thrift import ThriftHandler,Result



class UEditorHandler(ThriftHandler):
    def list_image(self,request):
        page = request.data['page']

        images = [{ 'url': 'https://www.baidu.com/img/bdlogo.png' }]
        total = 1

        return Result(data={ 'images': images, 'total': total })

    def list_file(self,request):
        page = request.data['page']

        files = [{ 'url': 'https://www.baidu.com/img/bdlogo.png', 'original': '百度Logo' }]
        total = 1

        return Result(data={ 'files': files, 'total': total })



