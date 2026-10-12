from playwright.sync_api import sync_playwright
import traceback

START_URL = “https://www.kenketsu.jp/ReservationHome”

年齢確認用の入力例。必要に応じて変更してください。

BIRTH_YEAR = “1980”
BIRTH_MONTH = “1”
BIRTH_DAY = “1”
GENDER = “男性”

def wait_after_action(page, seconds=2):
“”“ページ遷移またはAjax処理後の待機”””
try:
page.wait_for_load_state(
“domcontentloaded”,
timeout=10000
)
except Exception:
pass

page.wait_for_timeout(seconds * 1000)

def show_page(page, label, limit=10000):
“”“現在のページ情報を表示”””
print(f”\n=== {label} ===”)
print(“URL:”, page.url)
print(“TITLE:”, page.title())

try:
    print("\n--- 本文 ---")
    print(page.locator("body").inner_text()[:limit])
except Exception as e:
    print("本文取得エラー:", repr(e))

def show_links(page):
“”“リンク一覧を表示”””
print(”\n=== リンク一覧 ===”)

links = page.locator("a")
count = min(links.count(), 120)
for i in range(count):
    element = links.nth(i)
    try:
        text = (element.inner_text() or "").strip()
        href = element.get_attribute("href") or ""
        onclick = element.get_attribute("onclick") or ""
        if text or href or onclick:
            print(
                f"[{i}] text={text!r}, "
                f"href={href!r}, "
                f"onclick={onclick[:250]!r}"
            )
    except Exception:
        pass

def show_controls(page):
“”“フォーム・入力項目のHTMLを表示”””
print(”\n=== フォーム・入力項目 ===”)

elements = page.locator(
    "form, input, select, button, "
    "[role=button], [role=radio], [role=checkbox]"
)
count = min(elements.count(), 80)
for i in range(count):
    try:
        html = elements.nth(i).evaluate(
            "(el) => el.outerHTML"
        )
        print(f"\n[{i}] {html[:1000]}")
    except Exception:
        pass

def click_visible_text(page, text):
“”“指定テキストの表示されている要素をクリック”””
elements = page.get_by_text(text, exact=True)

for i in range(elements.count()):
    element = elements.nth(i)
    try:
        if element.is_visible() and element.is_enabled():
            element.click()
            wait_after_action(page)
            return True
    except Exception:
        continue
return False

def reach_reservation_home(page):
“”“予約検索画面まで進む”””

# 1. 予約トップを開く
page.goto(
    START_URL,
    wait_until="domcontentloaded"
)
wait_after_action(page)
show_page(page, "予約トップ")
# 2. 必要に応じて「都道府県から探す」をクリック
prefecture_tab = page.get_by_text(
    "都道府県から探す",
    exact=True
)
if prefecture_tab.count() > 0:
    try:
        if prefecture_tab.first.is_visible():
            prefecture_tab.first.click()
            wait_after_action(page)
    except Exception:
        pass
# 3. 北海道を選択
# 同名の要素がある場合は、表示されているリンクを優先
hokkaido = page.locator(
    'a[href="#"]'
).filter(has_text="北海道")
clicked = False
for i in range(hokkaido.count()):
    element = hokkaido.nth(i)
    try:
        if (
            element.is_visible()
            and element.is_enabled()
            and element.inner_text().strip() == "北海道"
        ):
            element.click()
            wait_after_action(page)
            clicked = True
            break
    except Exception:
        continue
if not clicked:
    raise RuntimeError(
        "表示されている北海道リンクをクリックできませんでした"
    )
show_page(page, "北海道選択後")
# 4. ログイン画面から予約案内へ
if "login" in page.url.lower():
    reservation = page.get_by_text(
        "献血の予約",
        exact=True
    )
    if reservation.count() == 0:
        raise RuntimeError(
            "ログイン画面で「献血の予約」が見つかりません"
        )
    if not click_visible_text(page, "献血の予約"):
        raise RuntimeError(
            "「献血の予約」をクリックできませんでした"
        )
# 5. 会員登録なしの予約開始
if "loginarousalpage" in page.url.lower():
    start = page.get_by_text(
        "献血予約の開始",
        exact=True
    )
    if start.count() == 0:
        raise RuntimeError(
            "「献血予約の開始」が見つかりません"
        )
    if not click_visible_text(page, "献血予約の開始"):
        raise RuntimeError(
            "「献血予約の開始」をクリックできませんでした"
        )
# 6. 年齢確認
if "blooddonationageform" in page.url.lower():
    gender = page.get_by_text(
        GENDER,
        exact=True
    )
    if gender.count() == 0:
        raise RuntimeError(
            f"性別「{GENDER}」が見つかりません"
        )
    if not click_visible_text(page, GENDER):
        raise RuntimeError(
            f"性別「{GENDER}」を選択できませんでした"
        )
    page.wait_for_timeout(300)
    selects = page.locator("form select")
    if selects.count() < 3:
        raise RuntimeError(
            "生年月日の選択欄が見つかりません"
        )
    selects.nth(0).select_option(BIRTH_YEAR)
    selects.nth(1).select_option(BIRTH_MONTH)
    selects.nth(2).select_option(BIRTH_DAY)
    if not click_visible_text(page, "次へ"):
        raise RuntimeError(
            "年齢確認画面の「次へ」をクリックできませんでした"
        )
# 7. 予約検索画面への到達を確認
if "reservationhome" not in page.url.lower():
    raise RuntimeError(
        "予約検索画面に到達できません。URL: "
        + page.url
    )
show_page(page, "予約検索画面")

def click_prefecture_search(page):
“””
非表示の「献血場所を探す」ボタンを避け、
表示されている北海道リンクを利用する。
“””

print("\n=== 献血場所検索の調査 ===")
buttons = page.get_by_text(
    "献血場所を探す",
    exact=True
)
print("「献血場所を探す」の要素数:", buttons.count())
for i in range(buttons.count()):
    try:
        element = buttons.nth(i)
        print(f"\nボタン候補 [{i}]")
        print(
            element.evaluate(
                "(el) => el.outerHTML"
            )[:1500]
        )
        print("表示状態:", element.is_visible())
    except Exception as e:
        print("要素調査エラー:", repr(e))
# 北海道のリンクをIDで特定する
hokkaido = page.locator(
    'a[id="ReservationHome:j_id63:j_id104:0:j_id106"]'
)
# IDが変わっていた場合は、テキストで検索する
if hokkaido.count() == 0:
    hokkaido = page.locator(
        'a[href="#"]'
    ).filter(has_text="北海道")
target = None
for i in range(hokkaido.count()):
    element = hokkaido.nth(i)
    try:
        if (
            element.is_visible()
            and element.is_enabled()
            and element.inner_text().strip() == "北海道"
        ):
            target = element
            break
    except Exception:
        continue
if target is None:
    print("\n表示されている北海道リンクが見つかりません。")
    show_page(page, "北海道リンク検索失敗")
    show_links(page)
    show_controls(page)
    raise RuntimeError(
        "クリック可能な北海道リンクが見つかりません"
    )
print("\nクリック前URL:", page.url)
print("北海道リンクをクリックします。")
target.click()
wait_after_action(page, seconds=3)
print("クリック後URL:", page.url)
show_page(page, "北海道の献血場所検索後")
show_links(page)
show_controls(page)

def main():
with sync_playwright() as p:
browser = p.chromium.launch(headless=True)

    context = browser.new_context()
    page = context.new_page()
    page.set_default_timeout(15000)
    try:
        reach_reservation_home(page)
        click_prefecture_search(page)
        print("\n=== 診断終了 ===")
    except Exception as e:
        print("\n=== ERROR ===")
        print(repr(e))
        traceback.print_exc()
        show_page(page, "エラー発生時")
        show_links(page)
        show_controls(page)
    finally:
        context.close()
        browser.close()

if name == “main”:
main()
