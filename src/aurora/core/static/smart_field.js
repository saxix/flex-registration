window.aurora = {
    Module: function (config) {
        var self = this;
        $form = $("#registrationForm");
        self.config = config;
        self.name = config.name;
        self.valid = true;
        $form.on('submit', function () {
            if (self.valid) {
                $(this).find("input[type=submit]").prop("disabled", "disabled").val(gettext("Please wait..."));
            } else {
                return false;
            }
        });

        self.enableSubmit = function (onOff) {
            if (onOff) {
                $form.find("input[type=submit]").prop("disabled", "")
            } else {
                $form.find("input[type=submit]").prop("disabled", "disabled")
            }
        }
    },
    Field: function (origin) {
        var self = this;
        self.origin = origin;
        const $me = $(origin);
        const $fieldset = $me.parents('fieldset');
        const id = $fieldset.data("fid");
        const pk = $fieldset.data("fpk");
        const name = $fieldset.data("fname");
        const $form = $me.parents('form');
        const $fieldContainer = $me.parents('.field-container');
        const $formContainer = $me.parents('.form-container');
        // const $input = $fieldset.find(`#${id}`);
        const $input = $(origin);
        const initial = {
            required: $input.attr("required"),
        }
        self.setRequired = function (onOff) {
            $input.attr("required", onOff);
            onOff ? $fieldset.find('.required-label').show() : $fieldset.find('.required-label').hide();
            return self;
        };
        self.hide = function () {
            $fieldContainer.hide();
            return self;
        };
        self.show = function () {
            $fieldContainer.show();
            return self;
        };
        self.toggle = function (value) {
            $fieldContainer.toggle();
            if (!$fieldContainer.is(":visible")) {
                self.setRequired(false);
            } else {
                self.setRequired(initial.required);
            }
            return self;
        };

        self.isChecked = function () {
            if ((inputType === "radio") || (inputType === "checkbox")) {
                return $input.is(":checked");
            }
        };
        self.hasValue = function () {
            var inputType = $input.attr('type')
            if ((inputType === "radio") || (inputType === "checkbox")) {
                return $input.is(":checked");
            } else {
                return $input.val().trim() !== '';
            }
        };
        self.setError = function (text) {
            if (text) {
                $fieldset.find(".errors").html(`<ul class="errorlist"><li>${text}</li></ul>`);
            } else {
                $fieldset.find(".errors").html("");
            }
            return self;
        }
        self.assertBetween = function (min, max) {

        };
        self.assertDateBetween = function (min, max) {

        };

        self.sameAs = function (target) {
            const $target = self.sibling(target);
            if ($target.getValue() == self.getValue()) {
                $input.css("background-color", "#d7f6ca");
            } else {
                $input.css("background-color", "#e1adad");
            }
        }
        self.setValue = function (value) {
            $input.val(value);
            return self;
        };
        self.getValue = function () {
            return $input.val();
        };
        self.setDescription = function (value) {
            $fieldset.find('.description').text(value);
            return self;
        };
        self.setHint = function (value) {
            $fieldset.find('.hint').text(value);
            return self;
        };
        self.sibling = function (name) {
            var $target = $formContainer.find(`input[data-flex=${name}]`);
            if (!$target[0]) {
                alert(`Cannot find "input[name=${name}]"`)
            }
            return new aurora.Field($target);
        };
        self.setRequiredOnValue = function (value, targets) {
            try {
                const cmp = value.toString().toLowerCase();
                const val = self.getValue();
                $form.find(targets).each(function (i, e) {
                    var $c = $(e).parents(".field-container");
                    if (val == cmp) {
                        $(e).attr("required", true);
                        $c.find('.required-label').show();
                    } else {
                        $(e).attr("required", false);
                        $c.find('.required-label').hide();
                    }
                })
            } catch (error) {
                console.error(error);
            }
        };
        self.inspect = function () {
            console.log(`${id}: `, {
                value: self.getValue(),
                id: id,
                me: $me,
                form: $form,
                fieldset: $fieldset,
                input: $input,
            })
        };
    }
};
