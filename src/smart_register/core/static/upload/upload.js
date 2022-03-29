;(function ($) {
    $(function () {
        function isUploadSupported() {
            if (navigator.userAgent.match(/(Android (1.0|1.1|1.5|1.6|2.0|2.1))|(Windows Phone (OS 7|8.0))|(XBLWP)|(ZuneWP)|(w(eb)?OSBrowser)|(webOS)|(Kindle\/(1.0|2.0|2.5|3.0))/)) {
                return false;
            }
            var elem = document.createElement("input");
            elem.type = "file";
            return !elem.disabled;
        };

        function processFile(dataURL, fileType) {
            var maxWidth = 800;
            var maxHeight = 800;

            var image = new Image();
            image.src = dataURL;

            image.onload = function () {
                var width = image.width;
                var height = image.height;
                var shouldResize = (width > maxWidth) || (height > maxHeight);

                if (!shouldResize) {
                    sendFile(dataURL);
                    return;
                }

                var newWidth;
                var newHeight;

                if (width > height) {
                    newHeight = height * (maxWidth / width);
                    newWidth = maxWidth;
                } else {
                    newWidth = width * (maxHeight / height);
                    newHeight = maxHeight;
                }

                var canvas = document.createElement("canvas");

                canvas.width = newWidth;
                canvas.height = newHeight;

                var context = canvas.getContext("2d");

                context.drawImage(this, 0, 0, newWidth, newHeight);

                dataURL = canvas.toDataURL(fileType);

                sendFile(dataURL);
            };

            image.onerror = function () {
                alert("There was an error processing your file!");
            };
        };

        function readFile(file, target) {
            var reader = new FileReader();

            reader.onloadend = function () {
                target.val(reader.result);
                console.log(reader.result, file.type);
            };

            reader.onerror = function () {
                alert("There was an error reading the file!");
            };

            reader.readAsDataURL(file);
        };
        var UploadHandler = function ($field) {
            var self = this;
            var $textArea = $field.parents(".field-container").find("textarea");
            console.log(1111, $field.attr("name"));
            $field.on("change", function (e) {
                var file = e.target.files[0];

                if (file) {
                    readFile(file, $textArea);
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
            window.uploadManager.addField(this);
        });

    });
})(jQuery);
