
function tinyURLConverter(url, name, elm) {
    return url;
};

function initTinyMCE(editor) {

    editor.ui.registry.addButton("buttonPrimary", {
        text: "Button",
        tooltip: "Create primary button",
        onAction: function (_) {
            editor.insertContent("<a href=\"\" class=\"button text-white border-0 py-4 px-8 rounded text-center\">Label</a>&nbsp;&nbsp;");
        }
    });

}