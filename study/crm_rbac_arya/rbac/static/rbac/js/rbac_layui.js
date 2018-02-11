/**
 * Created by liulixin on 2017/12/29.
 */

$('.permission_title').each(function () {
    if($(this).hasClass('layui-this')){
        $(this).parent().parent().addClass('layui-nav-itemed');
    }
});


