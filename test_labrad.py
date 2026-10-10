from playwright.sync_api import sync_playwright
BASE_URL = "https://www.kenketsu.jp/ReservationHome"
with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page(
        viewport={"width": 1280, "height": 3000},
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
    # テスト用生年月日
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
    # 10. 献血種類と日程の選択
    # ==========================================
    print()
    print("==========================================")
    print("=== 10. 献血種類と日程の選択 ===")
    print("==========================================")
    print()
    print("URL:")
    print(page.url)
    print()
    print("TITLE:")
    print(page.title())
    print()
    print("PAGE TEXT:")
    print(
        page.locator("body").inner_text()
    )
    # ==========================================
    # 11. 血漿（成分献血）を選択
    # ==========================================
    print()
    print("==========================================")
    print("=== 11. 血漿（成分献血）を選択 ===")
    print("==========================================")
    plasma_link = page.locator(
        'a[href="qs-type-plasma"]'
    ).first
    print(
        "血漿リンク数:",
        page.locator(
            'a[href="qs-type-plasma"]'
        ).count()
    )
    print()
    print("血漿リンクHTML:")
    print(
        plasma_link.evaluate(
            "(el) => el.outerHTML"
        )
    )
    print()
    print("血漿をクリックします...")
    plasma_link.click()
    page.wait_for_timeout(3000)
    # ==========================================
    # 12. 血漿選択後の画面
    # ==========================================
    print()
    print("==========================================")
    print("=== 12. 血漿選択後の画面 ===")
    print("==========================================")
    print()
    print("URL:")
    print(page.url)
    print()
    print("TITLE:")
    print(page.title())
    print()
    print("PAGE TEXT:")
    print(
        page.locator("body").inner_text()
    )
    # ==========================================
    # 13. カレンダー関連HTML
    # ==========================================
    print()
    print("==========================================")
    print("=== 13. カレンダー関連 ===")
    print("==========================================")
    calendar_candidates = page.locator(
        "[class*='calendar'], "
        "[id*='calendar'], "
        "[class*='Calendar'], "
        "[id*='Calendar']"
    )
    print(
        "カレンダー候補要素数:",
        calendar_candidates.count()
    )
    for i in range(
        min(calendar_candidates.count(), 50)
    ):
        el = calendar_candidates.nth(i)
        print()
        print(
            "--------------------------------"
        )
        print(
            "CALENDAR CANDIDATE:",
            i
        )
        try:
            print(
                "TAG:",
                el.evaluate(
                    "(e) => e.tagName"
                )
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
                "TEXT:",
                el.inner_text()[:1000]
            )
        except Exception as e:
            print(
                "取得失敗:",
                e
            )
    # ==========================================
    # 14. 日付関連リンク
    # ==========================================
    print()
    print("==========================================")
    print("=== 14. 日付関連リンク ===")
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
        # 日付・時間・予約関連のものを表示
        keywords = [
            "予約",
            "空き",
            "受付",
            "前月",
            "翌月",
            "月",
            "日",
            "午前",
            "午後",
            "時",
            "分"
        ]
        if (
            any(
                k in text
                for k in keywords
            )
            or (
                href
                and (
                    "calendar" in href.lower()
                    or "schedule" in href.lower()
                    or "reservation" in href.lower()
                )
            )
        ):
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
    # 15. SELECT
    # ==========================================
    print()
    print("==========================================")
    print("=== 15. SELECT ===")
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
    # 16. INPUT
    # ==========================================
    print()
    print("==========================================")
    print("=== 16. INPUT ===")
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
    # 17. 「予約」「空き」を含む要素
    # ==========================================
    print()
    print("==========================================")
    print("=== 17. 予約・空き関連要素 ===")
    print("==========================================")
    reservation_elements = page.locator(
        "text=予約"
    )
    print(
        "「予約」を含む要素数:",
        reservation_elements.count()
    )
    for i in range(
        min(
            reservation_elements.count(),
            100
        )
    ):
        el = reservation_elements.nth(i)
        try:
            text = el.inner_text().strip()
            if len(text) <= 500:
                print()
                print(
                    "ELEMENT:",
                    i
                )
                print(
                    "TEXT:",
                    text
                )
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
    # ==========================================
    # 18. 「血漿」を含む要素
    # ==========================================
    print()
    print("==========================================")
    print("=== 18. 血漿関連要素 ===")
    print("==========================================")
    plasma_elements = page.locator(
        "text=血漿"
    )
    print(
        "「血漿」を含む要素数:",
        plasma_elements.count()
    )
    for i in range(
        min(
            plasma_elements.count(),
            100
        )
    ):
        el = plasma_elements.nth(i)
        try:
            text = el.inner_text().strip()
            if len(text) <= 500:
                print()
                print(
                    "ELEMENT:",
                    i
                )
                print(
                    "TEXT:",
                    text
                )
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
    # ==========================================
    # 19. BODY HTML
    # ==========================================
    print()
    print("==========================================")
    print("=== 19. BODY HTML ===")
    print("==========================================")
    html = page.locator(
        "body"
    ).inner_html()
    print(
        html[:60000]
    )
    # ==========================================
    # 20. FINISHED
    # ==========================================
    print()
    print("==========================================")
    print("=== 20. FINISHED ===")
    print("==========================================")
    browser.close()
