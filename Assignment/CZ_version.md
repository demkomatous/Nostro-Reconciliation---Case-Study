# Zadání mezibankovní rekonciliace (Nostro / Clearing)

## Úvod do problematiky Nostro účtů

Aby mohly banky operovat s cizími měnami, musí mít účty u jiných bank, pro které je tato cizí měna měnou domácí. U těchto bank si vedou účty, tzv. Nostro účty, přes které cizoměnové transakce vypořádávají. Domácí banka je v našem případě Apex International Bank (AIB), která má pro účely tohoto zadání svůj Nostro účet pro EUR vedený u německé Eurozone Settlement Bank (ESB).

Klienti AIB každý den posílají eurové platby do celého světa. Každá tato transakce se zpracovává následovně:

1. Klient zadá požadavek na převod EUR (platební příkaz)  
2. AIB předá požadavek ESB  
3. ESB zašle AIB clearingové oznámení (tzv. clearing statement)  
4. AIB výpis schválí, nebo rozporuje  
5. ESB připíše EUR příjemci (beneficientovi)

To, co se klientům jeví jako prostý pokyn, který trvá jen pár sekund, ve skutečnosti zabere i několik dní, většinou dva. Standardně je časový harmonogram následující:

1. den:  
- Klient zadá požadavek na převod  
- AIB předá požadavek na převod ESB  
2. den  
- ESB clearingové vyrovnání  
- AIB oznámení schválí nebo rozporuje  
- ESB připíše EUR příjemci

Výše zmíněné platí pouze za předpokladu, že po sobě následující dny jsou pracovní. Během víkendu není toto vypořádání realizováno a tudíž požadavky na transakce uskutečněné klienty AIB po pracovní době nejsou odeslány ESB a neobjeví se tedy ani v pondělním výpisu. Tady nastává první nesrovnalost. AIB peníze klientovi z účtu odepsala, ale sama je ještě účetně nevypořádala s ESB. Rekonciliační analytik tuto nesrovnalost vidí, ale měl by odhalit, o jaký typ problému se jedná a podle toho s ním i naložit. Detailnější popis toho, jak s takovou transakcí naložit si ukážeme přímo při řešení konkrétních příkladů.

## Předpoklady pro cvičení

Každá banka má nastavený proces vypořádání SEPA plateb se svou protistranou jinak. Nastavme tedy předpoklady, za kterých budeme provádět rekonciliace našich modelových dat.

1. Bankovní systém je v provozu od 8:00 do 17:00  
2. Eurozone Settlement Bank si účtuje fixní poplatek 10 € za zpracování platby; žádné další poplatky žádná z bank neúčtuje

## Testová data, procesní chyby a nesrovnalosti

Jak jste pravděpodobně pochopili z předchozí kapitoly, v tomto procesu mohou nastat chyby nebo nesrovnalosti, na mnoha místech. Některé jsou sice díky eliminaci mnoha lidských kroků téměř vyloučeny, ale stále zůstává mnoho prostoru pro jejich vznik. Tyto nesrovnalosti se snažím demonstrovat na modelových datech, kterými jsou fiktivní transakce ve své co nejjednodušší podobě, ale navržené tak, aby co nejvěrněji odrážely realitu dané problematiky.

### Struktura dat – Apex International Bank

Datový set `Apex_International_Bank_transactions.csv` obsahuje data o odchozích transakcích, ke kterým dali klienti pokyn v pátek 12\. června 2026\.   
Hlavička souboru obsahuje následující pole:

- `tx_id`: Jedinečný identifikátor transakce v rámci systému Apex International Bank  
- `date`: Datum zadání transakce klientem  
- `time`: Čas zadání transakce klientem  
- `sender_acc_number`: Číslo účtu klienta v Apex International Bank  
- `beneficiary_iban`: IBAN příjemce bez regionálního omezení  
- `amount`: Částka převodu v EUR  
- `fee_type`: typ poplatku; nabývá jedné ze tří hodnot: `OUR | SHA | BEN` 
  * `OUR` – Poplatek hradí odesílatel; s bankou je vyrovnán dodatečně (tzv. off-statement); příjemci musí dorazit částka v plné výši  
  * `SHA` – Poplatek je sdílený; poplatek odesílatele je vyřízen off-statement; příjemce obdrží částku poníženou o poplatky na své straně  
  * `BEN` – Poplatek hradí příjemce; je stržen z transakce v průběhu jejího zpracování; příjemci dorazí zkrácená částka, která se v této snížené hodnotě objeví i na výpisu korespondenční banky  
- `catch`: Příznak „chytákové“ transakce, kterou je třeba v rámci cvičení odhalit; nabývá hodnot `1` (jedná se o chyták) nebo `0` (standardní transakce).

### Struktura dat – Eurozone Settlement Bank

Datový set `Eurozone_Settlement_Bank_statement.csv` obsahuje data o transakcích, které protistrana, Eurozone Settlement Bank, zpracovala a clearingově vypořádává s Apex International Bank. Tento výpis je z pondělí 15\. června 2026\.  
Hlavička souboru je:

- `ext_ref_id`: Jedinečný identifikátor transakce v rámci systému Eurozone Settlement Bank  
- `date`: Datum vypořádání (settlement date)  
- `remittance_info`: Podrobnosti o platbě (remitenda); obsahuje unikátní mezibankovní identifikátor transakce (UETR) pro spárování s AIB, případně specifický bankovní kód (`CHGS/...`, `INT.CALC/...`, `REV/...`) u transakcí iniciovaných přímo clearingovou bankou.  
- `cleared_amount`: Částka v EUR, kterou Eurozone Settlement Bank clearingově vyúčtovala vůči Apex International Bank  
- `catch`: Příznak „chytákové“ transakce, kterou je třeba v rámci cvičení odhalit. Nabývá hodnot `1` (jedná se o chyták) nebo `0` (standardní transakce)

### Procesní chyby

Tato kategorie obsahuje reálné chyby systémů nebo lidského faktoru na straně clearingové banky (Eurozone Settlement Bank). Tyto stavy vyžadují manuální zásah, podání reklamace (claimu) a v praxi znamenají přímé finanční nebo reputační riziko.

Procesní chyby jsou takové, které poškozují alespoň jednu ze stran smluvního vztahu: AIB, ESB nebo klienta AIB. Takovým poškozením může být například:

* **Chybějící transakce ve výpisu Eurozone Settlement Bank** – poškozen je klient AIB, protože jeho platba zpožděna  
* **Dvojí zaúčtování ve výpisu Eurozone Settlement Bank** – ESB zaúčtovala stejnou transakci dvakrát, čímž poškodila AIB  
* **Chybná částka `cleared_amount`** – ESB udělala chybu při započtení poplatků a vůči AIB vyúčtovala nižší, nebo naopak vyšší finanční vyrovnání  
* …

Takových procesních chyb může být opravdu celá řada. Typově je však lze rozdělit do dvou skupin:

1. Lidská chyba  
2. Chyba automatizace

Obě tyto skupiny jsou dnes v téměř 100 % případů eliminovány – ale opravdu jen téměř. Stát se může cokoliv a rekonciliační analytik musí být schopen nesrovnalost za všech okolností odhalit. Nezáleží přitom na tom, zda byla tato nesrovnalost odhalena automatizovaně nebo ručně. Oba přístupy vyžadují porozumění problematice a správné nastavení monitoringu.

### Procesní nesrovnalosti

Tyto stavy nejsou chybami v pravém slova smyslu. Jde o legitimní procesní jevy v rámci bankovních operací, které však rekonciliační analytik musí umět rozpoznat, oddělit od skutečných chyb a správně účetně ošetřit. 

Příkladem takové procesní nesrovnalosti je situace, kdy klient zadá standardní SEPA platbu ve večerních hodinách, tedy po 17:00. Podle našich předpokladů po 17\. hodině standardní bankovní systém již nepracuje, a tato transakce proto čeká na vypořádání do následujícího pracovního dne (kdy zpracování začíná v 8:00). Tyto večerní transakce tak zůstávají po určitou dobu nezaúčtované a do výpisu ESB se dostanou až další pracovní den. Pro účely našeho zadání to znamená, že transakce odeslané po 17:00 se objeví až ve výpisu, který AIB obdrží o dva dny později.

## Simulované chyby

### 1. Dvojí zaúčtování

- **Podstata:** Technická chyba na straně ESB způsobí, že jeden korektní klientský pokyn z AIB je v clearingu vypořádán vícekrát. V datech se to projeví tak, že clearingový výpis (ESB) obsahuje více samostatných řádků s unikátními `ext_ref_id`, ale všechny řádky nesou shodné UETR platby a shodnou kladnou částku.

- **Důsledek:** Pokud rekonciliační nástroj tuto duplicitu neodhalí a schválí ji, AIB odešle peníze vícekrát, čímž jí vzniká přímá finanční ztráta. Naopak na straně příjemce dochází k neoprávněnému obohacení.

### 2. Chybějící zaúčtování

- **Podstata:** ESB z technických důvodů (např. výpadek komunikačního uzlu) nezahrnula legitimní požadavek AIB do denního zúčtování. V interní evidenci (AIB) transakce existuje, ale v clearingovém výpisu (ESB) tento záznam zcela chybí.

- **Důsledek:** Klientovi AIB byly peníze z účtu zablokovány (případně již strženy), ale finanční prostředky nikdy neodešly z Nostro účtu do cílové banky. Výsledkem je nedoručená platba, penalizace za zpožděné zpracování a potenciální reklamace podaná klientem.

### 3. Chybně stržený poplatek

- **Podstata:** Clearingová banka nerespektovala instrukce o poplatcích (`fee_type`). U transakcí typu OUR (poplatky hradí plátce) a SHA (poplatky jsou rozděleny) má být clearingová částka rovna nominální hodnotě transakce. Pokud ESB nesprávně uplatní pravidla pro typ BEN (poplatek hradí příjemce), odečítá poplatek SEPA přímo z převáděné částky.

- **Dopad na data:** Jelikož jsou částky v clearingu vždy kladné, tato chyba se projeví tak, že ve výpisu ESB je uvedena nižší částka, než jakou eviduje AIB v poli `amount`. Rozdíl přesně odpovídá fixnímu bankovnímu poplatku.


- **Důsledek:** Příjemci dorazí méně peněz, než mělo. Vzniká tak ztráta buď na straně klienta, nebo ji musí kompenzovat AIB ze svých výnosů v rámci reklamačního řízení.

### 4. Nesouhlasící částka

- **Podstata:** Lidská chyba při manuálním zadávání nebo systémový glitch (např. chybná konverze měny) na straně ESB způsobí, že transakce je zaúčtována v naprosto chybné výši, přičemž tento rozdíl nelze vysvětlit ani odchylkou ve výši poplatku.

- **Dopad na data:** Obě strany sice sdílejí stejnou UETR referenci, ale částka v interním systému AIB (`amount`) nesouhlasí s částkou ve výpisu ESB (`cleared_amount`).


- **Důsledek:** Asymetrické riziko. Pokud clearingová banka zaúčtuje vyšší částku, z Nostro účtu AIB odejde více peněz, než klient požadoval (ztráta pro AIB). Pokud naopak ESB zaúčtuje nižší částku, odejde méně peněz,  transakce je nekompletní a vzniká ztráta pro ESB, která musí rozdíl doplácet ze svých vlastních zdrojů.

### 5. Chybně směrované transakce

- **Podstata:** Systém clearingové banky špatně spároval nebo směroval transakce, v důsledku čehož se do clearingového výpisu Nostro účtu AIB dostaly operace patřící Nostro účtu jiné banky (která má svůj Nostro účet rovněž vedený u ESB). 

- **Dopad na data:** Ve výpisu ESB existují záznamy, které v poli `remittance_info` sice obsahují klientskou referenci UETR, avšak toto UETR neodpovídá žádné transakci v interním systému AIB.

- **Důsledek**: Pokud by AIB takovou transakci schválila, vypořádala by platbu, kterou její vlastní klienti nikdy nezadali. Jelikož peníze není komu na straně AIB strhnout, banka by musela tento převod pokrýt ze svých vlastních zdrojů, což by znamenalo přímou finanční ztrátu.

## Simulované procesní nesrovnalosti

### 1. Chybějící zaúčtování transakce po 17\. hodině

- **Podstata:** Každý clearingový systém má svůj uzávěrkový čas (Cut-off time), který je v našich předpokladech stanoven na 17:00. Transakce zadané klienty po tomto čase sice AIB okamžitě zpracuje, ale clearingová banka je z logiky mezibankovního vypořádání zahrne až do zúčtování za následující (do samotného výpisu se tak dostanou o dva dny později)

 

- **Dopad na data:** V aktuální denní rekonciliaci se tato transakce jeví jako „chybějící ve výpisu Eurozone Settlement Bank“ (v AIB existuje, v ESB výpisu chybí).

- **Důsledek:** Nejedná se o chybu. Rekonciliační program musí tyto transakce identifikovat podle času zadání (17:00–23:59), automaticky je převést na tranzitní/přechodný účet a označit jako tzv. Outstanding Items (položky na cestě). Tím dochází k vytvoření dočasného otevřeného zůstatku na tomto tranzitním účtu, který se vyrovná, jakmile dorazí další výpis.

### 2. Položky iniciované clearingovou bankou

- **Podstata:** V clearingovém výpisu od ESB se objeví řádky s kladnou částkou, pro které v systémech AIB neexistuje žádný klientský pokyn (UETR reference). V praxi se jedná o transakce iniciované samotnou clearingovou bankou – nejčastěji jde o pravidelné poplatky za vedení Nostro účtu, připsané kreditní úroky, nebo opravné účtování z minulosti (reversals).

- **Dopad na data:** Ve výpisu ESB existují záznamy, které v `remittance_info` neobsahují klientskou referenci (UETR), ale specifický bankovní kód (např. `CHGS/...`, `INT.CALC/...`, `REV/...`). V systému AIB k těmto operacím neexistuje žádný protějšek.  
* **`CHGS/PERIODIC/MAINTENANCE FEE MAY 2026`**: Clearingová banka si účtuje poplatek za vedení účtu za měsíc květen  
* **`INT.CALC/CREDIT INTEREST BASE VALUE`**: Clearingová banka nám připisuje úrok za držení kladného zůstatku na Nostro účtu  
* **`SEPA SETTLEMENT ADJUSTMENT NOTE`**: Vyrovnání clearingu o drobné technické (zaokrouhlení) nebo kurzové rozdíly, které vznikly během dne  
* **`TRF FROM BNP BANK SA / CUSTOMER UNKNOWN`**: Neznámá příchozí platba z jiné banky (BNP Bank); peníze dorazily na Nostro účet, ale zpráva neobsahuje žádný smysluplný identifikátor ani číslo účtu koncového klienta v AIB. Finanční prostředky musí být dohledány a přiřazeny ručně.


- **Důsledek:** Pokud by rekonciliační program takovou položku slepě schválil jako standardní platbu, banka by mohla přijít o peníze (u poplatků) nebo by vykázala nezaúčtované příjmy (u úroků). Z pohledu banky jde o hrubé porušení účetních standardů. Program musí analyzovat text zprávy a místo hlášení chyby tyto položky automaticky zařadit: poplatky poslat do nákladů banky, úroky do výnosů banky a neznámé texty předat back-office k prověření.

## Výstup cvičení

### 1. Část: Kontrola a příprava dat

Pomocí SQL odhalte všechny výše zmíněné chyby a procesní nesrovnalosti. Do obou tabulek přidejte sloupec s názvem “tag”, který bude charakterizovat stav transakce podle následující tabulky:.

| Tag | Popis stavu |
| ----- | ----- |
| MATCHED | Transakce je plně v pořádku a odsouhlasena; AIB ji schvaluje |
| ERR\_DOUBLE\_POSTING | Transakce byla v clearingu vypořádána dvakrát (dvojí zaúčtování) |
| ERR\_MISROUTED\_TRANSACTION | Ve výpisu ESB se nachází transakce, kterou interní systém AIB vůbec neeviduje |
| ERR\_FEE\_MISMATCH | Ve výpisu ESB došlo k chybnému stržení poplatků (chybně stržený poplatek) |
| ERR\_MISSING\_BOOKING | Transakce byla v AIB zadána, ale clearingová banka (ESB) ji nezaúčtovala |
| ERR\_AMOUNT\_MISMATCH | U transakce nesouhlasí finanční částka mezi systémy AIB a ESB |
| OUTSTANDING\_ITEM | Transakce podle očekávání nebyla zaúčtována kvůli uzávěrce (cut-off). Očekává se její vypořádání další pracovní den (položka na cestě) |
| UNIDENTIFIED\_CUSTOMER | Transakce postrádá validní údaje v poli `remittance_info`. Příjemce nelze automaticky identifikovat a finanční prostředky je nutné dohledat a přiřadit manuálně |
| EXPENSE | Transakce představuje přímý náklad banky AIB (např. poplatky za vedení Nostro účtu) |
| REVENUE | Transakce představuje přímý výnos banky AIB (např. připsané kreditní úroky) |

### 2. Část: Vyčíslení dopadu

Pomocí SQL vyčíslete potenciální dopad na bilanci Apex International Bank v případě, že by byly odsouhlaseny veškeré transakce. Zodpovězte následující otázky:

1) O kolik peněz by AIB přišla v přímém důsledku dvojitě zaúčtovaných transakcí?  
2) Kolik finančních prostředků by AIB vynaložila na transakce, ke kterým její vlastní klienti nikdy nevydali pokyn?  
3) O kolik více by AIB zaplatila na chybně stržených poplatcích?  
4) Kolik peněz by zůstalo zmrazených (neodeslaných) v důsledku chybějícího zaúčtování ze strany ESB?  
5) Jaký je celkový nárůst objemu peněz na tranzitním (přechodném) účtu AIB jako outstanding items (položky na cestě)?  
6) Jaký objem příchozích peněz se nepodařilo automaticky připsat klientům v důsledku chybějících údajů o příjemci?   
7) Jaký je celkový absolutní objem transakcí, které byly iniciovány ESB?

### 3. Část: Denní přehled

Pomocí SQL udělejte přípravu dat pro denní přehled vedení banky. Vedení banky zajímají následující metriky:

1) K převodu jakého celkového finančního objemu dali klienti pokyn během pátku?  
2) Do jakých tří cílových zemí bylo převedeno nejvíce peněz?  
3) Do kterých pěti cílových zemí směřovalo nejvíce transakcí?  
4) Ve které denní době byli klienti nejaktivnější při zadávání plateb?  
   * Ráno \[6:00-8:30\]  
   * Dopoledne (8:30-11:30\]  
   * Poledne \[11:30-13:30\]  
   * Odpoledne (13:30-17:00)  
   * Večer \[17:00-20:00\]  
   * V noci  
5) Kolik procent plateb zadaných během pátku bylo úspěšně vypořádáno a v jakém celkovém objemu?  
6) Jaký celkový objem peněz z dnešního clearingu s ESB nebyl schválen rekonciliačním oddělením? Operace iniciované ESB by měly být považovány za schválené a neměly by být zahrnuty do objemu chyb.

### 4. Část: Denní přehled pro vedení banky v Excelu

Exportujte agregovaná data ze 3\. Části do Excelu a vytvořte funkční, vizuálně atraktivní a profesionálně naformátovaný manažerský přehled.

* Naprogramujte/nahrajte VBA makro, které automaticky aplikuje toto formátování a styl na surová data. Makro nastavte na klávesovou zkratku `CTRL \+ SHIFT \+ R`.  
* Výsledný soubor .xlsx bude sloužit jako standardizovaná datová příloha odesílaná vedení banky v rámci denního reportingu.

### 5. Část: Report pro vedení banky ve Wordu

Na základě dat a zjištění ze všech předchozích částí sestavte shrnující zprávu (Executive Summary) pro vedení AIB.

* Rozsah reportu nesmí přesáhnout jednu stranu A4.   
* Poskytněte stručnou, věcnou a srozumitelnou interpretaci klíčových faktů z dnešní rekonciliace. Nezahlcujte management detailními informacemi.  
* V textu jasně kvantifikujte zjištěné procesní problémy, vyčíslete potenciální finanční škody a popište navržená nápravná opatření pro jednotlivé typy chyb.
