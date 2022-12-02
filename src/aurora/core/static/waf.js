waf = {
    _aa: function (s) {
        return s.replace(/[^\w -?!]|[<>&]/g, c => "&#" + c.charCodeAt(0) + ";");
    },
    encodeJSON: function(obj, parse) {
        function isString(x) {
            return Object.prototype.toString.call(x) === "[object String]";
        }

        for (var k in obj) {
            if (typeof obj[k] === "object" && obj[k] !== null) {
                waf.encodeJSON(obj[k], parse);
            } else if (obj.hasOwnProperty(k) && isString(obj[k])) {
                obj[k] = waf._aa(obj[k]);
            }
        }
    },
    encode: function ($TARGETS) {
        $TARGETS.each(function (i, field) {
            field.value = waf._aa(field.value);
        });
    },
    encodeAdvanced: function () {
        django.jQuery("textarea[name=advanced],textarea[name=initial-advanced]").each(function (i, field) {
            var val = django.jQuery(field).val();
            var json = JSON.parse(val);
            waf.encodeJSON(json, waf._aa);
            field.value = JSON.stringify(json);
            // console.log(field.value);
        });
    },
    decode: function ($TARGETS) {
        $TARGETS.each(function (i, field) {
            field.value = decodeURIComponent(field.value);
        });
    },
    enable: function ($TARGETS) {
        console.log("WAF hack enabled");
        django.jQuery("form").submit(function (e) {
            // e.preventDefault();
            waf.encode($TARGETS);
            waf.encodeAdvanced();
        });
    }
};
(function ($) {
    $(function () {
        $TARGETS = $("textarea:not('[name=advanced]')");
        waf.enable($TARGETS);
        // waf.decode($TARGETS);
    });
})(django.jQuery);
