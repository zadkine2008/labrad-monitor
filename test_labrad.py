
from playwright.sync_api import sync_playwright
import traceback

START_URL = "https://www.kenketsu.jp/ReservationHome"


def show_page(page, label, limit=4000):
    print(f"\n=== {label} ===")
    print("URL:", page.url)
    print("TITLE:", page.title())

    try:
        print(page.locator("body").inner_text()[:limit])
    except Exception as e:
        print("本文取得エラー:", repr(e))


def wait_after_click(page):
    try:
        page.wait_for_load_state(
            "domcontentloaded",
            timeout=10000
        )
    except Exception:
        pass

    page.wait_for_timeout(2000)


def inspect_matching_elements(page, text):
    print(f"\n=== 「{text}」の要素調査 ===")

    locator = page.get_by_text(text, exact=False)
    print("要素数:", locator.count())

    for i in range(min(locator.count(), 10)):
        element = locator.nth(i)

        try:
            print(f"\n要素 [{i}]")
            print(
                "テキスト:",
                repr((element.inner_text() or "").strip()[:300])
            )
            print(
                "HTML:",
                element.evaluate(
                    "(el) => el.outerHTML"
                )[:2500]
            )
        except Exception as e:
            print("要素調査エラー:", repr(e))


def click_reservation_start(page):
    """
    会員登録なしの予約開始操作を調査してクリックする。
    クリック後は遷移先を表示し、以降の操作は行わない。
    """

    show_page(page, "ログイン喚起ページ")

    inspect_matching_elements(page, "献血予約の開始")
    inspect_matching_elements(page, "会員登録せずに献血する方はこちら")

    # リンクとして存在する場合
    links = page.locator("a").filter(
        has_text="献血予約の開始"
    )

    print("\n=== 開始リンクの確認 ===")
    print("リンク数:", links.count())

    for i in range(links.count()):
        try:
            print(
                f"LINK [{i}]:",
                links.nth(i).evaluate(
                    "(el) => el.outerHTML"
                )[:2000]
            )
        except Exception:
            pass

    before_url = page.url

    if links.count() > 0:
        print("\n開始リンクをクリックします")
        links.first.click()
        wait_after_click(page)

    else:
        # リンク以外のボタンや送信要素を調べる
        controls = page.locator(
            "button, input[type=submit], "
            "input[type=button], [role=button]"
        )

        candidates = []

        for i in range(controls.count()):
            element = controls.nth(i)

            try:
                text = (
                    element.inner_text()
                    or element.get_attribute("value")
                    or element.get_attribute("aria-label")
                    or ""
                ).strip()

                if "献血予約の開始" in text:
                    candidates.append(element)

            except Exception:
                pass

        if candidates:
            print("\n開始ボタンをクリックします")
            candidates[0].click()
            wait_after_click(page)

        else:
            print(
                "\n開始リンク・ボタンを特定できませんでした。"
            )
            print("クリック可能な要素を追加調査します。")

            controls = page.locator(
                "a, button, input, [role=button]"
            )

            for i in range(min(controls.count(), 80)):
                element = controls.nth(i)

                try:
                    text = (
                        element.inner_text()
                        or element.get_attribute("value")
                        or element.get_attribute("aria-label")
                        or ""
                    ).strip()

                    html = element.evaluate(
                        "(el) => el.outerHTML"
                    )

                    if text or "onclick" in html:
                        print(
                            f"[{i}] text={text!r} "
                            f"html={html[:800]}"
                        )

                except Exception:
                    pass

            return

    print("\nクリック前URL:", before_url)
    print("クリック後URL:", page.url)

    show_page(page, "献血予約の開始後", limit=6000)

    print("\n=== 遷移先のリンク ===")

    for i, link in enumerate(page.locator("a").all()):
        if i >= 80:
            break

        try:
            text = (link.inner_text() or "").strip()
            href = link.get_attribute("href") or ""

            if text or href:
                print(
                    f"[{i}] text={text!r}, href={href!r}"
                )

        except Exception:
            pass

    print("\n=== 遷移先のフォーム・入力項目 ===")

    elements = page.locator(
        "form, input, select, button, "
        "[role=button], [role=radio], "
        "[role=checkbox]"
    )

    for i in range(min(elements.count(), 50)):
        try:
            html = elements.nth(i).evaluate(
                "(el) => el.outerHTML"
            )

            print(f"[{i}] {html[:1200]}")

        except Exception:
            pass


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

        show_page(page, "都道府県検索")

        # 3. 北海道を選択する
        hokkaido = page.locator(
            'a[href="#"]'
        ).filter(has_text="北海道")

        if hokkaido.count() == 0:
            raise RuntimeError(
                "北海道リンクが見つかりません"
            )

        hokkaido.first.click()
        wait_after_click(page)

        show_page(page, "北海道選択後")

        # 4. ログイン画面の場合、予約の案内ページへ進む
        if "Login" in page.url:
            reservation = page.get_by_text(
                "献血の予約",
                exact=True
            )

            if reservation.count() == 0:
                raise RuntimeError(
                    "ログイン画面で「献血の予約」が見つかりません"
                )

            reservation.first.click()
            wait_after_click(page)

        # 5. 会員登録なしの予約開始を調査
        if "loginarousalpage" in page.url.lower():
            click_reservation_start(page)

        else:
            show_page(page, "想定外の遷移先")
            print(
                "ログイン喚起ページではないため、"
                "予約開始操作は行っていません。"
            )

        print("\n=== 診断終了 ===")

    except Exception as e:
        print("\n=== ERROR ===")
        print(repr(e))
        traceback.print_exc()
        show_page(page, "エラー発生時の画面")
        raise

    finally:
        context.close()
        browser.close()
