$("#set_language").on("change", function () {
    var url =$(this).find("option:selected").data("url");
    $('<form action="'+$(this).data("url") +'" method="post">' +
        '<input type="hidden" name="next" value="'+ url +'">' +
        '<input type="hidden" name="language" value="'+ $(this).val()+'">' +
        '<input type="hidden" name="csrfmiddlewaretoken" value="'+ $("input[name=csrfmiddlewaretoken]").val()+'">' +
        '</form>').appendTo('body').submit().remove();
}).parent().show();

$('a.i18n').on('click', function(e){
    var url = $(this).data("url");
    e.preventDefault();
    $('<form target="_edit" action="'+ url +'" method="post">' +
        '<input type="hidden" name="lang" value="'+ $(this).data('lang') +'">' +
        '<input type="hidden" name="msgid" value="'+ $(this).data('original') +'">' +
        '<input type="hidden" name="csrfmiddlewaretoken" value="'+ $("input[name=csrfmiddlewaretoken]").val()+'">' +
        '</form>').appendTo('body').submit().remove();
});
