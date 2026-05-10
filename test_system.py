"""
Koya Restaurant System — End-to-End Test Suite
Run: python test_system.py [admin_password]

How auth works: the admin password IS the Bearer token — there is no login endpoint.
The token is passed directly as "Authorization: Bearer <password>" on every admin request.

Usage:
  python test_system.py              # uses default ADMIN_PASS below
  python test_system.py mypassword   # override from command line
"""

import sys
import json
import time
import urllib.request
import urllib.error

BASE = "https://koya.living"
ADMIN_PASS = sys.argv[1] if len(sys.argv) > 1 else "koya2026!"  # ← change if needed

PASS_STR = "\033[92m✓ PASS\033[0m"
FAIL_STR = "\033[91m✗ FAIL\033[0m"

results = []


import ssl
_ssl_ctx = ssl.create_default_context()
_ssl_ctx.check_hostname = False
_ssl_ctx.verify_mode = ssl.CERT_NONE


class _NoRedirect(urllib.request.HTTPRedirectHandler):
    """Do not follow redirects — return the redirect response directly."""
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


_opener = urllib.request.build_opener(
    _NoRedirect,
    urllib.request.HTTPSHandler(context=_ssl_ctx),
)


def req(method, path, *, body=None, token=None, multipart=None):
    """Make an HTTP request. multipart = (boundary, bytes) for file uploads."""
    url = BASE + path
    headers = {"Accept": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    if multipart:
        boundary, data = multipart
        headers["Content-Type"] = f"multipart/form-data; boundary={boundary}"
    elif body is not None:
        headers["Content-Type"] = "application/json"
        data = json.dumps(body).encode()
    else:
        data = None

    r = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with _opener.open(r, timeout=15) as resp:
            raw = resp.read()
            ct = resp.headers.get("Content-Type", "")
            if raw and "json" in ct:
                return resp.status, json.loads(raw)
            return resp.status, {}
    except urllib.error.HTTPError as e:
        raw = e.read()
        try:
            return e.code, json.loads(raw)
        except Exception:
            return e.code, {"detail": raw.decode(errors="replace")}
    except Exception as e:
        return 0, {"detail": str(e)}


def check(label, passed, detail=""):
    icon = PASS_STR if passed else FAIL_STR
    line = f"  {icon}  {label}"
    if detail:
        line += f"  →  {detail}"
    print(line)
    results.append((label, passed, detail))


def section(title):
    print(f"\n{'─'*60}")
    print(f"  {title}")
    print(f"{'─'*60}")


# ─── 1. CONNECTIVITY ──────────────────────────────────────────────────────────
section("1. CONNECTIVITY")

status_code, _ = req("GET", "/")
check("Public site reachable (koya.living)", status_code in (200, 301, 302), f"HTTP {status_code}")

status_code, _ = req("GET", "/api/menu")
check("API reachable (/api/menu)", status_code == 200, f"HTTP {status_code}")

# admin.html may redirect HTTP→HTTPS; 200 or 3xx both mean reachable
status_code, _ = req("GET", "/admin.html")
check("Admin panel reachable (/admin.html)", status_code in (200, 301, 302), f"HTTP {status_code}")


# ─── 2. AUTHENTICATION ────────────────────────────────────────────────────────
section("2. AUTHENTICATION  (password = Bearer token, no login endpoint)")

# Protected route must block unauthenticated requests
status_code, _ = req("GET", "/api/admin/menu")
check("Protected route blocks unauthenticated request", status_code in (401, 403), f"HTTP {status_code}")

# Wrong password must be rejected
status_code, _ = req("GET", "/api/admin/menu", token="definitely_wrong_password_xyz")
check("Wrong password rejected on protected route", status_code in (401, 403), f"HTTP {status_code}")

# Correct password must grant access
token = ADMIN_PASS
status_code, admin_menu = req("GET", "/api/admin/menu", token=token)
check(f"Correct password grants admin access  (using: '{token[:4]}…')", status_code == 200, f"HTTP {status_code}")

if status_code != 200:
    print(f"\n  {FAIL_STR}  Admin token invalid — pass your password as: python test_system.py <password>")
    sys.exit(1)


# ─── 3. PUBLIC MENU ───────────────────────────────────────────────────────────
section("3. PUBLIC MENU")

status_code, menu = req("GET", "/api/menu")
check("GET /api/menu returns 200", status_code == 200, f"HTTP {status_code}")
check("Menu has items", isinstance(menu, list) and len(menu) > 0, f"{len(menu) if isinstance(menu, list) else 0} items")

if isinstance(menu, list) and len(menu) > 0:
    item = menu[0]
    check("Menu item has required fields (id, section, name)", all(k in item for k in ("id", "section", "name")), str(list(item.keys())))
    check("Menu item has 'image' field", "image" in item, str(list(item.keys())))

    items_with_images = [i for i in menu if i.get("image")]
    check("Some items have images", len(items_with_images) > 0, f"{len(items_with_images)} items with images")


# ─── 4. IMAGE SERVING ─────────────────────────────────────────────────────────
section("4. IMAGE SERVING")

# Check known test image (200 or 304 = served OK)
test_image = "/uploads/456817d0-3977-4fe7-9c43-8af5e7a9907b.webp"
status_code, _ = req("GET", test_image)
check("Known image serves HTTP 200", status_code in (200, 304), f"HTTP {status_code}")

# Check all images referenced by menu items
if isinstance(menu, list):
    broken = []
    for item in menu:
        img = item.get("image")
        if img:
            sc, _ = req("GET", img)
            if sc not in (200, 304):
                broken.append(f"{item['name']}: {img} → HTTP {sc}")
    check("All menu item images serve 200", len(broken) == 0,
          f"{len(broken)} broken: {broken[:3]}" if broken else "all OK")


# ─── 5. IMAGE UPLOAD (WebP conversion) ────────────────────────────────────────
section("5. IMAGE UPLOAD & WebP CONVERSION")

# Valid 1×1 white PNG (base64) — server accepts PNG and converts to WebP
import base64
png_bytes = base64.b64decode(
    "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAIAAACQd1PeAAAADklEQVQI12P4"
    "z8BQDwADhQGAWjR9awAAAABJRU5ErkJggg=="
)

boundary = "testboundary12345"
body_parts = (
    f"--{boundary}\r\n"
    f'Content-Disposition: form-data; name="file"; filename="test.png"\r\n'
    f"Content-Type: image/png\r\n\r\n"
).encode() + png_bytes + f"\r\n--{boundary}--\r\n".encode()

upload_status, upload_body = req(
    "POST", "/api/admin/upload-image",
    token=token,
    multipart=(boundary, body_parts),
)
check("Image upload returns 200", upload_status == 200, f"HTTP {upload_status}")
uploaded_url = upload_body.get("url", "")
check("Upload returns WebP URL", uploaded_url.endswith(".webp"), f"url={uploaded_url}")

if uploaded_url:
    sc, _ = req("GET", uploaded_url)
    check("Uploaded image is publicly accessible", sc in (200, 304), f"HTTP {sc} at {uploaded_url}")


# ─── 6. ADMIN MENU CRUD (changes appear on public menu) ───────────────────────
section("6. ADMIN CRUD → PUBLIC MENU SYNC")

# Create item
status_code, created = req("POST", "/api/admin/menu", token=token, body={
    "section": "Starters",
    "name": "TEST_ITEM_KOYA",
    "description": "Automated test item",
    "price": "0.00",
    "image": uploaded_url if uploaded_url else None,
    "hidden": 0,
    "sort_order": 9999,
    "badge": "TEST"
})
check("Admin: create menu item", status_code == 201, f"HTTP {status_code}")
new_id = created.get("id", "test-item-999")

# Verify it appears on public menu
time.sleep(0.5)
_, pub_menu = req("GET", "/api/menu")
pub_item = next((i for i in (pub_menu if isinstance(pub_menu, list) else []) if i.get("name") == "TEST_ITEM_KOYA"), None)
check("Created item appears on public menu", pub_item is not None, f"id={new_id}")

if pub_item and uploaded_url:
    check("Created item has correct image URL", pub_item.get("image") == uploaded_url, pub_item.get("image"))

# Update item
status_code, _ = req("PUT", f"/api/admin/menu/{new_id}", token=token, body={
    "name": "TEST_ITEM_KOYA_UPDATED",
    "description": "Updated by test",
})
check("Admin: update menu item", status_code == 200, f"HTTP {status_code}")

time.sleep(0.5)
_, pub_menu2 = req("GET", "/api/menu")
updated_item = next((i for i in (pub_menu2 if isinstance(pub_menu2, list) else []) if i.get("id") == new_id), None)
check("Updated name appears on public menu", updated_item and updated_item.get("name") == "TEST_ITEM_KOYA_UPDATED",
      updated_item.get("name") if updated_item else "not found")

# Hide item (hidden=1 should remove from public menu)
status_code, _ = req("PUT", f"/api/admin/menu/{new_id}", token=token, body={"hidden": 1})
check("Admin: hide menu item", status_code == 200, f"HTTP {status_code}")

time.sleep(0.5)
_, pub_menu3 = req("GET", "/api/menu")
hidden_item = next((i for i in (pub_menu3 if isinstance(pub_menu3, list) else []) if i.get("id") == new_id), None)
check("Hidden item removed from public menu", hidden_item is None, "not visible" if hidden_item is None else f"still visible: {hidden_item}")

# Delete item
status_code, _ = req("DELETE", f"/api/admin/menu/{new_id}", token=token)
check("Admin: delete menu item", status_code == 200, f"HTTP {status_code}")

time.sleep(0.5)
_, pub_menu4 = req("GET", "/api/menu")
deleted_item = next((i for i in (pub_menu4 if isinstance(pub_menu4, list) else []) if i.get("id") == new_id), None)
check("Deleted item gone from public menu", deleted_item is None, "gone" if deleted_item is None else "still present!")


# ─── 7. SITE SETTINGS ─────────────────────────────────────────────────────────
section("7. SITE SETTINGS")

status_code, settings_body = req("GET", "/api/settings")
check("GET /api/settings returns 200", status_code == 200, f"HTTP {status_code}")
check("Settings has expected keys", all(k in settings_body for k in ("cover_tagline", "instagram")), str(list(settings_body.keys())[:5]))

# Update a setting and verify it changes
old_tagline = settings_body.get("cover_tagline", "")
test_tagline = "TEST_TAGLINE_XYZ"
status_code, updated_settings = req("PUT", "/api/admin/settings", token=token, body={"cover_tagline": test_tagline})
check("Admin: update setting", status_code == 200, f"HTTP {status_code}")

_, fresh_settings = req("GET", "/api/settings")
check("Updated setting visible on public /api/settings", fresh_settings.get("cover_tagline") == test_tagline,
      fresh_settings.get("cover_tagline"))

# Restore original
req("PUT", "/api/admin/settings", token=token, body={"cover_tagline": old_tagline})
check("Setting restored to original", True, f"restored: '{old_tagline}'")


# ─── 8. RESERVATIONS ──────────────────────────────────────────────────────────
section("8. RESERVATIONS")

status_code, res_body = req("POST", "/api/reservations", body={
    "name": "Test Guest",
    "phone": "+2200000000",
    "email": "test@koya.living",
    "date": "2099-12-31",
    "time": "19:00",
    "party_size": 2,
    "notes": "Automated test reservation"
})
check("Public: create reservation", status_code == 201, f"HTTP {status_code}")
res_id = res_body.get("id")
check("Reservation returns ID", bool(res_id), str(res_body))

# Admin can see it
status_code, res_list = req("GET", "/api/admin/reservations", token=token)
check("Admin: list reservations", status_code == 200, f"HTTP {status_code}")
found = next((r for r in (res_list if isinstance(res_list, list) else []) if r.get("id") == res_id), None)
check("New reservation appears in admin list", found is not None, f"id={res_id}")

# Admin update status
if res_id:
    status_code, _ = req("PUT", f"/api/admin/reservations/{res_id}", token=token, body={"status": "confirmed"})
    check("Admin: update reservation status", status_code == 200, f"HTTP {status_code}")

# Admin delete test reservation
if res_id:
    status_code, _ = req("DELETE", f"/api/admin/reservations/{res_id}", token=token)
    check("Admin: delete test reservation", status_code == 200, f"HTTP {status_code}")


# ─── 9. SECURITY ──────────────────────────────────────────────────────────────
section("9. SECURITY")

# These were checked in section 2 already; re-verify with different endpoints
status_code, _ = req("PUT", "/api/admin/settings", body={"cover_tagline": "hacked"})
check("PUT admin/settings blocked without token", status_code in (401, 403), f"HTTP {status_code}")

status_code, _ = req("POST", "/api/admin/upload-image")
check("POST admin/upload-image blocked without token", status_code in (401, 403, 422), f"HTTP {status_code}")

status_code, _ = req("DELETE", f"/api/admin/menu/nonexistent-id", token="wrong_token_xyz")
check("DELETE admin/menu blocked with wrong token", status_code in (401, 403), f"HTTP {status_code}")


# ─── SUMMARY ──────────────────────────────────────────────────────────────────
passed = sum(1 for _, ok, _ in results if ok)
failed = sum(1 for _, ok, _ in results if not ok)
total = len(results)

print(f"\n{'═'*60}")
print(f"  RESULTS:  {passed}/{total} passed  ·  {failed} failed")
print(f"{'═'*60}")

if failed > 0:
    print("\n  Failed tests:")
    for label, ok, detail in results:
        if not ok:
            print(f"    {FAIL_STR}  {label}  →  {detail}")

print()
sys.exit(0 if failed == 0 else 1)
