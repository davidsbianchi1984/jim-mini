/*
 * Bot Account Cleaner — signup/login signal SDK for platform owners (Module B).
 *
 *   <script src="https://<your-botcleaner-host>/static/sdk.js"></script>
 *   <form id="signup" ...> ... </form>
 *   <script>
 *     const bc = BotCleaner.protect(document.getElementById("signup"));
 *     captcha.onStart(() => bc.captchaStarted());
 *     captcha.onSolved(() => bc.captchaSolved());
 *     // On submit, send bc.collect() to YOUR server with the signup, and have your
 *     // server call POST /api/purge/gate with it (never expose your API key here).
 *   </script>
 *
 * What it adds, all invisible to people:
 *  - a honeypot text field (people never see it, form-filling bots fill it in)
 *  - an invisible link (people never click it, crawling bots follow it)
 *  - headless / automation markers (navigator.webdriver, headless user agents)
 *  - CAPTCHA solve time in milliseconds
 *
 * It sets no cookies, reads no other page data, and sends nothing on its own.
 */
(function (global) {
  "use strict";
  var HIDE = "position:absolute!important;left:-10000px!important;top:auto!important;width:1px!important;height:1px!important;overflow:hidden!important;";
  var TRAP_NAMES = ["website_url", "company_fax", "confirm_address"];

  function protect(form, opts) {
    opts = opts || {};
    var state = { linkHit: false, captchaStart: null, captchaMs: null, loadedAt: Date.now() };
    var name = opts.fieldName || TRAP_NAMES[Math.floor(Math.random() * TRAP_NAMES.length)];

    var wrap = document.createElement("div");
    wrap.setAttribute("aria-hidden", "true");
    wrap.style.cssText = HIDE;
    var input = document.createElement("input");
    input.type = "text"; input.name = name; input.tabIndex = -1; input.autocomplete = "off";
    wrap.appendChild(input);

    var link = document.createElement("a");
    link.href = opts.baitHref || "#bc-trap";
    link.tabIndex = -1; link.rel = "nofollow";
    link.textContent = "Continue";
    link.addEventListener("click", function (e) { state.linkHit = true; e.preventDefault(); });
    wrap.appendChild(link);
    form.appendChild(wrap);

    // A bot that fetches the bait URL directly never triggers the click handler.
    // If you set baitHref to your own endpoint, record hits there as honeypot_link_hit.
    if (global.location && global.location.hash === "#bc-trap") state.linkHit = true;

    function markers() {
      var ua = (global.navigator && navigator.userAgent) || "";
      return {
        webdriver: !!(global.navigator && navigator.webdriver) || /HeadlessChrome|PhantomJS/i.test(ua),
        user_agent: ua,
      };
    }

    return {
      captchaStarted: function () { state.captchaStart = Date.now(); },
      captchaSolved: function () { if (state.captchaStart) state.captchaMs = Date.now() - state.captchaStart; },
      collect: function () {
        var m = markers();
        return {
          honeypot_filled: input.value.length > 0,
          honeypot_link_hit: state.linkHit,
          webdriver: m.webdriver,
          user_agent: m.user_agent,
          captcha_solve_ms: state.captchaMs,
          form_fill_ms: Date.now() - state.loadedAt,
        };
      },
    };
  }

  global.BotCleaner = { protect: protect, version: "0.2.0" };
})(typeof window !== "undefined" ? window : this);
