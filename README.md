# ⚽ Futbol - O'yinlar va Jadvallar (Otamiz Uchun Maxsus Ilova)

Otangiz futbol o'yinlari, boshlanish vaqtlari, natijalar va turnir jadvallarini katta shriftda, oson va qulay ko'rishlari uchun yaratilgan zamonaviy PWA va Telegram Mini App.

---

## 🌟 Asosiy Imkoniyatlari:

1. **👓 Katta Shriftlar va Oson O'qilish:**
   * Yuqori o'ng burchakdagi `A` / `A+` / `A++` tugmalari orqali shrift o'lchamini otangizning ko'rishiga moslab sozlash mumkin.
   * Jamoalar logolari va hisoblar katta va kontrastli.

2. **🇺🇿 Toshkent Vaqti bilan Boshlanish Soatlari:**
   * Barcha o'yinlar O'zbekiston (Toshkent, UTC+5) vaqtiga avtomatik o'giriladi: masalan `Bugun 23:00`, `Ertaga 00:45`.

3. **🏆 Barcha Asosiy Chempionatlar:**
   * **APL** (Angliya Premyer Ligasi)
   * **La Liga** (Ispaniya)
   * **Turkiya Superligasi** (Eldor Shomurodov, Husniddin Aliqulov va boshqa legionerlarimiz)
   * **A Seriya** (Italiya)
   * **Chempionlar Ligasi** (UEFA UCL)
   * **Bundesliga** (Germaniya)

4. **🇺🇿 Bizning Legionerlar Burchagi:**
   * Eldor Shomurodov va Abbosbek Fayzullayev jamoalarining navbatdagi o'yini va oxirgi natijasi birinchi sahifada alohida ko'rinadi.

5. **❤️ Sevimli Jamoalar:**
   * Har qanday jamoaning yonidagi yurakcha `🤍` belgisini bosib, uni `Sevimlilar` ro'yxatiga qo'shish mumkin.

6. **⚡ Smart Keshlash (RapidAPI tejamkorligi):**
   * Backend har bir ma'lumotni keshda saqlaydi, bu esa API limitlarini tejaydi va ilovani chaqmoqdek tez ochilishini ta'minlaydi.

---

## 🚀 Ishga tushirish:

### 1. Oddiy ishga tushirish:
`start_app.bat` fayliga 2 marta bosing yoki terminalda:
```bash
python server.py
```
Brauzerda oching: **http://localhost:8000**

---

### 2. Jonli natijalar qayerdan keladi:
* **Yevropa ligalari va UCL** — ESPN'ning ochiq API'si. Kalit kerak emas, server har daqiqada o'zi yangilaydi.
* **O'zbekiston Superligasi** — [API-Football](https://dashboard.api-football.com/register) (bepul tarif: kuniga 100 ta so'rov).
  Ro'yxatdan o'tib olingan kalitni serverda muhit o'zgaruvchisi sifatida bering:
  ```bash
  API_FOOTBALL_KEY=kalitingiz python server.py
  ```
  Kalit berilmasa, Superliga uchun bazadagi eski ma'lumot ko'rsatiladi. Server logida `❌ API-Football xatosi` chiqsa, xabar matnida sababi yoziladi (masalan, tarif bu mavsumga ruxsat bermasa).

---

## 📱 Otangizning Telefoniga O'rnatish (PWA):

1. Telefon brauzerida (Chrome yoki Safari) ilova manzilini oching.
2. Brauzer menyusidan (3 ta nuqta yoki ulashish tugmasidan) **"Bosh ekranga qo'shish" (Add to Home screen)** ni bosing.
3. Telefonda xuddi haqiqiy alohida ilova (Play Market'dan yuklab olingandek) paydo bo'ladi.

---

## 🤖 Telegram Bot (Telegram Mini App) orqali ulash:

1. `@BotFather` dan olingan bot tokeningizni `telegram_bot.py` fayliga yozing.
2. Botni ishga tushiring:
```bash
python telegram_bot.py
```
3. Telegramda botga `/start` yuborilsa, ilovani Telegram ichida to'liq ekranda ochish tugmasi chiqadi.
