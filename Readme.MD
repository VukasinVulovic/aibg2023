# Projekat za 2023 AIBG takmicenje
Ovo je projekat za takmicenje AIBG 2023

## Cilj
Cilj je napraviti AI koji će se boriti protiv drugih AI botova.
Cilj igre je da se sa lobonjom igrača dostigne centar polja.

## Pravila
Pravila su definisana kao ilegali potezi

### Ilegalni potezi
- Action is null.
- Nemate tri parametra vaše akcije.
- Pokušavate da pređete granice mape.
- Poslata pogrešna akcija.
- Niste uneli koordinate u pravom formatu.
- Pokušali ste da se pomerite na polje koje je tipa FULL ili Player.
- Pokušavate da pređete na polje koje nije pored vas.
- Pokušavate napasti igraca koji vam nije u range-u.
- Pokušali ste da napadnete stenu.
- Pokušali ste da zakoračite na stenu.
- Pokušali ste da napadnete lišće.
- Pokušali ste da zakoračite na drvo.
- Pokušali ste da napadnete kovčeg.
- Pokušali ste da napadnete prazno polje (Empty).
- Pokušali ste da zakoračite na drugog igrača.
- Pokušali ste da napadnete samog sebe.
- Pokušali ste da zakoračite na liticu.
- Pokušali ste da napadnete liticu.
- Pokušali ste da napadnete lobanju.
- Pokušali ste da stanete na polje centralne lobanje, ali nemate lobanju žrtve.

## Plan rada
Potrebno je detaljno analiyirati zadati zadatak.
Nakon toga je potrebno kodirati glavnu stukturu (API pozivi i strukture)
Potrebno je osmisliti najbolju strategiju za ovo

### Ispostavljenje komunikacije sa API

## API
1. Potrebno je poslati json body sa parametrima "username" i "password" na endpoint /user/login metodom POST
Ovaj poziv vraća jwt token koji će biti korišćen za dalju komunikaciju

2. Kako bi se kreirala igrica, potrebno je poslati POST request na endpoint /game/createGame sa json body koje ima parametre "playerUsernames" i "mapName".
playerUsernames je tipa string array i sadži igrače koji će biti dodani u igru

3. Za ulazak u postojeću igru, potrebno je poslati GET request na endpoint /game/joinGame
Nakon uspešnog izvršenja, response će sadržati stanje igre.

### Testiranje
Za testiranje bota putem API potrebno je uraditi sledeće korake:
1. Potrebno je kreirati listu username-a koji rade kao test igrači (imeTima1, imeTima2, imeTima3, imeTima4)

### Autorizacija
Autorizacja putem post requesta na endpoint *endpioint* sa basic auth kredencijalima.
Vraća jwt token.

### Najbitnije akcije
Attack - napadni protivnika/drvo
Move - pomeri se na poziciju