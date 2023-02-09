# PWA process

PWA process enables root/admin user to choose registration form which will be available offline.
Only one (active) registration form can be offline at once.

Steps to point out appropriate form to be offline:
1) Go to /registrations
2) Checkmark form that you would like to be offline
3) Click save

Not only registration is added to be offline, but also its resources (like optionsFields for AjaxFormFields).

### Before start

`BaseURL` should be changed in templates/base. By default, it is localhost:8000, but for development/production environment it should be adjusted.

### How to check that given registration was added by browser to cache?

1) Run devtools (if you use chrome)
2) Choose Application tab and in Cache Storage find `internalCache-1`
3) Appropriate form url should be added there and source code (HTML) for given link should be available

### External resources

In case of need, additional links should be added in file `serviceworker.js` (like cdn links for external JS libraries).

### Validation of encrypted forms

There is no backend validation of forms for encrypted data. However, user who sends form must be logged in.
Server encodes signed cookie of user and verify if she/he is user of Aurora.
