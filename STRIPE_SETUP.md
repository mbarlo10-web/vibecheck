# Stripe payment link – step by step

## 1. Open your secrets file

- In **Cursor**: `Cmd+P` (Mac) or `Ctrl+P` (Windows) → type **`secrets.toml`** → open **`.streamlit/secrets.toml`**.
- Or in Terminal:  
  `open /Users/markbarlow/Desktop/vibecheck/.streamlit/secrets.toml`

## 2. Add the Stripe section

In `secrets.toml` you must have a **`[stripe]`** section and **`payment_link`** on one line, in quotes:

```toml
[stripe]
payment_link = "https://buy.stripe.com/test_cNifZbchj20o4vB0Pq2go00"
```

- Use **your** test link from the Stripe Dashboard (replace the URL above if needed).
- No spaces around `=`.
- The link must be in **double quotes**.
- Nothing else on the same line as `payment_link`.

## 3. Save the file

Save `secrets.toml` (e.g. `Cmd+S`).

## 4. Run the app from the project folder

Stripe is read from **`vibecheck/.streamlit/secrets.toml`** (next to `app.py`). You must start Streamlit from the **vibecheck** folder:

```bash
cd /Users/markbarlow/Desktop/vibecheck
source venv/bin/activate
streamlit run app.py
```

If you run from another folder (e.g. `Desktop`), the app may not find `secrets.toml` and the warning will stay.

## 5. Check that it worked

1. Open the app in the browser (e.g. `http://localhost:8501`).
2. Go to **Confirm Plan**.
3. You should **not** see: “Stripe payment link not configured”.
4. You should see the **“Confirm Plan — Pay to lock ($99)”** button; clicking it should open your Stripe checkout.

## If the warning still appears

- Confirm the file path is exactly:  
  **`vibecheck/.streamlit/secrets.toml`**  
  (inside the same folder as `app.py`).
- Confirm you’re running:  
  `streamlit run app.py`  
  from **`/Users/markbarlow/Desktop/vibecheck`**.
- After any change to `secrets.toml`, **restart** Streamlit (Ctrl+C, then run the command again).
- Check for typos: section must be **`[stripe]`**, key must be **`payment_link`**.
