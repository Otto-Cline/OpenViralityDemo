import requests
import sqlite3
from datetime import datetime
from collections import Counter


# in collect() we grab data directly from hackernews api, populate the database with it.
# then in find_trends() we get all the titles from everything less than a week ago, put them in an array called words
# and get the 20 most common words in said array



#db setup
conn = sqlite3.connect('trends.db')
conn.execute('''CREATE TABLE IF NOT EXISTS signals 
(id TEXT PRIMARY KEY, title TEXT, score INT, date TEXT, source TEXT)''')

#hackernews collection
def collect():
    stories = requests.get('https://hacker-news.firebaseio.com/v0/topstories.json').json()[: 200]
    for story_id in stories:
        data = requests.get(f'https://hacker-news.firebaseio.com/v0/item/{story_id}.json').json()
        if data:
            conn.execute('INSERT OR IGNORE INTO signals VALUES (?,?,?,?,?)',
            (data['id'], data.get('title', ''), data.get('score', 0), datetime.now(), 'hackernews'))
    conn.commit()

#find trending topics
def find_trends():
    week_ago = datetime.now().timestamp() - 604800 * 3 #past 3 weeks cuz i multiplied by 3
    rows = conn.execute('SELECT title FROM signals WHERE date > ?', (week_ago,)).fetchall()

    #extract common words
    stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
                  'of', 'with', 'by', 'from', 'up', 'about', 'into', 'through', 'during',
                  'how', 'when', 'where', 'why', 'what', 'which', 'who', 'whom', 'this',
                  'that', 'these', 'those', 'is', 'are', 'was', 'were', 'be', 'been',
                  'being', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would',
                  'could', 'should', 'may', 'might', 'must', 'can', 'shall', 'as', 'it',
                  'if', 'then', 'else', 'so', 'than', 'such', 'no', 'not', 'only', 'own',
                  'same', 'too', 'very', 'just', 'now', 'here', 'there', 'i', 'you', 'we',
                  'they', 'them', 'their', 'what', 'which', 'who', 'whom', 'this', 'that',
                  'all', 'each', 'few', 'more', 'most', 'other', 'some', 'such', 'nor',
                  'only', 'own', 'same', 'so', 'than', 'too', 'very', 's', 't', 'can',
                  'will', 'just', 'don', 'should', 'now', 'new', 'using', 'building', 'making', 'built',
                    'show', 'hn', 'ask', 'tell', 'vs', 'launched', 'my', 'our', 'your', 'release', 'update', 'your',
                  'hn:', 'show', 'day', 'top', 'after', 'low',
                  # Articles & Determiners
                    'the', 'a', 'an', 'this', 'that', 'these', 'those', 'my',
                  'your', 'his', 'her',
                  'its', 'our', 'their', 'few', 'many', 'much', 'each', 'every', 'all', 'any',
                  'some', 'most', 'none', 'several', 'such', 'own', 'other', 'another', 'both',
                  'either', 'neither', 'one', 'two', 'three', 'four', 'five', 'six', 'seven',
                  'eight', 'nine', 'ten', 'hundred', 'thousand', 'million', 'billion', 'first',
                  'second', 'third', 'last', 'next', 'previous', 'following', 'above', 'below',

                  # Pronouns
                  'i', 'me', 'we', 'us', 'you', 'he', 'him', 'she', 'they', 'them', 'it',
                  'myself', 'yourself', 'himself', 'herself', 'itself', 'ourselves', 'themselves',
                  'who', 'whom', 'whose', 'which', 'what', 'whoever', 'whatever', 'whichever',
                  'somebody', 'someone', 'something', 'anybody', 'anyone', 'anything', 'nobody',
                  'everyone', 'everything', 'everybody', 'everywhere', 'nowhere', 'somewhere',

                  # Prepositions & Conjunctions
                  'of', 'in', 'to', 'for', 'with', 'on', 'at', 'from', 'by', 'about', 'as',
                  'into', 'through', 'during', 'before', 'after', 'above', 'below', 'between',
                  'under', 'over', 'up', 'down', 'out', 'off', 'again', 'further', 'then',
                  'once', 'here', 'there', 'where', 'when', 'why', 'how', 'because', 'since',
                  'until', 'while', 'although', 'though', 'if', 'unless', 'whether', 'whereas',
                  'and', 'but', 'or', 'nor', 'so', 'yet', 'both', 'either', 'neither', 'only',
                  'just', 'even', 'also', 'besides', 'furthermore', 'however', 'moreover',
                  'nevertheless', 'therefore', 'thus', 'hence', 'accordingly', 'consequently',
                  'meanwhile', 'otherwise', 'indeed', 'instead', 'likewise', 'namely', 'rather',
                  'still', 'too', 'besides', 'except', 'beyond', 'along', 'among', 'around',
                  'behind', 'beneath', 'beside', 'throughout', 'toward', 'upon', 'within',
                  'without', 'via', 'per', 'vs', 'versus', 'despite', 'regarding', 'concerning',

                  # Verbs (common/auxiliary)
                  'is', 'am', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had',
                  'do', 'does', 'did', 'doing', 'done', 'will', 'would', 'could', 'should',
                  'may', 'might', 'must', 'can', 'shall', 'ought', 'need', 'dare', 'going',
                  'able', 'used', 'get', 'got', 'getting', 'make', 'made', 'making', 'take',
                  'took', 'taking', 'taken', 'give', 'gave', 'giving', 'given', 'come', 'came',
                  'coming', 'go', 'went', 'gone', 'say', 'said', 'saying', 'tell', 'told',
                  'telling', 'think', 'thought', 'thinking', 'know', 'knew', 'known', 'knowing',
                  'see', 'saw', 'seen', 'seeing', 'look', 'looked', 'looking', 'use', 'using',
                  'find', 'found', 'finding', 'want', 'wanted', 'wanting', 'need', 'needed',
                  'try', 'tried', 'trying', 'keep', 'kept', 'keeping', 'let', 'letting',
                  'begin', 'began', 'beginning', 'seem', 'seemed', 'seeming', 'help', 'helped',
                  'show', 'showed', 'showing', 'shown', 'put', 'putting', 'bring', 'brought',

                  # Adverbs & Common Words
                  'very', 'really', 'quite', 'rather', 'somewhat', 'almost', 'nearly', 'barely',
                  'hardly', 'merely', 'simply', 'actually', 'certainly', 'definitely', 'probably',
                  'possibly', 'perhaps', 'maybe', 'always', 'never', 'often', 'sometimes',
                  'usually', 'generally', 'specifically', 'particularly', 'especially', 'mainly',
                  'mostly', 'typically', 'normally', 'previously', 'currently', 'recently',
                  'lately', 'eventually', 'finally', 'initially', 'originally', 'ultimately',
                  'already', 'yet', 'still', 'anymore', 'longer', 'far', 'away', 'back', 'forth',
                  'together', 'apart', 'aside', 'ahead', 'behind', 'forward', 'backward',
                  'yes', 'no', 'not', 'never', 'nothing', 'none', 'nobody', 'nowhere',
                  'good', 'bad', 'better', 'best', 'worse', 'worst', 'great', 'little', 'few',
                  'much', 'many', 'more', 'less', 'least', 'very', 'enough', 'almost', 'quite',
                  'well', 'right', 'wrong', 'true', 'false', 'new', 'old', 'young', 'big',
                  'small', 'large', 'long', 'short', 'high', 'low', 'same', 'different', 'similar',
                  'whole', 'entire', 'full', 'empty', 'general', 'specific', 'common', 'rare',

                  # Tech-specific common words to filter
                  'app', 'apps', 'using', 'building', 'making', 'built', 'created', 'launched',
                  'introducing', 'announcing', 'update', 'updated', 'release', 'released', 'new',
                  'show', 'hn', 'ask', 'tell', 'hey', 'hi', 'hello', 'guys', 'folks', 'people',
                  'user', 'users', 'way', 'ways', 'thing', 'things', 'stuff', 'part', 'parts',
                  'lot', 'lots', 'bit', 'piece', 'kind', 'type', 'sort', 'form', 'case', 'cases',
                  'fact', 'point', 'points', 'time', 'times', 'day', 'days', 'week', 'weeks',
                  'month', 'months', 'year', 'years', 'today', 'yesterday', 'tomorrow', 'now',
                  'then', 'soon', 'later', 'early', 'late', 'ago', 'since', 'already', 'still',
                  'just', 'like', 'love', 'hate', 'want', 'need', 'help', 'thanks', 'please',
                  'sorry', 'sure', 'okay', 'ok', 'yeah', 'yep', 'nope', 'maybe', 'probably',
                  'actually', 'basically', 'seriously', 'honestly', 'literally', 'totally',
                  'definitely', 'absolutely', 'exactly', 'simply', 'merely', 'purely',

                  # Single letters and contractions
                  'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o',
                  'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z',
                  "it's", "don't", "doesn't", "didn't", "won't", "wouldn't", "couldn't",
                  "shouldn't", "can't", "cannot", "i'm", "you're", "we're", "they're",
                  "i've", "you've", "we've", "they've", "i'd", "you'd", "we'd", "they'd",
                  "i'll", "you'll", "we'll", "they'll", "isn't", "aren't", "wasn't", "weren't",
                  "hasn't", "haven't", "hadn't", "that's", "what's", "where's", "who's",
                  "why's", "how's", "here's", "there's",
                  }
    words = []
    for row in rows:
        words.extend([w.lower() for w in row[0].split()
                     if w.lower() not in stop_words and len(w) > 2])

    #return top trending terms
    return Counter(words).most_common(20)

collect()
print(find_trends())


def check_db():
    count = conn.execute('SELECT COUNT(*) FROM signals').fetchone()[0]
    print(f"Total stories in DB: {count}")

    # Check for duplicates
    dupes = conn.execute('''SELECT id, COUNT(*) as cnt
                            FROM signals
                            GROUP BY id
                            HAVING cnt > 1''').fetchall()
    if dupes:
        print(f"Found {len(dupes)} duplicate stories")


check_db()



