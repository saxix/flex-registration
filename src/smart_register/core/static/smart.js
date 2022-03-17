smart = {
    showHideDependant: function (sender, target, value) {
        try {
            var $form = $(sender).parents(".form-container");
            var $target = $form.find(target).parents(".field-container");
            if ($(sender).val() == value) {
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
    }
};

(function ($) {
    $(function () {
        $('[data-visibility=hidden]').parents(".field-container").hide()
    });
})($);
