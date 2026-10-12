
from playwright.sync_api import sync_playwright
import traceback

START_URL = "https://www.kenketsu.jp/ReservationHome"
TARGET_FACILITY = "北海道赤十字血液センター"


def show_page(page, label):
    print(f"\n=== {label} ===")
    print("URL:", page.url)
    print("TITLE:", page.title())

    try:
        print(page.locator("body").inner_text()[:3000])
    except Exception as e:
        print("画面内容の取得に失敗:", repr(e))


def click_text_if_present(page, text, exact=True):
    locator = page.get_by_text(text, exact=exact)

    if locator.count() > 0:
        locator.first.click()
        page.wait_for_load_state(
            "domcontentloaded",
            timeout=15000
        )
        page.wait_for_timeout(2000)
        print(f"クリックしました: {text}")
        return True

    return False


def inspect_reservation_links(page):
    """予約関連のリンクとボタンを調べて表示する。"""

    print("\n=== 予約関連のリンク ===")

    keywords = [
        "献血の予約",
        "会員登録せず",
        "予約",
        "献血する",
    ]

    count = 0

    for i, link in enumerate(page.locator("a").all()):
        try:
            text = (link.inner_text() or "").strip()
            href = link.get_attribute("href") or ""

            if text and any(word in text for word in keywords):
                print(
                    f"LINK [{i}] "
                    f"text={text!r}, href={href!r}"
                )
                count += 1

        except Exception as e:
            print(f"リンク [{i}] の取得に失敗:", repr(e))

    if count == 0:
        print("該当するリンクは見つかりませんでした")

    print("\n=== 予約関連のボタン ===")

    button_count = 0

    for i, button in enumerate(
        page.locator(
            "button, input[type=submit], "
            "input[type=button], [role=button]"
        ).all()
    ):
        try:
            text = (
                button.inner_text()
                or button.get_attribute("value")
                or button.get_attribute("aria-label")
                or ""
            ).strip()

            if text and any(word in text for word in keywords):
                print(f"BUTTON [{i}] text={text!r}")
                button_count += 1

        except Exception as e:
            print(f"ボタン [{i}] の取得に失敗:", repr(e))

    if button_count == 0:
        print("該当するボタンは見つかりませんでした")


with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()
    page.set_default_timeout(15000)

    try:
        # 1. 予約ページを開く
        page.goto(
            START_URL,
            wait_until="domcontentloaded"
        )
        page.wait_for_timeout(3000)
        show_page(page, "予約ページ")

        # 2. 都道府県から探す
        click_text_if_present(
            page,
            "都道府県から探す"
        )
        show_page(page, "都道府県検索")

        # 3. 北海道のリンクを選択
        hokkaido_link = page.locator(
            'a[href="#"]'
        ).filter(has_text="北海道")

        if hokkaido_link.count() > 0:
            hokkaido_link.first.click()

            page.wait_for_load_state(
                "domcontentloaded",
                timeout=15000
            )
            page.wait_for_timeout(2000)

            show_page(page, "北海道選択後")

        else:
            show_page(
                page,
                "北海道リンクが見つからない画面"
            )
            raise RuntimeError(
                "北海道のリンクが見つかりません"
            )

        # 4. ログイン画面の場合は予約関連リンクを調査
        if "Login" in page.url:
            show_page(page, "ログイン画面")
            inspect_reservation_links(page)

            raise RuntimeError(
                "予約導線の特定が必要です。"
                "予約関連のリンク・ボタン情報を確認してください"
            )

        # 5. 年齢確認画面が表示されている場合
        age_select = page.locator(
            'select[name="Blooddonationageform:j_id41:j_id43"]'
        )

        if age_select.count() > 0:
            print("年齢確認画面を検出しました")

            page.locator(
                "#selectedmale input"
            ).check(force=True)

            age_select.select_option(label="1990")

            page.locator(
                'select[name="Blooddonationageform:j_id41:j_id46"]'
            ).select_option(label="1")

            page.locator(
                'select[name="Blooddonationageform:j_id41:j_id49"]'
            ).select_option(label="1")

            page.locator(
                "#Blooddonationageform\\:j_id41\\:nextButton"
            ).click(force=True)

            page.wait_for_load_state(
                "domcontentloaded",
                timeout=15000
            )
            page.wait_for_timeout(3000)

            show_page(page, "年齢確認後")

        # 6. 北海道の施設一覧へ進む
        # 現在の画面に北海道リンクがある場合のみ操作する
        hokkaido_links = page.locator("a").filter(
            has_text="北海道"
        )

        if hokkaido_links.count() > 0:
            hokkaido_links.first.click()

            page.wait_for_load_state(
                "domcontentloaded",
                timeout=15000
            )
            page.wait_for_timeout(3000)

        show_page(page, "施設一覧")

        # 7. 対象施設を探す
        card = page.locator(
            "li.mod-list-room__list"
        ).filter(has_text=TARGET_FACILITY)

        if card.count() == 0:
            raise RuntimeError(
                f"施設が見つかりません: {TARGET_FACILITY}"
            )

        reservation_link = card.get_by_text(
            "予約する",
            exact=True
        )

        if reservation_link.count() == 0:
            raise RuntimeError(
                "対象施設の「予約する」が見つかりません"
            )

        reservation_link.first.click()

        page.wait_for_load_state(
            "domcontentloaded",
            timeout=15000
        )
        page.wait_for_timeout(3000)

        show_page(page, "予約詳細画面")

        # 8. 血漿（成分献血）を選択
        plasma_link = page.locator(
            'a[href="qs-type-plasma"]'
        )

        if plasma_link.count() == 0:
            raise RuntimeError(
                "血漿（成分献血）のリンクが見つかりません"
            )

        plasma_link.first.click()

        page.wait_for_load_state(
            "domcontentloaded",
            timeout=15000
        )
        page.wait_for_timeout(3000)

        show_page(page, "血漿選択後")

        # 9. 日付・時刻・予約状況の候補を表示
        print("\n=== 日付・時刻・空き状況の候補 ===")

        keywords = [
            "09:", "10:", "11:", "予約", "空き",
            "満", "不可", "受付", "月", "日"
        ]

        count = 0

        for a in page.locator("a").all():
            try:
                text = (a.inner_text() or "").strip()
                href = a.get_attribute("href") or ""

                if text and any(
                    word in text for word in keywords
                ):
                    print(
                        f"{text[:60]} | "
                        f"href={href[:120]}"
                    )
                    count += 1

                    if count >= 60:
                        break

            except Exception:
                continue

        print("\n=== カレンダー関連要素 ===")

        elements = page.locator(
            '[class*="calendar"], [id*="calendar"], '
            '[class*="reserve"], [class*="schedule"]'
        )

        element_count = elements.count()
        print("関連要素数:", element_count)

        for i in range(min(element_count, 20)):
            try:
                text = (
                    elements.nth(i).inner_text() or ""
                ).strip()

                if text:
                    print(f"[{i}] {text[:200]}")

            except Exception:
                pass

        print("\n=== 診断終了 ===")

    except Exception as e:
        print("\n=== ERROR ===")
        print(repr(e))
        traceback.print_exc()
        show_page(page, "エラー発生時の画面")
        raise

    finally:
        browser.close()
