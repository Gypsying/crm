/**
 * Created by liulixin on 2017/12/29.
 */
$(function () {
    menu_swith();
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