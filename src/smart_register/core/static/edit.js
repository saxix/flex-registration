(function ($) {
    $(function () {
        $editCheckBox = $("#staff-editor");
        var setEditorIcons = function (onOff) {
            if (onOff) {
                $(".staff-editor").show();
            } else {
                $(".staff-editor").hide();
            };
        };
        $editCheckBox.on("click", function () {
            setEditorIcons($editCheckBox.is(":checked"));
            Cookies.set("staff-editor", $editCheckBox.is(":checked"));
        });
        var pref = Cookies.get("staff-editor") === "true";
        $editCheckBox.prop( "checked", pref );
        setEditorIcons(pref);
    });

})($);