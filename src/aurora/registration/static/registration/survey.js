(function ($) {
    var gst_session = function(){
        const queryString = window.location.search;
        const urlParams = new URLSearchParams(queryString);
        return urlParams.get('s')
    }
    $(function () {
        // we need this HACK to manage the stupid cache system in front of the app
        const slug = $("meta[name=\"Survey\"]").attr("content");
        $.get("/api/registration/" + slug + "/version/?" + Math.random(), function (data) {
            var parts = location.href.split("/");
            const version = parseInt(parts[parts.length - 2]);
            if (version !== data.version) {
                location.href = data.url;
            }
            else if (data.auth && (data.session_id !== gst_session())){
                location.href = data.url;
            }
        });
    });
})($);
