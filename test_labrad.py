
from playwright.sync_api import sync_playwright
import traceback

START_URL = "https://www.kenketsu.jp/ReservationHome"

# 年齢確認用の入力例。必要に応じて変更してください。
BIRTH_YEAR = "1980"
BIRTH_MONTH = "1"
BIRTH_DAY = "1"
GENDER = "男性"


def wait_after_action(page, seconds=2):
    try:
        page.wait_for_load_state(
            "domcontentloaded",
            timeout=10000
        )
    except Exception:
        pass

    page.wait_for_timeout(seconds * 1000)


def show_page(page, label, limit=10000):
    print(f"\n=== {label} ===")
    print("URL:", page.url)
    print("TITLE:", page.title())

    try:
        print("\n--- 本文 ---")
        print(page.locator("body").inner_text()[:limit])
    except Exception as e:
        print("本文取得エラー:", repr(e))


def show_links(page):
    print("\n=== リンク一覧 ===")

    links = page.locator("a")

    for i in range(min(links.count(), 120)):
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
    print("\n=== フォーム・入力項目 ===")

    elements = page.locator(
        "form, input, select, button, "
        "[role=button], [role=radio], [role=checkbox]"
    )

    for i in range(min(elements.count(), 80)):
        try:
            html = elements.nth(i).evaluate(
                "(el) => el.outerHTML"
            )
            print(f"\n[{i}] {html[:1000]}")
        except Exception:
            pass


def reach_reservation_home(page):
    # 1. 予約トップを開く
    page.goto(
        START_URL,
        wait_until="domcontentloaded"
    )
    wait_after_action(page)
    show_page(page, "予約トップ")

    # 2. 都道府県から探す
    prefecture_tab = page.get_by_text(
        "都道府県から探す",
        exact=True
    )

    if prefecture_tab.count() > 0:
        prefecture_tab.first.click()
        wait_after_action(page)

    # 3. 北海道を選択
    hokkaido = page.locator(
        'a[href="#"]'
    ).filter(has_text="北海道")

    if hokkaido.count() == 0:
        raise RuntimeError(
            "北海道のリンクが見つかりません"
        )

    hokkaido.first.click()
    wait_after_action(page)
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

        reservation.first.click()
        wait_after_action(page)

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

        start.first.click()
        wait_after_action(page)

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

        gender.first.click()
        page.wait_for_timeout(300)

        selects = page.locator("form select")

        if selects.count() < 3:
            raise RuntimeError(
                "生年月日の選択欄が見つかりません"
            )

        selects.nth(0).select_option(BIRTH_YEAR)
        selects.nth(1).select_option(BIRTH_MONTH)
        selects.nth(2).select_option(BIRTH_DAY)

        next_link = page.get_by_text(
            "次へ",
            exact=True
        )

        if next_link.count() == 0:
            raise RuntimeError(
                "年齢確認画面の「次へ」が見つかりません"
            )

        next_link.first.click()
        wait_after_action(page)

    if "reservationhome" not in page.url.lower():
        raise RuntimeError(
            "予約検索画面に到達できません。URL: "
            + page.url
        )

    show_page(page, "予約検索画面")


def click_prefecture_search(page):
    print("\n=== 献血場所を探すボタンを調査 ===")

    buttons = page.get_by_text(
        "献血場所を探す",
        exact=True
    )

    print("該当要素数:", buttons.count())

    for i in range(buttons.count()):
        try:
            print(
                f"\nボタン候補 [{i}]:",
                buttons.nth(i).evaluate(
                    "(el) => el.outerHTML"
                )[:1500]
            )
        except Exception:
            pass

    if buttons.count() < 2:
        raise RuntimeError(
            "「献血場所を探す」が2つ見つかりません。"
            "画面構成を再確認してください。"
        )

    # 2つ目は都道府県検索側のボタンと想定
    target = buttons.nth(1)

    print("\nクリック前URL:", page.url)
    print("2つ目の「献血場所を探す」をクリックします。")

    target.click()
    wait_after_action(page, seconds=4)

    print("クリック後URL:", page.url)

    show_page(page, "施設検索ボタン押下後")
    show_links(page)
    show_controls(page)


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
