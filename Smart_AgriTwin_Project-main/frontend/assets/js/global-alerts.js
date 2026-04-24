/* =====================================
   GLOBAL REAL-TIME ALERT POLLING
   Runs on EVERY page (except login)
===================================== */

// If user is not logged in → do nothing
/* =====================================
   GLOBAL REAL-TIME ALERT POLLING
===================================== */

// ✅ Use existing token from page scope
if (typeof token === "undefined" || !token) {
  console.log("🔕 Global alerts disabled (no token)");
} else {


  let lastAlertIds = new Set();

  // Ask permission once
  if ("Notification" in window && Notification.permission === "default") {
    Notification.requestPermission();
  }

  async function pollAlerts() {
    try {
      const res = await fetch("/api/alerts/?unread=true", {

  headers: {
    Authorization: "Bearer " + token
  }
});


      if (!res.ok) return;

      const alerts = await res.json();
      console.log("ALERTS POLLED:", alerts);

      if (!Array.isArray(alerts)) return;

      let newCount = 0;

      alerts.forEach(a => {
        if (!lastAlertIds.has(a.id)) {
          lastAlertIds.add(a.id);
          newCount++;

          // 🔔 Browser notification
          if ("Notification" in window && Notification.permission === "granted") {
            new Notification("🚨 New Alert", {
              body: a.message || "New alert triggered"
            });
          }



          // 🔥 Toast (Bootstrap)
          showToast(a.message || "New alert triggered");

           // ✅ Auto-mark alert as read
    fetch(`/api/alerts/${a.id}`, {
      method: "PATCH",
      headers: {
        "Authorization": "Bearer " + token,
        "Content-Type": "application/json"
      },
      body: JSON.stringify({ read: true })
    });
        }
      });

      updateBadge(alerts.length);

    } catch (err) {
      console.error("Global alert polling failed", err);
    }
  }

  // 🔴 Badge update
  function updateBadge(count) {
    const badge = document.getElementById("alertBadge");
    if (!badge) return;

    if (count > 0) {
      badge.innerText = count;
      badge.classList.remove("d-none");
    } else {
      badge.classList.add("d-none");
    }
  }

  // 🍞 Toast popup
  function showToast(message) {
    const toastEl = document.getElementById("alertToast");
    const toastBody = document.getElementById("alertToastBody");

    if (!toastEl || !toastBody) return;

    toastBody.innerText = message;

    const toast = new bootstrap.Toast(toastEl);
    toast.show();
  }

  // ⏱ Poll every 3 seconds
  pollAlerts();
  setInterval(pollAlerts, 3000);
}
