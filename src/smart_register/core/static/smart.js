smart = {
    showHideDependant: function (sender, target, value) {
        try {
            var cmp = value.toLowerCase();
            var $form = $(sender).parents(".form-container");
            var $target = $form.find(target).parents(".field-container");
            if ($(sender).val() == cmp) {
                $target.show();
            } else {
                $target.hide();
            }
            ;
        } catch (error) {
            console.error(error);
        }
    },
    setDependant: function (sender, target, value) {
        try {
            var $form = $(sender).parents(".form-container");
            var $target = $form.find(target);
            $target.prop("disabled", !($(sender).val() == value));
        } catch (error) {
            console.error(error);
        }
    },
    handleQuestion: function (e) {
        var $container = $(e).parents("fieldset").find(".field-container");
        if ($(e).is(":checked")) {
            $container.show();
        } else {
            $container.hide();
        }
    },
    updateDeleteLabel: function (sender, label){
        $(sender).parents('.form-container').find('.delete-button').text(label + $(sender).val());
    }
};

(function ($) {
    $(function () {
        $("[data-visibility=hidden]").parents(".field-container").hide();

        $(".question-visibility").on("click", function () {
            smart.handleQuestion(this);
        });
        $(".question-visibility.error").each(function (i, e){
            var $container = $(e).parents("fieldset").find(".field-container");
            $container.show();
        });
    });
})($);
