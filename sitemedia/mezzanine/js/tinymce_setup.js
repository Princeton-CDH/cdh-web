/**
 * This file overrides the default Mezzanine config for TinyMCE
 * (mezzanine/js/tinymce_setup.js) with some custom settings.
 * 
 * http://mezzanine.jupo.org/docs/configuration.html#tinymce-setup-js
 */

(function($) {
    'use strict';

    // Map Django language codes to valid TinyMCE language codes.
    // There's an entry for every TinyMCE language that exists,
    // so if a Django language code isn't here, we can default to en.

    var language_codes = {
        'ar': 'ar',
        'ca': 'ca',
        'cs': 'cs',
        'da': 'da',
        'de': 'de',
        'es': 'es',
        'et': 'et',
        'fa': 'fa',
        'fa-ir': 'fa_IR',
        'fi': 'fi',
        'fr': 'fr_FR',
        'hr-hr': 'hr',
        'hu': 'hu_HU',
        'id-id': 'id',
        'is-is': 'is_IS',
        'it': 'it',
        'ja': 'ja',
        'ko': 'ko_KR',
        'lv': 'lv',
        'nb': 'nb_NO',
        'nl': 'nl',
        'pl': 'pl',
        'pt-br': 'pt_BR',
        'pt-pt': 'pt_PT',
        'ru': 'ru',
        'sk': 'sk',
        'sr': 'sr',
        'sv': 'sv_SE',
        'tr': 'tr',
        'uk': 'uk_UA',
        'vi': 'vi',
        'zh-cn': 'zh_CN',
        'zh-tw': 'zh_TW',
        'zh-hant': 'zh_TW',
        'zh-hans': 'zh_CN'
    };

    function custom_file_browser(field_name, url, type, win) {
        tinyMCE.activeEditor.windowManager.open({
            title: 'Select ' + type + ' to insert',
            file: window.__filebrowser_url + '?pop=5&type=' + type,
            width: 800,
            height: 500,
            resizable: 'yes',
            scrollbars: 'yes',
            inline: 'yes',
            close_previous: 'no'
        }, {
            window: win,
            input: field_name
        });
        return false;
    }

    // Stylesheets are being compiled using django-compressor
    // (https://github.com/django-compressor/django-compressor),
    // which generates a single .css file on page load and inserts it
    // into the page using a django template tag. We ensure this happens
    // by including the "compress" tag on the edit form template
    // (templates/admin/change_form.html).
    function get_editor_stylesheet() {
        // We don't know what the name of the compressed stylesheet will be,
        // but we know it will have "site" somewhere in the href attribute,
        // because the base .scss file is sitemedia/scss/site.scss.
        var mainSheet;
        $.each(document.styleSheets, function(_, sheet) {
            if (sheet.href && sheet.href.match(/site/g)) {
                mainSheet = sheet;
            }
        })
        // Use the default tinyMCE style if we couldn't find the site styles
        return mainSheet ? mainSheet.href : window.__tinymce_css;
    }

    // get the main stylesheet so that we can apply it to tinyMCE only
    var editor_css = get_editor_stylesheet();

    var tinymce_config = {
        height: '500px',
        language: language_codes[window.__language_code] || 'en',
        plugins: [
            "advlist autolink lists link image charmap print preview anchor",
            "searchreplace visualblocks code fullscreen",
            "insertdatetime media contextmenu paste"
        ],
        link_list: window.__link_list_url,
        relative_urls: false,
        browser_spellcheck: true,
        convert_urls: false,
        menubar: false,
        statusbar: false,
        toolbar: ("insertfile undo redo | formatselect | bold italic | " +
                  "bullist numlist outdent indent | link image | " +
                  "code fullscreen"),
        block_formats: 'Paragraph=p;Header 2=h2;Header 3=h3;Div=div;Blockquote=blockquote;Preformatted=pre',
        file_browser_callback: custom_file_browser,
        image_caption: true, // use HTML5 <figcaption>s
        image_dimensions: false, // don't allow hardcoding image dimensions
        content_css: editor_css, // apply the main stylesheet
        body_id: 'maincontent', // this is necessary for most of our styles to apply
        invalid_elements: 'span' // strip out <span>s
    };

    // We could use the 'selector' property to initialize tinyMCE, but jQuery's selectors
    // are more powerful, so we use 'target' instead. This function always takes a single
    // DOM element as an argument (not a jQuery element).
    function initialise_richtext_field($element) {
        if ($element && typeof tinyMCE != 'undefined') {
            var conf = tinymce_config;
            conf.target = $element; // this always needs to be single DOM element
            tinymce.init(conf);
        }
    }

    // Register a handler for Django's formset:added event, to initialise
    // any rich text fields in dynamically added inline forms.
    $(document).on('formset:added', function(e, $row) {
        // convert found jQuery element to DOM element
        initialise_richtext_field($row.find('textarea.mceEditor')[0]);
    });

    // Initialise all existing editor fields, except those with an id
    // containing the string "__prefix__". Those elements are part of the
    // hidden template inline rows used by Django's dynamic inlines, and they
    // shouldn't be initialised as editors.
    $(document).ready(function() {
        $('textarea.mceEditor').filter(function() {
            return (this.id || '').indexOf('__prefix__') === -1;
        }).toArray().forEach(function($element) { // toArray() returns DOM elements
            initialise_richtext_field($element);
        });
    });

})(window.django ? django.jQuery : jQuery);
