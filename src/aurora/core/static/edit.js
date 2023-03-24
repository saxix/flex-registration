(function ($) {
    $(function () {
        var TOOLBAR = "<div class=\"fixed flex staff-toolbar\">" +
            "<div class=\"flex-shrink ml-3 block hidden lg:inline-flex\">" +
            "Version: {{project.version}}" +
            "</div>" +
            "<div class=\"flex-shrink block hidden lg:inline-flex\">" +
            "Build date: {{project.build_date}}" +
            "</div>" +
            "<span class=\"flex-grow block inline-flex\">" +
            "{{project.env}}" +
            "</span>" +
            "<div class=\"hidden md:inline-flex \">" +
            "<a href=\"{{admin_url}}\">Admin</a>&nbsp; | " +
            "</div>" +
            "<div class=\"ml-2 mr-5\">" +
            "<input id=\"staff-editor\" type=\"checkbox\" class=\" mt-1 chk cursor-pointer\">" +
            "<input id=\"staff-i18n\" type=\"checkbox\" class=\" mt-1 chk cursor-pointer\">" +
            "</div>" +
            "</div>";

        var seed = Date.now() + Math.random();
        $(".staff-editor").hide();
        $.get("/api/user/me/?" + seed).done(function (resp) {
            if (resp.canTranslate) {
                $.get("/api/project/?" + seed).done(function (resp1) {
                    var html = TOOLBAR.replaceAll("{{project.version}}", resp1.version)
                                      .replaceAll("{{project.build_date}}", resp1.build_date)
                                      .replaceAll("{{project.env}}", resp1.env)
                                      .replaceAll("{{admin_url}}", resp.adminUrl);
                    $("body").prepend(html);
                    i18n.displayIcons(resp);
                    $editCheckBox = $("#staff-editor");
                    $i18nCheckBox = $("#staff-i18n");
                    var setI18NIcons = function (onOff) {
                        if (onOff) {
                            $(".staff-18n").show();
                        } else {
                            $(".staff-i18n").hide();
                        }
                    };
                    var setEditorIcons = function (onOff) {
                        if (onOff) {
                            $(".staff-editor").show();
                        } else {
                            $(".staff-editor").hide();
                        }
                    };
                    $('.staff-toolbar input[type=checkbox]').on("click", function(){
                        var t = $(this).attr('id');
                        if ( $(this).is(":checked")) {
                            $(`.${t}`).show();
                        } else {
                            $(`.${t}`).hide();
                        }
                    });
                    // $editCheckBox.on("click", function () {
                    //     setEditorIcons($editCheckBox.is(":checked"));
                    //     Cookies.set("staff-editor", $editCheckBox.is(":checked"));
                    // });

                    $editCheckBox.prop("checked", Cookies.get("staff-editor") === "true")
                    $i18nCheckBox.prop("checked", Cookies.get("staff-i18n") === "true");
                    setEditorIcons($editCheckBox.is(':checked'));
                    setI18NIcons($i18nCheckBox.is(':checked'));
                });
            }else{
                $(".staff-editor").html("").hide();
            }
        });
    });
})($);
