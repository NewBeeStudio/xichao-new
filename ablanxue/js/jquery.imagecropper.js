/**
* Copyright (c) 2010 Viewercq (http://www.cnblogs.com/viewercq/archive/2010/04/04/1704093.html)
* Dual licensed under the MIT (http://www.opensource.org/licenses/mit-license.php)
* and GPL (http://www.opensource.org/licenses/gpl-license.php) licenses.
*
* Version: 1.0
*
* Demo: https://dl.dropbox.com/u/4390741/ImageCropper.htm
*/
; (function($) {
    $.fn.extend({
        imageCropper: function(options) {
            if (!this.is('img') || typeof this.attr('src') == 'undefined' || this.attr('src') == '') {
                throw 'Please notice that this jquery plguin only could be applied to img and the src of img could not be null!';
            }
            var defaults = {
                //原图路径
                imagePath: this.attr('src'),
                //缩放级别
                zoomLevel: 1,
                //图片相对于截取框是否居中
                center: false,
                //截取框与图片的相对位置
                left: 0, top: 0,
                //截取框的大小
                width: 200, height: 200,
                //工作区大小
                cropWorkAreaSize: { width: 600, height: 400 },
                //截取框相对于工作区的位置
                cropFrameRect: { center: true, top: 0, left: 0 },
                //缩放范围
                zoom: { min: 0, max: 2, step: 0.01 },
                //回调函数
                callbacks: {
                    //移动图片后
                    dragging: false,
                    //缩放后
                    zoomed: false
                }
            };
            if (options) {
                defaults = $.extend(defaults, options);
            }
            return new imageCropper(this, defaults);
        }
    });

    function imageCropper(image, settings) {
        this.init(image, settings);
    };

    imageCropper.prototype = {
        settings: false,
        wrapper: $('<div class="image-cropper-wrapper"/>'),
        zoomWrapper: $('<div class="zoom-wrapper"><div class="zoom-out-button"/><div class="zoom-scrollbar"><div class="zoom-scroller"/></div><div class="zoom-in-button"/></div>'),
        img: false,
        init: function(image, settings) {
            var context = this;
            this.settings = settings;
            image.addClass('background-img');
            //生成html
            image.wrap(this.wrapper).wrap('<div class="crop-work-area"/>').wrap('<div class="crop-background"/>');
            this.wrapper = $('.image-cropper-wrapper');
            $('.crop-work-area', this.wrapper).append('<div class="crop-frame"><img class="foreground-img" src="" /></div><div class="drag-containment"/>');
            this.wrapper.append(this.zoomWrapper);

            $('.image-cropper-wrapper', this.wrapper).disableSelection();
            this.reset();

            //图片的拖动
            $('.crop-background', this.wrapper).draggable({
                containment: $('.drag-containment', this.wrapper),
                cursor: 'move',
                drag: function(event, ui) {
                    var self = $(this).data('draggable');
                    //同时移动前景图
                    $('.foreground-img', this.wrapper).css({
                        left: (parseInt(self.position.left) - context.settings.cropFrameRect.left - 1) + 'px',
                        top: (parseInt(self.position.top) - context.settings.cropFrameRect.top - 1) + 'px'
                    });
                    //得到截图左上点坐标
                    context.settings.left = context.settings.cropFrameRect.left - parseInt($(this).css('left'));
                    context.settings.top = context.settings.cropFrameRect.top - parseInt($(this).css('top'));
                    //移动图片的callback
                    context.fireCallback(context.settings.callbacks.dragging);
                }
            });
            $('.foreground-img', this.wrapper).draggable({
                containment: $('.drag-containment', this.wrapper),
                cursor: 'move',
                drag: function(event, ui) {
                    var self = $(this).data('draggable');
                    //同时移动背景
                    $('.crop-background', this.wrapper).css({
                        left: (parseInt(self.position.left) + context.settings.cropFrameRect.left + 1) + 'px',
                        top: (parseInt(self.position.top) + context.settings.cropFrameRect.top + 1) + 'px'
                    });
                    //得到截图左上点坐标
                    context.settings.left = context.settings.cropFrameRect.left - parseInt($('.crop-background', this.wrapper).css('left'));
                    context.settings.top = context.settings.cropFrameRect.top - parseInt($('.crop-background', this.wrapper).css('top'));
                    //移动图片的callback
                    context.fireCallback(context.settings.callbacks.dragging);
                }
            });
            //点击缩放
            $('.zoom-out-button,.zoom-in-button', this.wrapper).click(function() {
                var step = $(this).hasClass('zoom-in-button') ? context.settings.zoom.step : -context.settings.zoom.step;
                var tempZoomLevel = context.formatNumber(context.settings.zoomLevel + step, 3);
                //如果缩放级别超出范围 或者 缩放导致图片右下角没在截取框内 则取消缩放
                if (context.settings.zoomLevel >= context.settings.zoom.min
                    && context.settings.zoomLevel <= context.settings.zoom.max
                    && parseInt($('.crop-background', this.wrapper).css('left')) + tempZoomLevel * context.img.width > context.settings.cropFrameRect.left + context.settings.width
                    && parseInt($('.crop-background', this.wrapper).css('top')) + tempZoomLevel * context.img.height > context.settings.cropFrameRect.top + context.settings.height
                ) {
                    context.settings.zoomLevel = tempZoomLevel;
                    context.zoom(context.img.width * context.settings.zoomLevel, context.img.height * context.settings.zoomLevel);
                    $('.zoom-scroller', this.wrapper).css('left', context.settings.zoomLevel * 200 / (context.settings.zoom.max - context.settings.zoom.min) + 'px');
                }
                context.fireCallback(context.settings.callbacks.zoomed);
            });
            //滚动条缩放
            var cancelZoomScroll = false;
            $('.zoom-scroller', this.wrapper).draggable({
                containment: $('.zoom-scrollbar', this.wrapper),
                axis: 'x',
                drag: function(event, ui) {
                    var tempZoomLevel = (context.settings.zoom.max - context.settings.zoom.min) * parseInt($(this).css('left')) / 200;
                    //如果缩放级别超出范围 或者 缩放导致图片右下角没在截取框内 则取消缩放
                    if (parseInt($('.crop-background', this.wrapper).css('left')) + tempZoomLevel * context.img.width > context.settings.cropFrameRect.left + context.settings.width
                        && parseInt($('.crop-background', this.wrapper).css('top')) + tempZoomLevel * context.img.height > context.settings.cropFrameRect.top + context.settings.height
                    ) {
                        context.settings.zoomLevel = tempZoomLevel;
                        context.zoom(context.img.width * context.settings.zoomLevel, context.img.height * context.settings.zoomLevel);
                        cancelZoomScroll = false;
                        context.fireCallback(context.settings.callbacks.zoomed);
                    }
                    else {
                        cancelZoomScroll = true;
                    }
                },
                stop: function(event, ui) {
                    //如果缩放级别无效 则重置滚动条的值
                    if (cancelZoomScroll) {
                        $('.zoom-scroller', this.wrapper).css('left', context.settings.zoomLevel * 200 / (context.settings.zoom.max - context.settings.zoom.min) + 'px');
                    }
                }
            });
        },
        reset: function() {
            this.img = new Image();
            this.img.src = this.settings.imagePath;
            //截取框大于工作区，则放大工作区
            var tempSize = {
                width: Math.max(this.settings.cropWorkAreaSize.width, this.settings.width),
                height: Math.max(this.settings.cropWorkAreaSize.height, this.settings.height)
            };
            //如果截取框在工作区中居中，则重新设置截取框的位置
            if (this.settings.cropFrameRect.center) {
                this.settings.cropFrameRect.left = (tempSize.width - this.settings.width) / 2;
                this.settings.cropFrameRect.top = (tempSize.height - this.settings.height) / 2;
            }
            //如果截取框在图片中居中，则重新设置图片与截取框的相对位置
            if (this.settings.center) {
                this.settings.left = (this.img.width * this.settings.zoomLevel - this.settings.width) / 2;
                this.settings.top = (this.img.height * this.settings.zoomLevel - this.settings.height) / 2;
            }

            this.wrapper.width(tempSize.width + 2).height(tempSize.height + 25);
            $('.foreground-img,.background-img', this.wrapper).attr('src', this.settings.imagePath);
            $('.crop-work-area', this.wrapper).width(tempSize.width).height(tempSize.height);
            $('.crop-frame', this.wrapper).css({
                left: this.settings.cropFrameRect.left + 'px',
                top: this.settings.cropFrameRect.top + 'px',
                width: this.settings.width + 'px',
                height: this.settings.height + 'px'
            });
            $('.foreground-img', this.wrapper).css({
                left: (-this.settings.cropFrameRect.left - 1) + 'px',
                top: (-this.settings.cropFrameRect.top - 1) + 'px'
            });
            $('.zoom-scroller', this.wrapper).css('left', this.settings.zoomLevel * 200 / (this.settings.zoom.max - this.settings.zoom.min) + 'px');


            $('.crop-background', this.wrapper).css({
                opacity: 0.3,
                left: this.settings.cropFrameRect.left - this.settings.left + 'px',
                top: this.settings.cropFrameRect.top - this.settings.top + 'px'
            });
            $('.foreground-img', this.wrapper).css({
                left: -this.settings.left + 'px',
                top: -this.settings.top + 'px'
            });

            this.settings.left = this.settings.cropFrameRect.left - parseInt($('.crop-background', this.wrapper).css('left'));
            this.settings.top = this.settings.cropFrameRect.top - parseInt($('.crop-background', this.wrapper).css('top'));

            this.zoom(this.img.width * this.settings.zoomLevel, this.img.height * this.settings.zoomLevel);
        },
        zoom: function(width, height) {
            $('.crop-background, .background-img, .foreground-img', this.wrapper).width(width).height(height);
            //调整拖动限制框
            $('.drag-containment', this.wrapper).css({
                left: this.settings.cropFrameRect.left + this.settings.width - this.settings.zoomLevel * this.img.width + 1 + 'px',
                top: this.settings.cropFrameRect.top + this.settings.height - this.settings.zoomLevel * this.img.height + 1 + 'px',
                width: 2 * this.settings.zoomLevel * this.img.width - this.settings.width + 'px',
                height: 2 * this.settings.zoomLevel * this.img.height - this.settings.height + 'px'
            });
        },
        formatNumber: function(number, bit) {
            return Math.round(number * Math.pow(10, bit)) / Math.pow(10, bit);
        },
        fireCallback: function(fn) {
            if ($.isFunction(fn)) {
                fn.call(this);
            };
        }
    };
})(jQuery);
