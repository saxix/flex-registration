(function ($) {
    $(function () {
        var seed = Date.now() + Math.random();
        $.get("/api/user/me/?" + seed).done(function (resp) {
            console.log(444, resp);
        });
    });
})($);
