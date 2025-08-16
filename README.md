Entwicklung einer nutzerspezifischen Lebensmittelmanagement-Webanwendung mit inkludiertem Reinforcement-Learning

Bei der Anwendung, welche im Rahmen der Studienarbeit entwickelt wird, handelt es sich um eine Webanwendung, in welcher die Vorräte eines Nutzers nach dem Mindesthaltbarkeitsdatum strukturiert dargestellt werden. Der Nutzer kann diese Struktur selbst mit den eingekauften Lebensmitteln befüllen, wofür er den Namen des Lebensmittels, die Anzahl und das Mindesthaltbarkeitsdatum angibt. Im Anschluss sortiert die Anwendung die neu hinzugefügten Lebensmittel automatisch in eine Übersicht, welche angibt, ob das Lebensmittel bereits abgelaufen ist oder es noch länger haltbar ist. Über Buttons in der Übersicht kann er nach dem Verbrauch das Lebensmittel löschen und somit der Anwendung vermitteln, dass dieses konsumiert ist. Weiterhin ist es möglich in einzelnen Schritten (über -1 oder +1) neue Produkte mit demselben MHD hinzuzufügen oder die Anzahl im Bestand zu verringern, sollte von einem Produkt die Menge verringert worden sein. Weiterhin soll dem Nutzer angezeigt werden, inwiefern er durch sein persönliches Verhalten in der Vergangenheit davon ausgehen muss, dass er dieses spezielle Lebensmittel vor oder nach dem MHD konsumiert. 


Systemarchitektur

- Frontend: Django Templates (HTML)
- Backend: Django Framework mit Python
- Datenbank: SQLite
- Machine Learning: Reinforcement Learning Modell (Multi-Armed Bandits Modell)
- Hosting: PythonAnywhere


Installation 

Repository klonen:
git clone https://github.com/sheeshmann/studienarbeit_softwareparadigmen.git
cd studienarbeit_softwareparadigmen