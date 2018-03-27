$(document).ready(function(){
    var $ribbon = $('.ribbon');
    if ($ribbon) {
        var faded = sessionStorage.getItem('fade-test-banner', true);
        if (! faded) {
            $('.ribbon-box').removeClass('fade');
        }
        $ribbon.on('click',function(){
            $('.ribbon-box').addClass('fade');
            sessionStorage.setItem('fade-test-banner', true);
        });
    }

    var scroll = 0;
    /*
      Check every time the window scrolls. If it's by 25px or more and
      the scroll is below 90px, hide the navi. If the scroll down isn't
      those, leave it as is.
      If the scroll is up by 5 px, bring the menu back.
    */
    $(window).scroll(function()
    {
        scrolled = $(document).scrollTop();
        if (scrolled - scroll > 25 && scrolled > scroll && scrolled >
            90)
        {
            $('header').addClass('hidden');
        }
        else if (scrolled > scroll)
        {
            // Do nothing since the scroll was either
            // too high or not 'enough'
        }
        else if (scrolled < scroll && scroll - scrolled > 5)
        {
            $('header').removeClass('hidden');
        }

        scroll = scrolled;

    });


    $('.menu-toggle').on('click', function(e){
        e.preventDefault();
        // toggle footer to act as main mobile nav
        $('footer').toggleClass('mobile-nav');
        $('body').toggleClass('fixed');
    });
    $('a.toggle').on('click', function(e){
        $(this).parent().toggleClass('open');
        $(this).parent().find('.submenu').toggle();
    });


    // show submenu on mouseover for main menu entry
    $('.primary-nav > li').not('.current-page').mouseover(function() {
        // hide all secondary nav, show this one
        $(this).parent().find('li .secondary-nav').hide();
        $(this).find('.secondary-nav').show();
    });
    // restore current page menu when mouse leaves primary nav
    $('.primary-nav').mouseout(function() {
        // hide all secondary nav, show the current one
        $(this).find('.secondary-nav').hide();
        $(this).find('.secondary-nav.active').show();
    })

    /*
     * Homepage carousel
     */

    var changeSlide = function(toIndex) {
        // show the slide
        $('#carousel .post-update.active').removeClass('active')
        $('#carousel .post-update').eq(toIndex).addClass('active')
        // highlight the button
        $('#post-controls a div.active').removeClass('active')
        $('#post-controls a div').eq(toIndex).addClass('active')
    }

    $('#post-controls a').each(function(i, button) {
        $(button).click(function() {
            changeSlide(i)
            // restart the autoplay "timer" from zero
            clearInterval(playerID)
            playerID = startAutoplay()
        })
    })

    // TODO maybe make mouseenter/mouseleave clear/reset autoplay - 
    // thus hovering would "freeze" the slideshow

    // autoplay function
    var startAutoplay = function() {
        return setInterval(function(){
            var activeIndex = $('#post-controls a div.active').data('index')
            var newIndex = (activeIndex + 1) % $('#post-controls a').length
            changeSlide(newIndex)
        }, 5000) // autoplay slide time is 5s
    }

    // start autoplay if there's more than one slide
    if ($('#carousel .post-update').length > 1) {
        var playerID = startAutoplay()
    }

});
