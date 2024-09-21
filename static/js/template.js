$(function () {
	//header 	



	$.fn.scrollStopped = function (callback) {
		var that = this,
			$this = $(that);
		$this.scroll(function (ev) {
			clearTimeout($this.data('scrollTimeout'));
			$this.data('scrollTimeout', setTimeout(callback.bind(that), 250, ev));
		});
	};

	$(window).scrollStopped(function (ev) {
		stickyHeader()
	})

	function stickyHeader() {
		// 스크롤시 하이딩 액션	
		var stickyY = $(window).scrollTop();
		$('header').css({
			'top': stickyY + 'px',
			'position': 'absolute'
		});

	}



	var $WIN = $(window); // window jQuery object
	var $DOC = $(document); // document jQuery object
	var $HEADER;

	var HEIGHT = $WIN.height(); // window height
	var WIDTH = $WIN.width(); // window width


	$WIN.resize(function () {
		HEIGHT = $WIN.height();
		WIDTH = $WIN.width();
		$DOC.trigger('scroll');
	});
	// window resize



	$(window).scroll(function () {
		var windowTop = $(window).scrollTop();
		var headerHeight = $('#header').height()
		$('header').css({
			'position': 'fixed',
			'top': 0
		})
		if ($(this).scrollTop() > $('#header').height()) {
			$('#header').addClass('fix');
		} else {
			$('#header').removeClass('fix');
		} //header fix

	})
	// 스크롤 멈춤 감지 




	//사이드툴팁
	// window resize
	//$(window).resize(function () {
	$(window).resize(function () {
		var myWinWidth = $(window).width()
		if (myWinWidth < 901) { // 900이하

			$('#wrap').removeClass('open');
			$('body').removeClass('hid');
			$('.alarm .btn_pop_open').removeClass('on');
			//페이지팝업
			var PopHidden = $('body');
			var PopCont = $('.popup');
			$('.btn_pop_open').click(function () {
				PopHidden.css('height', $(window).height());
				//console.log('@1');
				var activePop = $(this).attr("href");
				$(activePop).fadeIn(300);
				$('body').addClass("hid");
				$('body').bind('touchmove', function (e) { e.preventDefault() });
				return false;
			});

			$('.pop .btn_close').click(function () {
				$(PopCont).fadeOut(300);
				PopHidden.css('height', '100%');
				$('body').removeClass('hid');
				$('body').unbind('touchmove');
				return false;
			});


		} else if (myWinWidth > 900) {
			$('body').removeClass('hid');
			$('.alarm .btn_pop_open').click(function () {
				$('body').removeClass('hid');
				$(this).toggleClass('on');
				$(this).siblings('.tip01').toggleClass('active');
			});
			$('.btn_close').click(function () {
				$(this).parent().parent().removeClass('active');
				return false;
			});
		}

	}).resize()
	$(window).trigger('resize');
	// 메뉴
	$('.side_menu li a').on('mouseenter', function () {
		$(this).addClass('tooltip');
	});
	$('.side_menu li a').on('mouseleave', function () {
		$(this).removeClass('tooltip');
	});

	$('.all_menu').click(function () {
		$('#wrap').toggleClass('open');

		var $target = $(this).parent().parent('#wrap')
		if ($target.hasClass('open')) {
			$('.side_menu li a').on('mouseenter', function () {
				$(this).removeClass('tooltip');
			});
		} else {
			$('.side_menu li a').on('mouseenter', function () {
				$(this).addClass('tooltip');
			});
		}

	});

	
	
	



	
	//셀렉트		
	$(".select dt a, .select_box dt a").click(function () {
		if ($(this).hasClass('on')) {
			$(this).removeClass('on');
			$(this).parent().siblings("dd").removeClass('active')

		} else {
			$(".select dt a").removeClass('on');
			$(this).toggleClass('on');
			$('.select dd').removeClass('active');
			$(this).parent().siblings("dd").toggleClass('active')
		}
	});



	//2021. 08. 17 작품 셀렉트 스크립트 추가
	$(function () {
		var myWinWidth = $(window).width();
		$(document).ready(function () {
			if (myWinWidth <= 900) {
				$('.select').addClass('m_select');
				$('.filter').addClass('m_filter');
				$('.filter_cont').addClass('m_filter_cont').slideUp();

				$(".m_select dt a").click(function () {
					if ($(this).hasClass('on')) {
						$('.m_filter').removeClass('on');
						$('.m_filter_cont').slideUp();
					} else {
					}
				});
				$('.filter').click(function () {
					if ($(this).hasClass('on')) {
						$('.m_select dl dt a').removeClass('on');
						$('.m_select dl dd').removeClass('active');
					}
				});

			}//if end
			else if (myWinWidth > 900) {
				$('.select').removeClass('m_select');
				$('.filter').removeClass('m_filter');
				$('.filter_cont').removeClass('m_filter_cont').slideUp();
			}
		});



	});

}) //ready
