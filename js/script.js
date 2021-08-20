$(document).ready( function() {
    //need to record this at the begining of document ready, so that I am sure the Navbar is collapsed.
    var navbar_collapsed_height = $("#theNavbar").height();

    // banner height is in em so need this. .height will give in px.
    var banner_height = $("#banner").height();
    $('.navbar').affix({offset: {top: banner_height} });

    // from big screen to cellphone screen, the banner height is going to change, so need to change affix position.
    window.onresize=function(){
        banner_height = $("#banner").height();
        // alert(banner_height);
        $('.navbar').data('bs.affix').options.offset.top = banner_height
    }
    //this also works:
    // window.addEventListener("resize",function(){
    // banner_height = $("#banner").height();
    // // alert(banner_height);
    // $('.navbar').data('bs.affix').options.offset.top = banner_height
    // });

    // These alerts tell you the margin-right and the padding-right of all the elements around navbar-nav:
    // alerts_navbar_and_parents_paddings_margins();

    // on page first load, check scroll position. This is because maybe user refreshed page at not-top-location. If true, then use animationNavbarMoveRight to correctly place the navbar links.
    if (window.pageYOffset > banner_height) {
        animationNavbarMoveRight();
    };

    // Need these variables, because later need to compare things like handle_tab_shown == handle_tab_bio etc. ()而in js，两次generate jquery object $("#tab-bio") == $("#tab-bio")得到是false。)
    var handle_tab_bio = $("#tab-bio");
    var handle_tab_publications = $("#tab-publications");
    var handle_tab_education = $("#tab-education");
    var handle_tab_services = $("#tab-services");
    var handle_tab_links  = $("#tab-links");

    var handle_tab_shown = handle_tab_bio;
    // handle_tab_bio.hide();
    handle_tab_publications.hide();
    handle_tab_education.hide();
    handle_tab_services.hide();
    handle_tab_links.hide();

    // First time loading page, depending on querry script, show the corresponding tab.
    var url = window.location.href;
    tab_now = url.match(/tab_now=(.*)/);
    if (tab_now != null) {
        tab_now = tab_now[1];
    }
    else {
        // by default, show the Bio page, so make the Bio navbar link highlighted
        $(".navbar-nav li a").removeClass('selected');
        $("#navbar-nav-bio").addClass('selected');
    };
    switchTab(tab_now);

    // backward/forward clicks will fire onpopstate event. When this happens, change tab.
    window.onpopstate = function(e) {
        // alert("location: " + document.location + ", state: " + JSON.stringify(e.state));
        stt = e.state;
        if (stt != null) {
            tab_now = stt.tab_now;
            switchTab(tab_now);
        }
        else {
            tab_now = "bio";
            switchTab(tab_now);
        };
    };

    // switchTab is called when page first load (see above) and in onpopstate event. So write it here to avoid duplicate codes.
    function switchTab(tab_now) {
        // This function is defined inside document ready because it useses variables like handle_tab_bio etc.
        if (tab_now != null) {
            switch (tab_now) {
                // tab_now is an array. Can't use array in switch.
                case 'bio':
                changeTab(handle_tab_bio, handle_tab_shown, navbar_collapsed_height);
                handle_tab_shown = handle_tab_bio;
                $(".navbar-nav li a").removeClass('selected');
                $("#navbar-nav-bio").addClass('selected');
                break;  // Must have this break, otherwise all subsequent commands will be executed!
                case 'publications':
                changeTab(handle_tab_publications, handle_tab_shown, navbar_collapsed_height);
                handle_tab_shown = handle_tab_publications;
                $(".navbar-nav li a").removeClass('selected');
                $("#navbar-nav-publications").addClass('selected');
                break;
                case 'education':
                changeTab(handle_tab_education, handle_tab_shown, navbar_collapsed_height);
                handle_tab_shown = handle_tab_education;
                $(".navbar-nav li a").removeClass('selected');
                $("#navbar-nav-education").addClass('selected');
                break;
                case 'services':
                changeTab(handle_tab_services, handle_tab_shown, navbar_collapsed_height);
                handle_tab_shown = handle_tab_services;
                $(".navbar-nav li a").removeClass('selected');
                $("#navbar-nav-services").addClass('selected');
                break;
                case 'links':
                changeTab(handle_tab_links, handle_tab_shown, navbar_collapsed_height);
                handle_tab_shown = handle_tab_links;
                $(".navbar-nav li a").removeClass('selected');
                $("#navbar-nav-links").addClass('selected');
            };
        };
    };

    // when click my name in the navbar, smooth scroll to top.
    $(".navbar-brand").click(function(e){
        e.preventDefault();
        $("body, html").animate({ scrollTop: 0 });
        $("#myNavbar").collapse('hide');
    });

    $("#navbar-nav-bio").click(function(e){
        e.preventDefault();
        // $("#navbar-nav-bio").focus();
        $(".navbar-nav li a").removeClass('selected');
        $(this).addClass('selected');
        history.pushState({tab_now: 'bio'}, "title", "?tab_now=bio");
        changeTab(handle_tab_bio, handle_tab_shown, navbar_collapsed_height);
        handle_tab_shown = handle_tab_bio;
        $("#myNavbar").collapse('hide');
    });

    // Actions when clicking on an anchor that points to the publications tab.
    $("a[href='#tab-publications']").click(function(e){// All anchor that points to #tab-publications
        e.preventDefault();
        $(".navbar-nav li a").removeClass('selected');
        $('#navbar-nav-publications').addClass('selected');
        history.pushState({tab_now: 'publications'}, "title", "?tab_now=publications");
        changeTab(handle_tab_publications, handle_tab_shown, navbar_collapsed_height);
        handle_tab_shown = handle_tab_publications;
        $("#myNavbar").collapse('hide');
    });

    $("#navbar-nav-journal").click(function(e){
        e.preventDefault();
        $(".navbar-nav li a").removeClass('selected');
        $("#navbar-nav-publications").addClass('selected');
        history.pushState({tab_now: 'publications'}, "title", "?tab_now=publications");
        changeSubTab($("#tab-publications-journals"), handle_tab_publications, handle_tab_shown, navbar_collapsed_height);
        handle_tab_shown = handle_tab_publications;
        $("#myNavbar").collapse('hide');
    });

    $("#navbar-nav-conference").click(function(e){
        e.preventDefault();
        $(".navbar-nav li a").removeClass('selected');
        $("#navbar-nav-publications").addClass('selected');
        history.pushState({tab_now: 'publications'}, "title", "?tab_now=publications");
        changeSubTab($("#tab-publications-conferences"), handle_tab_publications, handle_tab_shown, navbar_collapsed_height);
        handle_tab_shown = handle_tab_publications;
        $("#myNavbar").collapse('hide');
    });

    $("#navbar-nav-education").click(function(e){
        e.preventDefault();
        $(".navbar-nav li a").removeClass('selected');
        $(this).addClass('selected');
        history.pushState({tab_now: 'education'}, "title", "?tab_now=education");
        changeTab(handle_tab_education, handle_tab_shown, navbar_collapsed_height);
        handle_tab_shown = handle_tab_education;
        $("#myNavbar").collapse('hide');
    });

    $("#navbar-nav-services").click(function(e){
        e.preventDefault();
        $(".navbar-nav li a").removeClass('selected');
        $(this).addClass('selected');
        history.pushState({tab_now: 'services'}, "title", "?tab_now=services");
        changeTab(handle_tab_services, handle_tab_shown, navbar_collapsed_height);
        handle_tab_shown = handle_tab_services;
        $("#myNavbar").collapse('hide');
    });

    $("#navbar-nav-links").click(function(e){
        e.preventDefault();
        $(".navbar-nav li a").removeClass('selected');
        $(this).addClass('selected');
        history.pushState({tab_now: 'links'}, "title", "?tab_now=links");
        changeTab(handle_tab_links, handle_tab_shown, navbar_collapsed_height);
        handle_tab_shown = handle_tab_links;
        $("#myNavbar").collapse('hide');
    });

    // Navbar links move to right of screen when it is affixed.
    $('.navbar').on('affixed.bs.affix', animationNavbarMoveRight);
    $('.navbar').on('affixed-top.bs.affix', animationNavbarMoveLeft);

});

var alerts_navbar_and_parents_paddings_margins = function () {

    // These alerts tell you the margin-right and the padding-right of all the elements around navbar-nav:

    var body_margin_right = $("body").css("margin-right");
    var body_padding_right = $("body").css("padding-right");
    alert("body_margin_right"+body_margin_right)
    alert("body_padding_right"+body_padding_right)

    var site_wrapper_margin_right = $(".content-wrapper").css("margin-right");
    var site_wrapper_padding_right = $(".content-wrapper").css("padding-right");
    alert("site_wrapper_margin_right"+site_wrapper_margin_right)
    alert("site_wrapper_padding_right"+site_wrapper_padding_right)

    var theNavbar_margin_right = $("#theNavbar").css("margin-right");
    var theNavbar_padding_right = $("#theNavbar").css("padding-right");
    alert("theNavbar_margin_right"+theNavbar_margin_right)
    alert("theNavbar_padding_right"+theNavbar_padding_right)

    var theNavbarContainerFluid_margin_right = $("#theNavbarContainerFluid").css("margin-right");
    var theNavbarContainerFluid_padding_right = $("#theNavbarContainerFluid").css("padding-right");
    alert("theNavbarContainerFluid_margin_right"+theNavbarContainerFluid_margin_right)
    alert("theNavbarContainerFluid_padding_right"+theNavbarContainerFluid_padding_right)

    var myNavbar_margin_right = $('#myNavbar').css("margin-right"); //不是数字
    alert("myNavbar_margin_right"+myNavbar_margin_right);
    var myNavbar_padding_right = $('#myNavbar').css("padding-right"); //不是数字
    alert("myNavbar_padding_right"+myNavbar_padding_right);

    var myNavbar_nav_margin_right = $('#myNavbar-nav').css('margin-right');
    alert("myNavbar_nav_margin_right"+myNavbar_nav_margin_right)
    var myNavbar_nav_padding_right = $('#myNavbar-nav').css('padding-right');
    alert("myNavbar_nav_padding_right"+myNavbar_nav_padding_right)
};

var animationNavbarMoveRight = function() {
    // alert('The navigation menu is about to be affixed - The .affix-top class has been replaced with the .affix class');

    // $('#theNavbar').animate( {"background-color":"rgba(200,200,200,0.9)"}, 1000)


    if ($(".navbar-toggle").css("display") == 'none') {

        var width_navbar_nav = $('.navbar-nav').width();
        var width_window = $(window).width();
        var width_navbar_brand = $(".navbar-brand").width();
        var margin_needed = width_window - width_navbar_nav ; // This shouldn't be divided by half because the myNavbar-nav are centered, so adding right margin of 2 effectively move content to the left by 1.

        $("#myNavbar-nav").css("margin-right",width_navbar_brand ) // the navbar-brand pushes the navbar-nav right. so now compensate for that.
        // 这里有时候有点问题如下：做navbar-brand 的动画带来一个问题，就是当窗口比较小的时候（大于768，没有collapse），compensate之后的myNavbar加上brand长度可能就超了屏幕width，这样会把navbar-nav挤到第二行

        $('#myNavbar-nav').animate( {"margin-right":-margin_needed}, 250, "easeOutQuad", function(){ // if animate padding-right, wont work, maybe a bug!
            // $('#theNavbar').addClass("navbar-fixed-top"); // this is not actualy needed. without this, the margin-right of #myNavbar-nav should be -30. with this, should be -15, because adding the navbar-fixed-top class make the navbar-collapse's padding-right to change from 15px to 0.
            $('#myNavbar-nav').addClass( "navbar-right"); // add navbar-right class make the div to be float:right, and navbar-right has a right margin of -15px. make this float:right is needed because later on you can change the browser size and the navbar-nav will be responsive.
            $('#myNavbar-nav').css("margin-right",-15); // because added navbar-right, it become a float:right, so now need to reset the margin-right back.

            //  show the navbar-brand, after the moving animation is done.
            $('.navbar-brand').css("display", "inline"); // was default none in the css.
            $('.navbar-brand').hide();
            $('.navbar-brand').show("fade", 200);

        });
    }
    else{  // navbar collapse成三条杠
        $('.navbar-brand').css("display", "inline"); // was default none in the css.
        $('.navbar-brand').hide();
        $('.navbar-brand').show("fade", 200);
    };

};

var animationNavbarMoveLeft = function() {

    // $('.navbar-brand').hide("fade", 300, function(){$('.navbar-brand').css("display", "none")});
    $('.navbar-brand').css("display", "none");

    // $('#theNavbar').animate( {"background-color":"rgba(0,0,0,0)"}, 1000)

    if ($(".navbar-toggle").css("display") == 'none') {  // 如果现在navbar不显示三条杠

        // calculate these variables locally because the browser size may have changed after document is ready.
        var width_navbar_nav = $('.navbar-nav').width();
        var width_window = $(window).width();
        var margin_needed = width_window - width_navbar_nav;

        // $('#theNavbar').removeClass("navbar-fixed-top");
        // $('#myNavbar-nav').css("marginRight",-0);
        // $('#myNavbar-nav').removeClass( "navbar-right");


        $('#myNavbar-nav').animate( {"margin-right":margin_needed/2-30}, 250, "easeOutQuad", function(){ // -30 because was in need of -30px to compensate the container-fluid padding-right 15px and navbar-collapse padding-right of 15px.
            $('#myNavbar-nav').css("marginRight",0);
            $('#myNavbar-nav').removeClass( "navbar-right");
        });
    };

};

//click anywhere to collapse the navbar on cellphone. Except clicking on the publications link on the publications page - you want to expand dropdown in this case.
// want to tap anywhere on cell phone and close the collapse as well.
var document_tap = false;
$(document).on('touchstart', function() {
    document_tap = true;
});
$(document).on('touchmove', function() {
    document_tap = false;
});
$(document).on('click touchend',function(e) {
    if (e.type == "click") document_tap = true;
    if (document_tap) {
        // 不是dropdown-toggle, 不是caret，也不是任何一个anchor的时候，collapse
        if(  ($(e.target).attr('class') != ('dropdown-toggle')) && ($(e.target).attr('class') != ('caret')) && (e.target.tagName != 'A') ) {
        // if(  $(e.target) != $('#navbar-nav-publications-caret') ) {
            $(".navbar-collapse.in").collapse('hide');
        };
    };
});

function changeTab(handle_new_tab, handle_tab_shown, navbar_collapsed_height){
    // A function to do various things when switching content tabs like bio, publications, etc..

    if (handle_tab_shown != handle_new_tab) {
        // during tab change, need to hide old tab, show new tab. During the process, the page length will change, causing scrollbar to jump, and other unwanted effect. So, need to hold the page length during the process
        var body_height = $("body").height();
        $("#spacer-temp").css("height", body_height);
        $("#spacer-temp").css("display", "block"); // to hold the space

        // Now change tab
        handle_tab_shown.hide("fade", 100, function(){
            handle_new_tab.show("fade", 250);

            // If was on the page position where the banner is shown, don't scroll after change tab; if was on the page position pass the banner, after change tab, also scroll to just past banner position.
            var pos = handle_new_tab.offset().top; 
            if ($("#theNavbar").hasClass("affix")) {
                $("body, html").scrollTop(pos-navbar_collapsed_height);
            };

            $("#spacer-temp").css("display", "none");
        });
    }
    else {
        // Was on the same tab that just clicked. Now do smooth scroll animation to just below banner (banner just outside of the screen above).
        scroll_pos = calc_scroll_pos(handle_new_tab, navbar_collapsed_height);
        $('body, html').animate({scrollTop: scroll_pos}, 200, 'easeOutQuad')
    }
};

function changeSubTab(handle_new_sub_tab, handle_new_tab, handle_tab_shown, navbar_collapsed_height){
    // A function to do various things when switching to a sub-tab like 'journal' (which belong to content tab 'publications')

    if (handle_tab_shown != handle_new_tab) {
        var body_height = $("body").height();
        $("#spacer-temp").css("height", body_height);
        $("#spacer-temp").css("display", "block"); // to hold the space
        handle_tab_shown.hide("fade", 100, function(){
            handle_new_tab.show("fade", 250);

            // scroll to the new subtab, after switching tab.
            scroll_pos = calc_scroll_pos(handle_new_sub_tab, navbar_collapsed_height);
            $('body, html').animate({scrollTop: scroll_pos}, 200, 'easeOutQuad')

            $("#spacer-temp").css("display", "none");
        });
    }
    else {
        scroll_pos = calc_scroll_pos(handle_new_sub_tab, navbar_collapsed_height);
        $('body, html').animate({scrollTop: scroll_pos}, 200, 'easeOutQuad')
    };
};

function calc_scroll_pos(obj, navbar_collapsed_height) {
    // Here calculates the scroll position of a certain obj. Assuming: 1. whichever starting situation (whether navbar collapse or not, whether navbar affix or not). 2. End with navbar affix.

    // the current position (maybe navbar is collapse or not, maybe it is affix or not)
    var pos = obj.offset().top;

    // If currently navbar is not affix, 并且，navbar要么是展开要么是正在collapsing(还未collapsed) 这时候，scroll position需要减去展开的navbar高度。
    if ( $("#theNavbar").hasClass("affix-top") && ($("#myNavbar").hasClass("in") || $("#myNavbar").hasClass("collapsing")) ) {
        scroll_pos = pos  - navbar_collapsed_height - $(".navbar-collapse").height();
    }
    else {
        scroll_pos = pos  - navbar_collapsed_height;
    };

    return scroll_pos
};
