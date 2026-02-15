from socket import *
from argparse import *
from functions import *
import sys

def argumenthåndtering():
    """
    Beskrivelse:
    Funksjon som håndterer og oppretter et objekt med kommandolinjeargumenter

    Returnerer:
    Et objekt med verdiene til kommandolinjeargumentene om verdiene samsvarer med kravene i funksjonen verdihåndtering(args).
    Om verdiene ikke samsvarer med kravene i verdihåndtering(args), vil verdihåndtering(args) returnere false. Da vil argumenthåndtering()
    avslutte programmet.
    """
    parser = ArgumentParser()           

    # Kommandolinjeargumenter 
    parser.add_argument("--server", "-s", action = "store_true", help= "Aktiverer servermodus")
    parser.add_argument("--client", "-c", action = "store_true", help= "Aktiverer klientmodus")
    parser.add_argument("--ip", "-i", type = str, default = "127.0.0.1", help = "Brukes for å sette servers IP-adresse (IPv4). Standard er 127.0.0.1")
    parser.add_argument("--port", "-p", type = int, default = 8088, help = "Brukes for å sette servers portnummer. Standard er 8080")
    parser.add_argument("--file", "-f", type = str, help = "Brukes i klientmodus for å angi filen (JPG) som skal sendes til server")
    parser.add_argument("--window", "-w", type = int, default = 3, help = "Brukes for å endre vindusstørrelsen. Standard vindusstørrelse er 3")
    parser.add_argument("--discard", "-d", type = int, help = "Brukes i servermodus for å angi sekvensnummeret til datapakken som skal forkastes (for testing av retransmission)")

    args = parser.parse_args()   

    if verdihåndtering(args):
        return args
    else:
        sys.exit()

def main():
    """
    Beskrivelse:
    Main-funksjonen utfører selve programmet: Pålitelig overføring av data over UDP. 
    """
    args = argumenthåndtering()                                         
    resultatHandshake = threeWayHandshake(args)                         

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

        


    

    








