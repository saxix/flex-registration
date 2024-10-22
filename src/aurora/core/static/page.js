window.addEventListener("load", function(event) {
    if (window.Sentry !== undefined) {
        Sentry.init({
            dsn: DSN,
            release: VERSION,
            tracesSampleRate: 1.0,
            ignoreErrors: [
                "datepicker.inputField.after is not a function",
                "num.toString(...).padStart is not a function",
                "Unexpected token =>",
                "Unexpected identifier",
            ]
        });
    }
});
