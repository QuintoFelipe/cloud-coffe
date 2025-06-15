# Cloud Coffee Agent

A multi-language Telegram chatbot for ordering coffee, tracking inventory, and syncing data to Google Sheets & BigQuery, plus a Looker dashboard for analytics.

---

## 🚀 Features

* **Order Processing**: Users can place orders in any language. Supports multiple items and quantities (including spelled-out numbers).
* **Inventory Checks**: Users can ask for current inventory in any language. Bot returns low-stock alerts.
* **Low-Stock Alerts**: Automatically notifies chat when an order causes any ingredient to fall below its minimum threshold.
* **Weather Data**: Captures current weather in Medellín for each order via OpenWeatherMap API.
* **Data Sync**:

  * Google Sheets as primary data store for `Products`, `Recipes`, `Orders`, and `Inventory`.
  * BigQuery Data Transfer syncs Sheets to BigQuery for analytics.
* **Looker Dashboard**: Visualize sales, revenue trends, and inventory health.

---

## 🧩 Architecture

![Untitled-2025-06-14-1953](https://github.com/user-attachments/assets/02055d91-860d-4d65-8b63-e324abe386ad)


---

## 🛠️ Getting Started

### Prerequisites

* Python 3.10
* Docker
* Google Cloud project with:

  * BigQuery
  * BigQuery Data Transfer API enabled
  * Google Sheets API
  * Cloud Run (or another host for your FastAPI service)
* Telegram Bot token (via BotFather)
* OpenWeatherMap API key

### 1. Clone the repository

```bash
git clone https://github.com/your-org/cloud-coffee.git
cd cloud-coffee
```

### 2. Create and populate Google Sheets

1. Create a new Google Sheet with tabs:

   * **Products**: `product`, `price_unit_dolars`
   * **Recipes**: `item`, `ingredient`, `quantity_per_unit`
   * **Orders**: `ID`, `product`, `timestamp`, `Quantity`, `TotalPrice`, `Weather`
   * **Inventory**: `item`, `quantity`, `unit`, `minimum_level`
2. Note the Sheet ID (`docs.google.com/spreadsheets/d/<SHEET_ID>/...`).

### 3. Configure environment

Create a `.env` file:

```dotenv
TELEGRAM_TOKEN=<your-telegram-bot-token>
GOOGLE_SHEET_ID=<your-sheet-id>
GEMINI_API_KEY=<your-gemini-key>
OWM_API_KEY=<your-openweathermap-key>
GCP_PROJECT=<your-gcp-project-id>
```

### 4. Install dependencies & run locally

```bash
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### 5. Expose webhook (local testing)

Use `ngrok` or similar:

```bash
ngrok http 8000
```

Point your Telegram webhook to the `ngrok` HTTPS URL + `/webhook`.

### 6. Deploy to Cloud Run (CI/CD)

The included GitHub Actions (`.github/workflows/ci.yml`) handles lint, tests, and deploy:

* Ensure GitHub secrets: `GCP_SA_KEY`, `TELEGRAM_TOKEN`, `GOOGLE_SHEET_ID`, `GEMINI_API_KEY`, `OWM_API_KEY`, `GCP_PROJECT`, `CLOUD_RUN_SA_EMAIL`, `GCP_REGION`.
* Push to `main` branch and let CI run.

---

## 📊 BigQuery & Looker Analytics

1. Use BigQuery Data Transfer (or CLI) to sync each sheet tab into BigQuery tables in dataset `cloud_coffe_data`:

   * `orders`, `inventory`, `products`, `recipes`
2. Confirm table schemas:

   ```sql
   -- orders
   ID STRING, product STRING, timestamp DATETIME, Quantity INT64, TotalPrice FLOAT64, Weather STRING

   -- inventory
   item STRING, quantity FLOAT64, unit STRING, minimum_level FLOAT64
   ```
3. Once your data is synced into BigQuery, you can also create your own custom dashboards using Looker Studio or Data Studio. 👉 [Example Looker Studio Dashboard](https://lookerstudio.google.com/reporting/23b9ffa3-103c-4421-bbbd-0cf8a1bb566a)

---

## 🤝 Contribution

Feel free to open issues or pull requests. Ensure tests pass via `pytest` and code follows existing style.

## 📄 License

MIT © Juan Felipe Quinto Rios

## 👤 Developer Contact

If you have questions or feedback about this project, feel free to reach out:

* **Name:** Juan Felipe Quinto Rios
* **Email:** [quintoriosjuanfelip@gmail.com](mailto:quintoriosjuanfelip@gmail.com)
* **GitHub:** [https://github.com/QuintoFelipe](https://github.com/QuintoFelipe)
* **LinkedIn:** [https://www.linkedin.com/in/juan-felipe-quinto-rios/](https://www.linkedin.com/in/juan-felipe-quinto-rios/)
