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
            hideCards()
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

    // show nav card on mouseover for main menu entry
    $('.primary-nav a').mouseenter(function(e) {
        showCard(e.target.id)
    })

    // hide all nav cards when we leave the nav
    $('.nav-wrap').mouseleave(function() {
        hideCards()
    })

    function showCard(id) {
        hideCards() // hide others
        $('.nav-card.menu-' + id).show()
        $('#' + id).attr('aria-expanded', true)
    }

    function hideCards() {
        $('.primary-nav a').attr('aria-expanded', false)
        $('.nav-card').hide()   
    }

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
