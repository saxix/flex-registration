var DEFAULT = {
    addText: "add another",
    deleteText: "remove",
    added: function (row) {
        var highlight = "border-gray-900 border-2 bg-gray-200";
        $(row).addClass(highlight);
        setTimeout(function () {
            $(row).removeClass(highlight);
        }, 400);
        $(row).find(".vDateField").each(function (i) {

        });
        $(row).find(".question-visibility").each(function (i, e) {
            $(e).on("click", function () {
                smart.handleQuestion(this);
            });
        });
    }
};

var configureFormsets = function (configs){
    configs.forEach(function (c){
        var config = {};
        Object.assign(config, DEFAULT, c);
        var $target = $("." + config.formCssClass);
        $target.formset(config);
    })
};
