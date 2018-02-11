
class Paginator(object):
    def __init__(self, all_count, current_page, base_url, per_page=10, per_page_count=11, query_params=None):
        """
        分页组件的初始化
        :param all_count: 数据的总条数
        :param current_page: 当前页码
        :param base_url: 基础url
        :param per_page: 每页显示的条目数
        :param per_page_count: 显示的页码数
        """
        self.base_url = base_url
        self.all_count = all_count
        self.per_page = per_page
        self.per_page_count = per_page_count
        self.query_params = query_params
        # request.GET 不是字典类型而是django自带的QueryDict类型（类似字典类型）
        # QueryDict具有一个 urlencode方法，可以把QueryDict数据转换成 字符串形式
        # QueryDict.urlencode() # /arya/app01/userinfo/?q=xxx&page=9
        """
            {
                keyword:'xxx', 
                page:2
            }
            query_params[page] = 9
            {
                keyword:'xxx',
                page:9
            }
        """
        # 规避类型异常：unsupported operand type(s) for -: 'str' and 'int'
        try:
            self.current_page = int(current_page)
            if self.current_page <= 0:
                raise Exception()
        except Exception as e:
            self.current_page = 1

        # 计算得出真实的页码数
        pager_count, remainder = divmod(self.all_count, self.per_page)
        if 0 != remainder:
            pager_count += 1
        self.pager_count = pager_count
        # 默认每次显示11个页码（除上一页、下一页、首页和尾页之外）并且让当前选择页码始终居中
        self.half_per_page_count = int(self.per_page_count / 2)

    @property
    def start(self):
        """
        数据条目的起始索引
        # x  -> items_per_page*(x-1) ~ items_per_page*x
        :return:
        """
        return self.per_page * (self.current_page - 1)

    @property
    def end(self):
        """
        数据条目的结束索引
        # x  -> items_per_page*(x-1) ~ items_per_page*x
        :return:
        """
        return self.per_page * self.current_page

    @property
    def page_html(self):
        # 获取正确的开始页码和结束页码
        # 判断真实的页码数是否超过 per_page_count
        if self.pager_count > self.per_page_count:
            # 如果当前页 < half_per_page_count
            if self.current_page <= self.half_per_page_count:
                pager_start = 1
                pager_end = self.per_page_count
            # 如果当前页码 大于 half_per_page_count 并且 小于 pager_count - half_per_page_count
            elif self.current_page <= self.pager_count - self.half_per_page_count:
                pager_start = self.current_page - self.half_per_page_count
                pager_end = self.current_page + self.half_per_page_count
            # 如果当前页码大于 pager_count - half_per_page_count
            else:
                pager_start = self.pager_count - self.per_page_count + 1
                pager_end = self.pager_count
        else:
            pager_start = 1
            pager_end = self.pager_count

        page_list = []
        self.query_params['page'] = 1
        first_page = '<li><a href="{0}?{1}">首页</a></li>'.format(self.base_url,self.query_params.urlencode())
        page_list.append(first_page)
        if self.current_page > 1:
            # 注意：query_params 包含了page和keyword
            # 这里更改了page对应的值，前一页，所以要把页码减一
            self.query_params['page'] = self.current_page - 1
            prev = '<li><a href="{0}?{1}">上一页</a></li>'.format(self.base_url, self.query_params.urlencode())
        else:
            prev = '<li><a href="javascript:void(0)" disabled="true">上一页</a></li>'
        page_list.append(prev)

        # 循环生成HTML
        for i in range(pager_start, pager_end + 1):
            # 生成对应page的url
            self.query_params['page'] = i
            if i == self.current_page:
                tpl = '<li><a class="active" href="{0}?{1}">{2}</a></li>'.format(self.base_url, self.query_params.urlencode(), i)
            else:
                tpl = '<li><a href="{0}?{1}">{2}</a></li>'.format(self.base_url, self.query_params.urlencode(), i)
            page_list.append(tpl)

        if self.current_page < self.pager_count:
            self.query_params['page'] = self.current_page + 1
            nex = '<li><a href="{0}?{1}">下一页</a></li>'.format(self.base_url, self.query_params.urlencode())
        else:
            nex = '<li><a href="javascript:void(0)" disabled="true">下一页</a></li>'
        page_list.append(nex)
        self.query_params['page'] = self.pager_count
        last_page = '<li><a href="{0}?{1}">尾页</a></li>'.format(self.base_url, self.query_params.urlencode())
        page_list.append(last_page)
        page_str = "".join(page_list)
        return page_str