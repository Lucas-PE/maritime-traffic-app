window.addEventListener("beforeunload", function (e) {
    // Call Flask route on tab close using navigator.sendBeacon
    navigator.sendBeacon("/shutdown");
});