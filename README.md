# Local Network Access demo: "Open in desktop app"

A stand-in for Box's "Open with Box Tools" flow, written the way the platform supports: a public
https page talks to a helper on `127.0.0.1` with `fetch(..., { targetAddressSpace: 'loopback' })`.
No site quirks, no mixed-content exemption beyond what `targetAddressSpace` already gives.

## Run

1. Start the helper (Terminal; it binds `127.0.0.1:17300`, clear of the real Box Tools on 17223):

       python3 helper/helper.py

2. Serve `docs/index.html` from a **public https** origin. It must be public, or the request is not
   less public than the page and nothing is checked. It must be https, or the page is not a secure
   context and LNA refuses before asking. Any static host works (GitHub Pages, an internal web host).

3. Open the page in MiniBrowser from a build that has 8a-i, with Local Network Access enabled.

## What the demo shows

| Step | Page | Helper terminal |
|---|---|---|
| Load the page | Nothing is sent; the permission reads `prompt` | silent |
| Click "Open in desktop app" | `GET /status` goes out and the prompt appears | `GET /status` already logged |
| Deny | Helper "not reachable"; permission `denied`; the log shows a generic `TypeError`. The file does not open | the status check still arrived |
| Reset the permission, reload, click, Allow | Helper "running", then `POST /open` succeeds | `GET /status`, `POST /open?...`, and the file opens in TextEdit |
| Reload | Permission already `granted`, so the page checks the helper on its own and no prompt appears | `GET /status` |

The page never sends `/open` as its first request. Enforcement currently happens once the helper has
answered, so a first request that opened the file would already have done so before the prompt.

The "What this page can observe" panel is the point to linger on: after a Deny, the page sees the same
`TypeError` it would see with nothing installed, plus a `denied` permission state. The one thing it can
still learn is timing, and the helper terminal shows the request was delivered anyway. Both close once
the check moves before the connection (the CFNetwork interface, rdar://183944437).

## Notes

- The prompt appears when the helper answers, so start the helper first, or nothing prompts.
- The page gives up after 5 seconds, as Box's own check does. Answering the prompt later than that
  shows "not reachable" once; reload and it connects, since the answer was recorded.
- Corporate Wi-Fi is fine for this demo, since it only uses loopback. A variant that targets a device
  on the LAN would need a `192.168.x`/`10.x` network, because Apple's `17.x` addresses classify as
  public and would never prompt.
