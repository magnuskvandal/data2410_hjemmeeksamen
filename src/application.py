from socket import *
from argparse import *
from functions import *
import sys

def argumenthåndtering():
    """
    Beskrivelse:
    Funksjon som håndterer og oppretter et objekt med disse kommandolinjeargumentene:
    -s for servermodus
    -c for klientmodus
    -i for servers ip-adresse
    -p for servers portnummer
    -f for fil som skal sendes til server
    -w for størrelsen på sliding window
    -d for å kaste en pakke med et spesifikk sekvensnummer

    Returnerer:
    Et objekt med verdiene til kommandolinjeargumentene om verdiene samsvarer med kravene i funksjonen verdihåndtering(args).
    Om verdiene ikke samsvarer med kravene i verdihåndtering(args), vil verdihåndtering(args) returnere false. Da vil argumenthåndtering()
    avslutte programmet.
    """
    parser = ArgumentParser()           # Argument-Parser-objekt

    # Kommandolinjeargumenter 
    parser.add_argument("--server", "-s", action = "store_true", help= "Aktiverer servermodus")
    parser.add_argument("--client", "-c", action = "store_true", help= "Aktiverer klientmodus")
    parser.add_argument("--ip", "-i", type = str, default = "10.0.1.2", help = "IP-adresse som bindes på serversiden eller kobles til på klientsiden")
    parser.add_argument("--port", "-p", type = int, default = 8088, help = "Portnummer server skal lytte på eller klient skal kobles til")
    parser.add_argument("--file", "-f", type = str, help = "Filen som skal sendes til server")
    parser.add_argument("--window", "-w", type = int, default = 3, help = "Størrelsen på det glidende vinduet")
    parser.add_argument("--discard", "-d", type = int, help = "Sekvensnummeret til en pakke som skal kastes. Brukes for å teste retransmission")

    args = parser.parse_args()          # Objekt med kommandolinjeverdiene

    gyldig = verdihåndtering(args)      # Variabel for å håndtere hva som skal returneres/gjøres ut fra hva verdihåndtering(args) returnerer

    if gyldig:
        return args
    else:
        sys.exit()

def main():
    """
    Beskrivelse:
    Main-funksjonen utfører selve programmet: Pålitelig overføring av data over UDP. 
    """
    args = argumenthåndtering()                                         # Henter kommandolinjeargumentene
    resultatHandshake = threeWayHandshake(args)                         # Kaller og Henter ut resultatet av threeWayhandshake
    # Klientsiden:                                   
    if args.client:
        dataliste = hentFil(args.file)
        if resultatHandshake is not None:
            GBN(resultatHandshake, dataliste, args)          # Starter dataoverføring om forbindelsen er opprettet
        else:
            sys.exit()                                                  # Avslutter om threeWayHandshake returnerer None (Ingen forbindelse)
    # Serversiden
    if args.server:
        if resultatHandshake is not None:
            GBN(resultatHandshake, None, args)               # Starter dataoverføring om forbindelsen er opprettet            
        else:
            sys.exit()                                                  # Avslutter om threeWayHandshake returnerer None (Ingen forbindelse)

if __name__ == "__main__":
    main()

        


    

    








