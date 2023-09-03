import re
import emoji
import pandas as pd
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize, sent_tokenize

# Additional Data for Normalization
stopwords_indonesian = stopwords.words('indonesian')
abusive = pd.read_csv('Data/abusive.csv', encoding='utf-8')
new_kamusalay = pd.read_csv('Data/new_kamusalay.csv', encoding='latin1')

abusive_words = abusive['ABUSIVE'].tolist()

new_kamus_alay = {}
for k,v in new_kamusalay.values:
    new_kamus_alay[k] = v

# Remove Emoji
def remove_emojis(original_text):
    # Check if original_text is a string
    if not isinstance(original_text, str):
        raise TypeError("The input must be a string.")
    
    # delete hexadecimal
    cleaned_text = re.sub(r'\\x[0-9a-fA-F]{2}', '', original_text)
    
    # Remove emojis from the text
    emoji_pattern = re.compile("["
                               u"\U0001F600-\U0001F64F"  # emoticons
                               u"\U0001F300-\U0001F5FF"  # symbols & pictographs
                               u"\U0001F680-\U0001F6FF"  # transport & map symbols
                               u"\U00002600-\U000027BF"  # miscellaneous symbols
                               u"\U000024C2-\U0001F251" 
                               "]+", flags=re.UNICODE)
    
    return emoji_pattern.sub('', cleaned_text)

# Cleansing tweets sentence
def cleanse_text(original_text):
    text = original_text.lower()  # Convert to lowercase
    text = re.sub(r"@[A-Za-z0-9_]+", "", text)  # Remove mentions
    text = re.sub(r"http\S+|www\S+|https\S+", "", text)  # Remove URLs
    text = re.sub(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b', 'email', text)  # Change email into 'email'
    text = text.replace(" 62", " 0")  # Change phone code from 62 into 0
    text = re.sub(r"\b\d{4}\s?\d{4}\s?\d{4}\b", "nomor_telefon", text)  # Change phone number into 'nomor_telefon'
    text = text.replace("USER", "pengguna")  # Change into 'pengguna'
    text = text.strip()  # Trim leading and trailing whitespaces
    text = re.sub(r"[^a-zA-Z0-9]", " ", text)  # Remove punctuation and special characters

    return text

# Remove Abusive Word and replace alay word
def cleanse_word(original_text):
    abusive_check = [] # set up new list for abusive check
    alay_check = [] # set up the next new list for alay word check
    split_text = original_text.split(" ") # split original_text into list of words
    for word in split_text:
        if word in abusive_words: # for all words in the text, check if any of those words belongs to abusive words
            continue # if yes, continue
        else:
            abusive_check.append(word) # if not, it belongs to the list of abusive_check
   
    for word in abusive_check:
        new_word = new_kamus_alay.get(word, word) # replace alay word
        alay_check.append(new_word)
    
    cleaned_word = " ".join(alay_check)
    return cleaned_word

# Remove stopwords
def remove_stopwords(sentence):
    tokenized_sentence = nltk.word_tokenize(sentence)
    new_tokenized_sentence = []
    
    for token in tokenized_sentence:
        if token in stopwords_indonesian:
            continue
        else:
            new_tokenized_sentence.append(token)
    
    return ' '.join(new_tokenized_sentence)


#==================================================================================
# Cleaning operation text
def cleansing_text(text):
    text = remove_emojis(text)
    text = cleanse_text(text)
    text = remove_stopwords(text)

    words = text.split()  # Apply word-level cleansing operations
    cleansed_words = [cleanse_word(word) for word in words]

    cleaned_text = ' '.join(cleansed_words)  # Join the cleansed words back into a tweet

    return cleaned_text

# Cleaning operation file
def cleansing_file(texts):
    cleaned_texts = []
    for text in texts:
        text = remove_emojis(text)
        text = cleanse_text(text)
        text = remove_stopwords(text)

        words = text.split()
        cleansed_words = [cleanse_word(word) for word in words if word]

        cleansed_text = ' '.join(cleansed_words)

        cleaned_texts.append(cleansed_text)

    return cleaned_texts
