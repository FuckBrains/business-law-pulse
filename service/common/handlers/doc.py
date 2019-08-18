# -*- coding: utf-8 -*-

from core.utils.exceptions import BizException
from core.utils.thrift import ThriftHandler,Result

from bson import ObjectId

from service.common.models import DocModule


class DocHandler(ThriftHandler):
    def list_modules(self,request):
        modules = DocModule.objects.exclude('items').all()
        _modules = [module.digest() for module in modules]
        return Result(data=dict(modules=_modules))

    def create_module(self,request):
        code = request.data['code'].strip()
        name = request.data['name'].strip()
        remark = request.data['remark'].strip()

        if DocModule.objects.filter(code=code):
            raise BizException('模块代码已被占用')

        if DocModule.objects.filter(name=name):
            raise BizException('模块名称已被占用')

        module = DocModule(code=code,name=name,remark=remark)
        module.switch_db('primary').save()

        _module = module.digest()
        return Result(msg='创建成功',data=dict(module=_module))

    def update_module(self,request):
        module_id = request.data['module']
        module = DocModule.objects.exclude('items').filter(id=module_id).first()
        if not module:
            raise BizException('模块记录不存在')

        code = request.data['code'].strip()
        name = request.data['name'].strip()
        remark = request.data['remark'].strip()

        if DocModule.objects.filter(id__ne=ObjectId(module_id),code=code).count():
            raise BizException('模块代码已被占用')

        if DocModule.objects.filter(id__ne=ObjectId(module_id),name=name).count():
            raise BizException('模块名称已被占用')

        module.code = code
        module.name = name
        module.remark = remark
        module.switch_db('primary').save()
        return Result(msg='更新成功')

    def get_module(self,request):
        module_id = request.data['module']
        module = DocModule.objects.exclude('items').filter(id=module_id).first()
        if not module:
            raise BizException('模块记录不存在')

        _module = module.digest()
        return Result(data=dict(module=_module))

    def list_items(self,request):
        module_id = request.data['module']
        module = DocModule.objects.filter(id=module_id).first()
        if not module:
            raise BizException('模块记录不存在')

        items = module.items.exclude(input=1,output=1)
        _items = [item.detail() for item in items]
        return Result(data=dict(items=_items))

    def create_item(self,request):
        module_id = request.data['module']
        module = DocModule.objects.filter(id=module_id).first()
        if not module:
            raise BizException('模块记录不存在')

        url = request.data['url'].strip()
        type = int(request.data['type'])
        remark = request.data['remark'].strip()
        input = request.data['input'].strip()
        output = request.data['output'].strip()

        item = module.items.create(id=str(ObjectId()),url=url,type=type,remark=remark,input=input,output=output)
        module.switch_db('primary').save()

        _item = item.detail()
        return Result(msg='创建成功',data=dict(item=_item))

    def update_item(self,request):
        module_id = request.data['module']
        module = DocModule.objects.filter(id=module_id).first()
        if not module:
            raise BizException('模块记录不存在')

        item_id = request.data['item']
        url = request.data['url'].strip()
        type = int(request.data['type'])
        remark = request.data['remark'].strip()
        input = request.data['input'].strip()
        output = request.data['output'].strip()

        module.items.filter(id=item_id).update(url=url,type=type,remark=remark,input=input,output=output)
        module.switch_db('primary').save()
        return Result(msg='更新成功')

    def remove_item(self,request):
        module_id = request.data['module']
        module = DocModule.objects.filter(id=module_id).first()
        if not module:
            raise BizException('模块记录不存在')

        item_id = request.data['item']
        module.items.filter(id=item_id).delete()
        module.switch_db('primary').save()
        return Result(msg='删除成功')

    def get_item(self,request):
        module_id = request.data['module']
        module = DocModule.objects.filter(id=module_id).first()
        if not module:
            raise BizException('模块记录不存在')

        item_id = request.data['item']
        item = module.items.filter(id=item_id).first()
        if not item:
            raise BizException('接口记录不存在')

        _item = item.detail()
        return Result(data=dict(item=_item))

    def seq_item(self,request):
        module_id = request.data['module']
        module = DocModule.objects.filter(id=module_id).first()
        if not module:
            raise BizException('模块记录不存在')

        item_id = request.data['item']
        item = module.items.filter(id=item_id).first()
        if not item:
            raise BizException('接口记录不存在')

        index = module.items.index(item)

        # P - 上移(Prev)
        # N - 下移(Next)
        # F - 置顶(First)
        # L - 置底(Last)
        action = request.data['action']

        if action in ('P','F'):
            if index == 0:
                raise BizException('已经排在第一位')

            if action=='P':
                tmp_item = module.items[index-1]
                module.items[index-1] = item
                module.items[index] = tmp_item
            else:
                del module.items[index]
                module.items = [item] + module.items

        elif action in ('N','L'):
            if index == len(module.items)-1:
                raise BizException('已经排在最后一位')

            if action=='N':
                tmp_item = module.items[index+1]
                module.items[index+1] = item
                module.items[index] = tmp_item
            else:
                del module.items[index]
                module.items = module.items + [item]

        module.switch_db('primary').save()
        return Result(msg='移动成功')


