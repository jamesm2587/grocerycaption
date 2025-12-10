# constants.py

INITIAL_BASE_CAPTIONS = {
    'LA_HACIENDA_MARKET': {
        'GENERAL_STOCK': {
            'id': 'lahacienda_stock',
            'name': "La Hacienda Market (General Stock)", 
            'language': "spanish", 
            'original_example': "¡Visítanos en La Hacienda Market! Tenemos burritos, quesadillas, y tacos recién hechos, y la carne y verdura más fresca. ¡Todo lo que necesitas para tu comida!",
            'defaultProduct': "Prepared Foods (Burritos, Tacos, etc.)",
            'defaultPrice': "", # Price is not the focus
            'dateFormat': "", # No sale dates needed
            'durationTextPattern': "",
            'location': "La Hacienda Market",
            'baseHashtags': "#LaHaciendaMarket #ComidaMexicana #HechoEnCasa #Burritos #Tacos #Quesadillas #Menudo #CarneFresca #VerdurasFrescas #ShopLocal"
        },
        'MENUDO_WEEKEND': {
            'id': 'lahacienda_menudo',
            'name': "La Hacienda Market (Menudo Weekend)", 
            'language': "spanish", 
            'original_example': "¡Ya es fin de semana y el cuerpo pide Menudo! Ven a La Hacienda Market por tu plato, calientito y con todo el sabor casero. ¡No te quedes con el antojo!",
            'defaultProduct': "Menudo Fresco",
            'defaultPrice': "", # Price is often variable or not the focus
            'dateFormat': "", # Assumed to be weekend, no specific dates
            'durationTextPattern': "Fin de Semana", # Implies weekend
            'location': "La Hacienda Market",
            'baseHashtags': "#Menudo #FinDeSemana #LaHaciendaMarket #SaborCasero #ComidaMexicana #MenudoTime #AntojoCumplido #Finde"
        }
    },
    'TEDS_FRESH_MARKET': {
        'THREE_DAY': {'id': 'teds_3_day', 'name': "Ted's Fresh Market (3-Day Sale)", 'language': "english", 'original_example': "Fresh Eggplant or Broccoli 79¢ x lb.\n3 DAYS ONLY 05/13-05/15\n2840 W. Devon Ave.\n...", 'defaultProduct': "Fresh Eggplant or Broccoli", 'defaultPrice': "79¢ x lb.", 'dateFormat': "MM/DD-MM/DD", 'durationTextPattern': "3 DAYS ONLY", 'location': "2840 W. Devon Ave.", 'baseHashtags': "#Sale #ShopLocal #Fresh #Groceries #Produce #USDA #Halal #TedsFreshMarket #GroceryDeals #WeeklyDeals #FreshProduce"},
        'FOUR_DAY': {'id': 'teds_4_day', 'name': "Ted's Fresh Market (4-Day Sale)", 'language': "english", 'original_example': "Sweet Minneola Orange 89¢ x lb.\n4 DAYS ONLY 05/09-05/12\n2840 W. Devon Ave.\n...", 'defaultProduct': "Sweet Minneola Oranges", 'defaultPrice': "89¢ x lb.", 'dateFormat': "MM/DD-MM/DD", 'durationTextPattern': "4 DAYS ONLY", 'location': "2840 W. Devon Ave.", 'baseHashtags': "#Sale #ShopLocal #Fresh #Groceries #Produce #USDA #Halal #TedsFreshMarket #GroceryDeals #WeeklyDeals #CitrusLove"}
    },
    'LA_PRINCESA_MARKET': {
        'WEEK_LONG': {'id': 'laprincesa_week', 'name': "La Princesa Market (Week-Long)", 'language': "spanish", 'original_example': "Bistec de Bola o Bistec de Espaldilla $4.99 x lb.\nHasta 05/20/25\n...", 'defaultProduct': "Bistec de Bola o Espaldilla", 'defaultPrice': "$4.99 x lb.", 'dateFormat': "Hasta DD/MM/YY", 'durationTextPattern': "Hasta el", 'location': "1260 Main st. & 1424 Freedom Blvd.", 'baseHashtags': "#Ofertas #LaPrincesaMarket #CarneFresca #Ahorra #ComidaLatina #TiendaLocal"}
    },
    'MI_TIENDITA': {
        'WEEKLY_SALE': {'id': 'mitiendita_weekly', 'name': "Mi Tiendita (Ahorros Semanales)", 'language': "spanish", 'original_example': "Trocitos de Puerco $3.49 x lb.\n Ahorros 05/14 - 05/20\n...", 'defaultProduct': "Trocitos de Puerco", 'defaultPrice': "$3.49 x lb.", 'dateFormat': "MM/DD - MM/DD", 'durationTextPattern': "Ahorros", 'location': "3145 Payne Ave. San Jose, CA 95117", 'baseHashtags': "#OfertasDeLaSemana #MiTiendita #Ahorra #Sabor #Carne #Verduras #ahorros #grocerydeal #weeklysavings #weeklydeals"}
    },
    'VIVA_SUPERMARKET': {
        'DEAL_UNTIL': {'id': 'viva_deal', 'name': "Viva Supermarket (Weekly Deal)", 'language': "english", 'original_example': "All Natural Halal Chicken Leg Meat $2.49 x lb.\n Deal until from 05/14-05/20\n...", 'defaultProduct': "All Natural Halal Chicken Leg Meat", 'defaultPrice': "$2.49 x lb.", 'dateFormat': "MM/DD-MM/DD", 'durationTextPattern': "Deal until from", 'location': "Viva Supermarket", 'baseHashtags': "#vivasupermarket #grocerydeals #groceryspecials #weeklysavings #weeklyspecials #grocery #abarrotes #carniceria #mariscos #seafood #produce #frutasyverduras #ahorros #ofertas"}
    },
    'INTERNATIONAL_FRESH_MARKET': {
        'THREE_DAY_SALE': {'id': 'ifm_3_day', 'name': "International Fresh Market (3 Day Sale)", 'language': "english", 'original_example': "3 DAY SALE\n 05/13 - 05/15\n Fresh Zucchini 35¢ x lb.\n...", 'defaultProduct': "Fresh Zucchini", 'defaultPrice': "35¢ x lb.", 'dateFormat': "MM/DD - MM/DD", 'durationTextPattern': "3 DAY SALE", 'location': "International Fresh Market, Naperville", 'baseHashtags': "#Naperville #Fresh #Market #Produce #Meat #internationalfreshmarket"},
        'CUSTOMER_APPRECIATION_SALE': {'id': 'ifm_customer_appreciation', 'name': "International Fresh Market (Customer Appreciation Sale)", 'language': "english", 'original_example': "CUSTOMER APPRECIATION SALE \n Fresh Green Cabbage 25¢ x lb.\n4 Days Only 05/09-05/12\n...", 'defaultProduct': "Fresh Green Cabbage", 'defaultPrice': "25¢ x lb.", 'dateFormat': "MM/DD-MM/DD", 'durationTextPattern': "4 Days Only", 'location': "International Fresh Market, Naperville", 'baseHashtags': "#Naperville #Fresh #Market #Produce #Meat #internationalfreshmarket"}
    },
    'SAMS_FOODS_SUPERMARKET': {
        'WEEKLY_SPECIALS': {
            'id': 'samsfods_weekly',
            'name': "Sams Foods Supermarket (Weekly Specials)",
            'language': "english",
            'original_example': "Beef Chuck Roast Steak $4.85 x lb.\n Pricing 05/28-06/03\n1805 Dairy Ave. Corcoran, CA.",
            'defaultProduct': "Beef Chuck Roast Steak",
            'defaultPrice': "$4.85 x lb.",
            'dateFormat': "MM/DD-MM/DD",
            'durationTextPattern': "Pricing",
            'location': "1805 Dairy Ave. Corcoran, CA.",
            'baseHashtags': "#SamsFods #Supermarket #CorcoranCA #GroceryDeals #WeeklySpecials #MeatDeals #BeefRoast #ShopLocal"
        }
    },
    # --- CORRECTED STORE PLACEMENT ---
    'RRANCH_MARKET': {
        'WEEKLY_DEAL': {
            'id': 'rranchmarket_weekly',
            'name': "RRanch Market (Weekly Deal)",
            'language': "spanish",
            'original_example': "Espinazo de Puerco $2.29 x lb.\nWeekly Deal 06/04-06/17\n...\n#weeklydeals #grocerydeals #groceryspecials",
            'defaultProduct': "Espinazo de Puerco",
            'defaultPrice': "$2.29 x lb.",
            'dateFormat': "MM/DD-MM/DD",
            'durationTextPattern': "Weekly Deal",
            'location': "RRanch Market",
            'baseHashtags': "#RRanchMarket #OfertasSemanales #weeklydeals #grocerydeals #groceryspecials #carniceria"
        }
    },
    'MI_RANCHO_SUPERMARKET': {
        'WEEKLY_OFFERS': {
            'id': 'mirancho_weekly',
            'name': "Mi Rancho Supermarket (Ofertas de la Semana)",
            'language': "spanish",
            'original_example': "🍖 Trocitos de Puerco $1.99 x lb.\nOfertas válidas 12/03 - 12/09 🗓️\n🕖 Horario: 7 AM – 9 PM\nDescubre todas las ofertas en 👉 miranchosupermarket.com\n#MiRanchoSupermarket #OfertasDeLaSemana #AhorraMás #CaliforniaMarkets",
            'defaultProduct': "Trocitos de Puerco",
            'defaultPrice': "$1.99 x lb.",
            'dateFormat': "MM/DD - MM/DD",
            'durationTextPattern': "Ofertas válidas",
            'location': "Mi Rancho Supermarket, California",
            'baseHashtags': "#MiRanchoSupermarket #OfertasDeLaSemana #AhorraMás #CaliforniaMarkets"
        }
    }
}
TONE_OPTIONS = [{'value': "Simple", 'label': "Simple & Clear"}, {'value': "Fun", 'label': "Fun & Engaging"}, {'value': "Excited", 'label': "Excited & Urgent"}, {'value': "Professional", 'label': "Professional & Direct"}, {'value': "Friendly", 'label': "Friendly & Warm"}, {'value': "Informative", 'label': "Informative & Detailed"}, {'value': "Humorous", 'label': "Humorous & Witty"}, {'value': "Seasonal", 'label': "Seasonal / Festive"}, {'value': "Elegant", 'label': "Elegant & Refined"}, {'value': "Bold", 'label': "Bold & Punchy"}, {'value': "Nostalgic", 'label': "Nostalgic & Heartfelt"}]
PREDEFINED_PRICES = [{'value': "¢ / lb.", 'label': "¢ / lb. (e.g., 69¢ / lb.)"}, {'value': "$ / lb.", 'label': "$X.XX / lb. (e.g., $4.99 / lb.)"}, {'value': "$ each", 'label': "$X.XX each (e.g., $1.50 each)"}, {'value': "¢ each", 'label': "¢ each (e.g., 99¢ each)"}, {'value': "X for $Y", 'label': "X for $Y.YY (e.g., 2 for $5.00)"}, {'value': "CUSTOM", 'label': "Enter Custom Price..."}]
