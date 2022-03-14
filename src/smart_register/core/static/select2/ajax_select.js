(function ($) {
    $(function () {
        $(".ajaxSelect").each(function (i, e) {
            if ($(e).data("select2")) {
                return;
            }
            var $target = $(e);
            var url = $target.data("ajax-url");
            var source = $target.data("source");
            var parentName = $target.data("parent");
            var label = $target.data("label");
            var name = $target.data("name");
            var $formContainer = $target.parents(".form-container");
            var $parent = null;

            if (parentName) {
                $parent = $formContainer.find("[data-source=" + parentName + "]");
                // if (!$parent.length) {
                //     throw Error("Cannot find parent element '" + parentName + "' for " + name);
                // }
                $parent.on("change", function () {
                    $target.trigger("change.select2");
                    $target.find("option[value]").remove();
                });
            }
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

        });
    });
})($);
