// formsetConfig.push({
//     formCssClass: "form-container.{{ formset.prefix }}",
//     prefix: "{{ formset.prefix }}",
//     deleteContainerClass: "{{ name }}-delete",
//     addContainerClass: "{{ name }}-add",
//     addText: "{{ config.addText|default_if_none:"add another" }}",
//     addCssClass: "add-button {{ config.addCssClass|default_if_none:"bg-white  text-gray-800 font-semibold py-2 px-4 border border-gray-400 rounded shadow" }}",
//     deleteText: "{{ config.deleteText|default_if_none:"remove" }}",
//     deleteCssClass: "delete-button {{ config.deleteCssClass|default_if_none:"bg-white  text-red-400 font-semibold py-2 px-4 border border-red-400 rounded shadow" }}",
//     keepFieldValues: "{{ config.keepFieldValues|default:"" }}"
// });

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
        $(row).find(".vPictureField").each(function () {
            initWebCamField(this);
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
        // var $target = $(".formset-" + config.formCssClass + " forms");
        var $target = $("." + config.formCssClass);
        $target.formset(config);
    })
};

(function ($) {
    $(function () {
        var formsetConfig = [];
        $('.formset-config script[type="application/json"]').each(function (i, e){
            var $e = $(e);
            var value = JSON.parse($e.text() );
            formsetConfig.push(value);
        });

        if (formsetConfig.length > 0) {
            configureFormsets(formsetConfig);
        }
        $("input:checked[onchange]").trigger("change");
    });
})($);
