/**
 * Created by liulixin on 2018/1/27.
 */

var $title = $('.layui-nav-itemed > a').text();
$('.breadcrumb_menu_title').text($title);

var $sub_title = $('.layui-this').text();
$('.breadcrumb_menu_item > cite').text($sub_title);
var $sub_title_url = $('.layui-this > a').attr('href');
$('.breadcrumb_menu_item').attr('href',$sub_title_url);


