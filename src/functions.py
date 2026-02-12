from socket import *
import struct
import sys
import datetime


def opprettePakke(seqNr, ackNr, flagNr, data):
    """
    Beskrivelse:
    Funksjon som oppretter en pakke bestående av header på 6 bytes og data som skal sendes. 
    Header skal bestå av feltene | Sequence Number | Acknowledgement Number | Flags | som 
    hver består av 2 bytes, (!hhh) gir dette formatet.

    Argumenter:
    - seqNr gir pakkens Sequence Number
    - ackNr gir pakkens Acknowledgement Number 
    - flagNr gir flaggnummeret 
    - data gir data som skal sendes i bytes (maks 994 bytes)

    Returnerer:
    En pakke bestående av en header på 6 bytes og data på maks 994 bytes

    Unntakshåndtering:
    Fanger "struct.error"-unntak. Dette kan oppstå om verdiene i header ikke er heltall som kan representeres
    med 2 bytes, eller hvis data ikke er en byte-streng. 
    Hvis dette skjer, skrives det ut en passende melding til skjerm og programmet avsluttes.
    """
    try:
        header = struct.pack("!hhh", seqNr, ackNr, flagNr)          # Pakke-header
        pakke = header + data                                       # Hele pakken som skal sendes
        return pakke
    except struct.error as e:
        print(f"kunne ikke opprette pakke: {e}")
        sys.exit()
    



def parsePakke(pakke):
    """
    Beskrivelse:
    Funksjon som deler en pakke opp i header og data. Denne funksjonen brukes når klienten/serveren 
    har mottatt en pakke. Den bruker struct sin unpack for å pakke ut header (6 første bytes), de
    resterende bytes (tilhørende data) legges i variabelen data.

    Argumenter:
    Tar en pakke (som beskrevet i funksjonen opprettePakke) som argument. 

    Returnerer:
    En tuple bestående av header og data

    Unntakshåndtering:
    Fanger "struct.error"-unntak. Dette kan skje om f.eks. pakken ikke er minst 6 bytes lang, 
    eller om den ikke inneholder byte-data. 
    Om dette skjer (kanskje ikke veldig sannsynlig i dette programmet), skrives det en passende
    melding til skjerm.
    """
    try:
        header = struct.unpack("!hhh", pakke[:6])           # Tuppel med heltallverdiene tilhørende header(pakkes ut i samme format som ved pakking)
        data = pakke[6:]                                    # data-bytes
        return header, data
    except struct.error as e:
        print("Kunne ikke parse pakke: " + str(e))
        sys.exit()



def parseFlags(flags):
    """
    Denne funksjonen har jeg lånt fra https://github.com/safiqul/2410/blob/main/header/header.py.
    Har bare endret dataverdien som lagres i variabelene (fra integer til boolean).
    Beskrivelse:
    Funksjon som tolker flaggverdien fra en pakkeheader og avgjør om flaggene SYN, ACK og FIN er satt.

    Argumenter:
    Tar en heltallsverdi som representerer falggfeltet i header

    Returnerer:
    En tuple bestående av boolske verdier for flaggene SYN, ACK og FIN. True om flagget er satt, False ellers.
    """
    syn = bool(flags & (1 << 3))            # Variabel som holder True om SYN er satt eller False om ikke
    ack = bool(flags & (1 << 2))            # Variabel som holder True om ACK er satt eller False om ikke
    fin = bool(flags & (1 << 1))            # Variabel som holder True om FIN er satt eller False om ikke
    return syn, ack, fin


def verdihåndtering(args):
    """
    Denne funksjonen har jeg hentet fra min egen obligatoriske innlevering fra filen args.py.
    Det er gjort noen små endringer på denne varianten, men den er i stor grad lik den funksjonen
    jeg lagde i filen args.py fra første obligatoriske innlevering. 
    Beskrivelse:
    Funksjon som sjekker om kommandolinjeverdiene tilfredstiller noen kriterier:
    - At ikke både klient- og servermodus er valgt
    - At minst en av klient- eller servermodus er valgt
    - At ikke fil oppgis ved valg av servermodus
    - At ikke discard-verdi er oppgitt sammen med klientmodus
    - At portnummeret og ip-adressen er oppgitt i riktig format 

    Argumenter:
    Kommandolinjeargumenter

    Returnerer:
    True om kommandolinjeargumentene er gyldige i henhold til kiteriene. Ellers False.

    Unntakshåndtering:
    Fanger ValueError-unntak som oppstår om man ikke oppgir heltallsverdier i ip-adressen
    """
    # Tester som håndterer argumentverdiene
    if args.server is True and args.client is True:                 # Sjekker om både klient og server er valgt
        print("Velg enten klientmodus eller servermodus")
        return False
    elif not(args.server or args.client):                           # Sjekker om verken klient eller server er valgt
        print("Må velge enten klientmodus eller servermodus")
        return False 
    else:
        if args.server is True and args.file is not None :          # Sjekker om -s og -f er satt 
            print("--file brukes kun ved valg av klientmodus")
            return False

        if args.client is True and args.discard is not None:        # Sjekker om -c og -d er satt
            print("--discard brukes kun ved valg av servermodus")
            return False

        if args.port != 8088:
            if args.port not in range(1024, 65535+1):               #Sjekker om portnummeret er gyldig
                print("Ugyldig portnummer! Den må være i intervallet [1024, 65535]")
                return False

        if args.ip != "10.0.1.2":
            ip = args.ip.split(".")             # Liste med tallverdiene fra innholdet i args.ip
            if len(ip) != 4:                    # Sjekker om formatet til IP-adressen er riktig
                print("Ugyldig IP. Adressen må være på dette formatet: 10.0.1.2 ")
                return False
            else:
                for i in ip:
                    try:
                        if int(i) not in range(0, 255+1):       # Sjekker om hver tallverdi i listen er gyldig 
                            print("Ugyldig IP. Hver tallblokk må være i intervallet [0, 255]")
                            return False
                    except ValueError as e:
                        print(f"Ikke et heltall: {e}")
                        return False
    return True




def hentFil(filnavn):
    """
    Beskrivelse:
    Funksjon som leser en jpg-fil i binær-modus og lagrer biter av filen, på maks 994 bytes, i en liste.

    Argumenter:
    Tar inn navnet(en streng) på filen som skal sendes til server.

    Returnerer:
    En liste med byte-strenger, hvor hver streng representerer en en del av filen.
    
    Unntakshåndtering:
    Fanger FileNotFoundError om ikke filen som skal leses finnes. 
    Fanger også OSError for andre feil som kan oppstå knyttet til lesing av filen.
    Om en unntak fanges, avsluttes programmet.
    """
    if filnavn is None:
        print("Må oppgi en fil")
        sys.exit()
    if not filnavn.lower().endswith(".jpg"):
        print("Feil filtype. Vennligst oppgi en jpg-fil")
        sys.exit()
    try:
        dataliste = []                              # Listen som skal inneholde filen
        with open(filnavn, "rb") as fil:
            while True:
                datablokk = fil.read(994)           # Hver bit av filen som legges til listen er på maks 994 bytes
                if not datablokk:                   # Avslutter om datablokk er tom
                    break
                dataliste.append(datablokk)
            return dataliste
    except FileNotFoundError:
        print(f"Fant ikke filen: {filnavn}")
        sys.exit()
    except OSError as e:
        print(f"Kunne ikke lese filen: {filnavn}: {e}")
        sys.exit()




def lagreFil(filnavn, data):
    """
    Beskrivelse:
    Funksjon som skriver data mottatt av serveren til en fil ved å åpne filen i binær append-modus.
    Om filen ikke eksisterer, opprettes den.

    Argumenter:
    - filnavn: Navnet på filen som data skal skrives til
    - data: Data i byte-format som sendes fra klient og skal lagres av server

    Unntakshåndtering:
    Fanger OSError-unntak som kan oppstå ved ulike problemer relatert til skriving til en fil. 
    """
    try:
        with open(filnavn, "ab") as f:
            f.write(data)
    except OSError as e:
        print(f"Kunne ikke skrive til filen {filnavn}: {e}")
        sys.exit()




def throughput(start, slutt, datapakker):
    """
    Beskrivelse:
    Funksjon som regner ut gjennomstrømmingsverdien av en overføring. 

    Argumenter:
    - start: Starttidspunktet for dataoverføringen
    - slutt: Slutttidspunktet for dataoverføringen
    - datapakker: En liste bestående av pakker(i form av byte-strenger) som er mottatt av server fra klient

    Returnerer:
    Gjennomstrømmingsverdien i megabits per sekund.
    """     
    antallBytes = 0                                             # Variabel som skal holde antall bytes server har mottatt
    for i in datapakker:
        antallBytes += len(i)                                   # Legger til antall bytes i hver pakke
    totalTid = slutt - start                                    # Total overføringstid
    return (antallBytes*8)/(1e6 * totalTid.total_seconds())     # Returnerer (megabits)/(antall sekunder)




def threeWayHandshake(args):
    """
    Beskrivelse:
    Funksjonen utfører en prosedyre kalt Three Way Handshake for å etablere en pålitelig forbindelse 
    mellom klient og server over transportprotokollen UDP. Funksjonen er delt opp i en klient- og serverdel.
    
    Argumenter:
    Tar inn og bruker de nødvendige kommandolinjeargumentene for å etablere forbindelsen. Dette inkluderer 
    servers ip-adresse og portnummer, samt hvem som er klient og server. 
    
    Returnerer:
    - klient: En tuple bestående av tilkoblingssocket, servers ip-adresse og portnummer, klientens siste sequence number
      og acknowledgement number
    - server: En tuple bestående av tilkoblingssocket, klientens IP-adresse og portnummer, servers siste sequence number.

    Unntakshåndtering:
    - klient: Håndterer TimeoutError som oppstår når klienten ikke mottar en SYN-ACK fra server innen en gitt tidsramme.
    - server: Håndterer TimeoutError som oppstår når server ikke har mottat en ACK fra klienten, og en OSError som kan 
      oppstå når server ikke kan binde til den gitte IP-adressen og portnummeret.
    """
    seqNrKlient = 0                         # Sekvensnummeret klienten starter med     
    seqNrServer = 0                         # Sekvensnummeret serveren starter med 
    ackNrKlient = 0                         # Ack-nummeret klienten starter med
    ackNrServer = 0                         # Ack-nummeret serveren starter med
    # ThreeWayHandshake sin klientkode:
    if args.client:
        serverip = args.ip                  # Henter server sin IP-adresse
        serverport = args.port              # Henter server sitt portnummer             
        flagNr = 8                                   # Syn-flagget er satt. 1 0 0 0 er 8 som desimaltall
        antall = 1                                  # Antall forsøk på å koble til server                                     
        print("Connection Establish Phase:\n")
        klientsocket = socket(AF_INET, SOCK_DGRAM)          # Oppretter UDP socket (klient)
        klientsocket.sendto(opprettePakke(seqNrKlient, ackNrKlient, flagNr, b''), (serverip, serverport))      # Sender SYN-pakke til server
        print("SYN packet is sent")
        klientsocket.settimeout(0.5)                    # Setter timeout til 0.5 sekunder
        while True:
            try:
                melding, serveradresse = klientsocket.recvfrom(2048)            # Pakke mottatt fra server
                header, data = parsePakke(melding)                              # Pakker ut pakken fra server
                serverSeq, serverAck, serverFlags = header                      # Henter ut verdiene fra pakkeheader
                syn, ack, fin = parseFlags(serverFlags)                         # Henter ut flaggene
                if syn and ack and not fin:
                    seqNrKlient += 1                # Øker sequence number til server med 1 for neste pakken som skal sendes (en ACK)
                    flagNr = 4                      # Ack-flagget satt. 0 1 0 0 blir 4
                    print("SYN-ACK packet is received")
                    klientsocket.sendto(opprettePakke(seqNrKlient, serverSeq, flagNr, b''), serveradresse)
                    print("ACK packet is sent")
                    print("Connection established\n")
                    return klientsocket, serveradresse, seqNrKlient, ackNrKlient
            except TimeoutError:
                klientsocket.sendto(opprettePakke(seqNrKlient, ackNrKlient, flagNr, b''), (serverip, serverport))
                antall += 1                             # Øker antall retransmissions med 1
                if antall >= 4:                         # Prøver å koble til server et gitt antall ganger før den den gir seg
                    print("\nConnection failed")
                    return None
    # ThreeWayHandshake sin serverkode:
    if args.server:
        flagNr = 12                                     # Syn og ack satt. 1 1 0 0 blir 12
        serversocket = socket(AF_INET, SOCK_DGRAM)      # Oppretter UDP socket (server)      
        try:
            serversocket.bind((args.ip, args.port))     # Prøver å binde socketen til den gitte IP-adressen og portnummeret
        except OSError as e:
            print("Kunne ikke binde socket: " + str(e))
            return None
        melding, klientadresse = serversocket.recvfrom(2048)            # Pakke mottatt fra klient
        header, data = parsePakke(melding)                              # Pakker ut pakken fra klient
        klientSeq, klientAck, klientFlags = header                      # Henter ut verdiene fra pakkeheader
        ackNrServer = klientSeq                                         # Setter serveren sin Acknowledgement number lik mottatt sequence number fra klient
        syn, ack, fin = parseFlags(klientFlags)                         # Henter ut flaggene
        if not(ack or fin) and syn:
            print("SYN packet is received")
            serversocket.sendto(opprettePakke(seqNrServer, ackNrServer, flagNr, b''), klientadresse)
            print("SYN-ACK packet is sent")
            serversocket.settimeout(0.5)   # Setter en timeout slik at det returneres None om ikke en ACK fra klient kommer fram til server
            try:
                # Samme som kommenter over:
                melding, klientadresse = serversocket.recvfrom(2048)
                header, data = parsePakke(melding)
                klientSeq, klientAck, klientFlags = header
                ackNrServer = klientSeq
                syn, ack, fin = parseFlags(klientFlags)
                if not(syn or fin) and ack:
                    print("ACK packet is received")
                    print("Connection established")
                    return serversocket, klientadresse, seqNrServer
                else:
                    return None                 # Returnerer None om ACK-flagget ikke er satt i mottatt pakke
            except TimeoutError:
                    return None                 # Returnerer None om det ikke er mottatt en ACK-pakke inne tidsrammen




def GBN(resultatHandshake, dataliste, args):
    """
    Beskrivelse:
    Funksjonen utfører pålitelig dataoverføring mellom klient og server over transportprotokollen UDP med Go-Back-N, og den 
    håndterer forbindelsesavslutning mellom server og klient når dataoverføringen er fullført.
    Denne funksjonen er i likhet med threeWayhandshake delt opp i en klient- og serverdel.

    Argumenter:
    - klient: En tuple som inneholder resultatet fra threeWayHandshake, en liste som inneholder datablokker
      på 994 bytes av filen som skal sendes og kommandolinjeargumentene.
    - server: En tuple som inneholder resultatet fra threeWayHandshake og kommandolinjeargumentene
    Unntakshåndtering:
    - klient: Håndterer TimeoutError som oppstår om det ikke mottas en pakke fra server innen den gitte tidsrammen.
    - server: Ingen spesifikk unntakshåndtering.

    """
    # GBN sin klientkode:
    if args.client:
        print("Data Transfer:\n")
        datablokker = dataliste                 # Filen som skal overføres til klient delt opp i en liste med datablokker
        tilkoblingssocket, serveradresse, seqNrKlient, ackNrKlient = resultatHandshake          # Resultatet fra threeWayHandshake
        flagNr = 4              # Setter ACK-flagget
        vinduStr = args.window  # Vindustørrelsen
        vindu = []              # sliding window
        antall = 0              # Variabel for antall retransmissions  
        # Sender de første n antall pakker 
        for i in range(vinduStr):            
                tilkoblingssocket.sendto(opprettePakke(seqNrKlient, ackNrKlient, flagNr, datablokker[seqNrKlient-1]), serveradresse)
                vindu.append(seqNrKlient)               # Legger til sendte pakkers sequence number til sliding window
                print(f"{datetime.datetime.now().time()} -- packet with seq = {seqNrKlient} is sent, sliding window = {str(vindu).replace('[', '{').replace(']', '}')}")
                seqNrKlient += 1

        while seqNrKlient-1 < len(datablokker):
            try:
                melding, serveradresse = tilkoblingssocket.recvfrom(2048)
                header, data = parsePakke(melding)
                serverSeq, serverAck, serverFlags = header
                ackNrKlient = serverAck
                syn, ack, fin = parseFlags(serverFlags)
                if not(syn or fin) and ack and serverAck == vindu[0]:              
                    print(f"{datetime.datetime.now().time()} -- ACK for packet = {serverAck} is received")
                    tilkoblingssocket.sendto(opprettePakke(seqNrKlient, serverSeq, flagNr, datablokker[seqNrKlient-1]), serveradresse)
                    vindu.append(seqNrKlient)               # Legger til siste sendte pakke (sequence number) i sliding window
                    vindu.pop(0)                            # Forskyver sliding window når ACK er mottatt for laveste sequence number i vinduet
                    print(f"{datetime.datetime.now().time()} -- packet with seq = {seqNrKlient} is sent, sliding window = {str(vindu).replace('[', '{').replace(']', '}')}")
                    seqNrKlient += 1
                    antall = 0          # Tilbakestiller antall retransmissions
                    # Koden under tar seg av de siste ACK-pakkene når det ikke er flere pakker å sende fra klienten:
                    if seqNrKlient-1 == len(datablokker):
                        while vindu:
                            try:
                                melding, serveradresse = tilkoblingssocket.recvfrom(2048)
                                header, data = parsePakke(melding)
                                serverSeq, serverAck, serverFlags = header
                                syn, ack, fin = parseFlags(serverFlags)
                                if not(syn or fin) and ack:
                                    print(f"{datetime.datetime.now().time()} -- ACK for packet = {serverAck} is received")
                                    vindu.pop(0)
                                    antall = 0
                            except TimeoutError:
                                # Kode for retransmissions:
                                antall += 1
                                if antall > 4:       # Setter et maks antall retransmissions. Sikrer at klienten ikke havner i en uendelig løkke om serveren avsluttes
                                    sys.exit()
                                else:
                                    print(f"{datetime.datetime.now().time()} -- RTO occured")
                                    # Sender alle pakkene i det nåværende sliding window:
                                    for i in vindu:
                                        tilkoblingssocket.sendto(opprettePakke(i, ackNrKlient, flagNr, datablokker[i-1]), serveradresse) 
                                        print(f"{datetime.datetime.now().time()} -- retransmitting packet with seq = {i}")
            except TimeoutError:
                # Kode for retransmissions:
                antall += 1
                if antall > 4:          # Setter et maks antall retransmissions. Sikrer at klienten ikke havner i en uendelig løkke om serveren avsluttes
                    sys.exit()
                else:
                    print(f"{datetime.datetime.now().time()} -- RTO occured")
                    # Sender alle pakkene i det nåværende sliding window:
                    for i in vindu:
                        tilkoblingssocket.sendto(opprettePakke(i, ackNrKlient, flagNr, datablokker[i-1]), serveradresse) 
                        print(f"{datetime.datetime.now().time()} -- retransmitting packet with seq = {i}")

        #teardown klient    
        print("DATA Finished\n\n")
        print("Connection Teardown:\n")
        flagNr = 2                      # FIN-flagget satt (0 0 1 0 blir 2)
        tilkoblingssocket.sendto(opprettePakke(seqNrKlient, ackNrKlient, flagNr, b''), serveradresse)
        print("FIN packet packet is sent")
        antall = 0          # Variabel for antall forsøk på å sende FIN til server 
        while True:
            try:
                melding, klientadresse = tilkoblingssocket.recvfrom(2048)
                header, data = parsePakke(melding)
                serverSeq, serverAck, serverFlags = header
                syn, ack, fin = parseFlags(serverFlags)
                if fin and ack and not syn:             # Avslutter om FIN-ACK mottas fra server
                    print("FIN ACK packet is received")
                    print("Connection Closes")
                    tilkoblingssocket.close()
                    break
            except TimeoutError:
                tilkoblingssocket.sendto(opprettePakke(seqNrKlient, ackNrKlient, flagNr, b''), serveradresse)
                antall += 1
                if antall >= 4:         # Slutter å sende FIN til server etter et gitt antall ganger
                    tilkoblingssocket.close()
                    break 
    # GBN sin serverkode:
    if args.server:
        tilkoblingssocket, klientadresse, seqNrServer = resultatHandshake
        flagNr = 4                                  # Setter ack-flagget slik at pakker fra server blir ack-pakker
        forventetSeqnr = 1                          # Variabel for forventet sekvensnummer. Brukes for å se om pakker ankommer i riktig rekkefølge
        pakkerMottatt = []                          # Liste som inneholder alle pakker mottatt fra klient. Brukes til å beregne Throughput
        tilkoblingssocket.settimeout(None)          # Setter timeout tilbake til None fordi timeout ble satt til 0.5s på serversiden i ThreeWayHandshake 
        startid = datetime.datetime.now()           # Tiden hvor overføring av data starter
        while True:                                 # Løkke som går helt til server mottar FIN
            melding, klientadresse = tilkoblingssocket.recvfrom(2048)
            pakkerMottatt.append(melding)
            header, data = parsePakke(melding)
            klientSeq, klientAck, klientFlags = header
            syn, ack, fin = parseFlags(klientFlags)
            if not(syn or ack) and fin:
                # teardown server
                sluttid = datetime.datetime.now()           # Tiden hvor overføring av data er fullført
                flagNr = 6                                  # Setter flaggene FIN og ACK (0 1 1 0 blir 6)
                print("FIN packet is received")                
                tilkoblingssocket.sendto(opprettePakke(seqNrServer, klientSeq, flagNr, b''), klientadresse)
                print("FIN ACK packet is sent\n")
                print(f"The throughput is {round(throughput(startid, sluttid, pakkerMottatt), 3)} Mbps")
                print("Connection Closes")
                tilkoblingssocket.close()
                break
            elif args.discard is not None and args.discard == klientSeq:   # Sender ikke ACK tilbake til server om pakken fra server har sequence number lik discard-verdi
                args.discard = None         # Setter discard-verdi til None for at ikke server skal forkaste pakken med et spesifikk sequence number hver gang.
                continue
            elif forventetSeqnr < klientSeq:            # Håndterer pakker som ikke ankommer i rekkefølge
                print(f"{datetime.datetime.now().time()} -- out-of-order packet {klientSeq} is received")
            elif forventetSeqnr > klientSeq:            # Håndterer duplikater ved å sende ACK for pakken på nytt
                tilkoblingssocket.sendto(opprettePakke(seqNrServer, klientSeq, flagNr, b''), klientadresse)         
            else:                                       # Håndterer pakker som ankommer i riktig rekkefølge
                print(f"{datetime.datetime.now().time()} -- packet {klientSeq} is received")
                print(f"{datetime.datetime.now().time()} -- sending ack for the received {klientSeq}")
                lagreFil("bilde.jpg", data)             # Lagrer data som ankommer i riktig rekkefølge
                tilkoblingssocket.sendto(opprettePakke(seqNrServer, klientSeq, flagNr, b''), klientadresse)
                forventetSeqnr += 1

                


           

        

        

                
        

            






