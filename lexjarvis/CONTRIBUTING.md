# Hissa qo'shish

Rahmat! LexJarvis o'zbek tilidagi huquqiy ta'lim uchun ochiq loyiha — har qanday hissa qadrli.

## Boshlash

```bash
git clone https://github.com/<foydalanuvchi>/lexjarvis.git && cd lexjarvis
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
pytest && ruff check .
```

Testlar tarmoqsiz ishlaydi (Claude klienti soxta obyekt bilan almashtiriladi), shuning uchun
API kaliti shart emas.

## Qoidalar

1. Kichik, aniq PR'lar yuboring; har bir o'zgarishga test qo'shing.
2. `ruff check .` va `pytest` o'tishi kerak (CI buni tekshiradi).
3. Prompt'larni (`prompts.py`) o'zgartirsangiz, nima uchun yaxshiroq ekanini PR'da tushuntiring.
4. **Manba matnlar:** faqat tarqatishga ruxsat berilgan matnlarni repoga qo'shing. Shubha bo'lsa,
   matnni emas, uni qanday yuklab olish yo'riqnomasini qo'shing.

## Good first issues

- [ ] **O'zbek stemmer:** `tokenize()` dagi oddiy qisqartirishni qo'shimchalarni (-lar, -ning, -ga, -dan...)
      kesadigan qoidaga almashtirish va testlar yozish.
- [ ] **Kirill yozuvi qo'llab-quvvatlash:** kirill matnlarni qidiruvdan oldin lotinga o'tkazish.
- [ ] **PDF va DOCX manbalar:** `knowledge.py` ga fayl o'qigichlar qo'shish.
- [ ] **Qidiruv sifatini o'lchash:** 20–30 ta savol-javob juftligidan iborat kichik baholash to'plami.
- [ ] **Tkinter GUI:** `cli.py` mantiqini qayta ishlatadigan oddiy desktop oyna.
- [ ] **Test natijalarini saqlash:** noto'g'ri javoblarni yozib, takrorlash uchun qaytarish.
- [ ] **Hujjatlar:** ingliz tilidagi README tarjimasi.
- [ ] **Embedding asosidagi qidiruv:** BM25 ga ixtiyoriy muqobil sifatida.
