# **Adam_Gal_Projekt_objektove_technologie**

V tomto repozitáry sa nachádza prototyp hry v Pygame, ktorá je záverečným projektom pre predmet Objektové technológie  

**Autor**: Adam Gál

**Vybraná téma**: Four elements (štyri elementy)

---
## **1. Úvod**
Navrhnutá hra slúži, ako ukážka pre predmet Objektové technológie, s cieľom vytvorenia funkčného prototypu hry, ako projektu ku skúške. Vytvorená hra spĺňa požiadavky zadanej témy (Four elements). Hra má charakter toho, že hráč otvára portály tým, že stláča tlačidlá, ale medzi tým na neho útočia príšery.

### **1.1 Inšpirácia**

Tým, že nemám rád a ani nehrávam 2D hry som nemal konkrétnu inšpiráciu. Dal som dokopy mechaniky, ktoré boli pre mňa zaujímavé a následne som ich vložil do hry.

### **1.2 Herný zážitok**
Cieľom hry je, aby hráč stlačil všetky tlačidlá v časovom limite a následne otvoril portál, pričom sa nenechá poraziť veľkým množstvom nepriateľov, ktorí sa na neho rútia keď je moc blízko a pri kontakte mu spôsobujú zranenia. Hráč sa môže pohybovať po mape a zároveň keď sú spustené tlačidlá môže likvidovať nepriateľov, čím má šancu získať aj nejaké životy naspäť.

### **1.3 Vývojový softvér**
- **Pygame-CE**: zvolený programovací jazyk.
- **PyCharm 2024.3**: vybrané IDE.
- **Tiled 1.11.1**: grafický nástroj na vytváranie levelov.
- **itch.io**: zdroj grafických assetov.
- **pixabay.com**: zdroj zvukových efektov.

---
## **2. Koncept**

### **2.1 Prehľad hry**
Hráč ovláda svoju postavu a po stlačení ***Controll panelu*** sa v hre zapne časový interval 2 minúty. Počas tohto času sú zapnuté všetky tlačidlá, ktoré treba stlačiť, medzitým nepriatelia útočia na hráča. Hráč má možnosť získať nejaké životy späť ak náhodne vypadnú po zabití nepriateľa.

### **2.2 Interpretácia témy Four elements**
**"Four elements"** - hráč je počas stláčania tlačidiel prenasledovaný veľkým množstvom nepriateľov, ktorých môže zabíjať svojimi tématicky prispôsobenými abilitami, avšak nepriatelia sú opätovne generovaný do sveta. Nepriatelia majú nastavený pohyb vždy smerom k hráčovi ak je dostatočne blízko, a tak sa ho snažia premôcť aby neotvoril portál. Vo vyšších leveloch je zmenený počet generovania nepriateľov a zvýšená ich odolnosť. Levely sú tématicky robené pre 4 elementy.

### **2.3 Základné mechaniky**
- **Pohyb**: hráč a nepriatelia sa môžu pohybovať po mape iba v prípade, že sú označené, ako priechodné ("canWalk").
- **Prekážky**: na mape sa nachádzajú objekty, ktoré tvoria aktívnu prekážku, ako pre hráča, pre nepriateľov nie kôly tomu, že to narúšalo gameplay.
- **Bonusové predmety**: hráč má možnosť získať po zabití nepriateľa srdce, ktoré dopĺňa zdravie ale dá sa zobrať iba na obmedzený čas, potom zmizne.
- **Získavanie spawn pozícií pre nepriateľov**: nepriatelia sa generujú iba na tiles, ktoré sú priechodné a zároveň vo vzdialenosti väčšej, ako je detekcia hráča pri nepriateľoch.
- **Hráč môže likvidovať nepriateľov**: hráč pomocou ohnivého útoku dokáže vystreľovať ohnivú guľu, ktorá pri náraze do nepriateľa spôsobuje jeho zranenie a dáva mu efekt prehriatia, ktorý mu následne uberá, ďalším útokom háč vystreľuje ľad, ktorý má následný efekt spomalenia nepriateľa, potom vzdušný útok neuberá nepriateľom skoro nič ale zato ich odhadzuje dosť ďaleko a posledný útok je zemný, ten sa dá použiť hocikde na mape a spôsobuje dosť veľký damage ale nevýhoda je, že sa dlho nabíja.
- **Zapínanie portálu**: po zapnutí Controll panelu sa dajú postupne vypínať tlačidlá, po stlačení všetkých tlačidiel za zapne portál ak nepresiahol časový limit, inak sa proces resetuje 

### **2.4 Návrh tried**

- **Game**: Trieda obsahujúca hlavnú hernú logiku, vrátane úvodnej obrazovky, hlavnej hernej slučky, spracovania vstupov, vykresľovania herných prvkov a vyhodnotenia hry.
- **Player**: Trieda reprezentujúca hráča, jeho pohyb, interakciu s prostredím, schopnosti a spracovanie kolízií.
- **NPC**: Trieda reprezentujúca nehrateľné postavy (nepriateľov). Obsahuje logiku pohybu smerom k hráčovi, útoky, animácie, efekty (napr. spomalenie, knockback) a interakcie s prostredím.
- **NPCManager**: Trieda spravujúca nepriateľov – ich spawnovanie na náhodných pozíciách, kontrolu ich počtu a vzdialenosti od hráča, aktualizáciu a vykresľovanie.
- **FloatingText**: Trieda zobrazujúca dočasný text (napr. poškodenie) nad postavou. Pohybuje sa nahor a po určitom čase zmizne.
- **DroppedHeart**: Trieda pre srdcia, ktoré môžu nepriatelia zanechať po smrti. Hráč ich môže zbierať na obnovu života, pričom srdce zmizne po určitom čase.
- **AbilitySystem**: Trieda zodpovedná za systém schopností, umožňujúca hráčovi používať a prepínať medzi rôznymi schopnosťami.
- **Camera**: Trieda sledujúca hráča a upravujúca pohľad na hernú mapu, aby sa hráč vždy nachádzal v zobrazenom priestore.
- **Map**: Trieda spravujúca načítanie a vykresľovanie hernej mapy, vrátane teleportov, ovládacích panelov a interakcií s prostredím.
- **StaminaBar, HealthBar, TimerDisplay, AbilityDisplay**: Triedy zodpovedné za zobrazovanie používateľského rozhrania (UI), ako je stav výdrže, zdravia, časovača a vybranej schopnosti.

---
## **3. Grafika**

### **3.1 Interpretácia témy**
Hra chce byť vizuálne pekná, kde pomocou assetov z itch.io boli vybrané assety hráča a následne nepriateľov. Hráč má iba animácie pohybu zatiaľ čo nepriatelia aj animácie, ako Idle, Attack a Walk. 

<p align="center">
  <img src="https://github.com/user-attachments/assets/a8e41a57-91b6-4390-88ac-9710626c05e3" alt="Nepriatelia">
  <br>
  <em>Obrázok 3 Ukážka sprite-ov nepriateľov</em>
</p>

### **3.2 Dizajn**
V hre boli použité rôzne assety prevažne z itch.io Cieľom bolo dosiahnuť na pohľad príjemný animovaný dizajn v kontexte stredovekej fantasy. Každý level má svoje vlastné assety, iba niektoré objekty sa opakujú, ako napríklad Controll panel, tlačidlá a portál.

<p align="center">
  <img src="https://github.com/user-attachments/assets/92bd7a37-016d-4762-81be-665bcf4df57b" alt="Level dizajn">
  <br>
  <em>Obrázok 4 Ukážka dizajnu levelu</em>
</p>

---
## **4. Zvuk**

- **Link**: Hudbu aj zvukové efekty som získaval zo stránky https://pixabay.com/
- Hudba pre boj prod. by Majkyyy

### **4.1 Hudba**
Do hry som zapracoval dve hudby, jednu iba na pozadie aby pekne dokresľovala atmosféru hry a druhá pre boj hráča s nepriateľmi aby hra dostala akčnejší nádych.

### **4.2 Zvuky**
Zvuky pre jednotlivé boli pečlivo vybrané aby sedeli do mojej hry a umocňovali zážitok z hrania.

---
## **5. Herný zážitok**

### **5.1 Používateľské rozhranie**
Používateľské rozhranie bude orientované do ostatného grafického štýlu a úvodná obrazovka bude obsahovať možnosť spustiť a ukončiť hru, obrazovka pre pauzu má možnosť pokračovať v hraní alebo ukončiť hru a záverečná obrazovka má len možnosť ukončenia hry.

### **5.2 Ovládanie**
<ins>**Klávesnica**</ins>
- **WASD**: pohyb hráča po mape.
- **Klávesa F**: interakcia s controll panelom a tlačidlami
- **Klávesa ESC**: otvára pause menu
- **Klávesy 1-4**: zmena vybranej ability

<ins>**Myš**</ins> 
- **Ľavé tlačidlo**: výstrel podľa vybranej ability
- **Koliečko**: zmena vybranej ability

---
