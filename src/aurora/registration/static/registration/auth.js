(function ($) {
    $(function () {
        var seed = Date.now() + Math.random();
        $.get("../auth/?" + seed).done(function (resp) {
            if (resp.registration) {
                if (resp.registration.protected && resp.user.anonymous) {
                    location.reload();
                }
                if (!window.module) {
                    window.module = new aurora.Module(resp.registration);
                }
                $('#loading').addClass("hidden");
                $('#formContainer').removeClass("hidden");
            } else {
                location.href = "/";
            }
        });
    });
})($);
