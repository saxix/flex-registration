(function ($) {
    $(function () {
        // we need this HACK to manage the stupid cache system in front of the app
        $.get("api/project/?" + Math.random(), function (data) {
            let params = (new URL(document.location)).searchParams;
            let version = params.get("ver");
            if (version != data.cache) {
                var url = window.location.origin + window.location.pathname;
                params.set("ver", data.cache);
                location.href = url + "?" + params.toString();
            }
        });
    });
})($);
