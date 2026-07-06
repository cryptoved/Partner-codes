# Bybit Thai Material Visual QA

Date: 2026-06-18

## Assets

- Desktop hero: `../../outputs/bybit-thai-active-trader-bonusok-hero.png`
- Mobile hero: `../../outputs/bybit-thai-active-trader-bonusok-mobile-hero.png`
- QR card: `../../outputs/bybit-thai-bonusok-qr-card.png`
- Source QR: `../../outputs/qr-code-BONUSOK.png`

## Canvas And Layout

Desktop hero canvas: 1600 x 900 px.

- Text zone: x=72, y=72, w=760.
- Tag zone: x=72, y≈460, w=650.
- Code/eligibility card: x=70, y=672, w=730, h≈166.
- QR card: x=1165, y=470, w=365, h=382.
- QR image box: 248 x 248 px inside the QR card; real QR image rendered at 224 x 224 px with white quiet zone.

Mobile hero canvas: 900 x 1050 px.

- Text zone: x=58, y=62, w=760.
- Tag zone: x=58, y≈532, w=720.
- Code/eligibility card: x=58, y≈799, w=760.
- Mobile hero intentionally omits QR because the public page shows a separate QR card below the intro.

QR card canvas: 420 x 500 px.

- QR image rendered at 292 x 292 px inside a single white card.
- QR label: `สแกนเพื่อเปิด`.

## Checks

- Source QR decoded locally to `https://partner.bybit.com/b/bonusok`.
- Desktop hero flattened image decoded locally to `https://partner.bybit.com/b/bonusok`.
- QR card flattened image decoded locally to `https://partner.bybit.com/b/bonusok`.
- Local desktop screenshot: `local-desktop-final.png`.
- Local mobile screenshot after responsive fixes: `local-mobile-final2.png`.
- Thai word-count check via `Intl.Segmenter`: 3392 word-like segments, 2422 Thai word-like segments.
- Public page must not include next verification date; that date remains only in the materials database.
