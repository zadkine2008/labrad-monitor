from playwright.sync_api import sync_playwright
BASE_URL = "https://www.kenketsu.jp/ReservationHome"
with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page(
        viewport={"width": 1280, "height": 2000},
        locale="ja-JP"
    )
    # ==========================================
    # 1. ReservationHome
    # ==========================================
    print("=== 1. ReservationHome ===")
    page.goto(
        BASE_URL,
        wait_until="domcontentloaded",
        timeout=60000
    )
    page.wait_for_timeout(3000)
    print("URL:", page.url)
    print("TITLE:", page.title())
    # ==========================================
    # 2. 北海道
    # ==========================================
    print()
    print("=== 2. 北海道を選択 ===")
    page.locator("a").filter(
        has_text="北海道"
    ).first.click()
    page.wait_for_timeout(3000)
    print("URL:", page.url)
    print("TITLE:", page.title())
    # ==========================================
    # 3. 献血の予約
    # ==========================================
    print()
    print("=== 3. 「献血の予約」 ===")
    page.locator("a").filter(
        has_text="献血の予約"
    ).first.click()
    page.wait_for_timeout(3000)
    print("URL:", page.url)
    print("TITLE:", page.title())
    # ==========================================
    # 4. 献血予約の開始
    # ==========================================
    print()
    print("=== 4. 「献血予約の開始」 ===")
    page.locator("a").filter(
        has_text="献血予約の開始"
    ).first.click()
    page.wait_for_timeout(3000)
    print("URL:", page.url)
    print("TITLE:", page.title())
    # ==========================================
    # 5. 年齢確認
    # ==========================================
    print()
    print("=== 5. 年齢確認 ===")
    page.locator("#selectedmale").click()
    # テスト用
    # 1990年1月1日
    page.locator("select").nth(0).select_option("1990")
    page.locator("select").nth(1).select_option("1")
    page.locator("select").nth(2).select_option("1")
    page.wait_for_timeout(500)
    page.locator(
        "#Blooddonationageform\\:j_id41\\:nextButton"
    ).click(force=True)
    page.wait_for_timeout(4000)
    print("URL:", page.url)
    print("TITLE:", page.title())
    # ==========================================
    # 6. 年齢確認後の北海道
    # ==========================================
    print()
    print("=== 6. 年齢確認後の北海道 ===")
    page.locator("a").filter(
        has_text="北海道"
    ).first.click()
    page.wait_for_timeout(4000)
    print("URL:", page.url)
    print("TITLE:", page.title())
    # ==========================================
    # 7. 北海道赤十字血液センター
    # ==========================================
    print()
    print(
        "=== 7. 北海道赤十字血液センター ==="
    )
    target_card = page.locator(
        "li.mod-list-room__list"
    ).filter(
        has_text="北海道赤十字血液センター"
    ).first
    print(
        "施設カード数:",
        page.locator(
            "li.mod-list-room__list"
        ).filter(
            has_text="北海道赤十字血液センター"
        ).count()
    )
    print()
    print("施設内容:")
    print(
        target_card.inner_text()
    )
    # ==========================================
    # 8. 血漿成分献血確認
    # ==========================================
    print()
    print("=== 8. 血漿成分献血 ===")
    plasma = target_card.locator(
        ".mod-icon-dnt-type-plasma.is-on"
    )
    print(
        "血漿成分献血 is-on:",
        plasma.count()
    )
    # ==========================================
    # 9. 予約する
    # ==========================================
    print()
    print("=== 9. 予約する ===")
    target_reserve = target_card.locator(
        "a"
    ).filter(
        has_text="予約する"
    ).first
    print(
        "予約リンク数:",
        target_card.locator(
            "a"
        ).filter(
            has_text="予約する"
        ).count()
    )
    print()
    print("予約リンクHTML:")
    print(
        target_reserve.evaluate(
            "(el) => el.outerHTML"
        )
    )
    target_reserve.click()
    page.wait_for_timeout(5000)
    # ==========================================
    # 10. 予約詳細画面
    # ==========================================
    print()
    print("==========================================")
    print("=== 10. 予約詳細画面 ===")
    print("==========================================")
    print()
    print("URL:")
    print(page.url)
    print()
    print("TITLE:")
    print(page.title())
    # ==========================================
    # 11. ページ本文
    # ==========================================
    print()
    print("==========================================")
    print("=== 11. PAGE TEXT ===")
    print("==========================================")
    body_text = page.locator(
        "body"
    ).inner_text()
    print(body_text)
    # ==========================================
    # 12. 日付・時間に関係しそうなテキスト
    # ==========================================
    print()
    print("==========================================")
    print("=== 12. 日付・時間関連テキスト ===")
    print("==========================================")
    keywords = [
        "予約",
        "空き",
        "空席",
        "受付",
        "時間",
        "時",
        "分",
        "午前",
        "午後",
        "献血",
        "血漿",
        "日",
        "月",
        "火",
        "水",
        "木",
        "金",
        "土",
        "日曜日",
        "月曜日",
        "火曜日",
        "水曜日",
        "木曜日",
        "金曜日",
        "土曜日"
    ]
    for line in body_text.splitlines():
        line = line.strip()
        if not line:
            continue
        if any(
            keyword in line
            for keyword in keywords
        ):
            print(
                line
            )
    # ==========================================
    # 13. 全リンクの詳細
    # ==========================================
    print()
    print("==========================================")
    print("=== 13. LINK 詳細 ===")
    print("==========================================")
    links = page.locator("a")
    print(
        "リンク総数:",
        links.count()
    )
    for i in range(
        links.count()
    ):
        link = links.nth(i)
        try:
            text = link.inner_text().strip()
        except:
            text = ""
        try:
            href = link.get_attribute(
                "href"
            )
        except:
            href = None
        try:
            class_name = link.get_attribute(
                "class"
            )
        except:
            class_name = None
        try:
            onclick = link.get_attribute(
                "onclick"
            )
        except:
            onclick = None
        if text or href or onclick:
            print()
            print(
                "--------------------------------"
            )
            print(
                "LINK:",
                i
            )
            print(
                "TEXT:",
                text
            )
            print(
                "HREF:",
                href
            )
            print(
                "CLASS:",
                class_name
            )
            print(
                "ONCLICK:",
                onclick
            )
            try:
                print(
                    "OUTERHTML:"
                )
                print(
                    link.evaluate(
                        "(el) => el.outerHTML"
                    )
                )
            except Exception as e:
                print(
                    "HTML取得失敗:",
                    e
                )
    # ==========================================
    # 14. SELECT 詳細
    # ==========================================
    print()
    print("==========================================")
    print("=== 14. SELECT 詳細 ===")
    print("==========================================")
    selects = page.locator(
        "select"
    )
    print(
        "select総数:",
        selects.count()
    )
    for i in range(
        selects.count()
    ):
        sel = selects.nth(i)
        print()
        print(
            "--------------------------------"
        )
        print(
            "SELECT:",
            i
        )
        try:
            print(
                "NAME:",
                sel.get_attribute("name")
            )
            print(
                "ID:",
                sel.get_attribute("id")
            )
            print(
                "VALUE:",
                sel.input_value()
            )
            print(
                "OUTERHTML:"
            )
            print(
                sel.evaluate(
                    "(el) => el.outerHTML"
                )
            )
        except Exception as e:
            print(
                "取得失敗:",
                e
            )
    # ==========================================
    # 15. INPUT 詳細
    # ==========================================
    print()
    print("==========================================")
    print("=== 15. INPUT 詳細 ===")
    print("==========================================")
    inputs = page.locator(
        "input"
    )
    print(
        "input総数:",
        inputs.count()
    )
    for i in range(
        inputs.count()
    ):
        el = inputs.nth(i)
        print()
        print(
            "--------------------------------"
        )
        print(
            "INPUT:",
            i
        )
        try:
            print(
                "TYPE:",
                el.get_attribute("type")
            )
            print(
                "NAME:",
                el.get_attribute("name")
            )
            print(
                "ID:",
                el.get_attribute("id")
            )
            print(
                "VALUE:",
                el.get_attribute("value")
            )
            print(
                "CLASS:",
                el.get_attribute("class")
            )
            print(
                "OUTERHTML:"
            )
            print(
                el.evaluate(
                    "(el) => el.outerHTML"
                )
            )
        except Exception as e:
            print(
                "取得失敗:",
                e
            )
    # ==========================================
    # 16. BUTTON 詳細
    # ==========================================
    print()
    print("==========================================")
    print("=== 16. BUTTON 詳細 ===")
    print("==========================================")
    buttons = page.locator(
        "button"
    )
    print(
        "button総数:",
        buttons.count()
    )
    for i in range(
        buttons.count()
    ):
        el = buttons.nth(i)
        print()
        print(
            "--------------------------------"
        )
        print(
            "BUTTON:",
            i
        )
        try:
            print(
                "TEXT:",
                el.inner_text()
            )
            print(
                "TYPE:",
                el.get_attribute("type")
            )
            print(
                "NAME:",
                el.get_attribute("name")
            )
            print(
                "ID:",
                el.get_attribute("id")
            )
            print(
                "CLASS:",
                el.get_attribute("class")
            )
            print(
                "OUTERHTML:"
            )
            print(
                el.evaluate(
                    "(el) => el.outerHTML"
                )
            )
        except Exception as e:
            print(
                "取得失敗:",
                e
            )
    # ==========================================
    # 17. 時間らしい文字列を含む要素
    # ==========================================
    print()
    print("==========================================")
    print("=== 17. 時間表示らしき要素 ===")
    print("==========================================")
    all_elements = page.locator(
        "body *"
    )
    found = 0
    for i in range(
        all_elements.count()
    ):
        el = all_elements.nth(i)
        try:
            text = el.inner_text().strip()
        except:
            continue
        if not text:
            continue
        # 時刻らしい表記
        if (
            "：" in text
            or ":" in text
            or "午前" in text
            or "午後" in text
        ):
            # あまりにも巨大な親要素は除外
            if len(text) <= 300:
                print()
                print(
                    "ELEMENT:",
                    i
                )
                print(
                    "TEXT:",
                    text
                )
                try:
                    print(
                        "TAG:",
                        el.evaluate(
                            "(e) => e.tagName"
                        )
                    )
                    print(
                        "CLASS:",
                        el.get_attribute(
                            "class"
                        )
                    )
                    print(
                        "ID:",
                        el.get_attribute(
                            "id"
                        )
                    )
                except:
                    pass
                found += 1
                if found >= 100:
                    break
    print()
    print(
        "時間らしい要素:",
        found
    )
    # ==========================================
    # 18. HTMLの一部
    # ==========================================
    print()
    print("==========================================")
    print("=== 18. HTML BODY ===")
    print("==========================================")
    html = page.locator(
        "body"
    ).inner_html()
    print(
        html[:50000]
    )
    print()
    print("==========================================")
    print("=== 19. FINISHED ===")
    print("==========================================")
    browser.close()
