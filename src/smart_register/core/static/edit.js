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
        // $('.i18n').each(function(i, e){
        //     $(e).prepend('???');
        //     console.log($(e).text().trim());
        // });
        var pref = Cookies.get("staff-editor") === "true";
        $editCheckBox.prop( "checked", pref );
        setEditorIcons(pref);


    });
})($);
