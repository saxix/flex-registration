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

            $target.select2({
                placeholder: "Select " + label,
                // disabled: true,
                ajax: {
                    minimumInputLength: 2,
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
                console.log(label, parentName, $parent);
                var subscribers = $parent.data("subscribers") || [];
                subscribers.push($target);
                $parent.data("subscribers", subscribers);
                $target.prop("disabled", true);

                var process = function($t){
                    $t.find("option[value]").remove();
                    $t.trigger("change.select2");
                    $.each($t.data("subscribers"), function(i, $e){
                        process($e);
                    });
                }
                $parent.on("change", function (e) {
                    var $self = $(e.target);
                    $target.prop("disabled", !$self.val());
                    $.each($self.data("subscribers"), function(i, $e){
                        process($e);
                    });
                });
            }
        });
    });
})($);
