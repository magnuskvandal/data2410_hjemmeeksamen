# README

## Hvordan kjøre programmet application.py

application.py må kjøres i enten klient- eller servermodus. Dette velges med opsjonene -s eller --server for servermodus, eller -c eller --client for klientmodus.

### Argumenter for klientmodus
application.py tar følgende argumenter for klientmodus:
- --ip      -i:        ip-adressen til server som skal kobles til 
- --port    -p:        portnummeret til server som skal kobles til 
- --file    -f:       en jpg-fil som skal sendes til server 
- --window  -w:        størrelsen på sliding window

### Argumenter for servermodus
application.py tar følgende argumenter for servermodus:
- --ip      -i:        ip-adressen til server
- --port    -p:        portnummeret til server
- --discard -d:        sekvensnummeret til pakken man ønsker å forkaste (brukes for å teste re-sending av pakker)

### Eksempler på bruk fra kommandolinjen
- python3 -c -i [ip-adress til server] -p [portnummer til server] -f [en jpg-fil] -w [vindusstørrelse du vil ha]    (klientmodus)
- python3 -s -i [servers ip-adresse] -p [servers portnummer] -d [sekvensnummer du ønsker server skal ignorere]      (servermodus)

