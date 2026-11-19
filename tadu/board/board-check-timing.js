// How often an open board checks that it may still show what it shows (the
// server is up, the session or token holds): light requests that read
// nothing. A failed check is tried again sooner (`retryMs`); after `downAfter`
// failures in a row the page is cleared until the board answers again.
export const BOARD_CHECK_TIMING = { everyMs: 30_000, retryMs: 5_000, downAfter: 2 };
