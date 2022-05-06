(function ($) {
    $(function () {
        // we need this HACK to manage the stupid cache system in front of the app
        const slug = $("meta[name=\"Survey\"]").attr("content");
        $.get("/api/registration/" + slug, function (data) {
            const parts = location.href.split("/");
            const version = parseInt(parts[parts.length - 2]);
            if (!isNaN(version)) {
                if (version !== data.version) {
                    parts[parts.length - 2] = version;
                    const url = parts.join("/");
                    location.href = url;
                }
            }
        });
    });
})($);
