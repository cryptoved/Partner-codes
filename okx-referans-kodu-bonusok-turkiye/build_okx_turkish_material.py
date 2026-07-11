import json
import math
from datetime import datetime, timezone
from pathlib import Path

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont


ROOT = Path(__file__).resolve().parents[4]
WORK = Path(__file__).resolve().parent
ASSETS = WORK / "assets"
ASSETS.mkdir(exist_ok=True)

SLUG = "okx-referans-kodu-bonusok-turkiye"
PUBLIC_URL = f"https://cryptoved.github.io/Partner-codes/{SLUG}/"
REFERRAL_URL = "https://www.okx.com/join/BONUSOK"
PROMO_CODE = "BONUSOK"
QR_SOURCE = ROOT / "exchanges" / "OKX" / "outputs" / "qr-code-BONUSOK.png"

FONT_REGULAR = "C:/Windows/Fonts/segoeui.ttf"
FONT_BOLD = "C:/Windows/Fonts/segoeuib.ttf"


def font(path, size):
    return ImageFont.truetype(path if Path(path).exists() else FONT_REGULAR, size=size)


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


def rounded(draw, xy, radius, fill, outline=None, width=1):
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


def draw_wrapped(draw, text, xy, fnt, fill, max_width, gap=8):
    x, y = xy
    max_seen = 0
    lines = wrap_text(draw, text, fnt, max_width)
    for line in lines:
        bbox = draw.textbbox((x, y), line, font=fnt)
        max_seen = max(max_seen, bbox[2] - bbox[0])
        draw.text((x, y), line, font=fnt, fill=fill)
        y += (bbox[3] - bbox[1]) + gap
    return y, max_seen, lines


def build_background(w, h):
    img = Image.new("RGB", (w, h), "#06110e")
    px = img.load()
    for y in range(h):
        for x in range(w):
            gx = x / w
            gy = y / h
            r = int(5 + 18 * gx + 10 * (1 - gy))
            g = int(15 + 36 * gx + 22 * (1 - gy))
            b = int(20 + 22 * (1 - gx) + 8 * gy)
            px[x, y] = (r, g, b)
    draw = ImageDraw.Draw(img, "RGBA")
    rng = np.random.default_rng(41)
    horizon = int(h * 0.59)
    for i in range(30):
        x = int(i * (w / 26) + rng.integers(-18, 18))
        bw = int(rng.integers(26, 72))
        bh = int(rng.integers(int(h * 0.16), int(h * 0.45)))
        y = horizon - bh
        draw.rectangle([x, y, x + bw, horizon + 40], fill=(7, 24, 30, 155))
        for wy in range(y + 18, horizon - 8, 34):
            if rng.random() > 0.42:
                draw.rectangle([x + 8, wy, x + bw - 8, wy + 3], fill=(88, 255, 124, 56))
    # Bosphorus-like bridge lights and trading monitors.
    draw.line([int(w * .55), int(h * .24), int(w * .93), int(h * .24)], fill=(255, 205, 108, 100), width=3)
    for i in range(12):
        x = int(w * .56 + i * w * .03)
        draw.line([x, int(h * .24), x - 18, int(h * .38)], fill=(255, 205, 108, 42), width=1)
    draw.rounded_rectangle([int(w * .35), int(h * .31), int(w * .63), int(h * .68)], radius=22, fill=(2, 15, 15, 185), outline=(80, 255, 110, 95), width=2)
    for i in range(9):
        y = int(h * .39) + i * int(h * .027)
        pts = []
        for x in range(int(w * .38), int(w * .60), 22):
            pts.append((x, y + math.sin((x + i * 44) / 33) * int(h * .016)))
        draw.line(pts, fill=(68, 255, 112, 145), width=2)
    draw.rectangle([0, horizon, w, h], fill=(0, 8, 8, 130))
    return img.filter(ImageFilter.GaussianBlur(0.15))


def build_desktop_hero():
    w, h = 1600, 900
    img = build_background(w, h).convert("RGBA")
    draw = ImageDraw.Draw(img, "RGBA")
    text_panel = [84, 72, 870, 802]
    qr_card = [1034, 108, 1518, 796]
    qr_box = [1110, 184, 1442, 516]
    code_panel = [116, 692, 650, 810]
    rounded(draw, text_panel, 28, (0, 0, 0, 170), (72, 255, 121, 112), 2)
    draw.text((124, 112), "TÜRKÇE REHBER - OKX TR / OKX", font=font(FONT_BOLD, 28), fill=(92, 255, 108, 255))
    for i, line in enumerate(["OKX referans kodu", "BONUSOK"]):
        draw.text((124, 166 + i * 78), line, font=font(FONT_BOLD, 66), fill=(255, 255, 255, 255))
    sub = "TRY, KYC, Campaign Center, Agent Trade Kit, X-Perps ve risk kontrolü."
    y, sub_w, sub_lines = draw_wrapped(draw, sub, (124, 338), font(FONT_REGULAR, 34), (232, 238, 236, 242), 650, 8)
    chips = ["OKX TR", "TRY transfer", "Agent Trade Kit", "Futures Cool-off"]
    cx, cy = 124, y + 30
    chip_font = font(FONT_REGULAR, 25)
    for chip in chips:
        tw = draw.textbbox((0, 0), chip, font=chip_font)[2]
        rounded(draw, [cx, cy, cx + tw + 34, cy + 48], 22, (248, 255, 250, 238), (86, 255, 91, 255), 3)
        draw.text((cx + 17, cy + 9), chip, font=chip_font, fill=(18, 34, 29, 255))
        cx += tw + 48
        if cx > 690:
            cx, cy = 124, cy + 62
    rounded(draw, code_panel, 18, (248, 255, 250, 246), (86, 255, 91, 255), 3)
    draw.text((148, 718), "REFERANS KODU", font=font(FONT_REGULAR, 22), fill=(75, 87, 80, 255))
    draw.text((148, 748), PROMO_CODE, font=font(FONT_BOLD, 46), fill=(5, 22, 18, 255))
    rounded(draw, qr_card, 44, (252, 255, 252, 250), (86, 255, 91, 255), 5)
    rounded(draw, [1088, 156, 1464, 540], 24, (255, 255, 255, 255), (133, 255, 130, 255), 3)
    placed_qr = paste_qr(img, qr_box, QR_SOURCE)
    note = "Yalnızca OKX/OKX TR hesabında bölge ve ürün uygunluğu görünüyorsa tara."
    draw_wrapped(draw, note, (1092, 596), font(FONT_BOLD, 25), (18, 25, 22, 255), 360, 4)
    draw.text((1092, 718), "okx.com/join/BONUSOK", font=font(FONT_REGULAR, 27), fill=(52, 60, 57, 255))
    out = ASSETS / "okx-bonusok-turkish-referans-kodu-hero.png"
    img.convert("RGB").save(out, quality=96)
    return out, {"canvas": [w, h], "text_panel": text_panel, "qr_card": qr_card, "qr_box": qr_box, "placed_qr": placed_qr, "code_panel": code_panel, "subtitle_max_width": sub_w, "subtitle_lines": sub_lines}


def build_mobile_hero():
    w, h = 900, 1300
    img = build_background(w, h).convert("RGBA")
    draw = ImageDraw.Draw(img, "RGBA")
    text_panel = [54, 54, 846, 575]
    qr_card = [116, 624, 784, 1228]
    qr_box = [250, 712, 650, 1112]
    code_panel = [104, 484, 796, 596]
    rounded(draw, text_panel, 26, (0, 0, 0, 178), (72, 255, 121, 112), 2)
    draw.text((92, 92), "TÜRKÇE REHBER - OKX", font=font(FONT_BOLD, 28), fill=(92, 255, 108, 255))
    for i, line in enumerate(["OKX referans", "kodu BONUSOK"]):
        draw.text((92, 148 + i * 70), line, font=font(FONT_BOLD, 58), fill=(255, 255, 255, 255))
    draw_wrapped(draw, "TRY, KYC, Campaign Center, Agent Trade Kit ve risk kontrolü.", (92, 306), font(FONT_REGULAR, 31), (232, 238, 236, 245), 690, 7)
    rounded(draw, code_panel, 18, (248, 255, 250, 246), (86, 255, 91, 255), 3)
    draw.text((132, 506), "REFERANS KODU", font=font(FONT_REGULAR, 22), fill=(75, 87, 80, 255))
    draw.text((132, 536), PROMO_CODE, font=font(FONT_BOLD, 42), fill=(5, 22, 18, 255))
    rounded(draw, qr_card, 42, (252, 255, 252, 250), (86, 255, 91, 255), 5)
    rounded(draw, [198, 684, 702, 1132], 24, (255, 255, 255, 255), (133, 255, 130, 255), 3)
    placed_qr = paste_qr(img, qr_box, QR_SOURCE)
    draw_wrapped(draw, "Önce bölge, KYC ve ürün uygunluğunu kontrol et.", (174, 1152), font(FONT_BOLD, 28), (18, 25, 22, 255), 560, 4)
    out = ASSETS / "okx-bonusok-turkish-referans-kodu-mobile.png"
    img.convert("RGB").save(out, quality=96)
    return out, {"canvas": [w, h], "text_panel": text_panel, "qr_card": qr_card, "qr_box": qr_box, "placed_qr": placed_qr, "code_panel": code_panel}


def build_compact_qr():
    w, h = 560, 640
    img = Image.new("RGB", (w, h), "#f7fff9")
    draw = ImageDraw.Draw(img, "RGBA")
    rounded(draw, [18, 18, w - 18, h - 18], 32, (255, 255, 255, 255), (74, 239, 92, 255), 4)
    draw.text((56, 52), "OKX referans kodu", font=font(FONT_BOLD, 34), fill=(9, 28, 21, 255))
    draw.text((56, 92), PROMO_CODE, font=font(FONT_BOLD, 46), fill=(0, 13, 10, 255))
    qr_card = [82, 156, 478, 552]
    qr_box = [122, 196, 438, 512]
    rounded(draw, qr_card, 24, (255, 255, 255, 255), (120, 255, 120, 255), 3)
    placed = paste_qr(img, qr_box, QR_SOURCE)
    draw.text((72, 574), "Önce KYC, bölge ve riski kontrol et.", font=font(FONT_REGULAR, 23), fill=(53, 63, 58, 255))
    out = ASSETS / "okx-bonusok-turkish-compact-qr.png"
    img.save(out, quality=96)
    return out, {"canvas": [w, h], "qr_card": qr_card, "qr_box": qr_box, "placed_qr": placed}


ARTICLE = """
<p class="lead">OKX referans kodu <strong>BONUSOK</strong> hakkında Türkçe arama yapan bir kullanıcı için en önemli konu sadece kodu bulmak değildir. Daha önemli olan şey, OKX TR veya OKX hesabında bölge uygunluğunu, KYC durumunu, TRY yatırma/çekme seçeneklerini, Campaign Center şartlarını ve işlem riskini kontrol etmektir. Bu rehber Türkiye, yurt dışındaki Türkçe konuşan traderlar ve OKX ekosistemini ciddi biçimde test etmek isteyen aktif kullanıcılar için hazırlanmış, uygunluk öncelikli bir kontrol listesidir.</p>
<h2>Kısa cevap: OKX referans kodu BONUSOK nedir?</h2>
<p><strong>BONUSOK</strong>, OKX kayıt sürecinde kullanılabilen bir referans kodudur. Ancak kodun görünmesi, kampanya görevinin açılması veya herhangi bir ödülün uygulanması otomatik garanti değildir. Kullanıcının ülkesi, hesabın bağlı olduğu OKX/OKX TR yapısı, KYC seviyesi, ürün erişimi, kampanya süresi, minimum yatırma koşulu, işlem hacmi ve risk kuralları sonucu değiştirebilir. Bu nedenle bu sayfa, “hemen kayıt ol” yerine “önce kontrol et, sonra küçük test yap” yaklaşımıyla yazıldı.</p>
<p>Türkiye açısından özellikle dikkatli olmak gerekir. OKX, OKX TR lansmanında Türk Lirası yatırma/çekme, yerel bankalar, Türkçe destek ve TRY işlem çiftleri gibi yerelleştirilmiş özelliklerden söz etti. Aynı zamanda OKX, Türkiye’deki yeni kripto düzenlemeleri nedeniyle global www.okx.com üzerindeki Türkçe dil desteği ve Türkiye’de ikamet eden kullanıcılara yönelik promosyon/marketing faaliyetleri hakkında ayrı bir hizmet güncellemesi yayımladı. Bu yüzden Türkçe bir kullanıcı, hangi platformu kullandığını, hangi hesabın açık olduğunu ve hangi ürünlerin yasal olarak erişilebilir olduğunu netleştirmeden işlem yapmamalıdır.</p>
<h2>Neden bu sayfa aktif trader odaklı?</h2>
<p>Basit bir referral sayfası yalnızca “OKX davet kodu BONUSOK” der ve biter. Aktif trader için bu yetersizdir. Haftada birkaç kez işlem yapan biri, sadece bir kod istemez; emir tiplerini, likiditeyi, komisyonları, TRY transfer hızını, para çekme testini, API güvenliğini, bot limitlerini, futures riskini ve kampanya şartlarını bilmek ister. Referral trafiğinin kalitesi de burada ortaya çıkar: Bilinçli kullanıcı KYC tamamlamaya, küçük depozito yapmaya, ilk işlemi ölçülü açmaya ve uzun vadede aktif kalmaya daha yakındır.</p>
<p>Bu nedenle Türkçe materyalde ana cazibe noktaları olarak OKX TR’nin yerel TRY akışı, OKX’in güncel X-Perps ve Equity X-Perps genişlemesi, Agent Trade Kit, Futures Cool-off Period, Campaign Center, Web3 Wallet, Trading Bots ve Copy Trading ele alındı. Bunların hepsi ancak doğru kullanıcıya ve doğru risk çerçevesine anlatıldığında işe yarar. Aksi halde sadece kısa vadeli bonus avcısı çeker, aktif trader değil.</p>
<h2>Türkiye ve OKX TR: yerel uygunluk kontrolü</h2>
<p>Türkiye’de kripto varlık hizmetleriyle ilgili düzenleyici ortam hızla geliştiği için ilk kontrol noktası resmi uygunluktur. OKX TR tarafında Türk Lirası ile doğrudan yatırma ve çekme, bankalar üzerinden transfer, TRY işlem çiftleri ve Türkçe/İngilizce destek gibi yerel unsurlar öne çıkar. Fakat her ürün, her kullanıcıya ve her bölgede aynı şekilde açık olmayabilir. OKX global tarafta ise Türkiye’de ikamet eden kullanıcılara yönelik pazarlama faaliyetleri hakkında sınırlamalar duyurulmuştur.</p>
<p>Pratik anlamı şu: Türkiye’de yaşıyorsan kayıt ekranında gerçek ülkeni, gerçek kimlik bilgini ve kendi hesabını kullan. VPN ile başka ülkede görünmeye çalışma. Başkasının hesabını, yanlış adresi, sahte belgeyi veya üçüncü taraf ödeme yolunu kullanma. OKX TR ve OKX arasındaki hesap yapısı, iç transfer ve ürün erişimi farklı olabilir. Bu rehberdeki QR ve link ancak hesabında uygunluk görünüyorsa ve ilgili ürünler sana resmi olarak sunuluyorsa kullanılmalıdır.</p>
<h2>Güncel OKX yenilikleri: Türk trader için ne anlam ifade ediyor?</h2>
<p>OKX’in 10 Temmuz 2026 tarihli son duyurularında SKHY equity perpetual futures, SLX Trade-to-Earn kampanyası, PENGUUSD Expiry X-Perps, AMDUSD Equity X-Perp, SHAZ/JNJ/PENG equity futures ve SLX/USDT spot listelemesi gibi başlıklar yer aldı. 9 Temmuz’da XPLUSD ve ALGOUSD X-Perps, AAOIUSD ve NBISUSD Equity X-Perps duyuruları; 8 Temmuz’da ise USDT/USDⓈ spot işlem çifti ücret güncellemesi ve INJUSD, ICPUSD, RENDERUSD X-Perps başlıkları vardı. Bu liste, OKX’in yeni piyasa ve türev ürün tarafında hızlı hareket ettiğini gösterir.</p>
<p>Fakat aktif trader için sonuç “her yeni ürünü al” değildir. Yeni X-Perps veya equity perpetual ürünlerinde likidite, spread, fonlama, endeks yapısı, vade, işlem saatleri, fiyat kayması, teminat yönetimi ve bölgesel erişim kontrol edilmelidir. Türkiye’deki veya diaspora kullanıcısı, özellikle kaldıraçlı ürünlerin kendi hesabında yasal ve teknik olarak erişilebilir olup olmadığını anlamalıdır. Spot işlemle başlayan ve önce likit pariteleri test eden bir kullanıcı, yeni ürünlere acele atlayan bir kullanıcıdan daha sağlıklı ilerler.</p>
<h2>TRY yatırma, çekme ve bankacılık akışı</h2>
<p>OKX TR sayfalarında TRY yatırma/çekme, 7/24 banka transferleri, TRY işlem çiftleri ve bazı yerel bankalar üzerinden transfer akışları anlatılır. Bu, Türkiye için güçlü bir acquisition açısıdır çünkü birçok traderın gerçek sorunu kriptoya ilk girişte veya çıkışta yaşadığı banka ve TRY sürecidir. Ancak bu bilgiyi bir söz değil, kontrol maddesi olarak kullanmak gerekir. Hesabında hangi banka seçenekleri görünüyor? İlk para çekmede güvenlik nedeniyle gecikme var mı? İç transfer OKX ve OKX TR arasında nasıl çalışıyor? UID doğru mu? Transfer geçmişi ve makbuzlar kaydediliyor mu?</p>
<p>Aktif traderların hatası genellikle küçük bir test yapmadan büyük para taşımaktır. Önce küçük TRY yatırma, küçük USDT veya BTC alımı, küçük iç transfer, küçük çekim ve işlem geçmişi dışa aktarımı test edilmelidir. Böylece hem bankacılık akışını hem de OKX TR/OKX ayrımını öğrenirsin. Referral kodu BONUSOK ancak bu operasyonel akış çalışıyorsa anlamlıdır.</p>
<h2>Komisyon, TRY pariteleri ve likiditeyi nasıl okuyacaksın?</h2>
<p>Türkiye’de aktif işlem yapan kullanıcı için komisyon yalnızca maker/taker tablosundan ibaret değildir. TRY paritelerinde spread, emir defteri derinliği, transfer ücreti, olası kampanya indirimi, para çekme süresi ve işlem saatine göre değişen likidite birlikte değerlendirilmelidir. Bir paritede sıfır maker ücreti veya düşük komisyon görsen bile, spread genişse gerçek maliyet daha yüksek olabilir. Bu yüzden ilk hafta kendi küçük işlem günlüğünü tut: emir büyüklüğü, beklenen fiyat, gerçekleşen fiyat, komisyon, spread ve çıkış maliyeti.</p>
<p>Özellikle BTC/TRY, ETH/TRY ve USDT/TRY gibi yerel pariteler, TRY bazlı kullanıcılar için doğal başlangıç noktasıdır. Ancak aktif trader, sadece TRY paritesine bakmaz; global USDT pariteleriyle fiyat farkını, transfer zamanını ve likiditeyi de karşılaştırır. Eğer TRY paritesinde derinlik düşükse, büyük emirleri parçalamak veya daha likit paritede işlem yapmak daha mantıklı olabilir. Bu davranış, referral sonrası gerçek aktif trader kalitesini artırır çünkü kullanıcı platformu maliyet bilinciyle kullanır.</p>
<p>Yeni listelenen tokenlar, Trade-to-Earn kampanyaları veya X-Perps duyuruları kısa vadeli ilgi çekebilir. Fakat yeni ürünlerde volatilite, slippage ve likidite riski daha yüksek olabilir. Bu nedenle iyi bir Türkçe OKX rehberi, kullanıcıya sadece “kod burada” demez; “hangi paritede, hangi büyüklükte, hangi maliyetle işlem yaptığını ölç” der. BONUSOK kodu, bu disiplinin yanında küçük bir başlangıç bağlantısıdır; stratejinin kendisi değildir.</p>
<h2>Campaign Center ve bonus şartlarını nasıl kontrol edersin?</h2>
<p>OKX veya OKX TR hesabında Campaign Center, My Rewards veya benzer görev ekranları görünüyorsa, önce şartları oku. “Bonus” kelimesi çoğu zaman minimum yatırma, minimum işlem hacmi, belirli ürünler, belirli süre, KYC seviyesi ve bölgesel uygunluk gibi koşullara bağlıdır. Bir dış sayfa sana “bonus var” dese bile, asıl kanıt hesabında gördüğün kampanya şartıdır. Eğer kampanya görünmüyorsa, sadece bir kod için para yatırmak doğru motivasyon değildir.</p>
<p>Sağlıklı kullanım sırası şöyledir: önce hesabında BONUSOK bağlantısının veya referans kodunun uygulanıp uygulanmadığını kontrol et, sonra görevlerin hangi ürünlere bağlı olduğunu oku, ardından küçük bir depozito ve düşük riskli işlemle platformu test et. Kampanya koşulu seni istemediğin bir futures işlemine, yüksek hacim çevirmeye veya anlamadığın ürüne zorluyorsa, bu kampanya sana uygun değildir.</p>
<h2>Agent Trade Kit ve AI trading: cazip ama riskli</h2>
<p>OKX’in Agent Trade Kit yaklaşımı, yapay zekâ ajanları ve araçlarla işlem süreçlerini otomatikleştirme fikrini öne çıkarır. Teknik kullanıcılar için bu güçlü bir hook olabilir: piyasa verisi okuma, teknik indikatörler, emir yönetimi, strateji araçları ve otomasyon. Ancak AI trading, otomatik kazanç anlamına gelmez. Yanlış API izni, kötü test edilmiş strateji, limit koyulmayan bot veya kontrolsüz kaldıraç çok hızlı kayıp yaratabilir.</p>
<p>Türkçe konuşan aktif trader için önerilen güvenlik sırası: önce sadece okuma izniyle başla, küçük hesap kullan, API anahtarına para çekme izni verme, IP kısıtlaması kullan, bot başına maksimum pozisyon limiti koy, her emir için log tut ve stratejiyi küçük hacimde gözlemle. Agent Trade Kit’i “sihirli sistem” değil, disiplinli bir araç kutusu gibi düşün. Bu yaklaşım hem daha güvenli hem de uzun vadeli referral kalitesi için daha değerlidir.</p>
<h2>Futures Cool-off Period neden önemli?</h2>
<p>OKX’in Futures Cool-off Period güncellemesi, web ve uygulama dışında REST API, WebSocket, üçüncü taraf yetkilendirme, Broker OAuth, Agent Trade Kit, Strategy Orders, Copy Trading ve Trading Bots gibi kanalları da ilgilendiren daha geniş bir kontrol çerçevesi sunar. Bu, aktif trader için çok önemlidir. Çünkü gerçek risk kontrolü sadece ekrandaki bir düğme değildir; botların, API emirlerinin ve kopya işlemlerin de durması gerekir.</p>
<p>Cool-off özelliği zararı otomatik önlemez, fakat kötü davranışı yavaşlatabilir. Büyük kayıptan sonra intikam işlemi açma, gece kontrolsüz pozisyon büyütme, botu gereğinden agresif bırakma veya kısa sürede çok fazla işlem yapma gibi hataları azaltmak için kullanılabilir. Bu yüzden bu sayfa, referans kodunun yanında Cool-off konusunu da anlatır: Çünkü aktif traderı çekmek, ona risk frenlerini de göstermek demektir.</p>
<h2>İlk 30 dakika kontrol listesi</h2>
<h3>Hesap ve güvenlik</h3>
<p>2FA aç, anti-phishing kodu kullan, güçlü parola belirle, e-posta güvenliğini kontrol et, cihazlarını temiz tut ve yedek kodlarını güvenli sakla. KYC için gerçek kimlik ve gerçek ikamet bilgisi kullan. Başkasının hesabı, ödünç alınmış banka hesabı, sahte belge, VPN veya yanlış ülke seçimi uzun vadede para çekme sorununa dönüşebilir.</p>
<h3>Para yatırma ve ilk işlem</h3>
<p>Önce küçük bir TRY veya kripto yatırma testi yap. Sonra likit bir paritede küçük spot işlem aç. Emir türlerini, komisyon ekranını, işlem geçmişini ve para çekme adımlarını kontrol et. İlk gün egzotik token, yeni X-Perp veya yüksek kaldıraçla başlama. Bir traderın ilk hedefi para kazanmak değil, sistemin nasıl çalıştığını düşük riskle öğrenmek olmalıdır.</p>
<h3>Raporlama ve vergi disiplini</h3>
<p>Türkiye’de vergi ve raporlama çerçevesi değişebilir. Bu nedenle işlem geçmişini, yatırma/çekme kayıtlarını, komisyonları, ödülleri ve transfer bilgilerini düzenli dışa aktar. Ay sonunda ne yaptığını açıklayamıyorsan, aktif trader değil dağınık bir spekülatörsün. İyi kayıt tutmak, risk yönetiminin sessiz ama kritik kısmıdır.</p>
<h2>OKX Web3 Wallet ve self-custody tarafı</h2>
<p>OKX TR lansman metinlerinde OKX Web3 Wallet’ın Türkiye’de global platform üzerinden kullanılabildiği belirtilir. Web3 Wallet, merkezi borsa dışındaki DEX, DeFi, NFT ve self-custody deneyimleri için ayrı bir katmandır. Bu fırsat olduğu kadar risk de taşır. Seed phrase kaybı, yanlış ağ, sahte token, zararlı dApp izni veya yanlış köprü kullanımı kullanıcıyı doğrudan kayba götürebilir.</p>
<p>Bu nedenle Wallet tarafını test ederken önce küçük miktar, doğru ağ, güvenilir kontrat, izin kontrolü ve revoke alışkanlığı gerekir. Borsa hesabı ile self-custody cüzdanı aynı risk modeli değildir. OKX referans kodu ile başlayan bir kullanıcı bile, Web3 Wallet tarafında kendi güvenliğinden daha fazla sorumludur.</p>
<h2>Kimler için uygun, kimler için uygun değil?</h2>
<p>OKX/OKX TR, gerçek KYC yapmaya, ürün uygunluğunu kontrol etmeye, TRY transfer akışını test etmeye, risk sınırı koymaya ve platformu disiplinli incelemeye hazır kullanıcılar için anlamlı olabilir. Özellikle TRY ile işlem yapmak isteyen, OKX TR ile global OKX arasındaki farkı anlamak isteyen, Web3 Wallet ve yeni X-Perps ürünlerini araştıran aktif traderlar bu rehberden fayda görebilir.</p>
<p>Uygun değildir: bölge kısıtını aşmak isteyenler, sahte KYC düşünenler, bonus için gereksiz hacim çevirenler, kaldıraç riskini anlamayanlar, kaybetmeyi göze alamadığı parayla işlem yapanlar. Bu kullanıcılara en iyi tavsiye kayıt değil, önce eğitim ve risk sınırıdır.</p>
<h2>Yurt dışındaki Türkçe konuşan kullanıcılar için ek not</h2>
<p>Almanya, Hollanda, Fransa, Birleşik Krallık, Orta Asya, Körfez ülkeleri veya başka bir ülkede yaşayan Türkçe konuşan kullanıcılar için en önemli konu, Türkiye’deki OKX TR akışı ile kendi ikamet ülkesindeki OKX ürün erişimini karıştırmamaktır. Arama motorunda Türkçe “OKX referans kodu”, “OKX davet kodu”, “OKX bonus kodu” veya “OKX komisyon indirimi” arıyor olabilirsin; fakat hesabın Türkiye’de değilse, TRY transferi, banka seçeneği, kampanya görevi, vergi raporlaması ve türev ürün erişimi tamamen farklı olabilir. Bu nedenle kayıt ekranında gerçek ikamet ülkeni seç, yerel düzenlemeyi oku ve sadece hesabında görünen ürünleri değerlendir.</p>
<p>Diaspora kullanıcısı için pratik kontrol listesi basittir: önce bölge ve KYC uygunluğu, sonra para yatırma/çekme yolu, ardından düşük tutarlı spot test, son olarak kampanya ve gelişmiş ürün kontrolü. Eğer bulunduğun ülkede futures, copy trading, botlar, belirli X-Perps ürünleri veya belirli kampanyalar açık değilse, bunu teknik bir engel gibi değil, uyulması gereken bir sınır gibi gör. Referral kodu BONUSOK ancak yasal erişim, açık kampanya şartı ve kişisel risk planı ile birlikte anlamlıdır.</p>
<h2>Sık sorulan sorular</h2>
<p><strong>OKX referans kodu BONUSOK Türkiye’de garanti bonus verir mi?</strong> Hayır. Bonus veya ödül varsa, hesabındaki Campaign Center şartlarına bağlıdır. Bölge, KYC, ürün ve süre koşulları değişebilir.</p>
<p><strong>OKX TR ile OKX aynı şey mi?</strong> Kullanıcı deneyimi bağlantılı olabilir, ancak OKX TR yerel TRY ve Türkiye odağıyla ayrı bir yerelleştirilmiş yapı sunar. Hangi hesapta hangi ürünlerin açık olduğunu kontrol etmelisin.</p>
<p><strong>VPN kullanarak daha fazla ürün açmak doğru mu?</strong> Hayır. Yanlış ülke, VPN, sahte KYC veya başkasının hesabı para çekme ve hesap güvenliği açısından ciddi risk yaratır.</p>
<p><strong>İlk işlem futures mı olmalı?</strong> Genellikle hayır. Önce spot, küçük tutar, para çekme testi, geçmiş exportu ve risk sınırı daha doğru başlangıçtır.</p>
<p><strong>Bu sayfa yatırım tavsiyesi mi?</strong> Hayır. Bu sayfa eğitim ve kontrol listesi niteliğindedir. Kripto varlıklar yüksek risk taşır; kendi hukuki, vergi ve finansal durumunu ayrıca değerlendirmelisin.</p>
"""


def build_html():
    title = "OKX referans kodu BONUSOK: Türkiye için aktif trader rehberi"
    description = "OKX referans kodu BONUSOK Türkçe rehber: OKX TR, TRY yatırma çekme, KYC, Campaign Center, Agent Trade Kit, X-Perps, Futures Cool-off ve risk kontrolü."
    desktop = "assets/okx-bonusok-turkish-referans-kodu-hero.png"
    mobile = "assets/okx-bonusok-turkish-referans-kodu-mobile.png"
    compact = "assets/okx-bonusok-turkish-compact-qr.png"
    html = f"""<!doctype html>
<html lang="tr-TR">
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
  <meta property="og:image" content="{PUBLIC_URL}{desktop}">
  <meta property="og:image:alt" content="Türkçe OKX referans kodu BONUSOK rehberi: OKX TR, TRY, KYC, Campaign Center, Agent Trade Kit, X-Perps ve gerçek QR kodu.">
  <style>
    :root{{color-scheme:dark;--bg:#07100e;--green:#65ff6c;--text:#edf7f0;--muted:#b9c8bf;--gold:#ffd36f}}
    *{{box-sizing:border-box}} body{{margin:0;background:var(--bg);color:var(--text);font-family:Segoe UI,Arial,sans-serif;line-height:1.65}} a{{color:#7dff83;overflow-wrap:anywhere}}
    .wrap{{width:min(1120px,calc(100% - 32px));margin:0 auto}} header{{padding:28px 0 10px;border-bottom:1px solid rgba(101,255,108,.18)}}
    .eyebrow{{color:var(--green);font-weight:800;text-transform:uppercase;font-size:.9rem}} h1{{font-size:clamp(2.1rem,5vw,4.8rem);line-height:1.02;margin:.35em 0 .22em;max-width:980px;letter-spacing:0}}
    .dek{{max-width:850px;color:var(--muted);font-size:1.16rem;margin:0 0 20px}} .hero{{width:100%;display:block;border:1px solid rgba(101,255,108,.34);border-radius:8px;margin:24px 0 12px;background:#111}}
    .hero-mobile{{display:none}} .caption{{color:var(--muted);font-size:.95rem;margin:0 0 28px}} .cta-row{{display:flex;flex-wrap:wrap;gap:12px;margin:20px 0 8px;align-items:center}}
    .btn{{display:inline-flex;align-items:center;justify-content:center;min-height:46px;padding:10px 18px;border-radius:8px;background:#ecfff0;color:#07100e;font-weight:800;text-decoration:none;border:2px solid var(--green)}} .ghost{{background:transparent;color:var(--green)}}
    main{{display:grid;grid-template-columns:minmax(0,1fr) 300px;gap:34px;padding:22px 0 56px}} article{{min-width:0}} article h2{{margin:2.1rem 0 .7rem;font-size:clamp(1.45rem,2.6vw,2.15rem);line-height:1.18;letter-spacing:0}} article h3{{margin:1.45rem 0 .45rem;font-size:1.22rem;color:#dfffe2}} article p{{margin:.8rem 0;color:#e2ede7;font-size:1.04rem}}
    .lead{{font-size:1.16rem;color:#f5fff7;border-left:4px solid var(--green);padding:14px 18px;background:rgba(101,255,108,.07);border-radius:8px}}
    aside{{position:sticky;top:18px;align-self:start;padding:18px;border:1px solid rgba(101,255,108,.28);border-radius:8px;background:rgba(11,23,18,.92)}} aside img{{width:100%;border-radius:8px;background:white;display:block}} aside p{{color:var(--muted);font-size:.94rem;margin:12px 0 0}}
    .notice{{margin:26px 0;padding:18px;border:1px solid rgba(255,211,111,.45);border-radius:8px;background:rgba(255,211,111,.08);color:#fff5d6}} .sources{{padding:18px;border-top:1px solid rgba(101,255,108,.24);color:var(--muted)}} footer{{border-top:1px solid rgba(101,255,108,.2);padding:24px 0 36px;color:var(--muted)}}
    @media(max-width:860px){{main{{display:block}}aside{{position:static;margin:22px 0}}h1{{font-size:2.36rem}}.wrap{{width:min(100% - 22px,1120px)}}.hero-desktop{{display:none}}.hero-mobile{{display:block}}}}
  </style>
  <script type="application/ld+json">{{"@context":"https://schema.org","@type":"Article","headline":"{title}","inLanguage":"tr-TR","datePublished":"2026-07-11","dateModified":"2026-07-11","mainEntityOfPage":"{PUBLIC_URL}","image":"{PUBLIC_URL}{desktop}"}}</script>
</head>
<body>
  <header><div class="wrap">
    <div class="eyebrow">Türkiye / OKX TR / Active Trader Guide</div>
    <h1>OKX referans kodu BONUSOK Türkiye rehberi</h1>
    <p class="dek">OKX TR, TRY transferi, KYC, Campaign Center, Agent Trade Kit, X-Perps, Futures Cool-off ve ilk işlem öncesi risk kontrolü için Türkçe rehber.</p>
    <div class="cta-row"><a class="btn" href="{REFERRAL_URL}" rel="sponsored nofollow">BONUSOK uygunluğunu kontrol et</a><a class="btn ghost" href="#kontrol-listesi">Kontrol listesini oku</a></div>
    <img class="hero hero-desktop" src="{desktop}" alt="Türkçe OKX referans kodu BONUSOK rehberi: İstanbul esintili trading desk, OKX TR, TRY yatırma çekme, KYC, Campaign Center, Agent Trade Kit, X-Perps, Futures Cool-off Period, Web3 Wallet, Trading Bots, Copy Trading, AI Trading ve gerçek QR kodu.">
    <img class="hero hero-mobile" src="{mobile}" alt="Mobil Türkçe OKX referans kodu BONUSOK görseli: gerçek QR kodu, OKX TR, TRY, KYC, Campaign Center ve risk kontrolü.">
    <p class="caption">Referral açıklaması: Bu bağlantıyla kayıt olursan komisyon alabiliriz. Kod kâr, bonus veya ürün erişimi garantilemez.</p>
  </div></header>
  <main class="wrap">
    <article>
      <div class="notice"><strong>Önemli uygunluk notu:</strong> QR ve linki yalnızca OKX/OKX TR hesabında ülke, KYC ve ürün uygunluğu görünüyorsa kullan. VPN, sahte KYC, başkasının hesabı veya kısıtlama aşma davranışı önerilmez.</div>
      {ARTICLE}
      <section class="sources"><h2>Kaynaklar ve güncel OKX bağlamı</h2><p>11 Temmuz 2026 kontrolü: <a href="https://www.okx.com/help/section/announcements-latest-announcements">OKX Latest Announcements</a>, <a href="https://www.okx.com/help/section/announcements-trading-updates">OKX Trading Updates</a>, <a href="https://www.okx.com/help/service-updates-under-new-crypto-regulation-for-our-customers-in-turkiye">Türkiye hizmet güncellemesi</a>, <a href="https://www.okx.com/learn/officially-launching-okx-tr-global-expansion">OKX TR lansmanı</a>, <a href="https://www.okx.com/campaigns/deposit-try">OKX TR TRY transfer sayfası</a>, <a href="https://github.com/okx/agent-trade-kit">OKX Agent Trade Kit GitHub</a>.</p></section>
    </article>
    <aside>
      <img src="{compact}" alt="Kompakt OKX referans kodu BONUSOK QR kartı: gerçek QR kodu ortada, BONUSOK, KYC, bölge uygunluğu ve Türkçe risk uyarısı.">
      <p><strong>Kod:</strong> BONUSOK</p>
      <p>Önce OKX/OKX TR hesabında bölge, KYC, kampanya ve ürün uygunluğunu kontrol et.</p>
      <a class="btn" href="{REFERRAL_URL}" rel="sponsored nofollow">Referral linkini aç</a>
    </aside>
  </main>
  <footer><div class="wrap">© 2026 Crypto referral guide. Eğitim amaçlıdır; yatırım tavsiyesi değildir.</div></footer>
</body>
</html>"""
    (WORK / "index.html").write_text(html, encoding="utf-8")
    return html


def count_words(text):
    import re
    return len(re.findall(r"[A-Za-zÇĞİÖŞÜçğıöşü0-9][A-Za-zÇĞİÖŞÜçğıöşü0-9\\-]+", text))


def main():
    source_decoded = decode_qr(QR_SOURCE)
    if source_decoded != REFERRAL_URL:
        raise RuntimeError(f"QR mismatch: {source_decoded}")
    desktop, desktop_layout = build_desktop_hero()
    mobile, mobile_layout = build_mobile_hero()
    compact, compact_layout = build_compact_qr()
    build_html()
    qa = {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "public_url": PUBLIC_URL,
        "source_qr": str(QR_SOURCE),
        "source_qr_decoded": source_decoded,
        "desktop_hero": str(desktop),
        "desktop_hero_decoded": decode_qr(desktop),
        "desktop_layout": desktop_layout,
        "mobile_hero": str(mobile),
        "mobile_hero_decoded": decode_qr(mobile),
        "mobile_layout": mobile_layout,
        "compact": str(compact),
        "compact_decoded": decode_qr(compact),
        "compact_layout": compact_layout,
        "article_word_count_source": count_words(ARTICLE),
    }
    (WORK / "visual-qa.json").write_text(json.dumps(qa, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(qa, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
