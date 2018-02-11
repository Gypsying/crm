/**
 * Created by liulixin on 2017/12/29.
 */
$(function () {
   menu_switch_layui();
});
function menu_swith() {
    $(".menu_title").click(function () {
        if($(this).children().hasClass("active")) {
            $(this).next().removeClass("active");
            $(this).children().removeClass("active");
        }else {
            $(this).children().addClass("active");
            $(this).next().addClass("active");
        }
    })
}

function menu_switch_layui() {
    $('.permission_title').each(function () {
        if($(this).hasClass('layui-this')){
            $(this).parent().parent().addClass('layui-nav-itemed');
        }
    });
}


