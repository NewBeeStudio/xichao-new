/**************************************************************/ 
    /*两边突出取得灰色背景效果*/
    /**************************************************************/
$(window).resize(function(){
    var bodyWidth = $(document.body).width();
    var marginLeft = (bodyWidth - 1160)/2;
    $(".long-background").css("margin-left", "-"+marginLeft.toString()+"px");
    $(".long-background").css("width", (bodyWidth> $("#content").width()?bodyWidth:$("#content").width()).toString()+"px");
});

function special_square_circle_onMouseIn(e){      
    var mousePosX = e.pageX;
    var mousePosY = e.pageY;

    var circleDiameter = parseInt($(this).css("height").slice(0, -2)); //圆的直径
    var circleLeftBorder = parseInt($(this).offset().left);
    var circleTopBorder = parseInt($(this).offset().top); //圆的位置

    var timeAway = 100, timeBack = 650; //拨过去和回来的时间(ms)
    var distance = 10; //拨的幅度(px)

    $(this).stop(true, true);
    //确定鼠标位置，完成jQuery动画
    if(mousePosX < circleLeftBorder + 0.25*circleDiameter)
        $(this).animate({marginLeft: distance+"px"}, timeAway)
           .animate({marginLeft: "0px"}, timeBack);
    else if(mousePosX > circleLeftBorder + 0.75*circleDiameter)
        $(this).animate({marginLeft: "-" + distance+"px"}, timeAway)
           .animate({marginLeft: "0px"}, timeBack);
    else if(mousePosY < circleTopBorder + 0.25*circleDiameter)
        $(this).animate({marginTop: distance+"px"}, timeAway)
           .animate({marginTop: "0px"}, timeBack);
    else if(mousePosY > circleTopBorder + 0.75*circleDiameter)
        $(this).animate({marginTop: "-"+distance+"px"}, timeAway)
           .animate({marginTop: "0px"}, timeBack);
}

function login_circle_onMouseOut(){
        
}

$(document).ready(function(){
    //如果在子页面没有重新定义标题，则采用默认标题
    if($("title").length == 0) {
        $("head").append("<title>曦潮书店 | 书香生态系统</title>");
    }
    
/**************************************************************/ 
    /*两边突出取得灰色背景效果*/
    /**************************************************************/
        var bodyWidth = $(document.body).width();
    var marginLeft = (bodyWidth - 1160)/2;
    $(".long-background").css("margin-left", "-"+marginLeft.toString()+"px");
    $(".long-background").css("width", (bodyWidth> $("#content").width()?bodyWidth:$("#content").width()).toString()+"px");
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

        var circleDiameter = parseInt($(this).css("height").slice(0, -2)); //圆的直径
        var circleLeftBorder = parseInt($(this).offset().left);
        var circleTopBorder = parseInt($(this).offset().top); //圆的位置

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
   

    $("#login-inside-circle").hover(login_circle_onMouseIn, login_circle_onMouseOut);
    $(".square-part1-img2").hover(special_square_circle_onMouseIn, login_circle_onMouseOut); //只能margin-left?
    
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
