# opravidlo annotations

### TODO pro vás:
1. mít github účet
2. naklonovat k sobě tento repozitář
3. vygenerovat si přístupové tokeny pro Kontext a Sketch Engine API a vložit je do souboru `.env` 
4. vytvořit virtuální prostředí a nainstalovat requirements
5. zkusit pustit soubory `kontext.py` a `sketch_engine.py`

### Disclaimery
- Ultimátní rada nad zlato: Když nevím, zeptám se ChatGPT:))
- Možná něco popisuju moc podrobně a něco málo, pardon... Nevím, co víte - kdyžtak se ptejte:)

### Git


### Struktura projektu
- Všechen kód patří do balíčku `opravidlo_annotations`, mimo to je jen readme, requirements a gitignore.


### Virtual environment and dependencies
- Obecně je fajn pro každý projekt mít vlastní virtuální prostředí - takovou krabičku, kde jsou uložené všechny knihovny k tomu projektu. Nemísí se to tak s dalšími projekty. Když pak končím projekt, můžu celou složku smazat a vím, že mi to nenaruší nic dalšího. Zároveň tak můžu mít třeba více verzí pythonu k různým projektům. Ne že by se nás tohle asi nějak extra týkalo, ale je to prostě best practise.
- V shellu se dostanu do složky s projektem a tam je potřeba zadat pro vytvoření toho virt. prostředí:
```
pip install virtualenv
python3 -m venv venv # první venv je příkaz, druhé venv je název tohoto konkrétního vrituálního prostředí
# vytvoří to složku venv
```
- A pak vždycky, než instaluju nové knihovny, tak to virtuální prostředí aktivuji takto (pro windows):
```
source venv/Scripts/activate
```
- pro linuxové systémy takto: `source venv/bin/activate`; a mac to má ještě asi trochu jinak :D
- že je aktivované, pak uvidím vždy na začátku řádku v shellu jako `(.venv)`
- příkaz `deactivate` zruší virtuální prostředí
- na začátek je fajn instalovat všechny knihovny a to pomocí
```
pip install -r requirements.txt
```
- Když nějakou knihovnu přidávám, tak ji napíšu do souboru `requirements.txt` - tam se udržuje seznam knihoven, co se používá.

### Environment variables (proměnné prostředí)
- Hesla a přístupové klíče a tokeny není fajn dávat na github. Protože je pak může použít kdokoliv jiný - lepší je, když má každý svůj přístup. Je to prostě bezpečnostní best-practise, i když v tomto konkrétním případě zas o tolik nejde.
- Pro nás se to týká přístupových tokenů k API Kontextu a Sketch Engine.
- Je potřeba, abyste si ve složce `opravidlo_annotations` vytvořily soubor `.env` a do něj vložily klíče ke kontext a sketch engine API a sketch engine username.

V tady takovém formátu:
```
KONTEXT_TOKEN="random_mess_of_digits_and_letters"
SKETCH_ENGINE_TOKEN="random_mess_of_digits_and_letters"
SKETCH_ENGINE_USERNAME="your_username"
``` 

- V souboru `settings.py` se pak ty klíče od vás nahrají pomocí `os.getenv("...")` do proměnných a ty proměnné se pak používají dál.
- Soubor `.env` je v `.gitignore` (= seznam věcí, co se nemají nahrát na git), takže se nikdy nenahraje na git a takto se zajistí, že všichni můžeme použít ten stejný kód, ale každý se svým přístupem a nesdílíme ho veřejně.


