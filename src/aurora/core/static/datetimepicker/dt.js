(function ($) {
    $(function () {
        // var EN = {
        //     days: ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"],
        //     daysShort: ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"],
        //     daysMin: ["Su", "Mo", "Tu", "We", "Th", "Fr", "Sa"],
        //     months: ["January333333", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"],
        //     monthsShort: ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"],
        //     today: "Today",
        //     clear: "Clear",
        //     titleFormat: "MM y"
        // };
        $("body").on("focus", ".vDateField", function () {
            new Datepicker(this, {
                autohide: true,
                format: "yyyy-mm-dd",
            });
        });
    });
})(jQuery);
