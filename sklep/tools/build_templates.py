import json, re
IMG = lambda n: f"shopify://shop_images/{n}"
def blocks(prefix, items):
    b = {}; order = []
    for i, (typ, settings) in enumerate(items, 1):
        k = f"{prefix}_{i}"; b[k] = {"type": typ, "settings": settings}; order.append(k)
    return b, order
S = {}; ORDER = []
def add(key, typ, settings, items=None, prefix="b"):
    d = {"type": typ, "settings": settings}
    if items:
        d["blocks"], d["block_order"] = blocks(prefix, items)
    S[key] = d; ORDER.append(key)

add("ks_hero", "ks-hero", {
  "product": "PRODUCT_PLACEHOLDER", "logo": IMG("ks-logo.png"),
  "eyebrow": "Dla opiekunów kociąt",
  "heading": "Twój kot nie jest agresywny. Po prostu jesteś jedyną rzeczą w domu, która się rusza.",
  "subheading": "Daj mu przeciwnika do zapasów, którego wolno gryźć i kopać. Twoje ręce zostają całe.",
  "points": "Długi rękaw chroni dłoń i przedramię\nKot gryzie i kopie pacynkę zamiast ciebie\nW zestawie pacynka i rękawica",
  "one_label": "1 pacynka", "one_sub": "Dla jednego kota",
  "two_label": "2 pacynki", "two_sub": "Druga 50 zł taniej. Dla dwóch kotów albo na prezent",
  "second_discount": 50, "button": "Dodaj do koszyka",
  "trust": "Darmowa dostawa|30 dni na zwrot|Numer do śledzenia paczki"
}, [("image", {"image": IMG("ks-hero.jpg"), "alt": "Kocię atakuje pacynkę Sparing Kot na ręce"}),
    ("image", {"image": IMG("ks-packshot.jpg"), "alt": "Pacynka Sparing Kot z długim rękawem"}),
    ("image", {"image": IMG("ks-lifestyle2.jpg"), "alt": "Kot kopie pacynkę tylnymi łapami"}),
    ("image", {"image": IMG("ks-step2.jpg"), "alt": "Kocię szykuje się do skoku na pacynkę"}),
    ("image", {"image": IMG("ks-after.jpg"), "alt": "Kocię przytula pacynkę na ręce"})], "img")
add("ks_bar", "ks-bar", {}, [
  ("item", {"strong": "1 do 3 dni", "text": "na wysyłkę"}),
  ("item", {"strong": "6 do 10 dni", "text": "roboczych dostawy"}),
  ("item", {"strong": "Numer", "text": "do śledzenia paczki"}),
  ("item", {"strong": "30 dni", "text": "na zwrot, polski adres"})], "bar")
add("ks_problem", "ks-problem", {
  "image": IMG("ks-before.jpg"), "alt": "Kocię gryzie dłoń z zadrapaniami", "eyebrow": "Znasz to?",
  "quote": "Masz na rękach więcej zadrapań, niż twój kot ma miesięcy.",
  "text": "<p>Kocię nie jest złośliwe. W miocie ćwiczyłoby polowanie na rodzeństwie: łapanie, gryzienie, kopanie tylnymi łapami. W mieszkaniu jedynym ruszającym się celem jesteś ty. Twoje dłonie, kostki, stopy pod kołdrą.</p><p>Uciekanie rękami tylko nakręca zabawę. Kot potrzebuje przeciwnika, którego wolno atakować.</p>"})
add("ks_steps", "ks-steps", {"eyebrow": "Jak to działa", "heading": "Kot dostaje rodzeństwo do zapasów", "lead": "Trzy kroki, bez nauki i bez baterii."}, [
  ("step", {"image": IMG("ks-step1.jpg"), "title": "Zakładasz na rękę", "text": "Wsuwasz dłoń do środka pacynki, a długi rękaw zakrywa przedramię aż do łokcia."}),
  ("step", {"image": IMG("ks-step2.jpg"), "title": "Kot poluje", "text": "Poruszasz łapkami i głową pacynki. Kot widzi przeciwnika, a nie twoje palce, i atakuje z pełną siłą."}),
  ("step", {"image": IMG("ks-step3.jpg"), "title": "Kot odpoczywa", "text": "Kilkanaście minut zapasów i kot ma gdzie wyładować energię. Potem zwykle przychodzi pora na drzemkę."})], "step")
add("ks_ba", "ks-before-after", {"eyebrow": "Przed i po", "heading": "Ten sam kot, te same zęby, inne ręce",
  "before": IMG("ks-before.jpg"), "before_label": "Przed", "before_text": "Kot gryzie dłonie, bo nie ma nic innego do łapania.",
  "after": IMG("ks-after.jpg"), "after_label": "Po", "after_text": "Kot gryzie pacynkę, a przedramię jest w osłonie."})
add("ks_foryou", "ks-for-you", {"eyebrow": "Czy to dla Ciebie", "heading": "Rozpoznajesz się?"}, [
  ("persona", {"who": "Masz pierwszego kota, kocię", "text": "Twój kot nie jest agresywny. Po prostu jesteś jedyną rzeczą w domu, która się rusza."}),
  ("persona", {"who": "Kot budzi cię w nocy", "text": "Jest 4:30, a kot właśnie skoczył ci na stopy, bo przez cały dzień nie miał się z kim wyszaleć."}),
  ("persona", {"who": "W domu jest małe dziecko", "text": "Twoje dziecko chowa nogi pod kocem, bo kot poluje na każdy ruch."})], "who")
add("ks_kit", "ks-kit", {"eyebrow": "Co dostajesz", "heading": "W paczce", "image": IMG("ks-kit.jpg")}, [
  ("item", {"num": "1", "label": "pacynka z długim rękawem"}),
  ("item", {"num": "1", "label": "rękawica"}),
  ("item", {"num": "53 × 22 × 10 cm", "label": "wymiary"}),
  ("item", {"num": "170 g", "label": "waga"})], "kit")
add("ks_compare", "ks-compare", {"eyebrow": "Porównanie", "heading": "A czym bawisz się z kotem dziś?",
  "col1": "Sparing Kot", "col2": "Gołe ręce", "col3": "Gruba rękawica", "col4": "Wędka z piórkiem"}, [
  ("row", {"label": "Kot może gryźć i kopać z całej siły", "values": "tak|nie|tak|nie"}),
  ("row", {"label": "Dłoń i przedramię chronione", "values": "tak|nie|częściowo|tak"}),
  ("row", {"label": "Zapasy jak z rodzeństwem", "values": "tak|tak|tak|nie"}),
  ("row", {"label": "Kot łapie zabawkę, a nie twoją rękę", "values": "tak|nie|nie|tak"})], "row")
add("ks_reviews", "ks-reviews", {"eyebrow": "Opinie", "heading": "Co mówią opiekunowie kotów"})
add("ks_shipping", "ks-shipping", {"eyebrow": "Dostawa i zwroty", "heading": "Mówimy wprost, ile to trwa",
  "lead": "Paczka jedzie z magazynu naszego dostawcy w Chinach. Nie udajemy, że to 24 godziny.",
  "link": "/pages/dostawa-i-zwroty", "link_label": "Pełne zasady dostawy i zwrotów"}, [
  ("step", {"days": "Dzień 0", "text": "Zamawiasz i dostajesz mail z potwierdzeniem."}),
  ("step", {"days": "1 do 3 dni", "text": "Przygotowujemy i wysyłamy paczkę. Dostajesz numer do śledzenia."}),
  ("step", {"days": "6 do 10 dni", "text": "Roboczych. Paczka jedzie do Polski i trafia do ciebie."}),
  ("step", {"days": "30 dni", "text": "Na zwrot od dnia otrzymania, na polski adres."})], "ship")
add("ks_guarantee", "ks-guarantee", {"days": "30", "days_label": "dni gwarancji", "eyebrow": "Gwarancja zabawy",
  "heading": "Kot się nie bawi? Oddajemy pieniądze",
  "text": "<p>Jeśli w ciągu 30 dni od otrzymania paczki twój kot nie zechce się bawić pacynką, napisz do nas. Odeślij ją na polski adres, a oddamy 100% ceny produktu, także gdy była używana.</p><p>Koszt odesłania pokrywa kupujący. Jeśli produkt przyszedł uszkodzony, pokrywamy go my.</p>"})
add("ks_faq", "ks-faq", {"eyebrow": "Pytania", "heading": "Zanim zamówisz"}, [
  ("qa", {"q": "Co jeśli mój kot się wystraszy?", "a": "<p>Niektóre koty na początku podchodzą ostrożnie do nowej zabawki z twarzą. Połóż pacynkę na podłodze i pozwól kotu ją obwąchać. Potem poruszaj nią powoli z daleka, bez podsuwania pod nos. Kilka krótkich sesji działa lepiej niż jedna długa. Jeśli po 30 dniach kot dalej nie chce się bawić, obowiązuje gwarancja zabawy.</p>"}),
  ("qa", {"q": "Czy kot nie nauczy się atakować rąk?", "a": "<p>Dłoń jest schowana w pacynce, więc kot łapie pacynkę, a nie palce. Poza zapasami nie bawimy się z kotem gołymi rękami, wtedy łatwiej mu odróżnić jedno od drugiego.</p>"}),
  ("qa", {"q": "Skąd idzie paczka i ile to trwa?", "a": "<p>Z magazynu naszego dostawcy w Chinach. Wysyłka w 1 do 3 dni roboczych, dostawa 6 do 10 dni roboczych, łącznie zwykle 7 do 13 dni roboczych. Numer do śledzenia dostajesz mailem.</p>"}),
  ("qa", {"q": "Co jeśli paczka nie dotrze?", "a": "<p>Napisz na kocisparing@gmail.com. Wyjaśnimy sprawę z przewoźnikiem, a jeśli paczka zaginęła, wyślemy nową albo zwrócimy pieniądze.</p>"}),
  ("qa", {"q": "Czy pasuje na moją rękę?", "a": "<p>Pacynkę zakłada się jak długą rękawicę na dłoń i przedramię. Wymiary to 53 × 22 × 10 cm.</p>"}),
  ("qa", {"q": "Od jakiego wieku kota?", "a": "<p>Najwięcej energii do zapasów mają kocięta od około 4 miesięcy i młode koty. Starsze koty też się bawią, zwykle krócej. Zabawa zawsze pod twoją opieką.</p>"}),
  ("qa", {"q": "Jak ją czyścić?", "a": "<p>Ręcznie, w letniej wodzie z łagodnym środkiem, a potem suszenie na płasko. Nie wrzucaj do suszarki.</p>"}),
  ("qa", {"q": "Co jest w paczce?", "a": "<p>Pacynka z długim rękawem i rękawica, po 1 sztuce.</p>"})], "qa")
add("ks_footer", "ks-footer", {"company": "<p>KociSparing, [IMIĘ I NAZWISKO SPRZEDAWCY], [ADRES SPRZEDAWCY]<br>Kontakt: kocisparing@gmail.com</p>"}, [
  ("link", {"label": "Regulamin", "link": "/pages/regulamin"}),
  ("link", {"label": "Dostawa i zwroty", "link": "/pages/dostawa-i-zwroty"}),
  ("link", {"label": "Kontakt", "link": "/pages/kontakt"}),
  ("link", {"label": "Polityka prywatności", "link": "/policies/privacy-policy"})], "link")
add("ks_sticky", "ks-sticky", {"product": "PRODUCT_PLACEHOLDER", "note": "Darmowa dostawa", "button": "Do koszyka"})

txt = json.dumps({"sections": S, "order": ORDER}, ensure_ascii=False, indent=2)
for bad in [" – ", " — ", " - "]:
    assert bad not in txt, bad
open('/home/user/moj-projekt/sklep/theme/templates/product.ks-landing.json','w').write(txt.replace('"product": "PRODUCT_PLACEHOLDER", ', '').replace(',\n        "product": "PRODUCT_PLACEHOLDER"', ''))
open('/home/user/moj-projekt/sklep/theme/templates/index.json','w').write(txt.replace('PRODUCT_PLACEHOLDER','sparing-kot'))
print("ok", len(txt))
