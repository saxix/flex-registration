;(function ($) {
    $(function () {
        var formInitializationTime = new Date()
        // $('#registrationForm input').bind('keypress change click', function () {
        // if (!formInitializationTime){ formInitializationTime = new Date()};
        $('input.CompilationTimeField').attr("data-start", formInitializationTime);
        // $('input.CompilationTimeField').val(formInitializationTime);
        console.log(1111, formInitializationTime);
        // });

        $('#registrationForm').bind('submit', function () {
            $('input.CompilationTimeField').val(new Date() - formInitializationTime);
        });

    });
})(jQuery);
