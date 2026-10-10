from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    browser = p.chromium.launch()
    page = browser.new_page()
    page.set_default_timeout(20000)
    try:
        # 1. ラブラッドを開く
        page.goto("https://www.kenketsu.jp/ReservationHome")
        page.wait_for_load_state("networkidle")
        # 2. 北海道を選択
        page.locator("a").filter(has_text="北海道").first.click()
        page.wait_for_load_state("networkidle")
        # 3. 献血予約へ進む
        page.get_by_text("献血の予約", exact=True).first.click()
        page.wait_for_load_state("networkidle")
        # 4. 献血予約の開始
        page.get_by_text("献血予約の開始", exact=True).click()
        page.wait_for_load_state("networkidle")
        # 5. 年齢確認（テスト用の仮データ）
        page.locator("#selectedmale input").check(force=True)
        page.locator(
            'select[name="Blooddonationageform:j_id41:j_id43"]'
        ).select_option(label="1990")
        page.locator(
            'select[name="Blooddonationageform:j_id41:j_id46"]'
        ).select_option(label="1")
        page.locator(
            'select[name="Blooddonationageform:j_id41:j_id49"]'
        ).select_option(label="1")
        page.locator(
            "#Blooddonationageform\\:j_id41\\:nextButton"
        ).click(force=True)
        page.wait_for_load_state("networkidle")
        # 6. 年齢確認後、再び北海道を選択
        page.locator("a").filter(has_text="北海道").first.click()
        page.wait_for_load_state("networkidle")
        # 7. 北海道赤十字血液センターのカードを取得
        card = page.locator("li.mod-list-room__list").filter(
            has_text="北海道赤十字血液センター"
        )
        card.get_by_text("予約する", exact=True).click()
        page.wait_for_load_state("networkidle")
        # 8. 血漿（成分献血）を選択
        page.locator('a[href="qs-type-plasma"]').click()
        page.wait_for_timeout(2000)
        print("血漿選択後URL:", page.url)
        page.wait_for_load_state("networkidle")
        page.wait_for_timeout(3000)
        # 9. 必要な情報だけ出力
        print("=== 血漿選択後の画面 ===")
        print("URL:", page.url)
        print("TITLE:", page.title())
        print("\n=== 日付・時刻・空き状況の候補 ===")
        keywords = [
            "09:", "10:", "11:", "予約", "空き",
            "満", "不可", "受付", "月", "日"
        ]
        count = 0
        for a in page.locator("a").all():
            text = (a.inner_text() or "").strip()
            href = a.get_attribute("href") or ""
            if text and any(word in text for word in keywords):
                print(f"{text[:40]} | href={href[:80]}")
                count += 1
                if count >= 50:
                    break
        print("\n=== カレンダー関連要素 ===")
        elements = page.locator(
            '[class*="calendar"], [id*="calendar"], '
            '[class*="reserve"], [class*="disable"]'
        )
        for i in range(min(elements.count(), 25)):
            el = elements.nth(i)
            cls = el.get_attribute("class") or ""
            txt = (el.inner_text() or "").strip()
            if cls or txt:
                print(f"class={cls[:100]} | text={txt[:70]}")
    except Exception as e:
        print("ERROR:", repr(e))
        print("URL at error:", page.url)
        print("TITLE at error:", page.title())
        raise
    finally:
        browser.close()
