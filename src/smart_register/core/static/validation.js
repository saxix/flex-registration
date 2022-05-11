var scripts = [];

function loadJS(FILE_URL, async = true) {
    let scriptEle = document.createElement("script");

    scriptEle.setAttribute("src", FILE_URL);
    scriptEle.setAttribute("type", "text/javascript");
    scriptEle.setAttribute("async", async);

    document.body.appendChild(scriptEle);

    // success event
    scriptEle.addEventListener("load", () => {
        console.log("File loaded")
    });
    // error event
    scriptEle.addEventListener("error", (ev) => {
        console.log("Error on loading file", ev);
    });
}
/*
$.getScript("ajax/test.js", function(data, textStatus, jqxhr) {
  console.log(data); // data returned
  console.log(textStatus); // success
  console.log(jqxhr.status); // 200
  console.log('Load was performed.');
});

 */
// loadJS("file1_path", true);

// <script src="/api/validator/{{ field.field.flex_field.validator.pk }}/script/"></script>
/*
let scriptEle = document.createElement("script");
scriptEle.setAttribute("src", "https://www.mywebsite.com/test.js");
document.body.appendChild(scriptEle);

 */

$('input[data-smart-validator]').each(function(i, e){
    var func = window[$(this).data('smart-validator')];

    console.log("Found validator for Field:", $(e).attr('name'));

    $(e).on('blur', function(){
        $(this).parent().find('ul.errorlist').remove();
        // var func = window[$(this).data('smart-validator')];
        var ret = func($(this).val());
        if (typeof ret === 'string') {
            $(this).parent().find('span.errors').html("<ul class='errorlist'><li>" + gettext(ret) +"</li></ul>")
        }
    });

});

$('.formset[data-smart-validator]').each(function(i, e){
    console.log("Found validator for FormSet:", e);
});

$('form[data-smart-validator]').each(function(i, e){
    console.log("Found validator for Field:", $(e).attr('id'));

});

$('.module[data-smart-validator]').each(function(i, e){
    console.log("Found validator for Module:", e);

});
