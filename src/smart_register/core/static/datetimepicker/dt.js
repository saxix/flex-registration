$("body").on("focus", ".vDateField", function () {
    new Datepicker(this, {
        autohide: true,
        format: 'yyyy-mm-dd',
    });
});
