import os

RAPIDAPI_KEY = os.environ.get("RAPIDAPI_KEY", "122ec983ecmshc311b9bfd74e54ap125147jsn64f37f88a8dd")
RAPIDAPI_HOST = "free-api-live-football-data.p.rapidapi.com"
PORT = int(os.environ.get("PORT", 8000))

# Mashhur va otamiz qiziqadigan ligalar
SUPPORTED_LEAGUES = [
    {
        "id": 47,
        "name": "APL",
        "fullName": "Angliya Premyer Ligasi",
        "country": "Angliya",
        "flag": "🇬🇧",
        "icon": "https://images.fotmob.com/image_resources/logo/leaguelogo/dark/47.png"
    },
    {
        "id": 87,
        "name": "La Liga",
        "fullName": "Ispaniya La Ligasi",
        "country": "Ispaniya",
        "flag": "🇪🇸",
        "icon": "https://images.fotmob.com/image_resources/logo/leaguelogo/dark/87.png"
    },
    {
        "id": 71,
        "name": "Turkiya Superligasi",
        "fullName": "Turkiya Super Ligasi",
        "country": "Turkiya",
        "flag": "🇹🇷",
        "badge": "O'zbek legionerlarimiz",
        "icon": "https://images.fotmob.com/image_resources/logo/leaguelogo/dark/71.png"
    },
    {
        "id": 55,
        "name": "A Seriya",
        "fullName": "Italiya A Seriyasi",
        "country": "Italiya",
        "flag": "🇮🇹",
        "icon": "https://images.fotmob.com/image_resources/logo/leaguelogo/dark/55.png"
    },
    {
        "id": 42,
        "name": "Chempionlar Ligasi",
        "fullName": "UEFA Chempionlar Ligasi",
        "country": "Yevropa",
        "flag": "🇪🇺",
        "icon": "https://images.fotmob.com/image_resources/logo/leaguelogo/dark/42.png"
    },
    {
        "id": 54,
        "name": "Bundesliga",
        "fullName": "Germaniya Bundesligasi",
        "country": "Germaniya",
        "flag": "🇩🇪",
        "icon": "https://images.fotmob.com/image_resources/logo/leaguelogo/dark/54.png"
    }
]

# Bizning o'zbek yulduzlarimiz (Legionerlar)
LEGIONER_PLAYERS = [
    {
        "id": "shomurodov",
        "name": "Eldor Shomurodov",
        "role": "Hujumchi",
        "teamName": "Roma",
        "teamId": 8686,
        "leagueId": 55,
        "leagueName": "Italiya A Seriyasi",
        "country": "O'zbekiston 🇺🇿",
        "teamLogo": "https://images.fotmob.com/image_resources/logo/teamlogo/8686.png",
        "badge": "O'zbekiston sardori"
    },
    {
        "id": "fayzullaev",
        "name": "Abbosbek Fayzullayev",
        "role": "Hujumkor yarim himoyachi",
        "teamName": "CSKA Moskva",
        "teamId": 10255,
        "leagueId": 109,
        "leagueName": "Rossiya Premyer-ligasi",
        "country": "O'zbekiston 🇺🇿",
        "teamLogo": "https://images.fotmob.com/image_resources/logo/teamlogo/10255.png",
        "badge": "Osiyoning eng yaxshi yosh futbolchisi"
    },
    {
        "id": "aliqulov",
        "name": "Husniddin Aliqulov",
        "role": "Markaziy himoyachi",
        "teamName": "Caykur Rizespor",
        "teamId": 9752,
        "leagueId": 71,
        "leagueName": "Turkiya Superligasi",
        "country": "O'zbekiston 🇺🇿",
        "teamLogo": "https://images.fotmob.com/image_resources/logo/teamlogo/9752.png",
        "badge": "Turkiyadagi legionerimiz"
    },
    {
        "id": "urunov",
        "name": "Oston O'runov",
        "role": "Hujumkor vinger",
        "teamName": "Persepolis",
        "teamId": 101610,
        "leagueId": 525,
        "leagueName": "OFK Chempionlar Ligasi",
        "country": "O'zbekiston 🇺🇿",
        "teamLogo": "https://images.fotmob.com/image_resources/logo/teamlogo/101610.png",
        "badge": "Osiyo Chempionlar Ligasi yulduzi"
    }
]
