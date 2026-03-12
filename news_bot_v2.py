# -*- coding: utf-8 -*-
"""
Умный Telegram-бот для агрегации новостей v2.0
С семантическим анализом и сравнением источников
"""

from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes, CallbackContext
import feedparser
import hashlib
from datetime import datetime, timedelta
import asyncio
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import re

# ========== КОНФИГУРАЦИЯ ==========
BOT_TOKEN = "8643615168:AAH-V36MWb8FYQ7rQFJslax6i3K8NTEGdis"

NEWS_SOURCES = {
    'BBC News': 'http://feeds.bbci.co.uk/news/rss.xml',
    'BBC World': 'http://feeds.bbci.co.uk/news/world/rss.xml',
    'Reuters World': 'https://www.reuters.com/rssFeed/worldNews',
    'Al Jazeera': 'https://www.aljazeera.com/xml/rss/all.xml',

    'Reuters Business': 'https://www.reuters.com/rssFeed/businessNews',
    'BBC Business': 'http://feeds.bbci.co.uk/news/business/rss.xml',
    'RBC': 'https://rssexport.rbc.ru/rbcnews/news/30/full.rss',
    'Коммерсант': 'https://www.kommersant.ru/RSS/main.xml',

    'CoinDesk': 'https://www.coindesk.com/arc/outboundfeeds/rss/',
    'CoinTelegraph': 'https://cointelegraph.com/rss',
    'Bitcoin Magazine': 'https://bitcoinmagazine.com/.rss/full/',
    'Crypto News': 'https://cryptonews.com/news/feed/',

    'Onliner': 'https://www.onliner.by/feed',
    'Naviny': 'https://naviny.online/rss.xml',

    'Meduza': 'https://meduza.io/rss/all',
    'Lenta.ru': 'https://lenta.ru/rss/news',
    'TASS': 'https://tass.ru/rss/v2.xml',

    'CNN': 'http://rss.cnn.com/rss/edition.rss',
    'Fox News': 'https://moxie.foxnews.com/google-publisher/latest.xml',
    'The Guardian': 'https://www.theguardian.com/world/rss',

    'ECNS.cn': 'https://www.ecns.cn/rss/rss.xml',
    'China.org.cn': 'https://www.china.org.cn/rss/1201719.xml',
    'China Underground': 'https://china-underground.com/feed/',
    
    'IRNA (English)': 'https://en.irna.ir/rss',
    'Tasnim News (English)': 'https://www.tasnimnews.com/en/rss/feed',
    'Tehran Times': 'https://www.tehrantimes.com/rss',

    'BBC News': 'http://feeds.bbci.co.uk/news/rss.xml',
    'The Guardian World': 'https://www.theguardian.com/world/rss',
    'Daily Mail': 'https://www.dailymail.co.uk/home/index.rss',

    'The New York Times': 'https://rss.nytimes.com/services/xml/rss/nyt/HomePage.xml',
    'CNN Top Stories': 'http://rss.cnn.com/rss/cnn_topstories.rss',
    'Reuters World News': 'https://feeds.reuters.com/reuters/worldNews',

    'RT News': 'https://www.rt.com/rss/',
    'TASS (English)': 'https://tass.com/rss/v2.xml',
    'RIA Novosti': 'https://ria.ru/export/rss2/index.xml',

    'Tagesschau': 'http://www.tagesschau.de/xml/rss2',
    'Deutsche Welle (EN)': 'https://rss.dw.com/rdf/rss-en-all',
    'ZEIT Online': 'http://newsfeed.zeit.de/index',

    'France 24 (EN)': 'https://www.france24.com/en/rss',
    'Le Monde': 'https://www.lemonde.fr/rss/une.xml',
    'Franceinfo': 'https://www.francetvinfo.fr/titres.rss',

    'El País Portada': 'https://feeds.elpais.com/mrss-s/pages/ep/site/elpais.com/portada',
    'El Confidencial España': 'https://rss.elconfidencial.com/espana/',
    'Agencia EFE (EN)': 'https://www.efe.com/efe/english/4/rss',

    'ANSA': 'https://www.ansa.it/sito/ansait_rss.xml',
    'La Repubblica': 'https://www.repubblica.it/rss/homepage/rss2.0.xml',
    'Corriere della Sera': 'https://www.corriere.it/rss/homepage.xml',

    'Anadolu Agency (World)': 'https://www.aa.com.tr/en/rss/default',
    'Daily Sabah': 'https://www.dailysabah.com/rssFeed/1',
    'Hurriyet Daily News': 'https://www.hurriyetdailynews.com/rss.php',

    'Ukrinform (EN)': 'https://www.ukrinform.net/rss/block-lastnews',
    'UNIAN': 'https://www.unian.info/rss',
    'Liga.net': 'https://www.liga.net/news/rss',

    'Onet Wiadomosci': 'https://wiadomosci.onet.pl/rss',
    'TVN24': 'https://tvn24.pl/najnowsze.xml',
    'Gazeta Wyborcza': 'https://wyborcza.pl/pub/rss/wiadomosci_kraj.jsp',

    'BelTA (EN)': 'https://eng.belta.by/rss',
    'BelTA (RU)': 'https://www.belta.by/rss',
    'SB Belarus Segodnya': 'https://www.sb.by/rss.html',

    'Saudi Gazette': 'https://saudigazette.com.sa/rssFeed/74',
    'Okaz': 'https://www.okaz.com.sa/rssFeed/190',
    'Al Yaum': 'https://www.alyaum.com/rssFeed/1',

    'Emirates News Agency (WAM)': 'https://wam.ae/en/rss',
    'UAE Today': 'https://blog.uaetoday.com/feed',
    'Zawya Press Releases': 'https://www.zawya.com/sitemaps/en/rss',

    'The Jerusalem Post': 'https://www.jpost.com/Rss/RssFeedsHeadlines.aspx',
    'Haaretz (EN)': 'https://www.haaretz.com/cmlink/1.663',
    'Ynetnews': 'https://www.ynetnews.com/Integration/StoryRss2.xml',

    'Ahram Online': 'https://english.ahram.org.eg/rss/1/0/0/Main-Section.aspx',
    'Daily News Egypt': 'https://dailynewsegypt.com/feed/',
    'Egypt Independent': 'https://egyptindependent.com/feed/',

    'APS (Algeria Press Service)': 'https://www.aps.dz/en/rss',
    'TSA Algérie': 'https://www.tsa-algerie.com/feed/',
    'El Moudjahid': 'https://www.elmoudjahid.com/en/rss.xml',

    'News24 Top Stories': 'https://feeds.24.com/articles/news24/TopStories/rss',
    'Mail & Guardian': 'https://mg.co.za/feed/',
    'TimesLIVE': 'https://www.timeslive.co.za/rss',

    'Folha de S.Paulo': 'https://feeds.folha.uol.com.br/emcimadahora/rss091.xml',
    'EBC Portal': 'http://www.ebc.com.br/rss/feed.xml',
    'UOL Notícias': 'http://rss.home.uol.com.br/index.xml',

    'The Hindu': 'https://www.thehindu.com/news/national/feeder/default.rss',
    'Times of India Top Stories': 'https://timesofindia.indiatimes.com/rssfeedstopstories.cms',
    'NDTV Top Stories': 'https://feeds.feedburner.com/ndtvnews-top-stories',

    'SUNA (Sudan News Agency)': 'https://suna-sd.net/en/rss',
    'Sudan Tribune': 'https://sudantribune.com/feed/',
    'Radio Dabanga': 'https://www.dabangasudan.org/en/all-news/feed',

    'The Punch': 'https://punchng.com/feed/',
    'Premium Times Nigeria': 'https://www.premiumtimesng.com/feed',
    'Channels TV': 'https://www.channelstv.com/feed/',

    'Télam Últimas Noticias': 'https://www.telam.com.ar/rss2/ultimasnoticias.xml',
    'La Nación': 'https://www.lanacion.com.ar/feed/',
    'Clarín Último Momento': 'https://www.clarin.com/rss/lo-ultimo/',

    'Telesur English': 'https://www.telesurenglish.net/rss/RssFeeds.html',
    'Correo del Orinoco': 'https://www.correodelorinoco.gob.ve/feed/',
    'Últimas Noticias': 'https://ultimasnoticias.com.ve/feed/',

    'El Universal': 'https://www.eluniversal.com.mx/rss/mxm.xml',
    'La Jornada': 'https://www.jornada.com.mx/rss/ultimas',
    'Milenio': 'https://www.milenio.com/rss/feed.xml',

    'Hungary Today': 'https://hungarytoday.hu/feed/',
    'Daily News Hungary': 'https://dailynewshungary.com/feed/',
    'Index.hu': 'https://index.hu/24ora/rss/',

    'Dawn': 'https://www.dawn.com/feed',
    'The Express Tribune': 'https://tribune.com.pk/feed/home',
    'The Nation Top Stories': 'https://nation.com.pk/rss/top-stories',

    'ABC News': 'https://www.abc.net.au/news/feed/1948/rss.xml',
    'Sydney Morning Herald': 'https://www.smh.com.au/rss/feed.xml',
    'The Age': 'https://www.theage.com.au/rss/feed.xml',
}

NEWS_LOOKBACK_HOURS = 3
SIMILARITY_THRESHOLD = 0.70
MAX_NEWS_PER_MESSAGE = 10
AUTO_SEND_INTERVAL_HOURS = 2  # авторассылка каждые 2 часа

# Какие категории нам интересны
ALLOWED_CATEGORIES = {
    '💰 Криптовалюты',
    '📈 Экономика',
    '⚔️ Конфликты',
    '🏛️ Политика',
}

class SmartNewsAnalyzer:
    def __init__(self):
        print("🧠 Загружаю AI-модель для анализа текстов...")
        self.model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')
        print("✅ Модель загружена!\n")
        self.threshold = SIMILARITY_THRESHOLD

    def clean_text(self, text):
        text = re.sub('<[^<]+?>', '', text)
        text = ' '.join(text.split())
        return text

    def group_similar_news(self, news_list):
        if not news_list:
            return []

        print(f"🔍 Анализирую {len(news_list)} новостей на схожесть...")

        texts = []
        for item in news_list:
            title = self.clean_text(item['title'])
            desc = self.clean_text(item.get('description', ''))
            combined = f"{title}. {desc[:200]}"
            texts.append(combined)

        embeddings = self.model.encode(texts, show_progress_bar=False)
        similarity_matrix = cosine_similarity(embeddings)

        grouped = []
        used_indices = set()

        for i in range(len(news_list)):
            if i in used_indices:
                continue

            similar_indices = np.where(similarity_matrix[i] >= self.threshold)[0]

            group = {
                'main_news': news_list[i],
                'sources': [],
                'similarity_count': len(similar_indices)
            }

            for idx in similar_indices:
                if idx not in used_indices:
                    news = news_list[idx]
                    group['sources'].append({
                        'name': news['source'],
                        'title': news['title'],
                        'description': news.get('description', ''),
                        'link': news['link'],
                        'region': self.detect_region(news['source'])
                    })
                    used_indices.add(idx)

            group['sources'].sort(key=lambda x: x['region'])
            grouped.append(group)

        print(f"✅ Сгруппировано в {len(grouped)} уникальных событий\n")
        grouped.sort(key=lambda x: x['similarity_count'], reverse=True)
        return grouped

    def detect_region(self, source_name):
        s = source_name.lower()

        if any(x in s for x in ['bbc', 'guardian', 'reuters', 'cnn', 'fox']):
            return '🇬🇧🇺🇸 Запад'
        elif any(x in s for x in ['rbc', 'lenta', 'tass', 'коммерсант', 'meduza']):
            return '🇷🇺 Россия'
        elif any(x in s for x in ['onliner', 'naviny']):
            return '🇧🇾 Беларусь'
        elif 'jazeera' in s:
            return '🌍 Ближний Восток'
        elif 'coin' in s or 'crypto' in s or 'bitcoin' in s:
            return '₿ Крипто'
        else:
            return '🌐 Международные'

    def categorize_news(self, text):
        """Определяет категорию новости по многоязычным ключевым словам"""
        t = text.lower()
        categories = []

        # 💰 КРИПТОВАЛЮТЫ
        crypto_words = [
            'bitcoin', 'crypto', 'cryptocurrency', 'blockchain', 'ethereum',
            'btc', 'eth', 'altcoin', 'stablecoin', 'defi', 'nft',
            'криптовалюта', 'крипта', 'биткоин', 'эфириум', 'блокчейн',
            'criptomoneda', 'criptomoeda', 'criptomonedas', 'criptos',
            'criptografía', 'kryptowährung', 'krypto', 'monnaie virtuelle',
        ]
        if any(w in t for w in crypto_words):
            categories.append('💰 Криптовалюты')

        # 📈 ЭКОНОМИКА
        economy_words = [
            'economy', 'economic', 'gdp', 'inflation', 'recession',
            'interest rate', 'interest rates', 'stock market', 'stocks',
            'bond yield', 'unemployment', 'trade deficit', 'trade surplus',
            'экономика', 'экономический', 'ввп', 'инфляция', 'рецессия',
            'ставка цб', 'ключевая ставка', 'процентная ставка',
            'фондовый рынок', 'акции', 'облигации', 'безработица',
            'торговый баланс', 'торговый дефицит',
            'wirtschaft', 'konjunktur', 'rezession', 'inflation',
            'bruttoinlandsprodukt', 'arbeitslosigkeit', 'zinssatz',
            'economía', 'economico', 'económico', 'recesión', 'inflación',
            'desempleo', 'tasa de interés', 'mercado bursátil',
            'economia', 'recessão', 'desemprego', 'taxa de juros',
            'économie', 'économique', 'récession', 'chômage',
            'taux d\'intérêt', 'marché boursier',
        ]
        if any(w in t for w in economy_words):
            categories.append('📈 Экономика')

        # ⚔️ КОНФЛИКТЫ / ВОЙНА
        conflict_words = [
            'war', 'conflict', 'clashes', 'shelling', 'airstrike',
            'offensive', 'counteroffensive', 'frontline', 'military operation',
            'troops', 'forces', 'army', 'drone strike', 'missile strike',
            'война', 'военный конфликт', 'конфликт', 'боевые действия',
            'обстрел', 'обстрелы', 'ракетный удар', 'удар дроном',
            'контрнаступление', 'наступление', 'линия фронта', 'фронт',
            'военная операция', 'мобилизация', 'армия', 'вооруженные силы',
            'війна', 'обстрiл', 'ракетний удар', 'контрнаступ',
            'krieg', 'konflikt', 'militärisch', 'frontlinie', 'luftangriff',
            'guerra', 'conflicto', 'ataque con misiles', 'ofensiva',
            'guerra civil', 'forças armadas', 'conflito armado',
            'guerre', 'conflit', 'frappe de missile', 'offensive militaire',
        ]
        if any(w in t for w in conflict_words):
            categories.append('⚔️ Конфликты')

        # 🏛️ ПОЛИТИКА
        politics_words = [
            'president', 'prime minister', 'government', 'parliament',
            'election', 'elections', 'vote', 'voting', 'coalition',
            'opposition', 'sanction', 'sanctions', 'diplomatic', 'referendum',
            'party leader', 'democrats', 'republicans', 'congress',
            'президент', 'премьер-министр', 'премьер министр',
            'правительство', 'парламент', 'сенат', 'дума',
            'выборы', 'голосование', 'референдум', 'коалиция',
            'оппозиция', 'санкции', 'санкция', 'дипломатия',
            'политическая партия', 'партия власти',
            'президент україни', 'верховна рада', 'уряд україни',
            'präsident', 'bundeskanzler', 'regierung', 'bundestag',
            'wahl', 'wahlen', 'koalition', 'opposition', 'sanktionen',
            'presidente', 'primer ministro', 'gobierno', 'parlamento',
            'elección', 'elecciones', 'votación', 'coalición', 'oposición',
            'sanciones', 'governo', 'parlamento', 'eleições', 'votação',
            'président', 'premier ministre', 'gouvernement', 'parlement',
            'élection', 'élections', 'vote', 'coalition', 'opposition',
            'sanctions',
        ]
        if any(w in t for w in politics_words):
            categories.append('🏛️ Политика')

        return categories if categories else ['📰 Общее']




class AdvancedNewsParser:
    def __init__(self, sources):
        self.sources = sources

    def fetch_news(self, hours_back=3):
        all_news = []
        cutoff_time = datetime.now() - timedelta(hours=hours_back)

        print(f"🔍 Собираю новости за последние {hours_back} часов из {len(self.sources)} источников...")
        success_count = 0

        for source_name, rss_url in self.sources.items():
            # 1) проверяем, что это строка‑URL
            if not isinstance(rss_url, str):
                print(f"   ❌ {source_name}: некорректный URL (ожидаю строку, а получил {type(rss_url)})")
                continue

            try:
                feed = feedparser.parse(rss_url)
                source_news_count = 0

                for entry in feed.entries:
                    pub_date = None
                    if hasattr(entry, 'published_parsed') and entry.published_parsed:
                        pub_date = datetime(*entry.published_parsed[:6])
                    elif hasattr(entry, 'updated_parsed') and entry.updated_parsed:
                        pub_date = datetime(*entry.updated_parsed[:6])
                    else:
                        pub_date = datetime.now()

                    if pub_date < cutoff_time:
                        continue

                    description = ''
                    if hasattr(entry, 'summary'):
                        description = entry.summary
                    elif hasattr(entry, 'description'):
                        description = entry.description

                                        # Аккуратно достаём ссылку
                    link = getattr(entry, "link", None)

                    # Если link — словарь (Atom: {'href': '...'}), вытаскиваем href
                    if isinstance(link, dict):
                        link = link.get("href") or link.get("url")

                    # Если ссылки нет вообще — пробуем id
                    if not link and hasattr(entry, "id"):
                        link = entry.id

                    # В крайнем случае просто приводим к строке
                    link_str = str(link) if link is not None else ""

                    if not link_str:
                        # Совсем без ссылки и id — пропускаем такую новость
                        continue

                    news_id = hashlib.md5(link_str.encode("utf-8", errors="ignore")).hexdigest()

                    news_item = {
                        "id": news_id,
                        "source": source_name,
                        "title": entry.title,
                        "description": description,
                        "link": link_str,
                        "published": pub_date,
                    }


                    all_news.append(news_item)
                    source_news_count += 1

                if source_news_count > 0:
                    print(f"   ✅ {source_name}: {source_news_count} новостей")
                    success_count += 1

            except Exception as e:
                print(f"   ❌ {source_name}: ошибка - {str(e)[:50]}")

        print(f"\n✅ Успешно: {success_count}/{len(self.sources)} источников")
        print(f"📰 Всего собрано: {len(all_news)} новостей\n")

        all_news.sort(key=lambda x: x['published'], reverse=True)
        return all_news


class SmartNewsBot:
    def __init__(self, token):
        self.token = token
        self.parser = AdvancedNewsParser(NEWS_SOURCES)
        self.analyzer = SmartNewsAnalyzer()
        print("🤖 Умный бот готов к работе!\n")
        self.subscribers = set()      # чат‑ID пользователей, подписанных на рассылку
        self.last_sent_ids = set()    # ID новостей, которые уже отправляли в авторассылке
        self.last_groups = {}   # chat_id -> список сгруппированных событий
        self.last_index = {}    # chat_id -> с какого индекса выдавать дальше

    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_id = update.effective_chat.id
        self.subscribers.add(user_id)

        welcome_text = (
            "🤖 *Привет! Я умный бот-агрегатор новостей v2.0!*\n\n"
            "🎯 *Мои возможности:*\n"
            "• Собираю новости из 20+ источников\n"
            "• Умею сравнивать, как разные СМИ освещают события\n"
            "• Группирую похожие новости по смыслу\n\n"
            "📂 *Категории:*\n"
            "🏛️ Политика | 📈 Экономика\n"
            "💰 Криптовалюты | ⚔️ Конфликты\n\n"
            "*Команды:*\n"
            "/news - Последние новости\n"
            "/sources - Список источников\n"
            "/subscribe - Подписаться на авторассылку\n"
            "/unsubscribe - Отписаться от авторассылки\n"
            "/help - Справка\n\n"
            "➡️ /more - Показать следующие новости из последнего запроса\n"
            f"✅ Ты подписан на авторассылку каждые {AUTO_SEND_INTERVAL_HOURS} часа!"
        )

        await update.message.reply_text(welcome_text, parse_mode='Markdown')
        print(f"👤 Новый пользователь: {update.effective_user.first_name} (ID: {user_id})")


    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await self.start_command(update, context)

    async def sources_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        by_region = {}
        for source in NEWS_SOURCES.keys():
            region = self.analyzer.detect_region(source)
            by_region.setdefault(region, []).append(source)

        text = "📋 *Мои источники новостей:*\n\n"
        for region, sources in sorted(by_region.items()):
            text += f"*{region}*\n"
            for source in sources:
                text += f"  • {source}\n"
            text += "\n"

        text += f"📊 *Всего источников:* {len(NEWS_SOURCES)}"
        await update.message.reply_text(text, parse_mode='Markdown')

    def filter_groups_by_categories(self, grouped_news):
        """Оставляет только события с нужными категориями"""
        filtered = []

        for group in grouped_news:
            main = group['main_news']
            text = main['title'] + ' ' + main.get('description', '')
            categories = self.analyzer.categorize_news(text)

            # если хотя бы одна категория из нужных — оставляем
            if any(cat in ALLOWED_CATEGORIES for cat in categories):
                filtered.append(group)

        return filtered


    async def subscribe_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Подписаться на авторассылку"""
        user_id = update.effective_chat.id
        self.subscribers.add(user_id)
        await update.message.reply_text(
            f"✅ Ты подписан на авторассылку.\n"
            f"Каждые {AUTO_SEND_INTERVAL_HOURS} часа буду присылать подборку событий."
        )

    async def unsubscribe_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Отписаться от авторассылки"""
        user_id = update.effective_chat.id
        if user_id in self.subscribers:
            self.subscribers.remove(user_id)
            await update.message.reply_text("❌ Ты отписан от авторассылки.")
        else:
            await update.message.reply_text("ℹ️ Ты и так не подписан на авторассылку.")


    async def news_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_name = update.effective_user.first_name
        print(f"\n📨 {user_name} запросил новости")

        status_msg = await update.message.reply_text(
            "🔄 Собираю свежие новости...\n"
            "⏳ Это займёт 10–15 секунд"
        )

        try:
            raw_news = self.parser.fetch_news(hours_back=NEWS_LOOKBACK_HOURS)

            if not raw_news:
                await status_msg.edit_text(
                    "😔 Свежих новостей пока нет\n\n"
                    "Попробуй позже!"
                )
                return

            await status_msg.edit_text(
                f"🧠 Нашёл {len(raw_news)} новостей!\n"
                f"Анализирую и группирую..."
            )

            grouped_news = self.analyzer.group_similar_news(raw_news)

            await status_msg.edit_text(
                f"✅ Готово! Найдено {len(grouped_news)} событий\n"
                f"Отправляю..."
            )

            grouped_news = self.analyzer.group_similar_news(raw_news)
            # если фильтруешь по темам – оставь эту строку
            # grouped_news = self.filter_groups_by_categories(grouped_news)

            if not grouped_news:
                await status_msg.edit_text(
                    "😊 Свежие новости есть, но ни одна не подходит под выбранные темы."
                )
                return

            # сохраняем список и сбрасываем индекс для этого чата
            chat_id = update.effective_chat.id
            self.last_groups[chat_id] = grouped_news
            self.last_index[chat_id] = 0

            await status_msg.edit_text(
                f"✅ Готово! Найдено {len(grouped_news)} событий\n"
                f"Показываю первые {min(MAX_NEWS_PER_MESSAGE, len(grouped_news))}.\n"
                f"Чтобы увидеть ещё, напиши /more"
            )

                        # Формируем первую страницу так, чтобы не было перекоса в один источник
            per_source_limit = 3  # максимум событий от одного источника на страницу
            selected = []
            per_source_count = {}

            for group in grouped_news:
                main_source = group["main_news"]["source"]
                count = per_source_count.get(main_source, 0)

                if count >= per_source_limit:
                    continue  # этот источник уже набрал лимит

                selected.append(group)
                per_source_count[main_source] = count + 1

                if len(selected) >= MAX_NEWS_PER_MESSAGE:
                    break

            if not selected:
                await status_msg.edit_text(
                    "😊 Свежие новости есть, но ни одна не прошла фильтры для первой страницы."
                )
                return

            news_to_send = selected
            self.last_index[chat_id] = len(selected)

            for i, group in enumerate(news_to_send, 1):
                message = self.format_grouped_news(group, i, len(news_to_send))
                try:
                    await update.message.reply_text(
                        message,
                        parse_mode='HTML',
                        disable_web_page_preview=False
                    )
                    await asyncio.sleep(0.7)
                except Exception as e:
                    print(f"❌ Ошибка отправки: {e}")

            total_sources = sum(len(g['sources']) for g in news_to_send)
            await update.message.reply_text(
                f"✅ *Готово!*\n\n"
                f"📰 Событий: {len(news_to_send)}\n"
                f"📡 Источников задействовано: {total_sources}\n"
                f"⏱️ За последние {NEWS_LOOKBACK_HOURS} часа\n\n"
                f"💡 Хочешь больше? Отправь /news снова!",
                parse_mode='Markdown'
            )

            print(f"✅ Отправлено {len(news_to_send)} событий пользователю {user_name}\n")

        except Exception as e:
            await status_msg.edit_text(
                f"❌ Произошла ошибка: {str(e)}\n\n"
                f"Попробуй ещё раз через минуту"
            )
            print(f"❌ ОШИБКА: {e}")

    async def more_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Показать следующую порцию новостей из последнего запроса"""
        chat_id = update.effective_chat.id

        if chat_id not in self.last_groups or chat_id not in self.last_index:
            await update.message.reply_text(
                "Пока нет сохранённого списка новостей.\n"
                "Сначала отправь /news 🙂"
            )
            return

        grouped_news = self.last_groups[chat_id]
        idx = self.last_index[chat_id]

        if idx >= len(grouped_news):
            await update.message.reply_text(
                "Ты уже посмотрел все события из последнего запроса.\n"
                "Отправь /news, чтобы загрузить свежие."
            )
            return

        end = min(idx + MAX_NEWS_PER_MESSAGE, len(grouped_news))
        news_to_send = grouped_news[idx:end]

        for i, group in enumerate(news_to_send, idx + 1):
            message = self.format_grouped_news(group, i, len(grouped_news))
            try:
                await update.message.reply_text(
                    message,
                    parse_mode='HTML',
                    disable_web_page_preview=False,
                )
                await asyncio.sleep(0.7)
            except Exception as e:
                print(f"❌ Ошибка отправки в /more: {e}")

        self.last_index[chat_id] = end

        await update.message.reply_text(
            f"✅ Показаны события {idx + 1}–{end} из {len(grouped_news)}.\n"
            "Чтобы увидеть ещё — снова /more, чтобы обновить список — /news."
        )

    async def periodic_news_job(self, context: CallbackContext):
        """Периодическая рассылка новостей подписчикам (JobQueue)"""
        if not self.subscribers:
            print("⏭️  Нет подписчиков для авторассылки")
            return

        print(f"\n⏰ Запущена авторассылка для {len(self.subscribers)} подписчиков")

        try:
            # Берём новости за последние N часов
            raw_news = self.parser.fetch_news(hours_back=NEWS_LOOKBACK_HOURS)

            if not raw_news:
                print("📭 Свежих новостей нет, рассылка пропущена")
                return

            # Оставляем только те, которые ещё не отправлялись в авторассылке
            new_news = [n for n in raw_news if n['id'] not in self.last_sent_ids]

            if not new_news:
                print("📭 Все свежие новости уже были отправлены ранее")
                return

            grouped = self.analyzer.group_similar_news(new_news)
            grouped = self.filter_groups_by_categories(grouped)

            if not grouped:
                print("📭 Есть свежие новости, но ни одной по нужным темам — авторассылка пропущена")
                return

            news_to_send = grouped[:MAX_NEWS_PER_MESSAGE]


            # Отправляем каждому подписчику
            for chat_id in list(self.subscribers):
                try:
                    await context.bot.send_message(
                        chat_id=chat_id,
                        text=(
                            "📬 *Автоматическая подборка новостей*\n\n"
                            f"Событий: {len(news_to_send)} за последние {NEWS_LOOKBACK_HOURS} часа."
                        ),
                        parse_mode='Markdown'
                    )

                    for i, group in enumerate(news_to_send, 1):
                        message = self.format_grouped_news(group, i, len(news_to_send))
                        await context.bot.send_message(
                            chat_id=chat_id,
                            text=message,
                            parse_mode='HTML',
                            disable_web_page_preview=False
                        )
                        await asyncio.sleep(0.7)

                    print(f"  ✅ Авторассылка отправлена пользователю {chat_id}")

                except Exception as e:
                    print(f"  ❌ Ошибка авторассылки пользователю {chat_id}: {e}")

            # Помечаем новости как отправленные
            for news in new_news:
                self.last_sent_ids.add(news['id'])

            # Чтобы set не разрастался бесконечно
            if len(self.last_sent_ids) > 2000:
                self.last_sent_ids = set(list(self.last_sent_ids)[-1000:])

            print("✅ Авторассылка завершена\n")

        except Exception as e:
            print(f"❌ Ошибка в periodic_news_job: {e}")


    def format_grouped_news(self, group, number, total):
        main = group['main_news']
        sources = group['sources']
        source_count = len(sources)

        categories = self.analyzer.categorize_news(
            main['title'] + ' ' + main.get('description', '')
        )
        category_str = ' '.join(categories[:2])

        message = f"📰 <b>Событие {number}/{total}</b> {category_str}\n"
        message += f"{'='*40}\n\n"
        message += f"<b>{main['title']}</b>\n\n"

        if source_count > 1:
            message += f"📊 <b>Освещение в {source_count} источниках:</b>\n\n"

            by_region = {}
            for src in sources:
                by_region.setdefault(src['region'], []).append(src)

            for region, region_sources in sorted(by_region.items()):
                message += f"<b>{region}:</b>\n"
                for src in region_sources:
                    desc = self.analyzer.clean_text(src['description'])
                    if len(desc) > 150:
                        desc = desc[:150] + "..."
                    if desc:
                        message += f"  • <i>{src['name']}</i>: {desc}\n"
                    else:
                        message += f"  • <i>{src['name']}</i>: {src['title'][:100]}\n"
                message += "\n"

            message += f"🔗 <b>Читать подробнее:</b>\n"
            for src in sources[:3]:
                message += f"  • <a href='{src['link']}'>{src['name']}</a>\n"
        else:
            desc = self.analyzer.clean_text(main.get('description', ''))
            if len(desc) > 250:
                desc = desc[:250] + "..."
            if desc:
                message += f"{desc}\n\n"
            message += f"🌐 Источник: <i>{main['source']}</i>\n"
            message += f"🔗 <a href='{main['link']}'>Читать полностью</a>"

        return message

import os
import asyncio
from telegram.ext import Application

async def main():
    bot = SmartNewsBot(BOT_TOKEN)
    
    # Создаём app
    application = Application.builder().token(BOT_TOKEN).build()
    
    # Все ваши handlers
    application.add_handler(CommandHandler("start", bot.start_command))
    application.add_handler(CommandHandler("help", bot.help_command))
    application.add_handler(CommandHandler("news", bot.news_command))
    application.add_handler(CommandHandler("sources", bot.sources_command))
    application.add_handler(CommandHandler("subscribe", bot.subscribe_command))
    application.add_handler(CommandHandler("unsubscribe", bot.unsubscribe_command))
    application.add_handler(CommandHandler("more", bot.more_command))
    
    # JobQueue для авторассылки работает!
    job_queue = application.job_queue
    job_queue.run_repeating(
        bot.periodic_news_job,
        interval=timedelta(hours=AUTO_SEND_INTERVAL_HOURS),
        first=timedelta(minutes=2),
        name="periodic_news"
    )
    
if __name__ == '__main__':
    import os
    PORT = int(os.environ.get('PORT', 8080))
    webhook_url = "botpy-production-e175.up.railway.app/webhook"  # ВАШ URL!
    app.run_webhook(
        listen="0.0.0.0",
        port=PORT,
        url_path="webhook",
        webhook_url=webhook_url
    )
