# PlayBook: OpenAI & Stripe Setup

## Option A: Use `.streamlit/secrets.toml` (recommended)

### 1. Open the secrets file

- Path: **`playbook/.streamlit/secrets.toml`**
- If it doesn’t exist, create the folder `.streamlit` and the file `secrets.toml` inside it.

### 2. Add your OpenAI API key

In `secrets.toml`, add an `[openai]` section with your key:

```toml
[openai]
api_key = "sk-proj-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
```

- Get a key at: https://platform.openai.com/api-keys  
- Create one, copy it, and paste it as the value of `api_key` (keep the quotes).
- **Do not share this file or commit it to git.** Add `.streamlit/secrets.toml` to `.gitignore`.

### 3. Add or update your Stripe test payment link

In the **same** `secrets.toml` file, you should have:

```toml
[stripe]
payment_link = "https://buy.stripe.com/test_xxxxxxxxxxxx"
```

- Get a test Payment Link in Stripe: Dashboard → Payments → Payment links → Create link (use Test mode).
- Copy the link and paste it as the value of `payment_link` (keep the quotes).

### 4. Full example `secrets.toml`

Your file can look exactly like this (with your real values):

```toml
[openai]
api_key = "sk-proj-your-openai-key-here"

[stripe]
payment_link = "https://buy.stripe.com/test_your-stripe-link-here"
```

### 5. Restart the app

- Stop Streamlit (Ctrl+C in the terminal).
- Start again: `streamlit run app.py`
- Generate an itinerary; the summary should use OpenAI for enthusiastic copy, and the “Confirm Plan — Pay to lock” button should open your Stripe test link.

---

## Option B: Use environment variables

If you prefer not to use `secrets.toml`:

### OpenAI

- **Variable name:** `OPENAI_API_KEY`
- **Value:** your OpenAI API key (e.g. `sk-proj-...`)

**Mac/Linux (current terminal only):**

```bash
export OPENAI_API_KEY="sk-proj-your-key-here"
streamlit run app.py
```

**Windows (Command Prompt):**

```cmd
set OPENAI_API_KEY=sk-proj-your-key-here
streamlit run app.py
```

### Stripe

- **Variable name:** `PLAYBOOK_STRIPE_PAYMENT_LINK`
- **Value:** your Stripe test payment link (e.g. `https://buy.stripe.com/test_...`)

**Mac/Linux:**

```bash
export PLAYBOOK_STRIPE_PAYMENT_LINK="https://buy.stripe.com/test_xxxx"
```

**Windows:**

```cmd
set PLAYBOOK_STRIPE_PAYMENT_LINK=https://buy.stripe.com/test_xxxx
```

---

## Security

- **Never commit** `.streamlit/secrets.toml` or put real keys in code.
- Add to `.gitignore`:  
  `.streamlit/secrets.toml`
- If you use env vars, don’t paste keys into shared scripts or docs.

## Troubleshooting

- **OpenAI not used:** Confirm the key is in `secrets.toml` under `[openai]` → `api_key` or in `OPENAI_API_KEY`, then restart Streamlit. Check the terminal for Python errors.
- **Stripe button does nothing or wrong link:** Confirm `payment_link` in `[stripe]` is the full test link and that you restarted the app after editing `secrets.toml`.
