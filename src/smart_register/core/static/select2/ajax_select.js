(function ($) {
    console.log("ajax_select.js");
    $(".ajaxSelect").each(function (i, e) {
        console.log("ajax_select.js", i, e);
        if ($(e).data('select2')){
            return
        }
        console.log("ajax_select.js", i, e);
        var $target = $(e);
        var url = $target.data("ajax-url");
        var source = $target.data("source");
        var parentName = $target.data("parent");
        var label = $target.data("label");
        var name = $target.data("name");
        var $formContainer = $target.parents(".form-container");
        var $parent = null;
        $target.select2({
            placeholder: "Select " + label,
            ajax: {
                url: url,
                dataType: "json",
                data: function (params) {
                    var query = {
                        q: params.term,
                    };
                    if ($parent) {
                        query.parent = $parent.val();
                    }
                    return query;
                }
            }
        });

        if (parentName) {
            $parent = $formContainer.find("[data-source=" + parentName + "]");
            $parent.on("change", function () {
                $target.trigger("change.select2");
                $target.find("option[value]").remove();
            });
        }
    });
})($);
