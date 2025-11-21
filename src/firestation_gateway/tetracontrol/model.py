from dataclasses import dataclass


@dataclass
class SDSModel:
    """
    Model for SDS.
    (For Callout see class SDSCalloutModel)

    Attributes:
        Ziel (int):      ISSI oder GSSI.
        Text (str):      Text für SDS.
        GerID (int):     Gerätenummer 1-4.
        Typ (int):       0=Einfache SDS, 1=Standard SDS, 138=verkettete SDS.
        Flash (int):     0=Normale SDS, 1=Flash SDS, Default=0
        Encr (int):      0=Ohne Verschlüsselung, 1=Mit Verschlüsselung, Default=1
        Prio (int):      0-15 Priorität, Default=0
    """

    Ziel: int
    Text: str
    GerID: int = 1
    Typ: int = 0
    Flash: int = 0
    Encr: int = 1
    Prio: int = 0

    def __post_init__(self):
        if self.GerID < 1 or self.GerID > 4:
            raise ValueError("'GerID' must be 1-4")
        if self.Typ not in [0, 1, 138]:
            raise ValueError(
                "'Typ' must be 0=Einfache SDS, 1=Standard SDS, "
                "138=verkettete SDS"
            )
        if self.Flash < 0 or self.Flash > 1:
            raise ValueError("'Flash' must be 0=Normale SDS, 1=Flash SDS")
        if self.Encr < 0 or self.Encr > 1:
            raise ValueError(
                "'Encr' must be 0=Ohne Verschlüsselung, 1=Mit Verschlüsselung"
            )
        if self.Prio < 0 or self.Prio > 15:
            raise ValueError("'Prio' must be 0-15 Priorität")


@dataclass
class SDSCalloutModel:
    """
    Model for SDS Callout

    Attributes:
        Ziel (int):      ISSI oder GSSI.
        Text (str):      Text für SDS.
        GerID (int):     Gerätenummer 1-4.
        Typ (int):       195=CallOut.
        Flash (int):     0=Normale SDS, 1=Flash SDS, Default=0
        Encr (int):      0=Ohne Verschlüsselung, 1=Mit Verschlüsselung, Default=1
        Prio (int):      0-15 Priorität, Default=0
        COPrio (int):    1-15: CallOut Prio/Severity. Optional. Nur bei CallOut
        CONum (int):     1-250: Vorfall-Nummer. Optional. Nur bei CallOut
        noreply (int):   0/1. Nur bei CallOut: Keine Antwort anfordern
        sub (str): Sub-Gruppen, mit Komma getrennt. Nur bei CallOut
            Der Parameter sub kann bei CallOut (Typ=195) angegeben werden. Bei den „Hessischen“ Sub-
            Typen (im &xx Format) können diese auch dem Text vorangestellt werden. Bei der Angabe des sub
            Parameters erfolgt keine Längenprüfung, daher ist ggf der Text von der aufrufenden Applikation um
            die zusätzlichen Zeichen der Subgruppen zu kürzen. Falls die Zulässige SDS Textlänge überschritten
            wird, wird die SDS bzw die Alarmierung automatisch verkettet.
    """

    Ziel: int
    Text: str
    GerID: int = 1
    Typ: int = 0
    Flash: int = 0
    Encr: int = 1
    Prio: int = 0
    COPrio: int = 1
    CONum: int = 1
    noreply: int = 0
    sub: str = ""

    def __post_init__(self):
        if self.GerID < 1 or self.GerID > 4:
            raise ValueError("'GerID' must be 1-4")
        if self.Typ not in [195]:
            raise ValueError("'Typ' must be 195=CallOut")
        if self.Flash < 0 or self.Flash > 1:
            raise ValueError("'Flash' must be 0=Normale SDS, 1=Flash SDS")
        if self.Encr < 0 or self.Encr > 1:
            raise ValueError(
                "'Encr' must be 0=Ohne Verschlüsselung, 1=Mit Verschlüsselung"
            )
        if self.Prio < 0 or self.Prio > 15:
            raise ValueError("'Prio' must be 0-15 Priorität")
        if self.COPrio < 1 or self.COPrio > 15:
            raise ValueError("'COPrio' 1-15: CallOut Prio/Severity.")
        if self.CONum < 1 or self.CONum > 250:
            raise ValueError("'CONum' 1-250: Vorfall-Nummer.")
        if self.noreply < 0 or self.noreply > 1:
            raise ValueError(
                "'noreply' 0/1. Nur bei CallOut: Keine Antwort anfordern"
            )


@dataclass
class RadioModel:
    """
    Model for getting device information

    Attributes:
        GerID (int):     Gerätenummer 1-4.
    """

    GerID: int = 1

    def __post_init__(self):
        if self.GerID < 1 or self.GerID > 4:
            raise ValueError("'GerID' must be 1-4")
