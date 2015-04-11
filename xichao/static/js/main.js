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

        console.log("hello");
        var mousePosX = e.pageX;
        var mousePosY = e.pageY;

        var circlePosX = 616;
        var circlePosY = -7; //获取对象位置，绝对坐标，防止圆离开最初位置

        var circleDiameter = parseInt($("#login-inside-circle").css("height").slice(0, -2)); //圆的直径
        var circleLeftBorder = parseInt($("#login-inside-circle").offset().left);
        var circleTopBorder = parseInt($("#login-inside-circle").offset().top); //圆的位置

        console.log(circleDiameter);
        console.log(circleTopBorder);
        console.log(circleLeftBorder);
        var timeAway = 100, timeBack = 650; //拨过去和回来的时间(ms)
        var distance = 15; //拨的幅度(px)

        $(this).stop(true, true);

        //确定鼠标位置，完成jQuery动画
        if(mousePosX < circleLeftBorder + 0.25*circleDiameter)
            $(this).animate({marginRight: "-"+distance+"px"}, timeAway)
               .animate({marginRight: "0px"}, timeBack);
        else if(mousePosX > circleLeftBorder + 0.75*circleDiameter)
            $(this).animate({marginRight: distance+"px"}, timeAway)
               .animate({marginRight: "0px"}, timeBack);
        else if(mousePosY < circleTopBorder + 0.25*circleDiameter)
            $(this).animate({marginTop: distance+"px"}, timeAway)
               .animate({marginTop: "0px"}, timeBack);
        else if(mousePosY > circleTopBorder + 0.75*circleDiameter)
            $(this).animate({marginTop: "-"+distance+"px"}, timeAway)
               .animate({marginTop: "0px"}, timeBack);

    };

    var login_circle_onMouseOut = function(){
        
    }

    $("#login-inside-circle").hover(login_circle_onMouseIn, login_circle_onMouseOut);


    /**************************************************************/
    /*登陆label/input提示*/
    /**************************************************************/
    $("#login-userinfo #email").attr({"placeholder": "输入邮箱"});
    $("#login-userinfo #password").attr({"placeholder": "输入密码"});
    $("#login-userinfo #confirm").attr({"placeholder": "确认密码"});

    //$(".login-userinfo #email").prev().children().first().text("注册邮箱");
    //$(".login-userinfo #password").prev().children().first().text("密码");
    //$(".login-userinfo #confirm").prev().children().first().text("确认密码");
});
