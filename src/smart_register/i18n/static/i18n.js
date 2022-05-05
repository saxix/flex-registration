$("#set_language").on("change", function () {
    var url = $(this).find("option:selected").data("url");
    $("<form action=\"" + $(this).data("url") + "\" method=\"post\">" +
        "<input type=\"hidden\" name=\"next\" value=\"" + url + "\">" +
        "<input type=\"hidden\" name=\"language\" value=\"" + $(this).val() + "\">" +
        "<input type=\"hidden\" name=\"csrfmiddlewaretoken\" value=\"" + $("input[name=csrfmiddlewaretoken]").val() + "\">" +
        "</form>").appendTo("body").submit().remove();
}).parent().show();
if (I18N_MESSAGE_URL !== undefined && I18N_MESSAGE_URL !== "") {

    $("<script type=“text/template” id=\"i18n-template\">\n" +
        "        <span class=\"inline-flex staff-editor staff-i18n staff-tooltip align-left \">\n" +
        "            <span class=\"tooltiptext\">\n" +
        "                <p><span class=\"label\">Lang</span>{{LANGUAGE_CODE}}</p>\n" +
        "                <p><span class=\"label\">Message</span>{{ORIGINAL1}}</p>\n" +
        "            </span>\n" +
        "            <label aria-label=\"Edit\">\n" +
        "                <a target=\"_edit\" class=\"i18n\"\n" +
        "                   data-url=\"" + I18N_MESSAGE_URL + "\"" +
        "                   data-lang=\"" + LANGUAGE_CODE + "\"" +
        "                   data-original=\"{{ORIGINAL2}}\"" +
        "                   href=\"#\"></a>\n" +
        "            </label>\n" +
        "        </span>\n" +
        "    </script>").appendTo("body");

    $(".itrans").each(function (i, e) {
        // var text=$(e).text().trim();
        var original = $(e).data("msgid");
        if (original) {
            var html = $("#i18n-template").html()
                                          .replace("{{ORIGINAL1}}", original)
                                          .replace("{{ORIGINAL2}}", encodeURIComponent(original))
                                          .replace("{{LANGUAGE_CODE}}", LANGUAGE_CODE);
            $(e).prepend(html);
        }
    });

    $("a.i18n").on("click", function (e) {
        var url = $(this).data("url");
        e.preventDefault();
        $("<form target=\"_edit\" action=\"" + url + "\" method=\"post\">" +
            "<input type=\"hidden\" name=\"lang\" value=\"" + $(this).data("lang") + "\">" +
            "<input type=\"hidden\" name=\"msgid\" value=\"" + $(this).data("original") + "\">" +
            "<input type=\"hidden\" name=\"csrfmiddlewaretoken\" value=\"" + $("input[name=csrfmiddlewaretoken]").val() + "\">" +
            "</form>").appendTo("body").submit().remove();
    });
}
