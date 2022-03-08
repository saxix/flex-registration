(function ($) {
    const cameraId = 'camera';
    var Session = function (fieldName) {
        var self = this;
        self.fieldName = fieldName;
        self.$container = $("#div_" + fieldName);
        self.canvas = $("#div_" + fieldName + " canvas")[0];
        self.context = self.canvas.getContext("2d");
        self.$image = $("#div_" + fieldName + " canvas img");
        self.$field = $("#id_" + fieldName);
    };
    $("<div class='modal' id='"+ cameraId +"'>" +
        "<div class='content'><video>Video stream not available.</video>" +
        "<button type='button' class='snap'>Take photo</button>" +
        "<button type='button' class='cancel'>Cancel</button>" +
        "</div></div>").appendTo("body");

    var session = null;
    var streaming = false;
    var width = 320;    // We will scale the photo width to this
    var height = 0;     // This will be computed based on the input stream
    var video = $('#' + cameraId).find('video')[0];

    $(".vPictureField").each(function () {
        var fieldName = $(this).data("target");
        var sess = new Session(fieldName);
        var currentValue = sess.$field.val();
        if (currentValue) {
            let img = new Image();
            img.addEventListener("load", function () {
                sess.context.clearRect(0, 0, sess.canvas.width, sess.canvas.height);
                sess.canvas.width = img.width;
                sess.canvas.height = img.height;
                sess.context.drawImage(img, 0, 0, img.width, img.height);
            });
            img.setAttribute("src", currentValue);
        }
    });

    $("div.formset").on("click", ".show-camera", function () {
        console.log('XD')
        var win = $(window);
        session = new Session($(this).data("target"));
        $("#camera div").css({
            position: "absolute",
            left: (win.width() - $(this).parent().outerWidth()) / 2,
            top: (win.height() - $(this).parent().outerHeight()) / 3
        });
        $("#camera").show();
        startup();
    });
    $("div.formset").on("click", ".clear-camera", function () {
        session = new Session($(this).data("target"));
        session.context.fillStyle = "#AAA";
        session.context.fillRect(0, 0, session.canvas.width, session.canvas.height);

        var data = session.canvas.toDataURL("image/png");
        session.$image.prop("src", data);
        session.$field.val("");
    });

    function cancel() {
        video.pause();
        $("#camera").hide();
    };
    function takepicture() {
        if (width && height) {
            session.canvas.width = width / 2;
            session.canvas.height = height / 2;
            session.context.drawImage(video, 0, 0, width / 2, height / 2);

            var data = session.canvas.toDataURL("image/png");
            session.$image.prop("src", data);
            session.$field.val(data);
            session = null;
            $("#camera").hide();
        } else {
            clearphoto();
            $("#camera").data("target", null).hide();
        }
    }

    $("#camera button.snap").on("click", function () {
        takepicture();
    });
    $("#camera button.cancel").on("click", function () {
        cancel();
    });

    function startup() {
        // snapshot = document.getElementById("snapshot");
        navigator.mediaDevices.getUserMedia({video: true, audio: false})
                 .then(function (stream) {
                     video.srcObject = stream;
                     video.play();
                 })
                 .catch(function (err) {
                     console.log("An error occurred: " + err);
                 });
    }

    video.addEventListener("canplay", function (ev) {
        if (!streaming) {
            height = video.videoHeight / (video.videoWidth / width);
            if (isNaN(height)) {
                height = width / (4 / 3);
            }
            video.setAttribute("width", width);
            video.setAttribute("height", height);
            streaming = true;
        }
    }, false);
})($);
