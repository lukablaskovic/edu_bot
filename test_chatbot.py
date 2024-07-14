import pytest
from deepeval import assert_test
from deepeval.metrics import AnswerRelevancyMetric, FaithfulnessMetric
from deepeval.test_case import LLMTestCase

CONTEXT = """
IZVEDBENI PLAN NASTAVE KOLEGIJA Kod i naziv kolegija 87243, INF007 Programsko inženjerstvo Nastavnik/nastavnica  Suradnik/suradnica doc. dr. sc. Nikola Tanković (nositelj) Studijski program Sveučilišni preddiplomski studij Informatika Vrsta kolegija Obvezan  Razina kolegija Preddiplomski Semestar Zimski  Godina studija III. Mjesto izvođenja Dvorana 402, nova zgrada FET-a „Dr. Mijo Mirković“ Jezik izvođenja Hrvatski Broj ECTS bodova 6,0 Broj sati u semestru 30P – 30V – 0S    Preduvjeti za upis i za svladavanje Odslušani kolegiji Programiranje, Baze podataka I, Napredne tehnike programiranja Korelativnost Programiranje, Baze podataka I, Baze podataka II, Strukture podataka i algoritmi, Napredne tehnike programiranja, Web aplikacije Cilj kolegija  Upoznati studente sa suvremenim tehnikama razvoja programskih aplikacija i sustava.   Savladati primjenjive paradigme, programske jezike, knjižnice i radne okvire za razvoj programskih rješenja.  Ishodi učenja 1. Prikupiti i analizirati korisničke zahtjeve 2. Primijeniti jezik UML pri oblikovanju sustava 3. Objasniti i primijeniti različite arhitekturne stilove 4. Primijeniti barem dva programska jezika i jedan okvir za razvoj aplikacija 5. Primijeniti agilnu metodu u razvoju programske podrške 6. Primijeniti metode za testiranje programske podrške i oblikovati sustav kontinuiranog testiranja 7. Timskim radom razviti kompletno programsko rješenje i pripadnu dokumentaciju koje udovoljava funkcionalnim i nefunkcionalnim zahtjevima Sadržaj kolegija 1. Uvod u programsko inženjerstvo. Metode razvoja programskih proizvoda s naglaskom na agilne metode. 2. Prikupljanje zahtjeva i prototipiranje sustava. 3. Modeliranje sustava u pomoću jezika UML. Modeli UML-a. 4. Programski jezik Javascript. Programski okvir Vue. 5. Implementacija aplikacije u oblaku pomoću okvira Vue/Javascript i usluge Firebase.
Struktura studija "Upravljanje poslovnim procesima" na prijediplomskom studiju Informatike uključuje kolegij pod nazivom "Upravljanje poslovnim procesima" (UPPFIPU) koji se izvodi u zimskom semestru treće godine studija u Puli. Kolegij nosi 6 ECTS bodova i sastoji se od 30 sati predavanja i 30 sati vježbi. Nema preduvjeta za upis kolegija, ali je potrebno položiti kolegij "Osnove IKT" za pristup testu ili ispitu.

Cilj kolegija je usvajanje kompetencija za upravljanje poslovnim procesima, dizajn modela poslovnih procesa te primjena metoda za analizu poslovnih procesa koristeći suvremene programske alate i okvire. Ishodi učenja uključuju opisivanje problematike upravljanja poslovnim procesima, objašnjavanje uloge informacijskih sustava, primjenu optimalnih načina upravljanja poslovnim procesima, usporedbu referentnih modela i metodoloških okvira te korištenje BPMN, UML i Petri Nets metoda za modeliranje poslovnih procesa.

Obvezna literatura za kolegij uključuje djela "Modeliranje poslovnih procesa" autora Brumec, J. i Brumec, S. (2018) te "Fundamentals of Business Process Management" autora Dumas, M. et al. (2013). Izborna literatura uključuje djela "Business Process Management: Concepts, Languages, Architectures" autora Weske, M. (2012) i "Upravljanje poslovnim procesima – organizacijski i informacijski pristup" autora Bosilj-Vukšić, V., Hernaus, T., Kovačić, A. (2008).

Dodatno, za kolegij "Programsko inženjerstvo" preporučena literatura uključuje knjige "Professional Software Development" autora Mike G. Miller (2020), "Software Engineering Body of Knowledge (SWEBOK)" od IEEE (2014), "Clean Architecture: A Craftsman's Guide to Software Structure and Design" autora Robert C. Martin (2017) i "Beginning Software Engineering" autora Rod Stephens (2015). Izborna literatura uključuje "Software Engineering at Google: Lessons Learned from Programming Over Time" autora Titues Winters, Tom Manshreck, Hyrum Wright (2020), dok priručna literatura uključuje "Eloquent JavaScript" autora Marijn Haverbeke (2019), "Learning Vue.js 2" autora Olga Filipova (2016) i "Version Control with Git" autora Jon Loeliger (2012).
Struktura studija UPRAVLJANJE POSLOVNIM PROCESIMA
Upravljanje poslovnim procesima
Kod i naziv kolegija: 199739, Upravljanje poslovnim procesima (UPPFIPU)
Nastavnici
izv. prof. dr. sc. Darko Etinger (nositelj)
Dario Kukuljan, mag. paed. et educ. inf.
Informacije o kolegiju
Studijski program: Informatika (prijediplomski)
Vrsta kolegija: obvezni
Razina kolegija: prijediplomski
Semestar: zimski
Godina studija: III.
Mjesto izvođenja: Pula
Jezik izvođenja: hrvatski, engleski
Broj ECTS bodova: 6
Broj sati u semestru: 30P - 30V - 0S
Korelativnost:
Fakultet organizacije i informatike Varaždin: Modeliranje poslovnih procesa
Ekonomski fakultet Zagreb: Upravljanje poslovnim procesima
Preduvjeti:
Nema preduvjeta za upis kolegija.
Preduvjet za pristup testu ili prijavu ispita je prethodno položen kolegij Osnove IKT.
Cilj kolegija
Usvojiti kompetencije za upravljanje poslovnim procesima, dizajn modela poslovnih procesa i primjena metoda
za analizu poslovnih procesa koristeći suvremene programske alate i okvire.
Ishodi učenja
1.Opisati problematiku upravljanja poslovnim procesima, interpretirati osnovna obilježja, prednosti i ne-
dostatke procesnog pristupa.
2.Objasniti ulogu integralnoga informacijskog sustava i sustava za upravljanje poslovnim procesima, u
postizanju više razine procesne zrelosti.
3.Primijeniti optimalni način upravljanja poslovnim procesima na temelju analize i prikazivanja, unaprjeđi-
vanja i mjerenja te primjene koncepta procesne zrelosti.
4.Usporediti referentne modele i metodološke okvire koji olakšavaju provedbu projekata promjene poslovnih
procesa.
5. Koristiti BPMN, UML i Petri Nets metode za modeliranje poslovnih procesa.
6. Primijeniti programske alate za oblikovanje i analizu poslovnih procesa.
Sadržaj kolegija
1. Procesni pristup - orijentacija na poslovne procese.
2. Procesno orijentirana organizacija.
3. Analiza poslovnih procesa, upravljanje poslovnim procesima.
4. Znanje u poslovnim procesima i informacijskom sustavu.
5. Organizacijski i informacijski pristup razvoju sustava za upravljanje poslovnim procesima.
6. Metode modeliranja poslovnih procesa i razvoja modela poduzeća.
7. BPMN - Business process model and notation
Stranica 214
Kolegij "Programsko inženjerstvo" na Sveučilišnom preddiplomskom studiju Informatika, kojeg vodi doc. dr. sc. Nikola Tanković, obvezan je za treću godinu studija u zimskom semestru. Kolegij se održava u dvorani 402 nove zgrade FET-a „Dr. Mijo Mirković“ na hrvatskom jeziku i nosi 6 ECTS bodova. Preduvjeti za upis uključuju odslušane kolegije Programiranje, Baze podataka I i Napredne tehnike programiranja. Cilj kolegija je upoznati studente sa suvremenim tehnikama razvoja programskih aplikacija i sustava, te savladati primjenjive paradigme, programske jezike, knjižnice i radne okvire.

Ishodi učenja uključuju prikupljanje i analizu korisničkih zahtjeva, primjenu UML jezika, objašnjavanje i primjenu različitih arhitekturnih stilova, korištenje barem dva programska jezika i jednog okvira za razvoj aplikacija, primjenu agilne metode, metode za testiranje programske podrške i oblikovanje sustava kontinuiranog testiranja, te timski rad na razvoju kompletnog programskog rješenja.

Sadržaj kolegija obuhvaća uvod u programsko inženjerstvo, prikupljanje zahtjeva i prototipiranje sustava, modeliranje sustava pomoću UML-a, programski jezik Javascript i okvir Vue, implementaciju aplikacije u oblaku pomoću Vue/Javascript i Firebase, alate za upravljanje inačicama koda (Git, GitHub), sustave za pohranu podataka u oblaku (Firebase Firestore i Storage), te verifikaciju programske podrške (unit testovi, end-to-end testovi, sustav za kontinuiranu integraciju).

Studenti su obvezni pohađati nastavu, izraditi projektni zadatak, pristupiti kontrolnim zadaćama i usmenom ispitu. Projektni zadatak nosi 50% ocjene, kontrolne zadaće 10%, a usmeni ispit 40%. Da bi položili kolegij, studenti moraju ostvariti najmanje 50% bodova putem aktivnosti kontinuiranog praćenja ili pristupiti završnom ispitu.
6. Alati za upravljanjem inačicama programskog koda. Alat Git, usluga GitHub i proces kolaborativnog razvoja. 7. Sustavi za pohranu podataka u oblaku Firebase Firestore i Storage. 8. Verifikacija programske podrške. Unit testovi i testovi end-to-end tipa. Sustav za kontinuiranu integraciju softvera.
Planirane aktivnosti, metode učenja i poučavanja i načini vrednovanja Obveze Ishodi Sati ECTS Maksimalni udio u ocjeni (%) Pohađanje nastave  1-6 28 1,0 0%  Projekt  1-7 98 3,5 50%  Kontrolne zadaće  1-6 14 0,5 10%  Usmeni ispit  1-6  28 1,0 40%  Ukupno 168 6,0 100%  Dodatna pojašnjenja (kriteriji ocjenjivanja):  Pohađanje nastave: Tijekom predavanja se studentima prezentiraju koncepti vezani uz razvoj raspodijeljenih višeslojnih aplikacija te se isti ilustriraju praktičnim primjerima kroz vježbe u računalnom laboratoriju.   Projektni zadatak: Studenti su dužni samostalno odabrati temu projektnoga zadataka koju im odobrava nastavnik. Unaprijed će se definirati tematski okvir i potrebna količina funkcionalnosti. Pri izradi projektnog zadatka moguće je samostalno odabrati korištene programske jezike i okvire. Projektni zadatak potrebno je realizirati kroz dvije komponente: prototip aplikacije i sama aplikacija. Studenti su dužni izrađen projekt postaviti na jedan od sustava za upravljanje inačicama izvorišnog koda pomoću kojega će se pratiti napredak u izgradnji projekta te dodatno postaviti poveznicu na izvorišni kod na za to predviđeno mjesto na e-učenju. Uspješno obranjen projekt nosi najviše 50 bodova, od čega se 5 bodova odnosi na prototip, 20 bodova na komponente klijenta, 20 bodova na komponente poslužitelja i 5 bodova na izlaganje projekta. Korištenje tuđeg rješenja (plagijat) je zabranjeno te povlači disciplinsku odgovornost.  Kontrolne zadaće: Tijekom izvođenja nastave provest će se provjere znanja koje će razmjerno pridonijeti konačnim bodovima u maksimalnom iznosu od 10%. Svaka provjera sastoji se u ostvarivanju tražene funkcionalnosti pomoću skriptnih jezika i biblioteka obrađenih kroz prethodna predavanja.  Usmeni ispit: Na usmenom ispitu u zadnjem tjednu nastave utvrđuje se poznavanje iznesene građe kolegija sukladno ishodima učenja. Moguće je ostvariti do 40% bodova.  Ispit je položen ukoliko je student putem aktivnosti kontinuiranog praćenja tijekom semestra ostvari najmanje 50% bodova. Ocjena kontinuiranog praćenja se temeljem ostvarenih bodova oblikuje prema sljedećoj skali:
Tekst pruža osnovne informacije o varijablama i operatorima u JavaScriptu, uključujući pravila za deklaraciju varijabli s `const`, različite tipove podataka, te korištenje stringova i eksponencijalne notacije. Objašnjava osnovne operatore kao što su aritmetički, pridruživanja, usporedni, logički i tipa operatori, te njihovu upotrebu. JavaScript se koristi za izradu interaktivnih web stranica, kao i za server-side, desktop i mobilne aplikacije. Postoje tri načina pisanja JavaScript koda u web pregledniku: inline, internal i external JavaScript.

Tekst također pokriva kontrolne strukture poput if-else, logičke operatore, uvjete za dobivanje zajma, iteracije i petlje, te korištenje break i continue naredbi. Detaljno se razrađuju funkcije, njihova deklaracija, pozivanje i različiti načini korištenja, uključujući funkcije višeg reda i rekurziju. Objašnjava se validacija forme i daje primjere funkcija za različite zadatke.

Struktura studija "Upravljanje poslovnim procesima" na prijediplomskom studiju Informatike uključuje kolegij "Upravljanje poslovnim procesima" koji se izvodi u zimskom semestru treće godine u Puli. Kolegij nosi 6 ECTS bodova, sastoji se od 30 sati predavanja i 30 sati vježbi, te nema preduvjeta za upis, ali je potrebno položiti kolegij "Osnove IKT". Cilj kolegija je usvajanje kompetencija za upravljanje poslovnim procesima, dizajn modela poslovnih procesa te primjena metoda za analizu poslovnih procesa koristeći suvremene alate i okvire.

Kolegij "Programsko inženjerstvo" na Sveučilišnom preddiplomskom studiju Informatika, kojeg vodi doc. dr. sc. Nikola Tanković, obvezan je za treću godinu studija u zimskom semestru. Kolegij se održava u dvorani 402 nove zgrade FET-a „Dr. Mijo Mirković“ na hrvatskom jeziku i nosi 6 ECTS bodova. Preduvjeti za upis uključuju odslušane kolegije Programiranje, Baze podataka I i Napredne tehnike programiranja. Cilj kolegija je upoznati studente sa suvremenim tehnikama razvoja programskih aplikacija i sustava, te savladati primjenjive paradigme, programske jezike, knjižnice i radne okvire.

Pravilnik o studiranju na daljinu na Sveučilištu Jurja Dobrile u Puli uređuje pravila online studiranja, organizaciju nastave, sustav praćenja i vrednovanja studenata, te prava i obveze studenata. Online nastava se izvodi na hrvatskom i engleskom jeziku, a Sveučilište osigurava potrebnu računalnu podršku i kontinuirano usavršavanje nastavnog osoblja. Studenti imaju pristup online mentorima, administrativnoj i tehničkoj podršci, te materijalima za nastavu u digitalnom obliku. Studenti su dužni ispuniti minimalne tehničke uvjete za praćenje nastave, a ispiti se provode online ili u kontroliranim uvjetima. Sveučilište također ima sustav osiguravanja kvalitete koji uključuje različite postupke praćenja i unapređivanja kvalitete studijskih programa.
"""

ACTUAL_OUTPUT = """
Dragi student, šifre kolegija "Upravljanje poslovnim procesima" i "Programsko inženjerstvo" su odgovarajuće 6 ECTS bodova.
"""


EXPECTED_OUTPUT= """
Šifra kolegija "Upravljanje poslovnim procesima" je 199739, a šifra kolegija "Programsko inženjerstvo" je 87243.
"""

def test_case():
    answer_relevancy_metric = AnswerRelevancyMetric(threshold=0.5)
    faithfulness_metric = FaithfulnessMetric(threshold=0.5)
    test_case = LLMTestCase(
        input="Koje su šifre kolegija Upravljanje poslovnim procesima i Programsko inženjerstvo?",
        actual_output=ACTUAL_OUTPUT,
        expected_output=EXPECTED_OUTPUT,
        retrieval_context=[CONTEXT]
    )
    assert_test(test_case, [answer_relevancy_metric, faithfulness_metric])

if __name__ == "__main__":
    test_case()
