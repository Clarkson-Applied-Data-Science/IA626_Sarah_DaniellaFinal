from flask import Flask, request, jsonify
import pymysql
import ollama
import random
import yaml

app = Flask(__name__)
def get_conn():
    with open('config.yml') as f:
        config = yaml.safe_load(f)['mysql']
    
    return pymysql.connect(
        host=config['host'],
        port=config['port'],
        user=config['user'],
        passwd=config['password'],
        db=config['db'],
        autocommit=True,
        cursorclass=pymysql.cursors.DictCursor
    )






# function to generate review and random rating
def generate_review_and_rating(title, author, model='llama3'):
    prompt = f"""
Write a concise and informative review (around 100-150 words) for the book "{title}" by {author}.
Only output the review text directly, without any introductions or explanations.
"""
    response = ollama.chat(model=model, messages=[{'role': 'user', 'content': prompt}])
    review = response['message']['content'].strip()

    rating = random.randint(2, 5)
    return review, rating


# function to generate review summary
def generate_review_summary(title, author, model='llama3'):
    prompt = f"""Create a short, catchy review headline (less than 10 words) for the book "{title}" by {author}.
Only return the headline, no extra text."""
    response = ollama.chat(model=model, messages=[{'role': 'user', 'content': prompt}])
    summary = response['message']['content'].strip()
    return summary


@app.route('/get_reviews', methods=['GET'])
def get_reviews():
    title = request.args.get('title')
    author = request.args.get('author')

    if not title or not author:
        return jsonify({'error': 'Missing title or author parameter'}), 400

    try:
        conn = get_conn()
        with conn.cursor() as cursor:
            # Step 1: Get book_id
            cursor.execute("""
                SELECT book_id FROM books_table
                WHERE LOWER(title) = LOWER(%s) AND LOWER(author) = LOWER(%s)
            """, (title, author))
            book = cursor.fetchone()

            if not book:
                return jsonify({'error': 'Book not found'}), 404

            book_id = book['book_id']

            # Step 2: Get existing reviews
            cursor.execute("""
                SELECT review_summary, review_text, rating, source
                FROM reviews_test
                WHERE book_id = %s
            """, (book_id,))
            reviews = cursor.fetchall()

            # Step 3: Generate and insert AI review if none exist
            if not reviews:
                review_summary = generate_review_summary(title, author)
                review_text = generate_review_and_rating(title, author)
                rating = float(random.choice([3.5, 4.0, 4.5, 5.0]))

                cursor.execute("""
                    INSERT INTO reviews_test (book_id, rating, review_summary, review_text, source)
                    VALUES (%s, %s, %s, %s, %s)
                """, (book_id, rating, review_summary, review_text, 'AI'))
                conn.commit()

                reviews = [{
                    'review_summary': review_summary,
                    'review_text': review_text,
                    'rating': rating,
                    'source': 'AI'
                }]

        return jsonify({
            'book_id': book_id,
            'title': title,
            'author': author,
            'reviews': reviews
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500

# --- RUN ---
if __name__ == '__main__':
    app.run(host='127.0.0.1', debug=True)            