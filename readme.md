
# 📚 Human vs. AI Book Review & Summary Comparison

![Alt text for image](istockphoto-1488555344-1024x1024.jpg )


A scalable SQL-powered framework for storing, analyzing, and comparing book metadata, human reviews, and AI-generated summaries (from Ollama or other LLMs).

---

## 🚀 Project Overview

This project merges multiple large book-related datasets, cleans and normalizes the data, and stores it in a SQL database.
It prepares the foundation for an API that generates AI-based reviews and summaries, enabling rich comparison between human feedback and LLM-generated responses to explore alignment, deviation, and accuracy.

We also implemented automated review and headline generation using prompts on Ollama (`llama3` model).

---

## 🗂️ Key Features

- Normalized SQL schema for books, reviews, and summaries
- Efficient ingestion of 3M+ reviews using `pandas`
- Book ID auto-mapping via `title` + `author`, with `AUTO_INCREMENT` fallback
- Advanced ETL: normalization, missing value handling, fuzzy author matching
- Clean LEFT and OUTER joins for full book coverage, even without reviews
- Support for AI-generated summaries/reviews (Ollama, OpenAI)
- Ready for sentiment and text similarity analysis

---

## 📊 Dataset Overview

| Dataset | Rows | Key Columns |
|:--------|:-----|:------------|
| `books.csv` | 1,247 | `title`, `author`, `isbn` |
| `books_1.Best_Books_Ever.csv` | 52,478 | `title`, `author`, `genres`, `awards`, etc. |
| `Books_rating.csv` | 3,000,000 | `title`, `user_id`, `rating`, `review_text` |

✅ Final merged dataset shape: **969,028 rows**  
✅ Final cleaned size after dropping NA: ~300,000 rows (~30% of original)  

### Data Insights
After full cleaning and processing of the dataset, we obtained the following insights:

📚 Unique book titles: 1,825

✍️ Unique authors: 1,292

📖 Unique (title, author) combinations: 1,969

🕵️ Titles shared by multiple authors: 110

📈 Average reviews per (title, author) combination: ~158.12 reviews

Interestingly, no two books with the same title but different authors shared the same ISBN — confirming the distinct identity of each book despite title overlaps.

These insights confirm the quality of our cleaned dataset and lay the foundation for deeper comparisons between human and AI-generated reviews.

---

## 🔄 ETL and Cleaning Process

### Step 1: Extract
- Load `books.csv` and `books_1.Best_Books_Ever.csv`.
- Normalize `title` and `author` fields (lowercase, strip whitespace).
- Outer join based on (`author`, `title`).
- Load `Books_rating.csv` in chunks (`100,000 rows per chunk`).
```python
chunk_size = 100_000
for chunk in pd.read_csv('Books_rating.csv', chunksize=chunk_size):
    ...
```

### Step 2: Transform
- Normalize titles again in each review chunk.
- Inner join with merged book metadata on `title`.
- Drop irrelevant columns.
```python
final_df_clean = final_df.drop(columns=columns_to_drop).dropna()
final_df_clean.to_csv('final_merged_books_clean.csv', index=False)
```

### Step 3: Load
- Drop and recreate tables carefully to respect foreign key constraints.
```python
drop_books_sql = "DROP TABLE IF EXISTS books;"
drop_reviews_sql = "DROP TABLE IF EXISTS reviews;"
drop_summaries_sql = "DROP TABLE IF EXISTS summaries;"
cur.execute(drop_reviews_sql)
cur.execute(drop_summaries_sql)
cur.execute(drop_books_sql)
```
- Create fresh tables `books`, `reviews`, `summaries`.

```python
create_books_sql = '''
CREATE TABLE books (
    book_id INT AUTO_INCREMENT PRIMARY KEY,
    title TEXT,
    author TEXT,
    isbn TEXT,
    publication_year TEXT,
    genre TEXT,
    cover_image TEXT
);
'''
cur.execute(create_books_sql)
```

- Insert books, map their IDs.
```python
for chunk in pd.read_csv('final_merged_books_clean.csv', chunksize=chunk_size):
    ...
    cur.executemany('''
        INSERT INTO books (title, author, isbn, publication_year, genre, cover_image)
        VALUES (%s, %s, %s, %s, %s, %s);
    ''', book_chunk)
```
🔄 Book ID Optimization
To improve performance during bulk insertion of summaries and reviews, we implemented a book dictionary lookup strategy. After inserting all unique books into the books table (with AUTO_INCREMENT book_id), we queried the table once to retrieve a mapping of each (title, author) pair to its assigned book_id. This mapping was stored as a Python dictionary:
```python
book_map = { (row['title'], row['author']) : row['book_id'] }```

Using this dictionary allowed us to avoid repeated database lookups during the summary and review insertions. Instead of querying the database for each review’s book ID, we simply used the dictionary to instantly retrieve the correct book_id for each (title, author) combination.

- Insert summaries and reviews linked to correct `book_id`.

```python
cur.executemany('''
    INSERT INTO summaries (book_id, summary_text, source)
    VALUES (%s, %s, %s);
''', summary_chunk)
```

```python
cur.executemany('''
    INSERT INTO reviews (book_id, rating, review_summary, review_text, source)
    VALUES (%s, %s, %s, %s, %s);
''', review_chunk)
conn.commit()
```

---

## 🏗️ Database Schema

### `books`
| Column | Type | Description |
|:-------|:-----|:------------|
| book_id | INT | Primary key |
| title | TEXT | Book title |
| author | TEXT | Author name |
| isbn | VARCHAR(50) | ISBN code |
| publication_year | TEXT | Year of publication |
| genre | TEXT | Main genres |
| cover_image | TEXT | Book cover URL |

### `reviews`
| Column | Type | Description |
|:-------|:-----|:------------|
| review_id | INT | Primary key |
| book_id | INT | Foreign key |
| rating | FLOAT | Review rating |
| review_summary | TEXT | Review headline |
| review_text | TEXT | Full review |
| source | TEXT | `human`, `ollama`, or `other` |

### `summaries`
| Column | Type | Description |
|:-------|:-----|:------------|
| summary_id | INT | Primary key |
| book_id | INT | Foreign key |
| summary_text | TEXT | Book summary |
| source | TEXT | `human`, `ollama`, or `other` |

---

## 🤖 AI Content Generation with Ollama


To enrich our dataset and enable comparison between human and AI-generated feedback, we implemented dynamic review and headline generation using Ollama's llama3 model. This functionality can be extended to any book in the database.
### Importance of Prompt Design
The quality and structure of prompts significantly influence the output from language models like llama3. In our case:

Instruction clarity ensures that LLMs avoid unnecessary filler or context.

Tone control keeps summaries catchy and concise.

Direct formatting commands ("no extra text", "100–150 words") guide output to match our schema.

**Generate Review Text:**
```python
def generate_review_and_rating(title, author, model='llama3'):
    prompt = f"""
Write a concise and informative review (around 100-150 words) for the book "{title}" by {author}.
Only output the review text directly, without any introductions or explanations.
"""
    response = ollama.chat(model=model, messages=[{'role': 'user', 'content': prompt}])
    review = response['message']['content'].strip()

    rating = random.randint(2, 5)
    return review, rating
```

**Generate Summary:**
```python
def generate_review_summary(title, author, model='llama3'):
    prompt = f"""Create a short, catchy review headline (less than 10 words) for the book "{title}" by {author}.
Only return the headline, no extra text."""
    response = ollama.chat(model=model, messages=[{'role': 'user', 'content': prompt}])
    summary = response['message']['content'].strip()
    return summary
```

---

## 💾 Tech Stack

- Python (`pandas`, `PyMySQL`)
- MySQL (cloud-hosted)
- Ollama (LLM API)

---

## 📈 Future Work

- Real-time Ollama-based generation
- REST API for summaries and reviews
- Text similarity scoring and sentiment analysis
- Full visualization dashboard (Plotly/Dash/Streamlit)

---



---
