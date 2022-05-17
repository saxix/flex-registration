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
            "<div class=\"ml-2 mr-5\"><input id=\"staff-editor\" type=\"checkbox\" class=\" mt-1 cursor-pointer\"></div>" +
            "</div>";

        var TOOLTIP_MODULE = "<script type=“text/template” id=\"tooltip-template\">" +
            "<span class=\"staff-editor staff-tooltip\">" +
            "    <span class=\"tooltiptext text-lower\">" +
            "        <p><span class=\"label\">Module</span>{{REGISTRATION}}</p>" +
            "        <p><span class=\"label\">Locale</span>{{REGISTRATION.LOCALE}}</p>" +
            "        <p><span class=\"label\">Version</span>{{REGISTRATION.VERSION}}</p>" +
            "        <p><span class=\"label\">Validator</span>{{REGISTRATION.VALIDATOR}}</p>" +
            "    </span>" +
            "    <a target=\"_edit\" class=\"module\"" +
            "       href=\"{% url \"admin:registration_registration_change\" registration.pk %}\">" +
            "    </a>" +
            "</span>" +
            "</script>";
        var seed = Date.now() + Math.random();

        $.get("/api/user/me?" + seed).done(function (resp) {
            if (resp.canTranslate) {
                $.get("/api/project/?" + seed).done(function (resp1) {
                    var html = TOOLBAR.replaceAll("{{project.version}}", resp1.version)
                                      .replaceAll("{{project.build_date}}", resp1.build_date)
                                      .replaceAll("{{project.env}}", resp1.env)
                                      .replaceAll("{{admin_url}}", resp.adminUrl);
                    $("body").prepend(html);
                    i18n.displayIcons(resp);
                    $editCheckBox = $("#staff-editor");
                    var setEditorIcons = function (onOff) {
                        if (onOff) {
                            $(".staff-editor").show();
                        } else {
                            $(".staff-editor").hide();
                        }
                    };
                    $editCheckBox.on("click", function () {
                        setEditorIcons($editCheckBox.is(":checked"));
                        Cookies.set("staff-editor", $editCheckBox.is(":checked"));
                    });
                    var pref = Cookies.get("staff-editor") === "true";
                    $editCheckBox.prop("checked", pref);
                    setEditorIcons(pref);

                });
                // $(TOOLTIP_MODULE).appendTo("body");
                // $("[data-module]").each(function (i, e) {
                //     var module = $(e).data("module");
                //     var html = $("#tooltip-template").html()
                //                                   .replaceAll("{{ORIGINAL}}", module)
                //                                   .replaceAll("{{ENCODED}}", encodeURIComponent(module))
                //                                   .replaceAll("{{LANGUAGE_CODE}}", LANGUAGE_CODE);
                //     $(e).html(html);
                // });
            }
        });
    });
})($);
