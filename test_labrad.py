
from playwright.sync_api import sync_playwright
import traceback

START_URL = "https://www.kenketsu.jp/ReservationHome"
TARGET_FACILITY = "北海道赤十字血液センター"


def show_page(page, label, limit=4000):
    print(f"\n=== {label} ===")
    print("URL:", page.url)
    print("TITLE:", page.title())

    try:
        print(page.locator("body").inner_text()[:limit])
    except Exception as e:
        print("画面内容の取得に失敗:", repr(e))


def click_text_if_present(page, text, exact=True):
    locator = page.get_by_text(text, exact=exact)

    if locator.count() == 0:
        print(f"クリック対象が見つかりません: {text}")
        return False

    locator.first.click()

    try:
        page.wait_for_load_state(
            "domcontentloaded",
            timeout=10000
        )
    except Exception:
        pass

    page.wait_for_timeout(1500)
    print(f"クリックしました: {text}")
    return True


def inspect_element(locator, label):
    print(f"\n--- {label} ---")

    try:
        print("要素数:", locator.count())

        for i in range(min(locator.count(), 10)):
            element = locator.nth(i)

            print(f"\n要素 [{i}]")

            try:
                print(
                    "テキスト:",
                    repr((element.inner_text() or "").strip()[:300])
                )
            except Exception:
                pass

            try:
                print(
                    "HTML:",
                    element.evaluate(
                        "(el) => el.outerHTML"
                    )[:2000]
                )
            except Exception as e:
                print("HTML取得失敗:", repr(e))

    except Exception as e:
        print("要素調査失敗:", repr(e))


def inspect_reservation_screen(page):
    """ログイン画面の予約導線を調査する。"""

    show_page(page, "クリック前のログイン画面")

    # 「献血の予約」のリンクと、同じ文字列を持つ要素を調べる
    inspect_element(
        page.locator("a").filter(has_text="献血の予約"),
        "献血の予約リンク"
    )

    inspect_element(
        page.get_by_text("献血の予約", exact=True),
        "献血の予約という文字列を持つ要素"
    )

    # 「会員登録せずに献血する」の周辺HTMLを調べる
    inspect_element(
        page.get_by_text(
            "会員登録せずに献血する",
            exact=False
        ),
        "会員登録せずに献血する"
    )

    # JavaScriptによる画面切り替えの可能性を調べる
    reservation = page.get_by_text(
        "献血の予約",
        exact=True
    )

    if reservation.count() == 0:
        print("「献血の予約」が見つからないためクリックを中止します")
        return

    before_url = page.url
    before_text = page.locator("body").inner_text()
    before_pages = list(page.context.pages)

    print("\n=== 「献血の予約」をクリック ===")

    try:
        reservation.first.click()
        page.wait_for_timeout(2500)
    except Exception as e:
        print("クリック時の例外:", repr(e))

    # 新しいタブが開いた場合にも対応する
    after_pages = list(page.context.pages)
    new_pages = [
        p for p in after_pages if p not in before_pages
    ]

    for i, new_page in enumerate(new_pages):
        try:
            new_page.wait_for_load_state(
                "domcontentloaded",
                timeout=10000
            )
        except Exception:
            pass

        show_page(new_page, f"新規ページ [{i}]")
        inspect_element(
            new_page.locator("a"),
            f"新規ページ [{i}] のリンク"
        )

    print("\nクリック前URL:", before_url)
    print("クリック後URL:", page.url)

    try:
        after_text = page.locator("body").inner_text()
        print("本文に変化あり:", before_text != after_text)

        if before_text != after_text:
            print("\n=== クリック後の本文 ===")
            print(after_text[:5000])

    except Exception as e:
        print("クリック後本文の取得失敗:", repr(e))

    show_page(page, "クリック後の画面")

    # クリック後の画面にあるフォームや操作要素を調べる
    inspect_element(
        page.locator(
            "form, button, input, select, "
            "[role=button], [role=tab]"
        ),
        "クリック後のフォーム・操作要素"
    )

    print("\n=== 予約導線の診断終了 ===")


with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    context = browser.new_context()
    page = context.new_page()
    page.set_default_timeout(15000)

    try:
        # 1. 予約トップページ
        page.goto(
            START_URL,
            wait_until="domcontentloaded"
        )
        page.wait_for_timeout(2500)
        show_page(page, "予約ページ")

        # 2. 都道府県から探す
        click_text_if_present(
            page,
            "都道府県から探す"
        )
        show_page(page, "都道府県検索")

        # 3. 北海道を選択
        hokkaido_link = page.locator(
            'a[href="#"]'
        ).filter(has_text="北海道")

        if hokkaido_link.count() == 0:
            show_page(page, "北海道リンク未検出")
            raise RuntimeError(
                "北海道のリンクが見つかりません"
            )

        hokkaido_link.first.click()

        try:
            page.wait_for_load_state(
                "domcontentloaded",
                timeout=15000
            )
        except Exception:
            pass

        page.wait_for_timeout(2500)
        show_page(page, "北海道選択後")

        # 4. ログイン画面なら予約導線を診断
        if "Login" in page.url:
            inspect_reservation_screen(page)

            # 今回は診断結果を得ることが目的
            # 実際の予約フローはリンク構造の確認後に実装する
            print(
                "\n診断を完了しました。"
                "出力されたHTMLとクリック後の画面を確認してください。"
            )

        else:
            print(
                "\nログイン画面以外に遷移しました。"
                "現在の画面構造を確認してください。"
            )
            show_page(page, "ログイン画面以外")

    except Exception as e:
        print("\n=== ERROR ===")
        print(repr(e))
        traceback.print_exc()
        show_page(page, "エラー発生時の画面")
        raise

    finally:
        context.close()
        browser.close()
