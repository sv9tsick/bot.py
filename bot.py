# -*- coding: utf-8 -*-
"""
Умный Telegram-бот v2.0 Lite для Railway
RSS без sentence_transformers/torch
"""

from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
import feedparser
import hashlib
from datetime import datetime, timedelta
import asyncio
import re
from collections import defaultdict

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
MAX_NEWS_PER_MESSAGE = 10
AUTO_SEND_INTERVAL_HOURS = 2


class SmartNewsAnalyzer:
    def __init__(self):
        print("🧠 Lite анализатор (hash заголовков)")
        self.threshold = 0.9  # условный порог для "похожих" заголовков

    def clean_text(self, text):
        text = re.sub('<[^<]+?>', '', str(text))
        return ' '.join(text.split())[:100].lower()

    def calc_text_hash(self, text: str) -> str:
        """Простой хеш от очищенного текста."""
        cleaned = self.clean_text(text)
        return hashlib.md5(cleaned.encode("utf-8")).hexdigest()

    def group_similar_news(self, raw_news: list[dict]) -> list[list[dict]]:
        """
        Группировка новостей по "похожим" заголовкам через хеши.
        Возвращаем список групп: [ [group1], [group2], ... ].
        """
        groups = []
        hashes = []  # [hash1, hash2, ...]

        for item in raw_news:
            title = item.get("title", "") or ""
            text_hash = self.calc_text_hash(title)

            # Сравниваем хеш с уже существующими (упрощённый вариант)
            matched = False
            for i, h in enumerate(hashes):
                if h == text_hash:
                    groups[i].append(item)
                    matched = True
                    break

            if not matched:
                hashes.append(text_hash)
                groups.append([item])

        return groups

async def fetch_news(analyzer: SmartNewsAnalyzer) -> list[dict]:
    now = datetime.now()
    cutoff = now - timedelta(hours=NEWS_LOOKBACK_HOURS)
    all_items = []

    for src_name, rss_url in NEWS_SOURCES.items():
        try:
            feed = feedparser.parse(rss_url)
            for entry in feed.entries:
                published = None

                # Пытаемся извлечь дату разными способами
                if hasattr(entry, "published_parsed") and entry.published_parsed:
                    published = datetime(*entry.published_parsed[:6])
                elif hasattr(entry, "published") and entry.published:
                    # Здесь нужно уметь парсить любой формат даты
                    try:
                        published = datetime.strptime(entry.published, "%Y-%m-%dT%H:%M:%SZ")
                    except ValueError:
                        try:
        # Обычный RFC‑822 / RSS-формат
                           published = datetime.strptime(entry.published, "%a, %d %b %Y %H:%M:%S %z")
                        except ValueError:
                           try:
            # Формат типа "Thursday Mar 12 2026 11:35:47"
                               published = datetime.strptime(entry.published, "%A %b %d %Y %H:%M:%S")
                           except ValueError:
            # Если дата в неподдерживаемом формате — просто пропускаем
                               continue

                else:
                    # если вообще нет даты — пропускаем
                    continue

                if published < cutoff:
                    continue

                all_items.append({ ... })
        except Exception as e:
            print(f"Ошибка парсинга {src_name}: {e}")

    return all_items


def format_news_list(group: list[dict]) -> str:
    """Форматирует одну группу новостей в строку."""
    if not group:
        return ""

    first = group[0]
    lines = [
        f"📰 *{first['title']}*",
        f"📍 Источник: {first['source']}",
        f"⏰ {first['published'].strftime('%Y-%m-%d %H:%M')}",
    ]
    if first["summary"]:
        lines.append(f"📝 {first['summary'][:200]}...")

    if len(group) > 1:
        lines.append(f"\n📋 *Другие источники по теме ({len(group) - 1}):*")
        for i, item in enumerate(group[1:], start=2):
            lines.append(f"{i}. {item['source']} → {item['link']}")

    lines.append(f"\n🔗 {first['link']}")
    return "\n".join(lines)


async def send_grouped_news(context: ContextTypes.DEFAULT_TYPE, chat_id: int, groups: list[list[dict]]):
    """Отправка сгруппированных новостей в Telegram."""
    for i, group in enumerate(groups):
        if not group:
            continue

        text = format_news_list(group)[:3500]  # ограничение по длине сообщения
        if text:
            try:
                await context.bot.send_message(
                    chat_id=chat_id,
                    text=text,
                    parse_mode="Markdown",
                )
                await asyncio.sleep(0.5)  # чтобы не упираться в лимиты Telegram
            except Exception as e:
                print(f"Ошибка отправки сообщения: {e}")


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_id = update.effective_chat.id
    await update.message.reply_text("🤖 Бот запущен.\nЖду команду /news для получения последних новостей.")

    analyzer = SmartNewsAnalyzer()
    raw_news = await fetch_news(analyzer)
    groups = analyzer.group_similar_news(raw_news)

    if not groups:
        await context.bot.send_message(chat_id=chat_id, text="Новых новостей за последние часы нет.")
        return

    # Разбиваем на группы по MAX_NEWS_PER_MESSAGE
    chunked = []
    current = []
    for g in groups:
        current.append(g)
        if len(current) >= MAX_NEWS_PER_MESSAGE:
            chunked.append(current)
            current = []
    if current:
        chunked.append(current)

    # Транслируем по чанкам
    for chunk in chunked:
        await send_grouped_news(context, chat_id, chunk)
        await asyncio.sleep(1)


async def auto_news_job(context: ContextTypes.DEFAULT_TYPE):
    """Фоновый job — отправка сводки по расписанию."""
    chat_ids = {update.effective_chat.id}  # тут нужно хранить актуальные chat_id (например, в БД или set)
    analyzer = SmartNewsAnalyzer()
    raw_news = await fetch_news(analyzer)
    groups = analyzer.group_similar_news(raw_news)

    if not groups:
        return

    for chat_id in chat_ids:
        chunked = []
        current = []
        for g in groups:
            current.append(g)
            if len(current) >= MAX_NEWS_PER_MESSAGE:
                chunked.append(current)
                current = []
        if current:
            chunked.append(current)

        for chunk in chunked:
            await send_grouped_news(context, chat_id, chunk)
            await asyncio.sleep(1)


async def setup_jobs(application: Application):
    application.job_queue.run_repeating(
        auto_news_job,
        interval=timedelta(hours=AUTO_SEND_INTERVAL_HOURS),
        first=timedelta(minutes=1),
    )


def main():
    application = Application.builder().token(BOT_TOKEN).build()

    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("news", start_command))  # quick alias

    application.job_queue.run_repeating(
        auto_news_job,
        interval=timedelta(hours=AUTO_SEND_INTERVAL_HOURS),
        first=timedelta(minutes=1),
    )

    application.run_polling()


if __name__ == "__main__":
    main()



