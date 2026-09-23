"""Färdiga mallar som visas på startsidan.

Varje mall har källor i formatet [namn, RSS-länk, filtrera]. filtrera=False betyder att allt från källan
tas med (för källor som redan handlar om ämnet), True betyder att bara artiklar med nyckelorden tas med.
Lägg gärna till egna mallar i samma format.
"""

# ---------- Källor som återkommer i flera mallar ----------
SVT_NYHETER = ["SVT Nyheter", "https://www.svt.se/nyheter/rss.xml", True]
SVT_INRIKES = ["SVT Inrikes", "https://www.svt.se/nyheter/inrikes/rss.xml", True]
SVT_UTRIKES = ["SVT Utrikes", "https://www.svt.se/nyheter/utrikes/rss.xml", True]
SVT_EKONOMI = ["SVT Ekonomi", "https://www.svt.se/nyheter/ekonomi/rss.xml", True]
EKOT = ["Sveriges Radio Ekot", "https://api.sr.se/api/rss/program/83", True]
AFTONBLADET = ["Aftonbladet", "https://rss.aftonbladet.se/rss2/small/pages/sections/senastenytt/", True]
EXPRESSEN = ["Expressen", "https://feeds.expressen.se/nyheter", True]
DN = ["Dagens Nyheter", "https://www.dn.se/rss/", True]
COMPUTER_SWEDEN = ["Computer Sweden", "https://computersweden.se/feed/", True]
NY_TEKNIK = ["Ny Teknik", "https://www.nyteknik.se/rss", True]
BREAKIT = ["Breakit", "https://www.breakit.se/feed/artiklar", True]
UPPHANDLING24 = ["Upphandling24", "https://upphandling24.se/feed/", False]
BBC_WORLD = ["BBC World", "http://feeds.bbci.co.uk/news/world/rss.xml", True]
BBC_BUSINESS = ["BBC Business", "http://feeds.bbci.co.uk/news/business/rss.xml", True]
BBC_TECH = ["BBC Technology", "http://feeds.bbci.co.uk/news/technology/rss.xml", True]
GUARDIAN_TECH = ["The Guardian Technology", "https://www.theguardian.com/technology/rss", True]
GUARDIAN_BUSINESS = ["The Guardian Business", "https://www.theguardian.com/business/rss", True]
GUARDIAN_WORLD = ["The Guardian World", "https://www.theguardian.com/world/rss", True]
POLITICO_EU = ["Politico Europe", "https://www.politico.eu/feed/", True]
EURACTIV = ["Euractiv", "https://www.euractiv.com/feed/", True]
HACKER_NEWS = ["Hacker News", "https://hnrss.org/frontpage", True]


def som(kalla, filtrera):
    """Samma källa men med ett annat filterval."""
    return [kalla[0], kalla[1], filtrera]


MALLAR = [
    # ================= SAMHÄLLE =================
    {
        "titel": "Offentlig upphandling", "grupp": "Samhälle", "etikett": "Upphandling",
        "farg": "#2563EB", "punkt": "blue",
        "text": "LOU, ramavtal, överprövningar och det som händer i upphandlingsvärlden.",
        "bevakning": {
            "namn": "Upphandlingsbevakning",
            "kallor": [
                UPPHANDLING24,
                ["Inköpsrådet", "https://inkopsradet.se/feed/", False],
                SVT_INRIKES, SVT_EKONOMI, EKOT, DN, COMPUTER_SWEDEN, POLITICO_EU, EURACTIV,
            ],
            "nyckelord": [
                "upphandling*", "offentlig upphandling", "lou", "luf", "lupp", "ramavtal*", "avtalsspärr*",
                "överprövning*", "direktupphandling*", "tilldelningsbeslut*", "anbud*", "anbudsgivare*",
                "förfrågningsunderlag*", "upphandlingsmyndigheten", "konkurrensverket", "upphandlingsskadeavgift*",
                "inköpscentral*", "adda", "kammarrätt*", "förvaltningsrätt*", "valfrihetssystem*",
                "upphandlingsdirektiv*", "hållbar upphandling", "sociala krav", "peppol", "e-handel",
                "leverantörsreskontra", "public procurement", "procurement", "tender*", "framework agreement*",
            ],
            "tvetydiga_ord": ["lov", "avtal", "leverantör*", "inköp*"],
            "kontextord": ["upphandl*", "kommun*", "region*", "offentlig*", "valfrihet*", "anbud*", "myndighet*", "ramavtal*"],
            "kategoriord": ["upphandling", "procurement", "lou"],
        },
    },
    {
        "titel": "Offentlig sektor", "grupp": "Samhälle", "etikett": "Kommun och region",
        "farg": "#0E7490", "punkt": "blue",
        "text": "Kommuner, regioner och myndigheter: välfärd, budget, beslut och reformer.",
        "bevakning": {
            "namn": "Offentlig sektor",
            "kallor": [SVT_INRIKES, SVT_NYHETER, EKOT, DN, AFTONBLADET, EXPRESSEN, som(UPPHANDLING24, True),
                       COMPUTER_SWEDEN],
            "nyckelord": [
                "kommun*", "region*", "landsting*", "skr", "sveriges kommuner och regioner", "myndighet*",
                "välfärd*", "äldreomsorg*", "hemtjänst*", "skolan", "förskol*", "vårdcentral*", "sjukvård*",
                "socialtjänst*", "statsbidrag*", "kommunalskatt*", "skattehöjning*", "budgetunderskott*",
                "kommunfullmäktig*", "regionfullmäktig*", "kommunstyrelse*", "kommunalråd*", "regionråd*",
                "offentlig sektor", "offentliga sektorn", "förvaltning*", "statlig utredning", "sou",
                "regeringen", "riksdag*", "proposition*", "reform*", "effektivisering*", "besparing*",
            ],
            "tvetydiga_ord": ["budget*", "nedskärning*"],
            "kontextord": ["kommun*", "region*", "statlig*", "myndighet*", "offentlig*"],
            "kategoriord": ["kommun", "region"],
        },
    },
    {
        "titel": "EU och lagstiftning", "grupp": "Samhälle", "etikett": "Politik och juridik",
        "farg": "#4338CA", "punkt": "violet",
        "text": "Nya EU-regler, förordningar, domar och lagändringar som påverkar verksamheten.",
        "bevakning": {
            "namn": "EU och lagstiftning",
            "kallor": [
                som(POLITICO_EU, False), som(EURACTIV, False),
                ["The Guardian Law", "https://www.theguardian.com/law/rss", True],
                SVT_UTRIKES, SVT_INRIKES, EKOT, GUARDIAN_WORLD, BBC_WORLD,
            ],
            "nyckelord": [
                "eu-kommissionen", "europeiska kommissionen", "europaparlamentet", "ministerrådet", "eu-domstolen",
                "eu-förordning*", "eu-direktiv*", "eu-regler*", "eu:s", "eu-lag*", "förordning*", "direktiv*",
                "lagförslag*", "lagändring*", "ny lag", "lagrådsremiss*", "proposition*", "remiss*",
                "högsta förvaltningsdomstolen", "högsta domstolen", "dom i", "gdpr", "nis2", "ai act",
                "data act", "dma", "dsa", "csrd", "european commission", "european parliament", "eu regulation*",
                "eu directive*", "court of justice", "brussels", "bryssel",
            ],
            "tvetydiga_ord": ["kommissionen", "parlamentet", "regulation*", "directive*"],
            "kontextord": ["eu", "eu:s", "eu-*", "europe*", "europa*", "brussels", "bryssel"],
            "kategoriord": ["europe", "law", "juridik", "eu-"],
        },
    },
    {
        "titel": "Arbetsliv och HR", "grupp": "Samhälle", "etikett": "Arbetsliv",
        "farg": "#DB2777", "punkt": "red",
        "text": "Arbetsmarknad, kompetensförsörjning, löner, avtal och arbetsmiljö.",
        "bevakning": {
            "namn": "Arbetsliv och HR",
            "kallor": [
                ["Arbetsvärlden", "https://www.arbetsvarlden.se/feed/", False],
                ["HR Dive", "https://www.hrdive.com/feeds/news/", False],
                SVT_INRIKES, SVT_EKONOMI, EKOT, DN, GUARDIAN_BUSINESS, BBC_BUSINESS,
            ],
            "nyckelord": [
                "arbetsmarknad*", "arbetslöshet*", "sysselsättning*", "rekryter*", "kompetensförsörjning*",
                "kompetensbrist*", "kompetensutveckling*", "omställning*", "vidareutbild*", "arbetsgivare*",
                "facket", "fackförbund*", "kollektivavtal*", "avtalsrörelse*", "lönebildning*", "löneökning*", "strejk*",
                "varsel*", "uppsägning*", "las", "arbetsmiljö*", "sjukskriv*", "utbrändhet", "psykosocial*",
                "distansarbete", "hybridarbete", "hemarbete", "fyradagarsvecka*", "arbetstid*", "chefer",
                "ledarskap*", "medarbetar*", "hr", "employer*", "workforce", "hiring", "layoff*", "remote work",
                "four-day week", "burnout",
            ],
            "tvetydiga_ord": ["lön*", "avtal"],
            "kontextord": ["arbets*", "facket", "fackförbund*", "anställ*", "medarbetar*", "kollektivavtal*"],
            "kategoriord": ["arbetsliv", "arbetsmarknad", "jobs", "careers"],
        },
    },
    # ================= TEKNIK =================
    {
        "titel": "AI", "grupp": "Teknik", "etikett": "Teknik", "farg": "#6D4AFF", "punkt": "violet",
        "text": "AI-modeller, bolagen bakom dem och regleringen runt omkring.",
        "bevakning": {
            "namn": "AI-bevakning",
            "kallor": [
                ["TechCrunch AI", "https://techcrunch.com/category/artificial-intelligence/feed/", False],
                ["The Verge AI", "https://www.theverge.com/rss/ai-artificial-intelligence/index.xml", False],
                ["MIT Technology Review AI", "https://www.technologyreview.com/topic/artificial-intelligence/feed", False],
                ["VentureBeat AI", "https://venturebeat.com/category/ai/feed/", False],
                ["Ars Technica AI", "https://arstechnica.com/ai/feed/", False],
                ["Wired AI", "https://www.wired.com/feed/tag/ai/latest/rss", False],
                ["Hugging Face Blog", "https://huggingface.co/blog/feed.xml", False],
                ["OpenAI News", "https://openai.com/news/rss.xml", False],
                ["Google AI Blog", "https://blog.google/technology/ai/rss/", False],
                BBC_TECH, GUARDIAN_TECH, SVT_NYHETER, COMPUTER_SWEDEN, NY_TEKNIK, BREAKIT, HACKER_NEWS,
            ],
            "nyckelord": [
                "ai", "ai-*", "artificiell intelligens", "artificial intelligence", "generativ ai", "generative ai",
                "chatgpt", "gpt-*", "openai", "anthropic", "deepmind", "deepseek", "mistral ai", "hugging face",
                "llm*", "språkmodell*", "large language model*", "maskininlärning", "machine learning",
                "djupinlärning", "deep learning", "neurala nätverk", "neural network*", "chatbot*", "ai-agent*",
                "ai agent*", "agentic", "copilot", "midjourney", "stable diffusion", "multimodal*",
                "ai act", "agi", "superintelligens", "ai-säkerhet", "ai safety", "promptning", "prompt engineering",
            ],
            "tvetydiga_ord": ["claude", "gemini", "llama", "grok", "sora", "nvidia", "perplexity", "qwen", "agent*"],
            "kontextord": ["ai", "ai-*", "modell*", "model*", "chatbot*", "openai", "anthropic", "google", "meta", "xai",
                           "chip*", "gpu*", "språkmodell*", "llm*"],
            "kategoriord": ["artificial intelligence", "artificiell intelligens", "machine learning"],
        },
    },
    {
        "titel": "Digitalisering och tech", "grupp": "Teknik", "etikett": "Digitalisering",
        "farg": "#0891B2", "punkt": "blue",
        "text": "IT-system, molntjänster, e-tjänster och stora techbolag.",
        "bevakning": {
            "namn": "Digitalisering och tech",
            "kallor": [
                som(COMPUTER_SWEDEN, False), som(NY_TEKNIK, False),
                ["The Verge", "https://www.theverge.com/rss/index.xml", True],
                ["Ars Technica", "https://feeds.arstechnica.com/arstechnica/index", True],
                ["Wired", "https://www.wired.com/feed/rss", True],
                ["TechCrunch", "https://techcrunch.com/feed/", True],
                ["Engadget", "https://www.engadget.com/rss.xml", True],
                BREAKIT, BBC_TECH, GUARDIAN_TECH, SVT_NYHETER, HACKER_NEWS,
            ],
            "nyckelord": [
                "digitaliser*", "digital transformation", "e-tjänst*", "molntjänst*", "moln*", "cloud",
                "saas", "it-system*", "it-upphandling*", "it-avdelning*", "systembyte*", "affärssystem*",
                "e-legitimation*", "bankid", "digg", "eidas", "e-hälsa", "journalsystem*", "öppen källkod",
                "open source", "öppna data", "open data", "api*", "dataskydd*", "gdpr", "digital suveränitet",
                "datacenter*", "microsoft", "google", "amazon web services", "aws", "azure", "apple", "meta",
                "salesforce", "sap", "oracle", "big tech", "techbolag*", "5g", "fiber*", "bredband*",
                "kvantdator*", "quantum computing",
            ],
            "tvetydiga_ord": ["plattform*", "app", "appen", "system"],
            "kontextord": ["digital*", "it-*", "teknik*", "tech*", "e-tjänst*", "data*", "mjukvar*", "software"],
            "kategoriord": ["teknik", "technology", "digitalisering"],
        },
    },
    {
        "titel": "Cybersäkerhet", "grupp": "Teknik", "etikett": "Säkerhet",
        "farg": "#DC2626", "punkt": "red",
        "text": "Attacker, dataläckor, sårbarheter och nya krav som NIS2.",
        "bevakning": {
            "namn": "Cybersäkerhet",
            "kallor": [
                ["The Hacker News", "https://feeds.feedburner.com/TheHackersNews", False],
                ["BleepingComputer", "https://www.bleepingcomputer.com/feed/", False],
                ["Krebs on Security", "https://krebsonsecurity.com/feed/", False],
                ["Dark Reading", "https://www.darkreading.com/rss.xml", False],
                ["SecurityWeek", "https://www.securityweek.com/feed/", False],
                ["Schneier on Security", "https://www.schneier.com/feed/atom/", False],
                COMPUTER_SWEDEN, NY_TEKNIK, SVT_NYHETER, SVT_INRIKES, EKOT, BBC_TECH, GUARDIAN_TECH,
            ],
            "nyckelord": [
                "cyberattack*", "cyberangrepp*", "it-attack*", "it-angrepp*", "dataintrång*", "intrång*",
                "hackare", "hackarna", "hackad*", "hackattack*", "ransomware", "gisslanprogram*", "utpressningsvirus",
                "överbelastningsattack*", "ddos*", "nätfiske*", "phishing", "bedrägeri*", "sårbarhet*",
                "säkerhetshål*", "vulnerabilit*", "zero-day", "nolldagssårbarhet*", "dataläck*", "data breach*",
                "läckt*", "skadlig kod", "malware", "trojan*", "botnät*", "cybersäkerhet*", "informationssäkerhet*",
                "it-säkerhet*", "nis2", "cyberresiliens*", "cert-se", "ncsc", "msb", "fra", "säpo",
                "cybersecurity", "cyber attack*", "threat actor*", "apt-grupp*",
            ],
            "tvetydiga_ord": ["attack*", "virus", "säkerhet"],
            "kontextord": ["it-*", "cyber*", "data*", "system*", "digital*", "hack*", "server*"],
            "kategoriord": ["security", "cybersäkerhet", "säkerhet", "cyber"],
        },
    },
    # ================= NÄRINGSLIV =================
    {
        "titel": "Ekonomi", "grupp": "Näringsliv", "etikett": "Finans", "farg": "#E8871E", "punkt": "orange",
        "text": "Räntor, inflation, börsen och konjunkturen i Sverige och världen.",
        "bevakning": {
            "namn": "Ekonomibevakning",
            "kallor": [
                ["Dagens industri", "https://www.di.se/rss", False],
                som(SVT_EKONOMI, False),
                som(BBC_BUSINESS, False), som(GUARDIAN_BUSINESS, False),
                ["New York Times Business", "https://rss.nytimes.com/services/xml/rss/nyt/Business.xml", False],
                ["MarketWatch", "https://feeds.content.dowjones.io/public/rss/mw_topstories", False],
                ["Yahoo Finance", "https://finance.yahoo.com/news/rssindex", False],
                ["CNBC", "https://www.cnbc.com/id/100003114/device/rss/rss.html", True],
                SVT_NYHETER, EKOT, DN, BREAKIT,
            ],
            "nyckelord": [
                "ekonomi*", "inflation*", "styrränt*", "ränt*", "riksbank*", "börs*", "stockholmsbörsen", "omx*",
                "kpi", "kpif", "bnp", "konjunktur*", "lågkonjunktur*", "högkonjunktur*", "recession",
                "arbetslöshet*", "kronan", "valuta*", "kvartalsrapport*", "delårsrapport*", "bokslut*",
                "vinstvarning*", "bostadspris*", "bolån*", "hushållens", "konkurs*", "statsbudget*",
                "finansminister*", "tullar", "tull", "handelskrig*", "interest rate*", "central bank*",
                "stock market*", "economy", "gdp", "ecb", "federal reserve", "tariff*", "earnings", "wall street",
            ],
            "tvetydiga_ord": ["fed", "räntan"],
            "kontextord": ["ränt*", "rate*", "inflation*", "powell", "centralbank*"],
            "kategoriord": ["ekonomi", "economy", "business", "näringsliv", "markets"],
        },
    },
    {
        "titel": "Hållbarhet och klimat", "grupp": "Näringsliv", "etikett": "Miljö",
        "farg": "#15803D", "punkt": "green",
        "text": "Klimatpolitik, utsläpp, energi, cirkularitet och hållbarhetsrapportering.",
        "bevakning": {
            "namn": "Hållbarhet och klimat",
            "kallor": [
                ["Aktuell Hållbarhet", "https://www.aktuellhallbarhet.se/feed/", False],
                ["The Guardian Environment", "https://www.theguardian.com/environment/rss", False],
                ["BBC Science & Environment", "http://feeds.bbci.co.uk/news/science_and_environment/rss.xml", False],
                ["Carbon Brief", "https://www.carbonbrief.org/feed/", False],
                ["New York Times Climate", "https://rss.nytimes.com/services/xml/rss/nyt/Climate.xml", False],
                ["Inside Climate News", "https://insideclimatenews.org/feed/", False],
                ["Grist", "https://grist.org/feed/", False],
                SVT_NYHETER, SVT_INRIKES, EKOT, DN, som(UPPHANDLING24, True),
            ],
            "nyckelord": [
                "klimat*", "hållbar*", "utsläpp*", "koldioxid*", "växthusgas*", "fossilfri*", "fossil*",
                "förnybar*", "solenergi", "solceller", "vindkraft*", "kärnkraft*", "vätgas*", "elektrifiering*",
                "cirkulär*", "återbruk*", "återvinning*", "biologisk mångfald", "biodiversitet*",
                "klimatanpassning*", "översvämning*", "värmebölj*", "torka", "taxonomi*", "csrd", "esg",
                "hållbarhetsrapport*", "klimatmål*", "parisavtalet", "cop30", "cop31", "klimattoppmöte*", "net zero", "netto noll",
                "climate", "emissions", "renewable*", "carbon", "sustainab*", "biodiversity",
            ],
            "tvetydiga_ord": ["miljö*", "energi*"],
            "kontextord": ["klimat*", "utsläpp*", "hållbar*", "fossil*", "förnybar*", "natur*"],
            "kategoriord": ["klimat", "miljö", "climate", "environment", "hållbarhet"],
        },
    },
    # ================= SPORT =================
    {
        "titel": "Fotboll", "grupp": "Sport", "etikett": "Sport", "farg": "#16A36A", "punkt": "green",
        "text": "Svensk och internationell fotboll från sportsajter.",
        "bevakning": {
            "namn": "Fotbollsnyheter",
            "kallor": [
                ["BBC Football", "http://feeds.bbci.co.uk/sport/football/rss.xml", False],
                ["ESPN FC", "https://www.espn.com/espn/rss/soccer/news", False],
                ["The Guardian Football", "https://www.theguardian.com/football/rss", False],
                ["New York Times Soccer", "https://rss.nytimes.com/services/xml/rss/nyt/Soccer.xml", False],
                ["Fotbollsdirekt", "https://www.fotbolldirekt.se/rss", False],
                ["Marca", "https://e00-marca.uecdn.es/rss/portada.xml", False],
                ["Sky Sports Football", "https://www.skysports.com/rss/12040", False],
                ["SVT Sport", "https://www.svt.se/sport/rss.xml", True],
                ["Aftonbladet Sport", "https://rss.aftonbladet.se/rss2/small/pages/sections/sportbladet/", True],
                ["Expressen Sport", "https://feeds.expressen.se/sport", True],
                ["BBC Sport", "http://feeds.bbci.co.uk/sport/rss.xml", True],
                ["NRK Sport", "https://www.nrk.no/sport/toppsaker.rss", True],
            ],
            "nyckelord": [
                "fotboll*", "football", "soccer", "målskytt*", "offside", "straffspark*", "hattrick",
                "allsvenskan", "allsvenska", "superettan", "damallsvenskan", "ettan", "svenska cupen",
                "champions league", "premier league", "la liga", "serie a", "bundesliga", "ligue 1",
                "europa league", "conference league", "nations league", "fifa", "uefa", "vm-kval*", "em-kval*",
                "herrlandslag*", "damlandslag*", "blågult", "transfer*", "övergång*", "värvning*",
                "malmö ff", "ifk göteborg", "ifk norrköping", "elfsborg", "häcken", "sirius", "mjällby",
                "kalmar ff", "degerfors", "värnamo", "brommapojkarna", "gais", "halmstad", "örebro sk",
                "varbergs bois", "real madrid", "barcelona", "atletico madrid", "liverpool", "manchester united",
                "manchester city", "arsenal", "chelsea", "tottenham", "newcastle", "aston villa",
                "bayern münchen", "borussia dortmund", "psg", "juventus", "ac milan", "inter", "napoli",
                "gyökeres", "isak", "kulusevski",
            ],
            "tvetydiga_ord": ["aik", "djurgården", "hammarby", "landslaget", "vm", "em"],
            "kontextord": ["fotboll*", "allsvensk*", "superettan", "tränar*", "mittfältar*", "anfallar*",
                           "försvarar*", "målvakt*", "straff*", "offside", "seriematch*", "bortamatch*",
                           "hemmamatch*", "poängtapp*", "mål", "målet", "football"],
            "kategoriord": ["fotboll", "football", "soccer"],
        },
    },
]

GRUPPER = ["Samhälle", "Teknik", "Näringsliv", "Sport"]
