function submit(action) {
    document.getElementById("action").value = action;
    document.getElementById("Form1").submit();
}

function showSource() {
    submit("source");
}

function showPage() {
    submit("render");
}

function savePage() {
    submit("save");
}

function sendMail() {
    submit("send");
}

function tinyURLConverter(url, name, elm) {
    return url;
};

function initTinyMCE(editor) {
    // editor.style_formats = [
    //     {title: 'Custom format', format: 'customformat'},
    //     {title: 'Align left', format: 'alignleft'},
    //     {title: 'Align center', format: 'aligncenter'},
    //     {title: 'Align right', format: 'alignright'},
    //     {title: 'Align full', format: 'alignfull'},
    //     {title: 'Bold text', inline: 'strong'},
    //     {title: 'Red text', inline: 'span', styles: {color: '#ff0000'}},
    //     {title: 'Red header', block: 'h1', styles: {color: '#ff0000'}},
    //     {
    //         title: 'Badge',
    //         inline: 'span',
    //         styles: {
    //             display: 'inline-block',
    //             border: '1px solid #2276d2',
    //             'border-radius': '5px',
    //             padding: '2px 5px',
    //             margin: '0 2px',
    //             color: '#2276d2'
    //         }
    //     },
    //     {title: 'Table row 1', selector: 'tr', classes: 'tablerow1'},
    //     {title: 'Image formats'},
    //     {title: 'Image Left', selector: 'img', styles: {'float': 'left', 'margin': '0 10px 0 10px'}},
    //     {title: 'Image Right', selector: 'img', styles: {'float': 'right', 'margin': '0 0 10px 10px'}},
    // ]

    editor.addShortcut(
        "ctrl+p", "Render page", showPage);
    editor.addShortcut(
        "ctrl+s", "Save page", savePage);
    editor.ui.registry.addButton("buttonPrimary", {
        text: "Button",
        tooltip: "Create primary button",
        onAction: function (_) {
            editor.insertContent("<a href=\"\" class=\"button primary large p-10\">Label</a>");
        }
    });

    editor.ui.registry.addButton("source", {
        icon: "format",
        tooltip: "Source",
        onAction: showSource
    });


}
