import json
import math
import shutil
import textwrap
from datetime import datetime, timezone
from pathlib import Path

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont


ROOT = Path(__file__).resolve().parents[4]
WORK = Path(__file__).resolve().parent
ASSETS = WORK / "assets"
ASSETS.mkdir(exist_ok=True)

SLUG = "okx-empfehlungscode-bonusok-deutschland"
PUBLIC_URL = f"https://cryptoved.github.io/Partner-codes/{SLUG}/"
REFERRAL_URL = "https://www.okx.com/join/BONUSOK"
PROMO_CODE = "BONUSOK"
QR_SOURCE = ROOT / "exchanges" / "OKX" / "outputs" / "qr-code-BONUSOK.png"

FONT_REGULAR = "C:/Windows/Fonts/segoeui.ttf"
FONT_BOLD = "C:/Windows/Fonts/segoeuib.ttf"
FONT_SEMIBOLD = "C:/Windows/Fonts/seguisb.ttf"


def font(path, size):
    fallback = FONT_BOLD if "b" in path.lower() else FONT_REGULAR
    return ImageFont.truetype(path if Path(path).exists() else fallback, size=size)


def decode_qr(path):
    raw = np.fromfile(str(path), dtype=np.uint8)
    img = cv2.imdecode(raw, cv2.IMREAD_COLOR)
    if img is None:
        return ""
    detector = cv2.QRCodeDetector()
    value, _, _ = detector.detectAndDecode(img)
    return value


def paste_qr(base, box, qr_path):
    qr = Image.open(qr_path).convert("RGB")
    size = min(box[2] - box[0], box[3] - box[1])
    qr = qr.resize((size, size), Image.Resampling.NEAREST)
    x = box[0] + ((box[2] - box[0]) - size) // 2
    y = box[1] + ((box[3] - box[1]) - size) // 2
    base.paste(qr, (x, y))
    return [x, y, x + size, y + size]


def rounded_rect(draw, xy, radius, fill, outline=None, width=1):
    draw.rounded_rectangle(xy, radius=radius, fill=fill, outline=outline, width=width)


def wrap_text(draw, text, fnt, max_width):
    words = text.split()
    lines = []
    line = ""
    for word in words:
        test = word if not line else f"{line} {word}"
        if draw.textbbox((0, 0), test, font=fnt)[2] <= max_width:
            line = test
        else:
            if line:
                lines.append(line)
            line = word
    if line:
        lines.append(line)
    return lines


def draw_wrapped(draw, text, xy, fnt, fill, max_width, line_gap=8):
    x, y = xy
    lines = wrap_text(draw, text, fnt, max_width)
    max_measured = 0
    for line in lines:
        bbox = draw.textbbox((x, y), line, font=fnt)
        max_measured = max(max_measured, bbox[2] - bbox[0])
        draw.text((x, y), line, font=fnt, fill=fill)
        y += (bbox[3] - bbox[1]) + line_gap
    return y, max_measured, lines


def build_background(w, h):
    img = Image.new("RGB", (w, h), "#07100e")
    px = img.load()
    for y in range(h):
        for x in range(w):
            gx = x / w
            gy = y / h
            r = int(5 + 16 * gx + 12 * (1 - gy))
            g = int(14 + 34 * gx + 18 * (1 - gy))
            b = int(18 + 30 * (1 - gx) + 10 * gy)
            px[x, y] = (r, g, b)
    draw = ImageDraw.Draw(img, "RGBA")

    horizon = 505
    rng = np.random.default_rng(31)
    for i in range(28):
        x = int(i * 58 + rng.integers(-18, 20))
        bw = int(rng.integers(28, 68))
        bh = int(rng.integers(120, 430))
        y = horizon - bh
        color = (12, 28, 35, 175)
        draw.rectangle([x, y, x + bw, horizon + 35], fill=color)
        for wy in range(y + 18, horizon - 8, 38):
            if rng.random() > 0.35:
                draw.rectangle([x + 7, wy, x + bw - 8, wy + 3], fill=(96, 220, 146, 60))
    draw.rectangle([0, horizon, w, h], fill=(2, 8, 8, 105))

    # Trading desk and monitors
    draw.rounded_rectangle([500, 290, 975, 620], radius=24, fill=(6, 18, 18, 210), outline=(70, 255, 122, 90), width=2)
    draw.rectangle([530, 325, 945, 565], fill=(5, 13, 14, 225))
    for i in range(8):
        y = 360 + i * 22
        points = []
        for x in range(550, 925, 24):
            points.append((x, y + math.sin((x + i * 31) / 31) * 16 + rng.integers(-3, 4)))
        draw.line(points, fill=(62, 255, 112, 150), width=2)
    for i in range(20):
        x = 560 + i * 18
        top = 505 - int(abs(math.sin(i * 0.71)) * 80)
        draw.rectangle([x, top, x + 7, 525], fill=(68, 255, 120, 80))
    draw.rounded_rectangle([1040, 260, 1240, 600], radius=18, fill=(5, 18, 19, 190), outline=(255, 198, 91, 80), width=2)
    for i, name in enumerate(["MiCA", "X-Perps", "Agent", "SEPA", "Risk"]):
        y = 306 + i * 48
        draw.text((1068, y), name, font=font(FONT_BOLD, 22), fill=(230, 255, 236, 150))
        draw.line([1145, y + 14, 1214, y + 14], fill=(63, 255, 122, 115), width=3)

    # Frankfurt-ish signal line
    draw.line([(1090, 138), (1130, 138), (1146, 82), (1168, 198), (1188, 138), (1244, 138)], fill=(255, 220, 130, 120), width=3)
    img = img.filter(ImageFilter.GaussianBlur(0.25))
    return img


def build_hero():
    w, h = 1600, 900
    img = build_background(w, h).convert("RGBA")
    draw = ImageDraw.Draw(img, "RGBA")
    draw.rectangle([0, 0, w, h], fill=(0, 0, 0, 35))

    text_panel = [84, 74, 870, 790]
    qr_card = [1034, 108, 1518, 786]
    qr_box = [1110, 190, 1442, 522]
    code_panel = [116, 690, 650, 810]

    rounded_rect(draw, text_panel, 28, (0, 0, 0, 164), (72, 255, 121, 105), 2)
    draw.text((124, 112), "DEUTSCHER GUIDE - OKX", font=font(FONT_BOLD, 30), fill=(92, 255, 108, 255))
    title = "OKX Empfehlungscode BONUSOK"
    y = 162
    for line in ["OKX Empfehlungscode", "BONUSOK"]:
        draw.text((124, y), line, font=font(FONT_BOLD, 68), fill=(255, 255, 255, 255))
        y += 78
    sub = "MiCA, KYC, Campaign Center, Agent Trade Kit, X-Perps und Risikocheck vor der ersten Einzahlung."
    y, sub_w, sub_lines = draw_wrapped(draw, sub, (124, 340), font(FONT_REGULAR, 34), (232, 238, 236, 242), 650, 8)
    chips = ["MiCA & Deutschland", "Agent Trade Kit", "X-Perps", "Futures Cool-off"]
    cx, cy = 124, y + 28
    chip_font = font(FONT_REGULAR, 25)
    for chip in chips:
        tw = draw.textbbox((0, 0), chip, font=chip_font)[2]
        rounded_rect(draw, [cx, cy, cx + tw + 34, cy + 48], 22, (248, 255, 250, 238), (86, 255, 91, 255), 3)
        draw.text((cx + 17, cy + 9), chip, font=chip_font, fill=(18, 34, 29, 255))
        cx += tw + 48
        if cx > 695:
            cx, cy = 124, cy + 62

    rounded_rect(draw, code_panel, 18, (248, 255, 250, 246), (86, 255, 91, 255), 3)
    draw.text((148, 716), "EMPFEHLUNGSCODE", font=font(FONT_REGULAR, 22), fill=(75, 87, 80, 255))
    draw.text((148, 744), PROMO_CODE, font=font(FONT_BOLD, 48), fill=(5, 22, 18, 255))

    rounded_rect(draw, qr_card, 44, (252, 255, 252, 250), (86, 255, 91, 255), 5)
    rounded_rect(draw, [1088, 162, 1464, 546], 24, (255, 255, 255, 255), (133, 255, 130, 255), 3)
    placed_qr = paste_qr(img, qr_box, QR_SOURCE)
    note = "Nur scannen, wenn OKX in deinem Land und Produktkonto verfügbar ist."
    draw_wrapped(draw, note, (1092, 594), font(FONT_BOLD, 25), (18, 25, 22, 255), 360, 4)
    draw.text((1092, 704), "okx.com/join/BONUSOK", font=font(FONT_REGULAR, 27), fill=(52, 60, 57, 255))

    out = ASSETS / "okx-bonusok-german-empfehlungscode-hero.png"
    img.convert("RGB").save(out, quality=96)
    return out, {
        "canvas": [w, h],
        "text_panel": text_panel,
        "qr_card": qr_card,
        "qr_box": qr_box,
        "placed_qr": placed_qr,
        "code_panel": code_panel,
        "subtitle_max_width": sub_w,
        "subtitle_lines": sub_lines,
    }


def build_compact_qr():
    w, h = 560, 640
    img = Image.new("RGB", (w, h), "#f7fff9")
    draw = ImageDraw.Draw(img, "RGBA")
    draw.rounded_rectangle([18, 18, w - 18, h - 18], radius=32, fill=(255, 255, 255, 255), outline=(74, 239, 92, 255), width=4)
    draw.text((56, 52), "OKX Empfehlungscode", font=font(FONT_BOLD, 34), fill=(9, 28, 21, 255))
    draw.text((56, 92), PROMO_CODE, font=font(FONT_BOLD, 46), fill=(0, 13, 10, 255))
    qr_card = [82, 156, 478, 552]
    qr_box = [122, 196, 438, 512]
    draw.rounded_rectangle(qr_card, radius=24, fill=(255, 255, 255, 255), outline=(120, 255, 120, 255), width=3)
    placed = paste_qr(img, qr_box, QR_SOURCE)
    draw.text((86, 574), "Erst Region, KYC und Risiko prüfen.", font=font(FONT_REGULAR, 24), fill=(53, 63, 58, 255))
    out = ASSETS / "okx-bonusok-german-compact-qr.png"
    img.save(out, quality=96)
    return out, {"canvas": [w, h], "qr_card": qr_card, "qr_box": qr_box, "placed_qr": placed}


ARTICLE = """
<p class="lead">Der OKX Empfehlungscode <strong>BONUSOK</strong> ist nur dann sinnvoll, wenn du ihn wie ein Trader nutzt: erst Verfügbarkeit und KYC prüfen, dann die Bedingungen im Campaign Center ansehen, danach klein testen und erst später Volumen aufbauen. Diese Seite ist kein Versprechen auf Gewinn und keine Aufforderung, regionale Regeln zu umgehen. Sie ist ein deutscher Leitfaden für Nutzer in Deutschland, Österreich, der Schweiz und der deutschsprachigen Diaspora, die OKX, MiCA, Web3 Wallet, Futures, X-Perps und Trading-Automation nüchtern vergleichen möchten.</p>

<h2>Kurze Antwort: Was ist der OKX Empfehlungscode BONUSOK?</h2>
<p><strong>BONUSOK</strong> ist ein Empfehlungscode, den du bei der Registrierung über den offiziellen OKX-Link verwenden kannst. Ob ein Bonus, eine Prämie, ein Handelsvorteil oder eine Aufgabe sichtbar wird, hängt nicht allein vom Code ab. Entscheidend sind dein Land, dein Wohnsitz, dein KYC-Status, dein Gerät, die aktuelle Kampagne, dein Kontotyp und die Frage, ob das jeweilige Produkt in deiner Region angeboten wird. Deshalb sollte ein ernsthafter Trader nicht blind einzahlen, sondern zuerst im Konto kontrollieren, ob der Code wirklich angewendet wurde und welche Bedingungen im Campaign Center angezeigt werden.</p>
<p>Für Deutschland ist 2026 besonders wichtig, dass OKX seine europäischen Leistungen über eine MiCA-lizenzierte Struktur kommuniziert. Das ist für Suchende nach „OKX Deutschland“, „OKX Empfehlungscode“ oder „OKX Bonuscode“ relevant, weil viele europäische Nutzer nach dem MiCA-Stichtag wissen wollen, welche Plattform reguliert auftritt, welche Daten für Transfers benötigt werden und wie Produkte wie Spot, Earn, Futures oder Web3 Wallet tatsächlich freigeschaltet sind. Diese Seite legt deshalb mehr Gewicht auf Prüfung, Risiko und Workflow als auf eine aggressive Bonusformulierung.</p>

<h2>Warum dieser Guide für aktive Trader anders aufgebaut ist</h2>
<p>Viele Referral-Seiten wiederholen nur einen Code. Das hilft einem aktiven Trader kaum. Wer mehrmals pro Woche handelt, braucht andere Informationen: Wie prüfe ich Gebühren? Wie vermeide ich falsche Ordertypen? Was passiert mit Bots, Copy Trading oder API-Zugriffen, wenn ich eine Cool-off-Funktion aktiviere? Welche neuen Märkte sind nur interessant, wenn Liquidität, Spread und Produktverfügbarkeit passen? Genau hier liegen die stärkeren Referral-Chancen: Ein Nutzer, der versteht, warum er OKX testen will, wird eher KYC abschließen, eine kleine Einzahlung machen, einen ersten Spot-Trade durchführen und später aktiv bleiben.</p>
<p>Die aktuellen OKX-Hooks für Deutschland und Europa sind aus meiner Sicht: MiCA-Positionierung, neue X-Perps und Equity-X-Perps, Agent Trade Kit, Campaign Center, Futures Cool-off Period, Web3 Wallet und saubere EUR/SEPA-orientierte Onboarding-Fragen. Das ist stärker als ein reiner „Bonus bis zu“-Text, weil es Suchende mit echtem Handelsinteresse anspricht.</p>

<h2>Deutschland, MiCA und EEA: Erst rechtlich denken, dann handeln</h2>
<p>Wenn du aus Deutschland kommst, ist die erste Frage nicht „Wie hoch ist der Bonus?“, sondern „Welche OKX-Einheit bedient mich, welche Produkte sind verfügbar, welche Regeln gelten für Transfers und welche Risikohinweise muss ich verstehen?“ OKX beschreibt seine europäische Struktur als MiCA-lizenziert und verweist auf OKX Europe Limited. Für Nutzer bedeutet das nicht, dass jedes Produkt automatisch für jeden Account verfügbar ist. Es bedeutet aber, dass die Plattform in Europa stärker über regulierte Prozesse, getrennte Kundengelder, Proof of Reserves, Beschwerden und MiCA-konforme Informationen spricht.</p>
<p>Für aktive Trader ist das relevant, weil regulatorische Klarheit ein Teil des Risikomanagements ist. Wenn du regelmäßig handelst, willst du nicht nur wissen, ob eine App funktioniert. Du willst wissen, ob Einzahlung, Auszahlung, KYC, Steuerdokumentation, Produktzugang und Kontosicherheit zu deinem Wohnsitz passen. Nutzer in Österreich, der Schweiz, Luxemburg, Belgien oder der deutschsprachigen Diaspora sollten dieselbe Logik anwenden: Nicht aus Gewohnheit registrieren, sondern erst prüfen, welche OKX-Version und welche Produktliste im eigenen Land gilt.</p>

<h2>Aktuelle OKX-Neuigkeiten, die für deutsche Trader interessant sind</h2>
<p>Auf der OKX-Announcements-Seite tauchten am 10. Juli 2026 neue Hinweise zu PENGUUSD Expiry X-Perps, AMDUSD Equity X-Perp, weiteren Equity-Futures und SLX/USDT Spot Trading auf. Am 9. Juli kamen XPLUSD, ALGOUSD und weitere Equity-X-Perps hinzu, und am 8. Juli wurden unter anderem INJUSD, ICPUSD und RENDERUSD X-Perps genannt. Für einen deutschen Trader ist die wichtige Schlussfolgerung nicht: „Alles sofort handeln.“ Die wichtige Schlussfolgerung lautet: OKX baut aktiv Märkte aus, aber neue Produkte brauchen immer eine eigene Prüfung von Liquidität, Spread, Hebel, Laufzeit, Finanzierung, Gebühren und regionaler Freischaltung.</p>
<p>Gerade X-Perps und Equity-X-Perps können für erfahrene Trader interessant sein, weil sie Exposure auf Märkte außerhalb klassischer Krypto-Spots abbilden können. Gleichzeitig sind sie komplexer als ein einfacher BTC- oder ETH-Spotkauf. Du solltest jedes neue Produkt erst im Demo- oder Kleinstbetrag-Modus verstehen: Was ist die Indexbasis? Welche Handelszeiten gelten? Wie wird liquidiert? Welche Gebühren gelten? Wie hoch ist der effektive Spread? Gibt es ein Ereignisrisiko, wenn eine Aktie stark schwankt? Wer diese Fragen nicht beantworten kann, sollte den Referral-Code nicht als Startschuss zum Hebelhandel verstehen.</p>

<h2>Agent Trade Kit: Warum AI-Trading nur mit Sicherheitsregeln Sinn ergibt</h2>
<p>Das Agent Trade Kit ist für aktive Nutzer spannend, weil es die Idee verfolgt, KI-Assistenten oder lokale Tools mit Handelsfunktionen zu verbinden. Die öffentlich sichtbare GitHub-Dokumentation beschreibt unter anderem MCP-Server, CLI-Pakete, Markt- und Orderwerkzeuge, technische Indikatoren, Algo-Orders und lokale API-Nutzung. Für deutschsprachige Trader klingt das modern, aber es ist kein Autopilot für sichere Gewinne. Es ist eher ein Werkzeugkasten, der nur so gut ist wie deine Schlüsselverwaltung, Positionsgröße, Limits und Kontrollroutine.</p>
<p>Wenn du OKX wegen Agent Trade Kit testest, solltest du API-Schlüssel nie leichtfertig freigeben. Starte mit read-only, wenn möglich. Nutze IP-Beschränkungen, kleine Konten, klare Orderlimits, kein unbegrenztes Withdraw-Recht, keine unbekannten Skills und kein Copy-Paste fremder Strategien. Ein guter Workflow ist: erst Marktdaten lesen, dann Paper-Logik prüfen, dann eine Mini-Order, dann Logging und erst später Wiederholung. Das macht die Seite für aktive Trader wertvoller, weil sie nicht nur auf den Code verweist, sondern den realen Kontrollbedarf erklärt.</p>

<h2>Futures Cool-off Period: Eine unterschätzte Schutzfunktion</h2>
<p>OKX kündigte für den 7. Juli 2026 eine Erweiterung der Futures Cool-off Period an. Nach der Beschreibung betrifft die erweiterte Sperre nicht nur Web und App, sondern auch REST API, WebSocket, Drittanbieter-Autorisierung, Broker OAuth, Agent Trade Kit, Strategy Orders, Copy Trading, Trading Bots und weitere Kanäle. Das ist für aktive Trader wichtig, weil echte Risikokontrolle nicht nur im Frontend passieren darf. Wenn ein Bot oder ein API-Skript weiter Positionen öffnet, obwohl du eigentlich stoppen wolltest, ist der Schutz unvollständig.</p>
<p>Die Cool-off-Funktion ist trotzdem keine Versicherung. Sie verhindert nicht automatisch Verluste, sie garantiert keine bessere Entscheidung und sie ersetzt keinen Stop-Loss. Aber als Verhaltensbremse kann sie wertvoll sein, wenn du merkst, dass du nach Verlusten überhandelst, nachts impulsiv Positionen öffnest oder Bots zu aggressiv laufen lässt. Für einen deutschen OKX-Einsteiger gehört diese Funktion deshalb in die erste Checkliste, noch bevor größere Futures-Positionen eröffnet werden.</p>

<h2>Wie du BONUSOK sauber prüfst</h2>
<p>Öffne den offiziellen Link, registriere dich nur mit deinen echten Daten, wähle dein tatsächliches Wohnsitzland und schließe KYC nur ab, wenn OKX für dich und das gewünschte Produkt verfügbar ist. Danach prüfst du im Konto, ob der Empfehlungscode <strong>BONUSOK</strong> sichtbar ist oder ob die Registrierung über den Link korrekt erkannt wurde. Suche anschließend im Campaign Center nach Aufgaben, Fristen, Mindesteinzahlung, Mindesthandelsvolumen, Ausschlüssen, Produktbedingungen und Ablaufdatum. Wenn dort nichts angezeigt wird, solltest du nicht einfach einzahlen, nur weil eine externe Seite einen Bonus erwähnt.</p>
<p>Bei jedem Bonus gilt: „bis zu“ ist nicht „garantiert“. Viele Rewards hängen von Aufgaben, Volumen, Zeitfenstern, Produktzugang, KYC, Region und Kontostatus ab. Wenn du ohnehin aktiv handeln willst, kann ein sauber angewendeter Code ein Zusatz sein. Wenn du nur wegen einer Prämie handelst, ist das meist die falsche Motivation. Gute Trader optimieren Kosten und Prozesse, aber sie handeln nicht, nur um eine Aufgabe zu erfüllen.</p>

<h2>30-Minuten-Checkliste vor der ersten Einzahlung</h2>
<h3>Kontosicherheit und KYC</h3>
<p>Aktiviere 2FA, prüfe Anti-Phishing-Code, sichere deine E-Mail, verwende ein starkes Passwort und speichere Backup-Codes offline. KYC sollte mit echten Daten erfolgen. Keine geliehenen Accounts, keine falschen Adressen, keine VPN-Tricks, keine Dokumente anderer Personen. Wer solche Umgehungen nutzt, riskiert Sperren, eingefrorene Gelder und Probleme bei Auszahlungen.</p>
<h3>Produktzugang und Gebühren</h3>
<p>Kontrolliere, ob Spot, Convert, Earn, Futures, X-Perps, Options, Bots, Copy Trading und Web3 Wallet in deinem Konto tatsächlich verfügbar sind. Vergleiche Maker- und Taker-Gebühren, Funding, Spread und Auszahlungsgebühren. Für deutsche Nutzer sind EUR-Einzahlung, SEPA-Verfügbarkeit, Travel-Rule-Daten und Steuerdokumentation ebenso wichtig wie die reine Trading-Oberfläche.</p>
<h3>Erster Testtrade</h3>
<p>Starte mit einem Betrag, dessen Verlust dich nicht stört. Kaufe nicht sofort exotische neue Listings. Teste erst einen liquiden Markt, die Ordermaske, Limit-Order, Stop-Funktion, Gebührenanzeige, Auszahlungsadresse und Portfolio-Übersicht. Notiere, wie lange Einzahlung und Auszahlung dauern. Ein aktiver Trader sollte zuerst Prozesse testen, nicht Rendite jagen.</p>

<h2>Welche OKX-Produkte können aktive Trader anziehen?</h2>
<p>Für deutsche und europäische Suchende sind mehrere Produktcluster interessant. Spot und Convert sind für den Einstieg wichtig, weil sie einfacher zu verstehen sind. Futures und X-Perps sprechen erfahrenere Nutzer an, die Hedging, taktische Trades oder breiteres Exposure suchen. Trading Bots und Copy Trading können für Nutzer interessant sein, die Strategien strukturieren möchten, brauchen aber Grenzen und Monitoring. Web3 Wallet ist relevant für Nutzer, die zwischen zentraler Börse, DEX, DeFi und Self-Custody wechseln wollen. Campaign Center und Rewards sind eher Ergänzungen, nicht die Grundlage der Entscheidung.</p>
<p>Der stärkste Referral-Winkel für aktive Trader ist deshalb ein kombinierter Workflow: reguliertes europäisches Onboarding, sauberer Code, kleine erste Einzahlung, produktbezogene Checkliste, Sicherheitsfunktionen, später erst Automatisierung. So entsteht eher ein langfristiger Trader als ein einmaliger Bonusjäger.</p>

<h2>Deutschland-spezifischer Workflow: EUR, SEPA, Historie und Steuern</h2>
<p>Für deutsche Nutzer ist ein Exchange-Test erst vollständig, wenn auch die langweiligen Teile funktionieren. Prüfe vor größerem Volumen, ob du EUR sauber einzahlen kannst, ob SEPA oder andere Zahlungswege in deinem Konto sichtbar sind, welche Bankdaten verlangt werden, wie schnell eine kleine Testeinzahlung ankommt und ob Auszahlungen ohne manuelle Überraschungen möglich sind. Achte außerdem darauf, welche Angaben bei Krypto-Transfers wegen der Travel Rule verlangt werden. Wenn Sender- oder Empfängerdaten fehlen, kann ein Transfer verzögert oder abgelehnt werden. Das ist kein Marketingdetail, sondern ein operatives Risiko für jeden, der aktiv zwischen Wallet, Börse und Bankkonto arbeitet.</p>
<p>Ebenso wichtig ist die Dokumentation. Exportiere Transaktionshistorie, Trades, Einzahlungen, Auszahlungen, Rewards, Funding, Gebühren und mögliche Earn-Erträge regelmäßig. Wer erst am Jahresende versucht, alles aus mehreren Plattformen zu rekonstruieren, verliert Zeit und macht leichter Fehler. Ein guter deutscher Trader behandelt Reporting wie Risikomanagement: monatlicher Export, klare Wallet-Labels, keine Vermischung fremder Gelder, keine privaten Notizen als einzige Datenquelle. Wenn du den Empfehlungscode BONUSOK nutzt, sollte der erste Monat deshalb nicht nur aus Trades bestehen, sondern auch aus einem Test, ob du deine Historie später steuerlich nachvollziehen kannst.</p>
<p>Für die deutschsprachige Diaspora gilt dasselbe Prinzip mit lokalen Abweichungen. Ein Nutzer in der Schweiz, Österreich, Luxemburg oder außerhalb Europas sollte nicht einfach den deutschen MiCA-Teil übernehmen, sondern die eigene Plattformversion, lokale Steuerlogik, KYC-Anforderungen und Produktliste prüfen. Der Wert dieses Guides liegt darin, dass du eine robuste Reihenfolge bekommst: Verfügbarkeit, Identität, Zahlungsweg, kleine Order, Auszahlungsprobe, Historie, dann erst Strategie und Volumen.</p>

<h2>Häufige Fehler deutscher OKX-Einsteiger</h2>
<p>Der erste Fehler ist, nur nach „OKX Bonuscode“ zu suchen und die Bedingungen nicht zu lesen. Der zweite Fehler ist, ein neues X-Perp- oder Futures-Produkt zu handeln, ohne Index, Hebel, Liquidation und Funding zu verstehen. Der dritte Fehler ist, API-Schlüssel für AI-Tools zu breit freizugeben. Der vierte Fehler ist, aus steuerlicher Sicht keine Historie zu exportieren. Der fünfte Fehler ist, die Travel Rule und Empfängerdaten bei Transfers zu ignorieren. Der sechste Fehler ist, Verluste durch mehr Hebel zurückholen zu wollen.</p>
<p>Diese Fehler sind vermeidbar. Nutze OKX erst als System, nicht als Casino: Watchlist, Gebührencheck, kleine Orders, Auszahlungsprobe, Risikolimit, Cool-off-Regel, Monatsreview. Wenn du nach 30 Tagen noch weißt, welche Strategie funktioniert und welche nicht, bist du näher an einem echten aktiven Trader als jemand, der nur einem Bonus hinterherläuft.</p>

<h2>Für wen ist OKX mit BONUSOK geeignet?</h2>
<p>Geeignet ist OKX eher für Nutzer, die bereit sind, KYC und regionale Verfügbarkeit sauber zu prüfen, eine moderne Börse mit Web3- und Trading-Funktionen testen wollen und Risikoregeln ernst nehmen. Besonders interessant kann es für deutschsprachige Nutzer sein, die nach MiCA-konformer europäischer Struktur, Proof-of-Reserves-Kommunikation, Spotmärkten, neuen X-Perps, Agent-Tools und einem strukturierten Onboarding suchen.</p>
<p>Nicht geeignet ist es für Menschen, die in einem nicht unterstützten Land wohnen, falsche Angaben machen wollen, Verluste nicht verkraften können, Hebel nicht verstehen oder glauben, ein Empfehlungscode garantiere Profit. Wenn du diese Risiken ernst nimmst, kann der Code <strong>BONUSOK</strong> ein sauberer Einstiegspunkt sein. Wenn nicht, ist die beste Entscheidung oft: erst lernen, später handeln.</p>

<h2>FAQ zum OKX Empfehlungscode in Deutschland</h2>
<p><strong>Ist BONUSOK ein offizieller OKX-Code?</strong> BONUSOK ist der in diesem Projekt genutzte Empfehlungscode mit dem offiziellen Referral-Link. Prüfe im OKX-Konto, ob der Code oder die Kampagne nach der Registrierung sichtbar ist.</p>
<p><strong>Gibt es einen garantierten Bonus?</strong> Nein. Prämien können abhängig von Region, KYC, Aufgaben, Fristen und Kampagnen sein. Lies immer die Bedingungen im Konto.</p>
<p><strong>Kann ich OKX aus Deutschland nutzen?</strong> OKX kommuniziert eine MiCA-lizenzierte europäische Struktur. Trotzdem musst du in deinem Konto prüfen, welche Produkte für deinen Wohnsitz und Status verfügbar sind.</p>
<p><strong>Sollte ich sofort Futures handeln?</strong> Nein. Futures, X-Perps und Equity-X-Perps sind für erfahrene Nutzer. Starte mit Verständnis, kleinen Beträgen und klarer Verlustgrenze.</p>
<p><strong>Warum steht hier so viel über Risiko?</strong> Weil aktive Trader nicht durch Werbung entstehen, sondern durch kontrollierte Prozesse. Ein guter Referral-Klick ist ein informierter Klick.</p>
"""


def build_html():
    title = "OKX Empfehlungscode BONUSOK: Deutscher Guide für aktive Trader"
    description = "OKX Empfehlungscode BONUSOK auf Deutsch: MiCA, KYC, Campaign Center, Agent Trade Kit, X-Perps, Futures Cool-off und Risikocheck für Deutschland und deutschsprachige Trader."
    hero = "assets/okx-bonusok-german-empfehlungscode-hero.png"
    compact = "assets/okx-bonusok-german-compact-qr.png"
    html = f"""<!doctype html>
<html lang="de-DE">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{title}</title>
  <meta name="description" content="{description}">
  <meta name="robots" content="index,follow,max-image-preview:large">
  <link rel="canonical" href="{PUBLIC_URL}">
  <meta property="og:type" content="article">
  <meta property="og:title" content="{title}">
  <meta property="og:description" content="{description}">
  <meta property="og:url" content="{PUBLIC_URL}">
  <meta property="og:image" content="{PUBLIC_URL}{hero}">
  <meta property="og:image:alt" content="Deutscher OKX Empfehlungscode BONUSOK Guide mit Trading-Desk, MiCA, KYC, Agent Trade Kit, X-Perps und realem QR-Code.">
  <style>
    :root {{ color-scheme: dark; --bg:#07100e; --panel:#0e1714; --line:#285b39; --green:#65ff6c; --text:#edf7f0; --muted:#b9c8bf; --gold:#ffd36f; }}
    * {{ box-sizing:border-box; }}
    body {{ margin:0; background:var(--bg); color:var(--text); font-family: Segoe UI, Arial, sans-serif; line-height:1.65; }}
    a {{ color:#7dff83; }}
    .wrap {{ width:min(1120px, calc(100% - 32px)); margin:0 auto; }}
    header {{ padding:28px 0 10px; border-bottom:1px solid rgba(101,255,108,.18); }}
    .eyebrow {{ color:var(--green); font-weight:800; letter-spacing:.02em; text-transform:uppercase; font-size:.9rem; }}
    h1 {{ font-size:clamp(2.1rem, 5vw, 4.9rem); line-height:1.02; margin:.35em 0 .22em; max-width:980px; letter-spacing:0; }}
    .dek {{ max-width:850px; color:var(--muted); font-size:1.16rem; margin:0 0 20px; }}
    .hero {{ width:100%; display:block; border:1px solid rgba(101,255,108,.34); border-radius:8px; margin:24px 0 12px; background:#111; }}
    .caption {{ color:var(--muted); font-size:.95rem; margin:0 0 28px; }}
    .cta-row {{ display:flex; flex-wrap:wrap; gap:12px; margin:20px 0 8px; align-items:center; }}
    .btn {{ display:inline-flex; align-items:center; justify-content:center; min-height:46px; padding:10px 18px; border-radius:8px; background:#ecfff0; color:#07100e; font-weight:800; text-decoration:none; border:2px solid var(--green); }}
    .ghost {{ background:transparent; color:var(--green); }}
    main {{ display:grid; grid-template-columns:minmax(0,1fr) 300px; gap:34px; padding:22px 0 56px; }}
    article {{ min-width:0; }}
    article h2 {{ margin:2.1rem 0 .7rem; font-size:clamp(1.45rem, 2.6vw, 2.15rem); line-height:1.18; letter-spacing:0; }}
    article h3 {{ margin:1.45rem 0 .45rem; font-size:1.22rem; color:#dfffe2; }}
    article p {{ margin:.8rem 0; color:#e2ede7; font-size:1.04rem; }}
    .lead {{ font-size:1.16rem; color:#f5fff7; border-right:4px solid var(--green); padding:14px 18px; background:rgba(101,255,108,.07); border-radius:8px; }}
    aside {{ position:sticky; top:18px; align-self:start; padding:18px; border:1px solid rgba(101,255,108,.28); border-radius:8px; background:rgba(11,23,18,.92); }}
    aside img {{ width:100%; border-radius:8px; background:white; display:block; }}
    aside p {{ color:var(--muted); font-size:.94rem; margin:12px 0 0; }}
    .notice {{ margin:26px 0; padding:18px; border:1px solid rgba(255,211,111,.45); border-radius:8px; background:rgba(255,211,111,.08); color:#fff5d6; }}
    .sources {{ padding:18px; border-top:1px solid rgba(101,255,108,.24); color:var(--muted); }}
    footer {{ border-top:1px solid rgba(101,255,108,.2); padding:24px 0 36px; color:var(--muted); }}
    @media (max-width: 860px) {{
      main {{ display:block; }}
      aside {{ position:static; margin:22px 0; }}
      h1 {{ font-size:2.42rem; }}
      .wrap {{ width:min(100% - 22px, 1120px); }}
    }}
  </style>
  <script type="application/ld+json">{{
    "@context":"https://schema.org",
    "@type":"Article",
    "headline":"{title}",
    "inLanguage":"de-DE",
    "datePublished":"2026-07-10",
    "dateModified":"2026-07-10",
    "mainEntityOfPage":"{PUBLIC_URL}",
    "image":"{PUBLIC_URL}{hero}"
  }}</script>
</head>
<body>
  <header>
    <div class="wrap">
      <div class="eyebrow">Deutschland / EEA / Active Trader Guide</div>
      <h1>OKX Empfehlungscode BONUSOK für Deutschland</h1>
      <p class="dek">Ein deutscher, compliance-bewusster Leitfaden für OKX, MiCA, KYC, Campaign Center, Agent Trade Kit, X-Perps, Futures Cool-off und den ersten kontrollierten Trade.</p>
      <div class="cta-row">
        <a class="btn" href="{REFERRAL_URL}" rel="sponsored nofollow">OKX mit BONUSOK prüfen</a>
        <a class="btn ghost" href="#checkliste">Checkliste lesen</a>
      </div>
      <img class="hero" src="{hero}" alt="Deutscher OKX Empfehlungscode BONUSOK Guide: moderner Trading Desk in Europa, MiCA und Deutschland, KYC, Campaign Center, Agent Trade Kit, X-Perps, Futures Cool-off Period, Web3 Wallet, Trading Bots, Copy Trading, AI Trading und realer QR-Code für OKX BONUSOK.">
      <p class="caption">Referral-Hinweis: Wenn du dich über diesen Link registrierst, können wir eine Provision erhalten. Der Code garantiert keinen Gewinn und keine bestimmte Prämie.</p>
    </div>
  </header>
  <main class="wrap">
    <article>
      <div class="notice"><strong>Wichtige Einschränkung:</strong> Nutze OKX und den Code BONUSOK nur, wenn OKX und das gewünschte Produkt in deinem Wohnsitzland offiziell verfügbar sind. Keine VPN-Umgehung, keine falschen KYC-Daten, keine geliehenen Konten.</div>
      {ARTICLE}
      <section class="sources">
        <h2>Quellen und aktuelle OKX-Hooks</h2>
        <p>Geprüft am 10. Juli 2026: <a href="https://www.okx.com/help/section/announcements-latest-announcements">OKX Latest Announcements</a>, <a href="https://www.okx.com/help/section/announcements-trading-updates">OKX Trading Updates</a>, <a href="https://www.okx.com/help/notice-on-upgrade-to-the-futures-cool-off-period">Futures Cool-off Period</a>, <a href="https://www.okx.com/learn/okx-regulated-crypto-exchange-mica-europe">OKX MiCA Europe</a>, <a href="https://www.okx.com/learn/regulated-crypto-exchange-protections-mica-europe">MiCA protections</a>, <a href="https://github.com/okx/agent-trade-kit">OKX Agent Trade Kit GitHub</a>.</p>
      </section>
    </article>
    <aside>
      <img src="{compact}" alt="Kompakte QR-Karte für OKX Empfehlungscode BONUSOK: realer QR-Code mittig, Code BONUSOK, KYC und Risikohinweis für deutsche Trader.">
      <p><strong>Code:</strong> BONUSOK</p>
      <p>Scanne nur, wenn OKX in deinem Land und Produktkonto verfügbar ist. Prüfe KYC, Kampagnenbedingungen und Risiko vor jeder Einzahlung.</p>
      <a class="btn" href="{REFERRAL_URL}" rel="sponsored nofollow">Referral-Link öffnen</a>
    </aside>
  </main>
  <footer>
    <div class="wrap">© 2026 Crypto referral guide. Bildungs- und Informationsmaterial, keine Anlageberatung.</div>
  </footer>
</body>
</html>
"""
    (WORK / "index.html").write_text(html, encoding="utf-8")
    return html


def count_words(text):
    import re
    return len(re.findall(r"[A-Za-zÄÖÜäöüß0-9][A-Za-zÄÖÜäöüß0-9\-]+", text))


def main():
    if not QR_SOURCE.exists():
        raise FileNotFoundError(QR_SOURCE)
    source_decoded = decode_qr(QR_SOURCE)
    if source_decoded != REFERRAL_URL:
        raise RuntimeError(f"QR mismatch: {source_decoded}")
    hero, hero_layout = build_hero()
    compact, compact_layout = build_compact_qr()
    html = build_html()
    qa = {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "public_url": PUBLIC_URL,
        "source_qr": str(QR_SOURCE),
        "source_qr_decoded": source_decoded,
        "hero": str(hero),
        "hero_decoded": decode_qr(hero),
        "hero_layout": hero_layout,
        "compact": str(compact),
        "compact_decoded": decode_qr(compact),
        "compact_layout": compact_layout,
        "article_word_count_source": count_words(ARTICLE),
    }
    (WORK / "visual-qa.json").write_text(json.dumps(qa, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(qa, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
