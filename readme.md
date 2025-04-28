# 📚 Human vs. AI Book Review & Summary Comparison

A scalable SQL-powered framework for storing, analyzing, and comparing book metadata, human reviews, and AI-generated summaries (from Ollama or other LLMs).

---

## Our Project Overview

This project merges multiple large book-related datasets, cleans and normalizes the data, and stores it in a SQL database.
It prepares the foundation for an API that generates AI-based reviews and summaries, enabling rich comparison between human feedback and LLM-generated responses to explore alignment, deviation, and accuracy.

---

## Key Features

-  Normalized SQL schema for books, reviews, and summaries
-  Efficient ingestion of 3M+ reviews using `pandas`
-  Book ID auto-mapping via `title` + `author`, with `AUTO_INCREMENT` fallback
- Advanced ETL: normalization, missing value handling, fuzzy author matching
-  Clean LEFT and OUTER joins for full book coverage, even without reviews
- Support for AI-generated summaries/reviews (Ollama, OpenAI)
- -ready for sentiment and text similarity analysis

---

## 📊 Dataset Overview

| Dataset                  | Rows        | Key Columns                         |
|---------------------------|-------------|-------------------------------------|
| `books.csv`               | 1,247       | `title`, `author`, `isbn`           |
| `books_1.Best_Books_Ever.csv | 52,478   | `title`, `author`, `genres`, `awards`, etc. |
| `Books_rating.csv`        | 3,000,000   | `title`, `user_id`, `rating`, `review_text` |

- ✅ Final merged dataset shape: **969,028 rows**
- ✅  Final cleaned size after dropping NA: ~300,000 rows (~30% of original).
- ✅ Unique titles and authors combinations: **~7100**
- ✅ Unique authors: **~**
- ✅ Books with same title but different authors detected: **~646**

---

## ETL and Cleaning Process

### Step 1: Extract
- Load `books.csv` and `books_1.Best_Books_Ever.csv`.
- Normalize `title` and `author` fields (convert to lowercase, strip whitespace) immediately.
- Outer join both books metadata datasets on (`author`, `title`).
- Load `Books_rating.csv` in chunks (`100,000 rows per chunk`) to preserve memory.

### Step 2: Transform
- Normalize `title` in each review chunk (lowercase, strip whitespace).
- Inner join each chunk with the merged books dataset on `title`.
- Concatenate all merged chunks into a single final dataset (`final_df`).
- Drop unnecessary columns:
  - `Unnamed: 0`, `release year`, `synopsis`, `book length`, `rating_x`, `number of ratings`, `Price`, `price`, `edition`, `series`, `profileName`, `User_id`, `pages`
- Dropped rows with missing critical fields: description, review/text, author, title, isbn, etc.

-Result: Fully clean dataset — no missing values (NaN) left.



### Step 3: Load
- Create SQL tables: `books`, `reviews`, and `summaries`.


- Insert cleaned books into `books`.
- Insert human reviews into `reviews`.
- Insert book descriptions into `summaries` with source = `'human'`.


---

## 🏗️ Database Schema

### `books`
Stores unique book metadata.

| Column             | Type        | Description                        |
|--------------------|-------------|------------------------------------|
| book_id            | INT         | Primary key (auto-incremented)     |
| title              | TEXT        | Book title                         |
| author             | TEXT        | Author name                        |
| isbn               | VARCHAR(50) | ISBN code                          |
| language           | VARCHAR(50) | Language                           |
| publisher          | TEXT        | Publisher                          |
| publishDate        | VARCHAR(50) | Publish date                       |
| firstPublishDate   | VARCHAR(50) | First publish date                 |
| bookFormat         | VARCHAR(100)| Format (hardcover, paperback, etc.)|
| coverImg           | TEXT        | URL to book cover                  |
| genres             | TEXT        | Main genre(s)                      |


### `reviews`
Stores both human and AI-generated reviews.

| Column             | Type        | Description                       |
|--------------------|-------------|-----------------------------------|
| review_id          | INT         | Primary key                      |
| book_id            | INT         | Foreign key to `books`            |
| review_score       | FLOAT       | User or AI-assigned rating        |
| review_time        | BIGINT      | Unix timestamp                    |
| review_summary     | TEXT        | Optional review headline          |
| review_text        | TEXT        | Full review                       |
| review_helpfulness | VARCHAR(10) | Helpfulness votes (e.g., 2/5)      |
| source             | TEXT        | `'human'`, `'ollama'`, or `'other'`|

### `summaries`
Stores multiple summaries per book.

| Column             | Type    | Description                        |
|--------------------|---------|------------------------------------|
| summary_id         | INT     | Primary key                       |
| book_id            | INT     | Foreign key to `books`             |
| description        | TEXT    | Summary text                      |
| source             | TEXT    | `'human'`, `'ollama'`, or `'other'`|

---

## 💾 Tech Stack

- Python (`pandas`, `pymysql`)
- MySQL (cloud-hosted)
- Ollama (for future AI content generation)

---

## 🔍 Example Use Case

- Compare AI-generated reviews with human ones:
  - Average sentiment alignment
  - Deviation from user consensus
  - Text similarity scoring
- Identify controversial books with high disagreement
- Build dashboards showing AI vs human review patterns

---

## 🛠️ Setup & Usage

1. Clone the repository  
2. Ensure your MySQL database credentials are configured  
3. Load your cleaned `final_df` DataFrame  
4. Run the `insert_into_mysql.py` script to populate the database

---

## 📈 Future Work

- Integrate Ollama API to generate AI summaries and reviews on-demand
- Add text similarity metrics (cosine similarity, embeddings)
- Build a REST API to generate summaries or reviews for any book
- Build an interactive dashboard to visualize sentiment differences
- Predict review agreement/disagreement using machine learning

---

## 🧑‍💻 Author

**Bekobo Daniella**  


---
