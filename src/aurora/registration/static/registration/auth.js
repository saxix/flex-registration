(function ($) {
    $(function () {
        var seed = Date.now() + Math.random();
        $.get("../auth/?" + seed).done(function (resp) {
            if (resp.registration.protected && resp.user.anonymous){
                location.reload();
            }
            $('#loading').addClass("hidden");
            $('#formContainer').removeClass("hidden");
        });
    });
})($);
