
from playwright.sync_api import sync_playwright
import traceback

START_URL = "https://www.kenketsu.jp/ReservationHome"

# ご自身の生年月日に変更してください（以下は入力例です）
BIRTH_YEAR = "1980"
BIRTH_MONTH = "1"
BIRTH_DAY = "1"

# "男性" または "女性"
GENDER = "男性"


def wait_after_click(page):
    try:
        page.wait_for_load_state(
            "domcontentloaded",
            timeout=10000
        )
    except Exception:
        pass

    page.wait_for_timeout(2000)


def show_page(page, label, limit=7000):
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

    for i in range(min(links.count(), 100)):
        element = links.nth(i)

        try:
            text = (element.inner_text() or "").strip()
            href = element.get_attribute("href") or ""
            onclick = element.get_attribute("onclick") or ""

            if text or href or onclick:
                print(
                    f"[{i}] text={text!r}, "
                    f"href={href!r}, "
                    f"onclick={onclick[:300]!r}"
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
            print(f"\n[{i}] {html[:1500]}")
        except Exception:
            pass


def enter_age_information(page):
    print("\n=== 年齢確認画面の入力 ===")

    # 性別を選択
    gender_locator = page.get_by_text(
        GENDER,
        exact=True
    )

    if gender_locator.count() == 0:
        raise RuntimeError(
            f"性別「{GENDER}」が見つかりません"
        )

    gender_locator.first.click()
    page.wait_for_timeout(500)

    # 生年月日を選択
    selects = page.locator("form select")

    if selects.count() < 3:
        raise RuntimeError(
            "生年月日の選択欄が3つ見つかりません"
        )

    selects.nth(0).select_option(value=BIRTH_YEAR)
    selects.nth(1).select_option(value=BIRTH_MONTH)
    selects.nth(2).select_option(value=BIRTH_DAY)

    print("性別・生年月日の入力操作を行いました。")

    # 入力後の状態を確認
    print("\n--- 入力欄の状態 ---")

    for i in range(selects.count()):
        try:
            print(
                f"select[{i}]:",
                selects.nth(i).input_value()
            )
        except Exception:
            pass

    radios = page.locator('input[type="radio"]')

    for i in range(radios.count()):
        try:
            print(
                f"radio[{i}]:",
                radios.nth(i).evaluate(
                    "(el) => ({"
                    "name: el.name, "
                    "value: el.value, "
                    "checked: el.checked, "
                    "outerHTML: el.outerHTML"
                    "})"
                )
            )
        except Exception:
            pass

    # 「次へ」をクリック
    next_link = page.get_by_text("次へ", exact=True)

    if next_link.count() == 0:
        raise RuntimeError(
            "「次へ」が見つかりません"
        )

    print("\n「次へ」をクリックします。")
    next_link.first.click()
    wait_after_click(page)


with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    context = browser.new_context()
    page = context.new_page()
    page.set_default_timeout(15000)

    try:
        # 1. 予約ページを開く
        page.goto(
            START_URL,
            wait_until="domcontentloaded"
        )
        page.wait_for_timeout(2000)
        show_page(page, "予約ページ")

        # 2. 都道府県検索へ進む
        prefecture = page.get_by_text(
            "都道府県から探す",
            exact=True
        )

        if prefecture.count() > 0:
            prefecture.first.click()
            wait_after_click(page)

        # 3. 北海道を選択
        hokkaido = page.locator(
            'a[href="#"]'
        ).filter(has_text="北海道")

        if hokkaido.count() == 0:
            raise RuntimeError(
                "北海道リンクが見つかりません"
            )

        hokkaido.first.click()
        wait_after_click(page)

        # 4. ログイン画面から予約案内へ
        if "Login" in page.url:
            reservation = page.get_by_text(
                "献血の予約",
                exact=True
            )

            if reservation.count() == 0:
                raise RuntimeError(
                    "「献血の予約」が見つかりません"
                )

            reservation.first.click()
            wait_after_click(page)

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
            wait_after_click(page)

        # 6. 年齢確認画面
        if "blooddonationageform" not in page.url.lower():
            show_page(page, "想定外の画面")
            show_links(page)
            show_controls(page)

            raise RuntimeError(
                "年齢確認画面に到達できませんでした"
            )

        show_page(page, "年齢確認画面")

        # 7. 性別・生年月日を入力して次へ
        enter_age_information(page)

        # 8. 遷移後の画面を調査
        show_page(page, "年齢確認後の画面")
        show_links(page)
        show_controls(page)

        print("\n=== 診断終了 ===")

    except Exception as e:
        print("\n=== ERROR ===")
        print(repr(e))
        traceback.print_exc()

        show_page(page, "エラー発生時の画面")
        show_links(page)
        show_controls(page)

    finally:
        context.close()
        browser.close()
