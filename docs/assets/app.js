/* FLABSENGY docs — shared behavior: active nav + ledger filtering */
(function () {
  "use strict";

  // Highlight current page in sidebar
  var path = (location.pathname.split("/").pop() || "index.html").toLowerCase();
  document.querySelectorAll("nav.side a.page").forEach(function (a) {
    var href = (a.getAttribute("href") || "").split("/").pop().toLowerCase();
    if (href === path) {
      a.classList.add("active");
      a.setAttribute("aria-current", "page");
    }
  });

  // Ledger: text + class filter (ledger.html only)
  var q = document.getElementById("ledger-q");
  var sel = document.getElementById("ledger-class");
  var rows = document.querySelectorAll("tr.ledger-row");
  if (q && sel && rows.length) {
    var apply = function () {
      var text = (q.value || "").toLowerCase();
      var cls = sel.value;
      rows.forEach(function (tr) {
        var hay = tr.textContent.toLowerCase();
        var okText = !text || hay.indexOf(text) !== -1;
        var okCls = cls === "all" || tr.getAttribute("data-class") === cls;
        tr.style.display = okText && okCls ? "" : "none";
      });
    };
    q.addEventListener("input", apply);
    sel.addEventListener("change", apply);
  }

  // Metrics page: search box
  var mq = document.getElementById("metric-q");
  var mrows = document.querySelectorAll("tr.metric-row");
  if (mq && mrows.length) {
    mq.addEventListener("input", function () {
      var text = (mq.value || "").toLowerCase();
      mrows.forEach(function (tr) {
        tr.style.display = !text || tr.textContent.toLowerCase().indexOf(text) !== -1
          ? "" : "none";
      });
    });
  }
})();
