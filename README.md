# Scoutnet & Google G-Suite

_scoutnet2google_ synkroniserar epostlistor definerade i 
Scoutnet med Google G-Suite.

## Förberedelser i ScoutNet

### API-nyckel

Synkroniseringen kräver att man skapar en **API-nyckel** i 
Scoutnet. För att kunna göra detta krävs det att man har 
rollen IT-ansvarig för sin kår. 

1. Gå till kårens sida i Scoutnet.
2. Välj fliken *Webbkoppling*.
3. Expandera *"API-nycklar och Endpoints"*
4. Om API för kår inte är aktiverat måste man aktivera det.
5. Leta upp *"Get a csv/xls/json list of members, based on 
   mailing lists you have set up [ Expandera ]"*. 
6. Generera en API-nyckel.
7. Kopiera nyckeln och lägg till den i konfigurations-filen 
   (scoutnet2google.ini) i fältet api_key_groups.
8. Leta upp *"Get a detailed csv/xls/json list of all 
   members [ Expandera ]"*. 
9. Generera en API-nyckel.
10. Kopiera nyckeln och lägg till den i konfigurations-filen 
   (scoutnet2google.ini) i fältet api_key_users.

Inställningar gör att skriptet kan läsa e-postlistor som 
finns konfigurerade i Scoutnet.

### E-postlistor

1. Gå till kårens sida i Scoutnet och välj fliken Epostlistor.
2. Välj *"Skapa en ny lista..."*
3. Fyll i namn och beskrivning, tex "Medlemmar utmanare". Ange det
   e-postadress som listan skall få som ett alias (tex 
   "utmanare@exempel.com"). Glöm inte att klicka "Lägg till".
4. Tryck på "Spara..."
5. I steget "Skapa en ny maillisteregel" anger man namn och 
   beskrivning på den regel som gör urvalet till listan. 
   Fortsätt genom att trycka på "Nästa steg".
6. I det här steget anger man regler för vilka medlemmar 
   som skall ingå i e-postlistan. Exempelvis kan man 
   välja alla medlemmar i en avdelning genom att klicka på
   "Filter för medlemsskap" och därefter ange Avdelning som 
   filter för underliggande nivåer. Därefter anger man 
   vilken avdelning.
7. I sista steget kan man verifiera att urvalet blev som man
   tänkt sig.

För varje e-postlista som konfigurerats på detta sätt kommer
skriptet att skapa/synkronisera en grupp i Gsuite.

Listor som skapas har "(Scoutnet)" i beskrivningen. Detta är
används för att identifiera vilka listor som skriptet skall
synkronisera.

## Förberedelser i Google

För att kunna kommunicera med Google behövs en API-nyckel.
Googles version är en JSON-fil som behöver vara läsbar för
skriptet.

### API-nyckel

1. Gå till Googles utvecklar-portal: 
   https://console.developers.google.com/
2. Autentisera med ett konto som har administratörs-rättigheter
   för domänen.
3. 

## Förberedelser lokalt på maskinen

En konfigurations-fil måste skapas. Denna ligger "där den 
ska" ligga:

* Windows: C:\Documents and Settings\<User>\Application Data\Local Settings\Scoutnet2Google\Scoutnet2Google
* MacOSX: ~/Library/Application Support/Scoutnet2Google
* Linux/Unix: ~/.local/share/Scoutnet2Google

Filen heter scoutnet2google.ini och ser som exemplet nedan:

<pre>
[scoutnet]
api_id: 1234
api_key_groups: mekmitasdigoat
api_key_users: mekmitasdigoat
youthgroup_with_accounts:

[google]
auth: installed
#auth: compute_engine
domain: example.com
</pre>

* api_id: Logga in till Scoutnet och navigera till kårens 
  sida. URL:en kommer att se ut som följer: https://www.scoutnet.se/organisation/group/home/1234. 
  Siffrorna efter home är api_id (dvs de är inte 1234 för 
  din kår).
* api_key_groups: här skall API-nyckeln för mailinglistor 
  som genererats i Scoutnet anges.
* api_key_users: här skall API-nyckeln för användare som 
  genererats i Scoutnet anges.
* youthgroup_with_accounts: här skriver man en kommaseparerad
  lista över avdelningar där även medlemmar under 18 år skall
  ha konton i Google-system (tex Utmanare)
* domain: här anger man kårens domän-namn som används i 
  Google (dvs har man epost-adresser ledare@superscout.se 
  så skall det stå superscout.se här).