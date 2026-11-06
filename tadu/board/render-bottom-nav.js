import { navItem } from "./nav-item.js";
import { requestRender } from "./request-render.js";
import { setView } from "./set-view.js";

// The phone's bottom nav: Work, Blocked, Portfolio and More (the sidebar).
export function renderBottomNav(store) {
  const work = store.payload?.me ? "mine" : "all";
  const workActive = ["mine", "all", "board", "done"].includes(store.view) && !store.navOpen;
  document.getElementById("bottom-nav").replaceChildren(
    navItem("Work", "home", workActive, () => setView(work)),
    navItem("Blocked", "alert", store.view === "blocked" && !store.navOpen, () =>
      setView("blocked"),
    ),
    navItem("Portfolio", "briefcase", store.view === "portfolio" && !store.navOpen, () =>
      setView("portfolio"),
    ),
    navItem("More", "more", store.navOpen, () => {
      store.navOpen = !store.navOpen;
      requestRender();
    }),
  );
}
