$(document).ready(function(){
    /**************************************************************/ 
    /*nav-bar hover效果*/
    /**************************************************************/
    var nav_onMouseIn = function(){
        $(this).addClass("hover");
        $(this).children().css("color","#ffffff");
    };

    var nav_onMouseOut = function(){
        $(this).removeClass("hover");
        $(this).children().css("color","#000000");
    };

    $("li.nav-bar-item").hover(nav_onMouseIn, nav_onMouseOut);


    /**************************************************************/
    /*login页面滑动效果*/
    /**************************************************************/

    var login_circle_onMouseIn = function(e){      
        $(this).stop(true, true);

        var mousePosX = e.pageX;
        var mousePosY = e.pageY;
        var circlePosX = 643;
        var circlePosY = -7;

        var timeAway = 100, timeBack = 650;
        var distance = 15;

        //确定鼠标位置
        if(mousePosX < 960)
            $(this).animate({left: circlePosX+distance+"px"}, timeAway)
               .animate({left: circlePosX+"px", top: circlePosY+"px"}, timeBack);
        else if(mousePosX > 1180)
            $(this).animate({left: circlePosX-distance+"px"}, timeAway)
               .animate({left: circlePosX+"px", top: circlePosY+"px"}, timeBack);
        else if(mousePosY < 430)
            $(this).animate({top: circlePosY+distance+"px"}, timeAway)
               .animate({top: circlePosY+"px", left: circlePosX+"px"}, timeBack);
        else if(mousePosY > 650)
            $(this).animate({top: circlePosY-distance+"px"}, timeAway)
               .animate({top: circlePosY+"px", left: circlePosX+"px"}, timeBack);
    };

    var login_circle_onMouseOut = function(){
        
    }

    $("#login-inside-circle").hover(login_circle_onMouseIn, login_circle_onMouseOut);


    /**************************************************************/
    /*登陆input提示*/
    /**************************************************************/
    $(".login-userinfo > #email").attr({"placeholder": "输入用户名/邮箱"});
    $(".login-userinfo > #password").attr({"placeholder": "密码"});







});