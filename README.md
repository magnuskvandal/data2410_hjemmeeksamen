# Hjemmeeksamen i DATA2410 Nettverk og skytjenester, vår 2024
Dette er min implementasjon av et enkelt filoverføringsprogram som benytter DATA2410 Reliable Transport Protocol (DRTP). Protokollen er implementert på toppen av UDP og sikrer pålitelig og ordnet overføring av data. Eksamenoppgaven finnes her: https://github.com/safiqul/DRTP-v25 (samme oppgave som i 2024)

## Hvordan bruke application.py

Start først server, og deretter klienten i et nytt terminalvindu.

Serveren startes slik:

`python3 application.py -s`

Klienten starter du slik:

`python3 application.py -c -f <filnavn>`

Klienten vil da prøve å sende filen "filnavn" til serveren ved å bruke standard IP-adresse (127.0.0.1) og portnummer (8088). Filen må være en JPG-fil. 

## Argumenter
Både server og klient har noen valgfrie argumenter. 
> **MERK** Bruk alltid samme IP-adresse og portnummer for både server og klient, ellers vil ikke klienten kunne koble til serveren.
### Argumenter for klientmodus
application.py tar følgende argumenter for klientmodus:
- --ip      -i:        ip-adressen til server. Standardverdien er satt til 127.0.0.1
- --port    -p:        portnummeret server lytter på. Standardverdien er satt til 8088
- --file    -f:        en jpg-fil som skal sendes til server.
- --window  -w:        størrelsen på sliding window. Standardstørrelsen er satt til 3

Eksempel på bruk fra kommandolinjen:

`python3 application.py -c -i <ip-adresse_til_server> -p <portnummer_til_server> -f <en_jpg-fil> -w <vindusstørrelse>` 

### Argumenter for servermodus
application.py tar følgende argumenter for servermodus:
- --ip      -i:        ip-adressen til server. Standardverdien er satt til 127.0.0.1
- --port    -p:        portnummeret til server. Standardverdien er satt til 8088
- --discard -d:        Angir sekvensnummeret til datapakken som skal forkastes, og brukes for å teste mekanismen for re-sending av datapakker. Dersom -d 2 angis, forkastes datapakke nr. 2.

Eksempel på bruk fra kommandolinjen:

`python3 application.py -s -i <servers_ip-adresse> -p <servers_portnummer> -d <sekvensnummer_som_skal_ignoreres>`



