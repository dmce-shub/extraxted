
import requests
import asyncio
import json

from pyrogram import Client, filters
from pyrogram.types import Message


# Make sure your main bot instance is named "app"
# If your bot instance has another name, replace "app" below.


@app.on_message(filters.command(["cp"]))
async def account_login(app: Client, m: Message):

    editable = await m.reply_text(
        "**🔐 Classplus Login**\n\n"
        "Please send your Classplus access token."
    )

    try:
        # Receive token
        input1: Message = await app.listen(
            editable.chat.id,
            filters=filters.text,
            timeout=60
        )

        if not input1.text:
            await editable.edit("❌ No token received.")
            return

        token = input1.text.strip()

        # Clean token
        if token.lower().startswith("bearer "):
            token = token[7:].strip()

        # Validate basic input
        if not token or len(token) < 10:
            await editable.edit("❌ Invalid token format.")
            return

        # Classplus API headers
        headers = {
            "accept": "application/json, text/plain, */*",
            "accept-language": "en",
            "api-version": "28",
            "cache-control": "no-cache",
            "device-id": "516",
            "origin": "https://web.classplusapp.com",
            "pragma": "no-cache",
            "referer": "https://web.classplusapp.com/",
            "region": "IN",
            "user-agent": (
                "Mozilla/5.0 (X11; Linux x86_64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/107.0.0.0 Safari/537.36"
            ),
            "x-access-token": token
        }

        # API endpoint
        url = (
            "https://api.classplusapp.com/"
            "v2/batches/details"
            "?limit=20&offset=0&sortBy=createdAt"
        )

        await editable.edit(
            "⏳ **Checking Classplus authentication...**"
        )

        # Make API request without blocking bot
        def fetch_data():
            with requests.Session() as session:
                return session.get(
                    url,
                    headers=headers,
                    timeout=25
                )

        response = await asyncio.to_thread(fetch_data)

        # Handle HTTP errors
        if response.status_code != 200:

            try:
                error_data = response.json()
                error_text = json.dumps(
                    error_data,
                    indent=2
                )
            except ValueError:
                error_text = response.text

            await editable.edit(
                "❌ **Classplus API Request Failed**\n\n"
                f"**HTTP Status:** `{response.status_code}`\n\n"
                f"**Server Response:**\n"
                f"```{error_text[:2500]}```\n\n"
                "Please check the API response."
            )
            return

        # Parse JSON
        try:
            result = response.json()

        except ValueError:
            await editable.edit(
                "❌ **Invalid API Response**\n\n"
                "Classplus did not return valid JSON.\n\n"
                f"Response:\n`{response.text[:1500]}`"
            )
            return

        if not isinstance(result, dict):
            await editable.edit(
                "❌ Unexpected API response format."
            )
            return

        # Extract response data
        data = result.get("data", {})

        batches = []

        if isinstance(data, list):
            batches = data

        elif isinstance(data, dict):

            possible_keys = [
                "totalBatches",
                "batches",
                "batchList",
                "items"
            ]

            for key in possible_keys:

                value = data.get(key)

                if isinstance(value, list):
                    batches = value
                    break

        # Check for batches
        if not batches:

            response_preview = json.dumps(
                result,
                indent=2
            )

            await editable.edit(
                "⚠️ **API Request Successful, But No Batches Found**\n\n"
                "**Response received:**\n"
                f"```{response_preview[:2500]}```"
            )
            return

        # Delete token message for privacy
        try:
            await input1.delete()
        except Exception:
            pass

        # Format batches
        output = ""
        skipped = 0

        for item in batches:

            if not isinstance(item, dict):
                skipped += 1
                continue

            batch_name = item.get(
                "batchName",
                "N/A"
            )

            batch_id = (
                item.get("batchId")
                or item.get("id")
                or "N/A"
            )

            entry = (
                f"`{batch_id}` - **{batch_name}**\n\n"
            )

            if len(output) + len(entry) > 3500:

                await m.reply_text(
                    "**✅ Classplus Login Successful!**\n\n"
                    "**BATCH ID - BATCH NAME**\n\n"
                    + output
                )

                output = ""

            output += entry

        # Send remaining batches
        if output:

            await editable.edit(
                "**✅ Classplus Login Successful!**\n\n"
                "**BATCH ID - BATCH NAME**\n\n"
                + output
            )

        elif skipped:
            await editable.edit(
                "⚠️ No valid batch entries were found."
            )

    except asyncio.TimeoutError:

        await editable.edit(
            "⌛ **Time Expired**\n\n"
            "You did not send a token within 60 seconds."
        )

    except requests.RequestException as e:

        await editable.edit(
            "❌ **Network Error**\n\n"
            f"`{str(e)[:1000]}`"
        )

    except Exception as e:

        await editable.edit(
            "❌ **Unexpected Error**\n\n"
            f"`{str(e)[:1000]}`"
        )
