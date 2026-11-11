# LexJarvis

O'zbek tilidagi ochiq manbali **yuridik o'quv yordamchisi**, [Claude](https://claude.com) asosida.
Asosiy g'oya: **faqat siz bergan manbalarga tayanib javob beradi** — modda raqamlari va qonun
matnini o'zidan to'qimaydi.

## Nima uchun?

DTM "Davlat va huquq asoslari" imtihonida savollar ko'pincha darslikdan emas, kodekslar va
qonunlarning aniq matnidan keladi. Umumiy AI yordamchilar esa ba'zan ishonarli, lekin noto'g'ri
modda raqamlarini aytadi. LexJarvis bu muammoni shunday hal qiladi:

* **Manbaga asoslangan javoblar:** savol bo'yicha eng mos matn parchalari topiladi va Claude'ga
faqat shular beriladi; har bir fikr `\[fayl.md#N]` havolasi bilan ko'rsatiladi.
* **Manba topilmasa — javob yo'q:** model umuman chaqirilmaydi, sizga qaysi matn yetishmasligi aytiladi.
* **DTM uslubidagi testlar:** mavzu bo'yicha 4 variantli savollar, izoh va manba havolasi bilan.
* **Ochiq va mahalliy:** manbalar kompyuteringizda qoladi, qidiruv hech qanday qo'shimcha xizmatsiz ishlaydi.

## O'rnatish

```bash
git clone https://github.com/<Maxmudjonorifov>/lexjarvis.git
cd lexjarvis
python -m venv .venv \&\& source .venv/bin/activate   # Windows: .venv\\Scripts\\activate
pip install -e .
export ANTHROPIC\_API\_KEY="sk-ant-..."                # Windows: set ANTHROPIC\_API\_KEY=...
```

API kalitini [Claude Console](https://platform.claude.com) dan olasiz. Model `LEXJARVIS\_MODEL`
muhit o'zgaruvchisi orqali almashtiriladi (standart: `claude-sonnet-5-5`).

## Ishlatish

Avval manbalaringizni qo'shing: `sources/` papkasiga kodeks, qonun yoki konspekt matnlarini
`.md` / `.txt` formatida joylang (rasmiy matnlar: [lex.uz](https://lex.uz); foydalanish shartlarini
tekshiring). Shaxsiy matnlar uchun `sources/private/` ishlating — u git'ga kirmaydi.

```bash
lexjarvis --sources sources ask "Huquq normasi qanday qismlardan iborat?"
lexjarvis --sources sources chat
lexjarvis --sources sources quiz "huquq normasi" -n 5
```

`sources/example/namuna.md` — kichik namuna matn (rasmiy manba emas), tizimni sinash uchun.

## Qanday ishlaydi

```
sources/\*.md ──► bo'laklash (sarlavha bo'yicha) ──► BM25 qidiruv ──► top-4 parcha
                                                                        │
         javob + \[havolalar] ◄── Claude (faqat <manba> ga tayanadi) ◄──┘
```

Kod `src/lexjarvis/` ichida: `knowledge.py` (qidiruv), `tutor.py` (Claude bilan ishlash),
`prompts.py` (o'zbekcha tizim ko'rsatmalari), `cli.py` (buyruqlar).

## Cheklovlar (ochiq aytamiz)

* Bu **o'quv vositasi**, huquqiy maslahat emas. Real ishlar uchun advokatga murojaat qiling.
* Javob sifati manbalaringiz to'liqligi va yangiligiga bog'liq: qonunlar o'zgaradi, matnni yangilab turing.
* Qidiruv hozircha oddiy (BM25 + qisqartirilgan so'z boshi). O'zbek tili morfologiyasi uchun
yaxshilash kerak — [CONTRIBUTING.md](CONTRIBUTING.md) ga qarang.
* Model xato qilishi mumkin; muhim joylarda havola qilingan manbani o'zingiz tekshiring.

## Hissa qo'shish

Yangi kontributorlar xush kelibsiz! Boshlash uchun [CONTRIBUTING.md](CONTRIBUTING.md) va
`good first issue` ro'yxatiga qarang.

## Litsenziya

MIT — [LICENSE](LICENSE).

