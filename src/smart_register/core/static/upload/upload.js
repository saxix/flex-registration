;(function ($) {
    $(function () {
        var M = 1048576;
        function returnFileSize(number) {
            if (number < 1024) {
                return number + "bytes";
            } else if (number >= 1024 && number < 1048576) {
                return (number / 1024).toFixed(1) + "KB";
            } else if (number >= 1048576) {
                return (number / 1048576).toFixed(1) + "MB";
            }
        };

        var UploadHandler = function ($field) {
            var $error = $field.parents(".field-container").find(".size-error");
            $field.on("change", function (e) {
                var file = e.target.files[0];
                var size = returnFileSize(file.size);
                if (file.size > M *2){
                    $field.attr("type", "text");
                    $field.attr("type", "file");
                    $error.html('<ul class="errorlist"><li>File too big. Max 2 Mb</li></ul>');
                }else{
                    $error.html('');
                }
            });
        };
        var UploadManager = function () {
            var self = this;
            var fields = [];
            self.addField = function (f) {
                var $field = $(f);
                var name = $field.attr("id");
                if (!fields.includes(name)) {
                    $field.data("handler", new UploadHandler($field));
                    fields.push(name);
                }
            };
        };
        window.uploadManager = new UploadManager();

        $("input.vUploadField").each(function () {
            console.log(2222);
            window.uploadManager.addField(this);
        });

    });
})(jQuery);
